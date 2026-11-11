# Weekly comment insights

Every Sunday 9am (Malaysia time), one hour before the content engine, a GitHub
Action uses Apify to read the last 7 days of public comments on Instagram
@coachkimii_ and TikTok @transformwithkimi. Claude then writes
`content-engine/insights.md`: which posts pulled the most leads, top
questions, objections, requested topics and post ideas. The content engine
reads that file when it plans next week.

Most Instagram comments are CTA keywords ("Plan", "Serat"), so those are
counted per post as a demand signal. DMs are private and not included.

The report never has usernames, names or phone numbers, because this repo is
public. Cost is about US$0.30 a week of Apify credit (free plan gives US$5 a
month) plus a few cents of Claude API credit.

## One-time setup (Kimi)

1. Apify token: console.apify.com > Settings > API & Integrations > copy the
   Personal API token.
2. In GitHub: this repo > Settings > Secrets and variables > Actions >
   New repository secret. Add:
   - `APIFY_TOKEN`: the token from step 1
   - `ANTHROPIC_API_KEY`: from console.anthropic.com > API keys (skip if the
     content engine already has it)
3. Actions tab > "Weekly comment insights" > Run workflow, to test it.

To change accounts, edit IG_USERNAME / TIKTOK_USERNAME at the top of
`weekly_insights.py`. If you ever want DMs too, that needs a Meta developer
app (see git history of this folder).
