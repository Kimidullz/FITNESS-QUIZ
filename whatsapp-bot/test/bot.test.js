import test from "node:test";
import assert from "node:assert/strict";
import { handleMessage } from "../src/index.js";
import worker from "../src/index.js";
import { parseWebhook, validSignature } from "../src/whatsapp.js";
import { SYSTEM, OUTPUT_SCHEMA } from "../src/prompt.js";

function fakeKV() {
  const m = new Map();
  return {
    m,
    async get(k, type) { const v = m.get(k); return v == null ? null : type === "json" ? JSON.parse(v) : v; },
    async put(k, v) { m.set(k, v); },
  };
}
function fakeWA() {
  const sent = [];
  return {
    sent,
    async sendText(env, to, text) { if (env.failTo === to) { const e = new Error("window"); e.code = 131047; throw e; } sent.push({ to, text }); },
    async sendTemplate(env, to, name, lang, params) { sent.push({ to, template: name, params }); },
    async markReadTyping() {},
  };
}
const env = () => ({ BOT_KV: fakeKV(), KIMI_WHATSAPP: "60111111111", ZARA_WHATSAPP: "60122222222", ANTHROPIC_API_KEY: "x" });
let n = 0;
const msg = (text, from = "60199999999", extra = {}) => ({ id: `m${++n}`, from, name: "Aina", type: "text", text, timestamp: Math.floor(Date.now() / 1000), ...extra });
const reply = (over = {}) => async () => ({
  reply: "Hi! Saya assistant Coach Kimi 😊 Boleh saya tahu nama awak?",
  status: "chatting", handoff: false, handoff_coach: "kimi", handoff_reason: "",
  lead: { name: "", sex: "unknown", language: "ms", goal: "", why_now: "", obstacle: "", commitment: "", assessment_done: "unknown", notes: "" },
  ...over,
});

test("normal chat: replies and remembers", async () => {
  const e = env(), wa = fakeWA();
  await handleMessage(e, msg("hi nak tanya pasal program"), { wa, think: reply() });
  assert.equal(wa.sent.length, 1);
  assert.match(wa.sent[0].text, /assistant Coach Kimi/);
  const st = JSON.parse(e.BOT_KV.m.get("lead:60199999999"));
  assert.equal(st.history.length, 2);
});

test("duplicate delivery is ignored", async () => {
  const e = env(), wa = fakeWA();
  const m = msg("hello");
  await handleMessage(e, m, { wa, think: reply() });
  await handleMessage(e, m, { wa, think: reply() });
  assert.equal(wa.sent.length, 1);
});

test("hot lead goes to Zara with alert and link, then bot goes quiet", async () => {
  const e = env(), wa = fakeWA();
  const hot = reply({ status: "hot", handoff: true, handoff_coach: "zara", handoff_reason: "Wants to start, asked price",
    lead: { name: "Aina", sex: "f", language: "ms", goal: "-5kg", why_now: "kenduri", obstacle: "", commitment: "8", assessment_done: "yes", notes: "" },
    reply: "Coach Zara akan WhatsApp awak nanti!" });
  await handleMessage(e, msg("macam mana nak join?"), { wa, think: hot });
  const toLead = wa.sent.filter((s) => s.to === "60199999999");
  const toZara = wa.sent.filter((s) => s.to === "60122222222");
  assert.equal(toLead.length, 2);
  assert.match(toLead[1].text, /wa\.me\/60122222222/);
  assert.equal(toZara.length, 1);
  assert.match(toZara[0].text, /HOT lead/);
  assert.match(toZara[0].text, /wa\.me\/60199999999/);

  // Next message: no Claude call, coach gets it, lead not spammed again within 6h.
  let called = false;
  await handleMessage(e, msg("ok tunggu"), { wa, think: async () => { called = true; } });
  assert.equal(called, false);
  assert.equal(wa.sent.filter((s) => s.to === "60122222222").length, 2);
  assert.equal(wa.sent.filter((s) => s.to === "60199999999").length, 2);
});

test("medical words force a handoff even if the model missed it", async () => {
  const e = env(), wa = fakeWA();
  await handleMessage(e, msg("saya tengah menyusu, boleh minum shake?"), { wa, think: reply({ lead: { ...(await reply()()).lead, sex: "f" } }) });
  const st = JSON.parse(e.BOT_KV.m.get("lead:60199999999"));
  assert.equal(st.status, "medical");
  assert.equal(st.handedOff.coach, "zara");
});

