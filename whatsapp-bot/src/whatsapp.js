// Small helpers around Meta's WhatsApp Cloud API.
const GRAPH = "https://graph.facebook.com/v23.0";

async function post(env, body) {
  const r = await fetch(`${GRAPH}/${env.WHATSAPP_PHONE_NUMBER_ID}/messages`, {
    method: "POST",
    headers: { Authorization: `Bearer ${env.WHATSAPP_TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify({ messaging_product: "whatsapp", ...body }),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    const err = new Error(`WhatsApp ${r.status}: ${data?.error?.message || "error"}`);
    err.code = data?.error?.code;
    throw err;
  }
  return data;
}

export const sendText = (env, to, text) =>
  post(env, { recipient_type: "individual", to, type: "text", text: { body: text.slice(0, 4000), preview_url: true } });

// Blue ticks + "typing..." while Claude thinks. Never fails the main flow.
export const markReadTyping = (env, messageId) =>
  post(env, { status: "read", message_id: messageId, typing_indicator: { type: "text" } }).catch(() => {});

export const sendTemplate = (env, to, name, lang, params) =>
  post(env, {
    to,
    type: "template",
    template: {
      name,
      language: { code: lang },
      components: [{ type: "body", parameters: params.map((p) => ({ type: "text", text: String(p).slice(0, 900) || "-" })) }],
    },
  });

/** Pull the useful bits out of a webhook payload. Returns a list of incoming messages. */
export function parseWebhook(payload) {
  const out = [];
  for (const entry of payload?.entry || []) {
    for (const change of entry.changes || []) {
      const v = change.value || {};
      const names = Object.fromEntries((v.contacts || []).map((c) => [c.wa_id, c.profile?.name || ""]));
      for (const m of v.messages || []) {
        let text = "";
        if (m.type === "text") text = m.text?.body || "";
        else if (m.type === "button") text = m.button?.text || "";
        else if (m.type === "interactive") text = m.interactive?.button_reply?.title || m.interactive?.list_reply?.title || "";
        out.push({ id: m.id, from: m.from, name: names[m.from] || "", type: m.type, text: text.trim(), timestamp: Number(m.timestamp || 0) });
      }
    }
  }
  return out;
}

/** Check Meta's X-Hub-Signature-256 header against the raw body. */
export async function validSignature(appSecret, rawBody, header) {
  if (!appSecret || !header?.startsWith("sha256=")) return false;
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(appSecret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(rawBody));
  const hex = [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
  const given = header.slice(7);
  if (given.length !== hex.length) return false;
  let diff = 0;
  for (let i = 0; i < hex.length; i++) diff |= hex.charCodeAt(i) ^ given.charCodeAt(i);
  return diff === 0;
}
