// WDT WhatsApp lead bot: Cloudflare Worker that receives WhatsApp messages from Meta,
// answers with Claude, and hands hot leads to Coach Kimi or Coach Zara.
import { think, assistantTurn, DEFAULT_MODEL } from "./claude.js";
import { sendText, sendTemplate, markReadTyping, parseWebhook, validSignature } from "./whatsapp.js";

const DAY = 86400;
const MAX_TURNS = 30; // turns of history kept per person
const MEDICAL = /\b(hamil|pregnan\w*|mengandung|menyusu\w*|breastfe\w*|bf\s?susu|pantang|diabet\w*|kencing manis|darah tinggi|high blood|blood pressure|hypertens\w*|jantung|heart (problem|disease|attack)|buah pinggang|kidney|dialysis|thyroid|tiroid|pcos|ubat|medication|insulin|metformin|surgery|pembedahan|operation|bulimi\w*|anorexi\w*|eating disorder)\b/i;
const STOP_WORDS = /^(stop|berhenti|unsubscribe|jangan mesej|don'?t message)\b/i;

const json = (obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json" } });
const today = () => new Date(Date.now() + 8 * 3600e3).toISOString().slice(0, 10); // Malaysia date
const month = () => today().slice(0, 7);
const digits = (s) => String(s || "").replace(/\D/g, "");

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Meta checks the webhook once when you connect it.
    if (request.method === "GET" && url.pathname === "/webhook") {
      const ok = url.searchParams.get("hub.mode") === "subscribe" && url.searchParams.get("hub.verify_token") === env.WHATSAPP_VERIFY_TOKEN;
      return ok ? new Response(url.searchParams.get("hub.challenge") || "") : new Response("forbidden", { status: 403 });
    }

    if (request.method === "POST" && url.pathname === "/webhook") {
      const raw = await request.text();
      if (!(await validSignature(env.WHATSAPP_APP_SECRET, raw, request.headers.get("x-hub-signature-256")))) {
        return new Response("bad signature", { status: 401 });
      }
      let payload;
      try { payload = JSON.parse(raw); } catch { return new Response("bad json", { status: 400 }); }
      const msgs = parseWebhook(payload);
      // Answer Meta straight away, do the work in the background.
      ctx.waitUntil(Promise.all(msgs.map((m) => handleMessage(env, m).catch((e) => console.error("handle", e?.message)))));
      return new Response("ok");
    }

    if (url.pathname === "/") return json({ ok: true, bot: "WDT lead bot", model: env.BOT_MODEL || DEFAULT_MODEL });
    return new Response("not found", { status: 404 });
  },
};

// ---------- main flow ----------

