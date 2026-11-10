# Weekly comment and DM insights

Every Sunday 8am (Malaysia time) a GitHub Action reads the last 7 days of
Instagram comments and DMs on @transformwithkimi, asks Claude what people ask
most, and writes `content-engine/insights.md`: top questions, objections,
requested topics, post ideas and buying signals. The content engine reads that
file to pick next week's topics.

The report never has usernames, names, phone numbers or word-for-word DMs,
because this repo is public. Cost is roughly RM1 a week of Claude API credit.

## One-time setup (Kimi)

1. Instagram app: Settings > Account type and tools. It must be a Professional
   account (Creator or Business).
2. Go to developers.facebook.com, log in, and click Create app. Pick the use
   case "Manage messaging and content on Instagram".
3. In the app, open Instagram > API setup with Instagram login. Click
   "Add account" and log in as @transformwithkimi. Allow comments and messages.
4. Click "Generate token" next to the account and copy it. You don't need
   App Review, because you are the app's admin and only read your own account.
5. In GitHub: this repo > Settings > Secrets and variables > Actions >
   New repository secret. Add:
   - `IG_ACCESS_TOKEN`: the token from step 4
   - `ANTHROPIC_API_KEY`: from console.anthropic.com > API keys (skip if the
     content engine already added it)
6. Actions tab > "Weekly comment and DM insights" > Run workflow, to test it.

The token lasts 60 days and the job refreshes it each week. If the report ever
says the token is expiring, repeat step 4 and update the secret.

TikTok has no API for comments or DMs. For TikTok, send screenshots in the
Claude project and ask for them to be added to the week's report.
