# WhatsApp lead bot

People message the bot's WhatsApp number. The bot (Claude) answers their questions, finds out their goal, sends the free body assessment, and passes keen people to Coach Kimi or Coach Zara with a short summary. Anything medical goes straight to a coach. It never promises results, never takes payment, and says it's an AI assistant.

- `knowledge.md`: everything the bot knows (program, RM259, links, answers, which coach gets who). **Edit this to change what it says.**
- `src/prompt.js`: the bot's rules (safety, style, when to hand off).
- `src/index.js`: the WhatsApp side (memory, handoffs, coach commands, spend limits).

## Setup (once, about 45 minutes after the Meta steps)

Never paste keys in chat. They only go into GitHub's secret settings.

### A. Get 4 values from Meta
In developers.facebook.com, open your app (WDT Lead Bot):
1. **Phone number ID**: WhatsApp > API Setup, under your bot number. Copy it.
2. **App secret**: App settings > Basic > App secret > Show. Copy it.
3. **Permanent token**: business.facebook.com > Settings > Users > System users > Add (name "bot", role Admin). Click Assign assets: add your app (full control) and your WhatsApp account (full control). Then Generate new token: pick the app, expiry **Never**, tick `whatsapp_business_messaging` and `whatsapp_business_management`. Copy it.
4. **Verify token**: make up any password-like word, e.g. `wdt-bot-2026-kimi`.

### B. Free Cloudflare account (keeps the bot online 24/7)
1. Sign up at dash.cloudflare.com (free plan). Open **Workers & Pages** once and pick your workers.dev name when it asks.
2. **Account ID**: on the Workers & Pages page, right side, "Account ID". Copy it.
3. **API token**: My Profile > API Tokens > Create Token > template **Edit Cloudflare Workers** > Continue > Create. Copy it.

### C. Put everything into GitHub
Repo **Settings > Secrets and variables > Actions > New repository secret**, one at a time:

| Name | Value |
| --- | --- |
| `CLOUDFLARE_API_TOKEN` | from B3 |
| `CLOUDFLARE_ACCOUNT_ID` | from B2 |
| `WHATSAPP_TOKEN` | from A3 |
| `WHATSAPP_PHONE_NUMBER_ID` | from A1 |
| `WHATSAPP_APP_SECRET` | from A2 |
| `WHATSAPP_VERIFY_TOKEN` | from A4 |
| `KIMI_WHATSAPP` | your personal number, digits only, e.g. `60123456789` |
| `ZARA_WHATSAPP` | Coach Zara's number, same format |
| `ANTHROPIC_API_KEY` | already there (the content engine uses it) |

Optional: `LEADS_SHEET_URL` (your lead tracker's Apps Script link, so bot leads land in the Sheet), `LEAD_ALERT_TEMPLATE` (see F), `BOT_MODEL` (leave empty).

### D. Put the bot online
1. **Actions** tab > **WhatsApp bot** > **Run workflow** > pick `deploy` > Run. Wait about 2 minutes for a green tick.
2. Your bot's address is `https://wdt-lead-bot.<your-workers-name>.workers.dev`. Open it in a browser: it should say `"ok": true`.
3. Back in your Meta app: WhatsApp > **Configuration** > Webhook > Edit.
   - Callback URL: your bot address + `/webhook`
   - Verify token: the word from A4
   - Verify and save. Then under Webhook fields, **Subscribe** to `messages`.

### E. Test it
From a phone that is not yours, WhatsApp the bot number "Hi, berapa harga program?". You should get a reply in a few seconds. Then say you want to join: you (or Zara) should get a lead alert.

### F. Lead alerts when you haven't messaged the bot today (recommended)
WhatsApp only lets the bot send you a normal message if you messaged the bot in the last 24 hours. Two easy options:
- Message the bot "hi" from your personal number each morning, or
- Make an alert template once: WhatsApp Manager > Message templates > Create > **Utility**, name `lead_alert`, language English, body:
  `New lead from the bot: {{1}} ({{2}}). Reason: {{3}}. Open WhatsApp to reply.`
  When it's approved, add the secret `LEAD_ALERT_TEMPLATE` = `lead_alert` and run deploy again. Each alert costs a few sen.

## Using it day to day

- When the bot hands someone over, you get their name, a tap-to-chat link, their goal, commitment and the last messages. **Message them from your own WhatsApp.** The bot stops replying to them so it doesn't talk over you.
- Send these to the bot from your personal number:
  - `leads`: last 10 handoffs and how many replies the bot sent this month
  - `resume 60123456789`: let the bot keep chatting with that person
  - `pause 60123456789`: make the bot go quiet with someone
- Change the website's "Free Body Assessment" / WhatsApp buttons to the bot number when you're happy with it (ask Claude in the project).

## Practice before going live

Actions > WhatsApp bot > Run workflow > `test`. It runs 7 practice chats (price asker, busy dad, breastfeeding mum, MLM skeptic, someone wanting a guarantee, a trick message, side-income question) with the real bot brain and shows the full chats on the run's Summary page. No WhatsApp needed. Costs a few cents.

## Cost and limits

- WhatsApp: replies to people who message first are free.
- Claude: roughly US$0.01 to 0.02 per reply (Claude Opus 5.5, low effort, cached instructions), so about US$10 to 20 for 1,000 replies, from your API credit.
- Built-in brakes: 40 bot replies per person per day and 3,000 per month in total. After that the bot hands chats to a coach instead of calling Claude. Change them in `wrangler.toml`.
- Cloudflare free plan covers 100,000 requests a day.

## For developers

```
cd whatsapp-bot
npm ci
npm test                                 # offline tests (fake WhatsApp + fake Claude)
ANTHROPIC_API_KEY=... npm run try        # practice chats with the real model
npx wrangler deploy --dry-run            # check the bundle
```
Conversation memory is Cloudflare KV (`lead:<number>`, kept 90 days). Webhooks are checked with the app secret signature. Deploys run on every push to `main` that touches `whatsapp-bot/` (skipped until the Cloudflare secrets exist).