export async function handleMessage(env, msg, deps = {}) {
  const wa = deps.wa || { sendText, sendTemplate, markReadTyping };
  const brain = deps.think || think;
  const kv = env.BOT_KV;

  // Meta sometimes delivers the same message twice.
  if (await kv.get(`seen:${msg.id}`)) return;
  await kv.put(`seen:${msg.id}`, "1", { expirationTtl: DAY });
  // Ignore very old messages (e.g. replayed after downtime).
  if (msg.timestamp && Date.now() / 1000 - msg.timestamp > 6 * 3600) return;

  const coaches = coachNumbers(env);
  if (Object.values(coaches).includes(msg.from)) return handleCoach(env, msg, wa);

  const key = `lead:${msg.from}`;
  const st = (await kv.get(key, "json")) || { history: [], lead: null, status: "new", firstSeen: Date.now() };
  const save = () => kv.put(key, JSON.stringify(st), { expirationTtl: 90 * DAY });
  const ms = (st.lead?.language || "ms") === "ms";

  if (!msg.text) {
    // Voice notes, photos, stickers: we only read text for now.
    if (msg.type === "reaction") return;
    await wa.sendText(env, msg.from, ms
      ? "Maaf, buat masa ni saya hanya boleh baca mesej bertulis 🙏 Boleh taip soalan awak?"
      : "Sorry, for now I can only read typed messages 🙏 Could you type your question?");
    return;
  }

  if (STOP_WORDS.test(msg.text)) {
    st.optedOut = true; st.status = "not_interested"; await save();
    await wa.sendText(env, msg.from, ms ? "Baik, saya takkan mesej lagi. Terima kasih! Kalau perlukan apa-apa, mesej je bila-bila 😊" : "Okay, I won't message again. Thank you! Message anytime if you need anything 😊");
    return;
  }
  if (st.optedOut) { st.optedOut = false; }

  // A coach has taken over this chat: pass the message on, don't let the bot talk over them.
  if (st.paused || st.handedOff) {
    st.history.push({ role: "user", text: msg.text }); trim(st); await save();
    const coach = st.handedOff?.coach || "kimi";
    await notifyCoach(env, wa, coach, `💬 ${displayName(st, msg)} (+${msg.from}) wrote to the bot again:\n"${msg.text.slice(0, 500)}"\nChat: https://wa.me/${msg.from}`, st, msg, "Wrote again");
    const lastNote = st.lastWaitNote || 0;
    if (Date.now() - lastNote > 6 * 3600e3) {
      st.lastWaitNote = Date.now(); await save();
      await wa.sendText(env, msg.from, waitNote(env, coach, ms));
    }
    return;
  }

  // Spend guards: per person per day, and for the whole bot per month.
  if (st.day !== today()) { st.day = today(); st.dayCount = 0; }
  st.dayCount = (st.dayCount || 0) + 1;
  const monthKey = `count:${month()}`;
  const monthCount = Number((await kv.get(monthKey)) || 0) + 1;
  await kv.put(monthKey, String(monthCount), { expirationTtl: 40 * DAY });
  const overDay = st.dayCount > Number(env.DAILY_LIMIT_PER_PERSON || 40);
  const overMonth = monthCount > Number(env.MONTHLY_REPLY_LIMIT || 3000);

  await wa.markReadTyping(env, msg.id);

  let out;
  if (overDay || overMonth) {
    out = forcedHandoff(st, overMonth ? "Bot monthly limit reached, please reply personally" : "Very long chat today, please take over", ms);
  } else {
    try {
      out = await brain({ apiKey: env.ANTHROPIC_API_KEY, model: env.BOT_MODEL, history: st.history, lead: st.lead, text: msg.text, contactName: msg.name });
    } catch (e) {
      console.error("claude", e?.message);
      out = forcedHandoff(st, `Bot could not answer (${e?.message || "error"}), please reply personally`, ms);
    }
  }

  // Safety net: medical words always go to a coach, even if the model missed it.
  if (MEDICAL.test(msg.text) && !out.handoff) {
    out.handoff = true;
    out.status = "medical";
    out.handoff_coach = out.lead?.sex === "m" ? "kimi" : out.lead?.sex === "f" ? "zara" : out.handoff_coach || "kimi";
    out.handoff_reason = `Medical/safety mention: "${msg.text.slice(0, 120)}"`;
  }

  st.history.push({ role: "user", text: msg.text });
  st.history.push({ role: "assistant", text: assistantTurn(out) });
  trim(st);
  const prevStatus = st.status;
  st.lead = { ...(st.lead || {}), ...(out.lead || {}) };
  st.status = out.status || st.status;

  await wa.sendText(env, msg.from, out.reply);

  if (out.handoff) {
    const coach = coaches[out.handoff_coach] ? out.handoff_coach : "kimi";
    st.handedOff = { coach, at: Date.now(), reason: out.handoff_reason };
    st.lastWaitNote = Date.now();
    await save();
    const link = coaches[coach] ? `https://wa.me/${coaches[coach]}` : "";
    if (link) await wa.sendText(env, msg.from, ms ? `Kalau nak terus chat dengan ${coachName(coach)}: ${link}` : `To chat with ${coachName(coach)} directly: ${link}`);
    await notifyCoach(env, wa, coach, leadAlert(st, msg, out), st, msg, out.handoff_reason);
    await addRecentHandoff(kv, { from: msg.from, name: displayName(st, msg), coach, reason: out.handoff_reason, status: st.status, at: Date.now() });
  } else {
    await save();
  }

  if (prevStatus === "new" || out.handoff || prevStatus !== st.status) await logToSheet(env, st, msg, out);
}

// ---------- coaches ----------

function coachNumbers(env) {
  const c = {};
  if (digits(env.KIMI_WHATSAPP)) c.kimi = digits(env.KIMI_WHATSAPP);
  if (digits(env.ZARA_WHATSAPP)) c.zara = digits(env.ZARA_WHATSAPP);
  return c;
}
const coachName = (c) => (c === "zara" ? "Coach Zara" : "Coach Kimi");

function waitNote(env, coach, ms) {
  const n = coachNumbers(env)[coach];
  const link = n ? ` ${ms ? "Atau terus" : "Or go straight to"}: https://wa.me/${n}` : "";
  return ms
    ? `Terima kasih! Saya dah sampaikan pada ${coachName(coach)}, dia akan WhatsApp awak secepat mungkin 😊${link}`
    : `Thank you! I've passed this to ${coachName(coach)}, who will WhatsApp you as soon as possible 😊${link}`;
}

function forcedHandoff(st, reason, ms) {
  const sex = st.lead?.sex;
  return {
    reply: ms ? "Terima kasih! Saya sampaikan pada coach, nanti coach sendiri akan WhatsApp awak ya 😊" : "Thank you! I'll pass this to a coach, who will WhatsApp you personally 😊",
    status: st.status === "new" ? "chatting" : st.status,
    handoff: true,
    handoff_coach: sex === "f" ? "zara" : "kimi",
    handoff_reason: reason,
    lead: st.lead || {},
  };
}

function displayName(st, msg) {
  return st.lead?.name || msg.name || "Someone";
}

