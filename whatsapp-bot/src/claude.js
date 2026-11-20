import Anthropic from "@anthropic-ai/sdk";
import { SYSTEM, OUTPUT_SCHEMA } from "./prompt.js";

export const DEFAULT_MODEL = "claude-opus-5-5";

// Malaysia time, so the bot can say "tonight" or "tomorrow" sensibly.
function myTime(now = new Date()) {
  return now.toLocaleString("en-MY", { timeZone: "Asia/Kuala_Lumpur", weekday: "short", day: "numeric", month: "short", hour: "numeric", minute: "2-digit" });
}

function profileLine(lead) {
  if (!lead) return "Nothing known yet (new person).";
  const bits = Object.entries(lead).filter(([, v]) => v && v !== "unknown").map(([k, v]) => `${k}: ${v}`);
  return bits.length ? bits.join("; ") : "Nothing known yet.";
}

/**
 * Ask Claude for the next reply.
 * history: [{role:"user"|"assistant", text}] (earlier turns, raw text, oldest first)
 * Returns the parsed JSON object from OUTPUT_SCHEMA plus usage info.
 */
export async function think({ apiKey, model, history, lead, text, contactName, client }) {
  // Cloudflare keeps background work alive about 30 seconds, so keep this short.
  client = client || new Anthropic({ apiKey, maxRetries: 1, timeout: 25_000 });

  const context =
    `[Context, not from the person. Time in Malaysia: ${myTime()}. WhatsApp profile name: ${contactName || "unknown"}. ` +
    `What we know so far: ${profileLine(lead)}]\n\n${text}`;
  // Merge back-to-back turns from the same side (e.g. messages sent while a coach had the chat).
  const messages = [];
  for (const m of [...history.map((h) => ({ role: h.role, content: h.text })), { role: "user", content: context }]) {
    const last = messages[messages.length - 1];
    if (last && last.role === m.role) last.content += "\n\n" + m.content;
    else messages.push({ ...m });
  }

  const res = await client.beta.messages.create({
    model: model || DEFAULT_MODEL,
    max_tokens: 4000,
    system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
    messages,
    output_config: { effort: "low", format: { type: "json_schema", schema: OUTPUT_SCHEMA } },
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
  });

  if (res.stop_reason === "refusal") throw new Error("refusal");
  if (res.stop_reason === "max_tokens") throw new Error("max_tokens");
  const raw = res.content.filter((b) => b.type === "text").map((b) => b.text).join("").trim();
  const out = JSON.parse(raw);
  return { ...out, usage: res.usage, model: res.model };
}

// What gets stored as the assistant's side of the history: just the message it sent.
export const assistantTurn = (out) => out.reply;
