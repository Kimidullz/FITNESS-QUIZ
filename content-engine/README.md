# Content engine

Every Sunday at 10am (Malaysia time, after the comment/DM insights update) it writes next week's posts in Coach Kimi's voice. On the 25th of each month it fills next month's content plan. Everything lands in `content-engine/output/`.

## What you get

- **Weekly** (`output/weekly/<monday>.md`): 5 carousels with all 6 slides written, 2 reel scripts, captions, TikTok titles, pinned comments, numbers to double-check, 10 spare hooks and 5 Threads/Stories ideas.
- **Monthly** (`output/monthly/<yyyy-mm>.md` + `.csv`): one row per day. The CSV columns match the Plan tab of the content planner Google Sheet, so you can import it (File > Import > Upload > "Insert new sheet") or ask Claude in the project to put it into the Sheet.

## One-time setup (5 minutes)

1. Get an API key: go to https://console.anthropic.com/settings/keys, click **Create Key**, copy it. (Your API credit is used, not your Claude subscription.)
2. Put it in GitHub, never in chat: in this repo open **Settings > Secrets and variables > Actions > New repository secret**. Name: `ANTHROPIC_API_KEY`. Value: paste the key. Save.
3. Test it now: open the **Actions** tab > **Content engine** > **Run workflow** > pick `weekly` > **Run workflow**. After about 2 to 4 minutes, the new file appears in `content-engine/output/weekly/`.

That's it. It then runs by itself.

## Steering it

- `voice.md`: how you talk, what works, your rules. Edit it whenever you learn something.
- `topics.md`: add a line like `- Raya open house: what to eat` and the next batch uses it first. Delete lines once used.
- `insights.md` (optional): a weekly summary of what people ask in comments and DMs. The engine answers the most common questions with posts.
- It reads the last few batches so it doesn't repeat itself.

## Cost

Each weekly batch costs roughly US$0.25 to 0.40 and each monthly plan roughly US$0.30 to 0.50 (Claude Opus 5.5, medium effort). That is about US$2 a month, so US$100 of credit lasts years. You can see the exact spend at https://console.anthropic.com/usage.

## Change the schedule or turn it off

- Turn off: Actions tab > Content engine > "..." > **Disable workflow**.
- Change days: edit the `cron` lines in `.github/workflows/content-engine.yml` (times are UTC; Malaysia is UTC+8).

## Run it on a computer instead (optional)

```
pip install anthropic
set ANTHROPIC_API_KEY=...     (Windows)   or   export ANTHROPIC_API_KEY=...   (Mac/Linux)
python content-engine/generate.py weekly
python content-engine/generate.py monthly
python content-engine/generate.py weekly --dry-run   (shows the prompt, costs nothing)
```

Always check numbers and prices before posting. The engine marks them approximate and lists them under "Numbers to double-check".