function leadAlert(st, msg, out) {
  const l = st.lead || {};
  const heat = st.status === "hot" ? "🔥 HOT lead" : st.status === "medical" ? "⚕️ Lead with a health question" : "👋 Lead to follow up";
  const lines = [
    `${heat} from the bot`,
    `Name: ${displayName(st, msg)}${msg.name && msg.name !== l.name ? ` (WhatsApp: ${msg.name})` : ""}`,
    `Chat: https://wa.me/${msg.from}`,
    `Why: ${out.handoff_reason || "-"}`,
  ];
  const facts = [["Goal", l.goal], ["Why now", l.why_now], ["Obstacle", l.obstacle], ["Commitment", l.commitment], ["Body assessment", l.assessment_done], ["Notes", l.notes]]
    .filter(([, v]) => v && v !== "unknown").map(([k, v]) => `${k}: ${v}`);
  if (facts.length) lines.push(facts.join("\n"));
  const last = st.history.slice(-6).map((h) => `${h.role === "user" ? "Them" : "Bot"}: ${h.text.replace(/\s+/g, " ").slice(0, 160)}`);
  lines.push("Last messages:\n" + last.join("\n"));
  lines.push(`The bot has stopped replying to them. Send "resume ${msg.from}" here to let it carry on.`);
  return lines.join("\n");
}

async function notifyCoach(env, wa, coach, text, st, msg, reason) {
  const to = coachNumbers(env)[coach] || coachNumbers(env).kimi;
  if (!to) return;
  try {
    await wa.sendText(env, to, text);
  } catch (e) {
    // Outside WhatsApp's 24-hour window a free-form message is refused; use the approved template instead.
    if (env.LEAD_ALERT_TEMPLATE) {
      try {
        await wa.sendTemplate(env, to, env.LEAD_ALERT_TEMPLATE, env.LEAD_ALERT_LANG || "en", [displayName(st, msg), `+${msg.from}`, reason || "New lead"]);
      } catch (e2) { console.error("template", e2?.message); }
    } else console.error("alert", e?.message);
  }
}

async function addRecentHandoff(kv, item) {
  const list = (await kv.get("recent-handoffs", "json")) || [];
  list.unshift(item);
  await kv.put("recent-handoffs", JSON.stringify(list.slice(0, 30)));
}

// Messages from Kimi's or Zara's own number to the bot = commands.
async function handleCoach(env, msg, wa) {
  const kv = env.BOT_KV;
  const t = msg.text.trim();
  const m = t.match(/^(pause|stop|resume|start)\s+\+?([\d\s-]{8,})$/i);
  if (m) {
    const num = digits(m[2]).replace(/^0/, "60");
    const key = `lead:${num}`;
    const st = (await kv.get(key, "json")) || { history: [], lead: null, status: "new", firstSeen: Date.now() };
    const resume = /resume|start/i.test(m[1]);
    st.paused = !resume;
    if (resume) { st.handedOff = null; st.lastWaitNote = 0; }
    await kv.put(key, JSON.stringify(st), { expirationTtl: 90 * DAY });
    await wa.sendText(env, msg.from, resume ? `✅ The bot will reply to +${num} again.` : `⏸️ The bot will stay quiet with +${num}. Send "resume ${num}" to switch it back on.`);
    return;
  }
  if (/^(leads|status|list)$/i.test(t)) {
    const list = (await kv.get("recent-handoffs", "json")) || [];
    const n = Number((await kv.get(`count:${month()}`)) || 0);
    const lines = list.slice(0, 10).map((x) => `• ${x.name} (${coachName(x.coach)}, ${x.status}) wa.me/${x.from}\n  ${x.reason || ""}`);
    await wa.sendText(env, msg.from, `Last handoffs:\n${lines.join("\n") || "none yet"}\n\nBot replies this month: ${n}`);
    return;
  }
  await wa.sendText(env, msg.from,
    "Hi Coach! Commands:\n• leads (last 10 handoffs)\n• pause 60123456789 (bot goes quiet with that person)\n• resume 60123456789 (bot replies again)\n\nTip: message me once a day so lead alerts arrive as normal messages.");
}

// ---------- extras ----------

function trim(st) {
  if (st.history.length > MAX_TURNS) st.history = st.history.slice(-MAX_TURNS);
  // History must start with the person's turn.
  while (st.history.length && st.history[0].role !== "user") st.history.shift();
}

async function logToSheet(env, st, msg, out) {
  if (!env.LEADS_SHEET_URL) return;
  const l = st.lead || {};
  const params = new URLSearchParams({
    type: "bot", via: "whatsapp-bot", name: l.name || msg.name || "", phone: `+${msg.from}`, result: st.status,
    goal: l.goal || "", why: l.why_now || "", commit: l.commitment || "", weak: l.obstacle || "",
    coach: out.handoff ? coachName(st.handedOff?.coach) : "", answers: out.handoff_reason || l.notes || "", src: "WhatsApp bot",
  });
  await fetch(`${env.LEADS_SHEET_URL}?${params}`).catch(() => {});
}