test("Claude error: polite reply and handoff to a coach", async () => {
  const e = env(), wa = fakeWA();
  await handleMessage(e, msg("hello"), { wa, think: async () => { throw new Error("timeout"); } });
  assert.match(wa.sent[0].text, /coach/i);
  assert.ok(wa.sent.some((s) => s.to === "60111111111" && /timeout/.test(s.text)));
});

test("alert falls back to template outside the 24h window", async () => {
  const e = { ...env(), failTo: "60111111111", LEAD_ALERT_TEMPLATE: "lead_alert" }, wa = fakeWA();
  await handleMessage(e, msg("nak join"), { wa, think: reply({ handoff: true, status: "hot", handoff_reason: "Wants to start" }) });
  const t = wa.sent.find((s) => s.template);
  assert.equal(t.template, "lead_alert");
  assert.deepEqual(t.params.slice(1), ["+60199999999", "Wants to start"]);
});

test("coach commands: resume lets the bot reply again", async () => {
  const e = env(), wa = fakeWA();
  await handleMessage(e, msg("nak join"), { wa, think: reply({ handoff: true, status: "hot" }) });
  await handleMessage(e, msg("resume 0199999999", "60111111111"), { wa, think: reply() });
  assert.match(wa.sent.at(-1).text, /reply to \+60199999999 again/);
  const before = wa.sent.length;
  await handleMessage(e, msg("satu lagi soalan"), { wa, think: reply() });
  assert.equal(wa.sent.length, before + 1);
});

test("stop word opts out", async () => {
  const e = env(), wa = fakeWA();
  await handleMessage(e, msg("stop"), { wa, think: async () => { throw new Error("should not call"); } });
  assert.match(wa.sent[0].text, /takkan mesej/);
});

test("voice notes get a type-please reply", async () => {
  const e = env(), wa = fakeWA();
  await handleMessage(e, msg("", undefined, { type: "audio" }), { wa, think: reply() });
  assert.match(wa.sent[0].text, /taip/);
});

test("monthly limit hands off without calling Claude", async () => {
  const e = { ...env(), MONTHLY_REPLY_LIMIT: "0" }, wa = fakeWA();
  await handleMessage(e, msg("hi"), { wa, think: async () => { throw new Error("should not call"); } });
  assert.ok(wa.sent.some((s) => s.to === "60111111111" && /monthly limit/.test(s.text)));
});

test("webhook parsing and signature check", async () => {
  const payload = { entry: [{ changes: [{ value: { contacts: [{ wa_id: "6012", profile: { name: "Ali" } }], messages: [{ id: "w1", from: "6012", type: "text", text: { body: " hi " }, timestamp: "1" }] } }] }] };
  assert.deepEqual(parseWebhook(payload)[0], { id: "w1", from: "6012", name: "Ali", type: "text", text: "hi", timestamp: 1 });
  const body = JSON.stringify(payload);
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode("s3cret"), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const hex = [...new Uint8Array(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body)))].map((b) => b.toString(16).padStart(2, "0")).join("");
  assert.equal(await validSignature("s3cret", body, `sha256=${hex}`), true);
  assert.equal(await validSignature("s3cret", body, `sha256=${hex.replace(/^./, "0")}`), hex[0] === "0");
  assert.equal(await validSignature("", body, `sha256=${hex}`), false);
});

test("webhook verify handshake", async () => {
  const e = { WHATSAPP_VERIFY_TOKEN: "abc" };
  const ok = await worker.fetch(new Request("https://x/webhook?hub.mode=subscribe&hub.verify_token=abc&hub.challenge=42"), e, {});
  assert.equal(await ok.text(), "42");
  const bad = await worker.fetch(new Request("https://x/webhook?hub.mode=subscribe&hub.verify_token=no&hub.challenge=42"), e, {});
  assert.equal(bad.status, 403);
  const unsigned = await worker.fetch(new Request("https://x/webhook", { method: "POST", body: "{}" }), { WHATSAPP_APP_SECRET: "s" }, {});
  assert.equal(unsigned.status, 401);
});

test("prompt includes knowledge and schema is strict", () => {
  assert.match(SYSTEM, /RM259/);
  assert.match(SYSTEM, /wedotransformations\.com\/coach/);
  assert.equal(OUTPUT_SCHEMA.additionalProperties, false);
  assert.deepEqual(new Set(OUTPUT_SCHEMA.required), new Set(Object.keys(OUTPUT_SCHEMA.properties)));
});
