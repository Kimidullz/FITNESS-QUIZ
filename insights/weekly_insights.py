"""Weekly comment and DM insights for @transformwithkimi.

Pulls the last 7 days of Instagram comments and DMs, asks Claude what people
ask most, and writes content-engine/insights.md (read by the content engine).

Privacy: the repo is public, so the output never contains usernames, names,
phone numbers or word-for-word DMs. Raw comments and DMs are never printed
or saved; they only go to the Claude API.

Env:
  IG_ACCESS_TOKEN    Instagram long-lived token (Instagram API with Instagram Login)
  ANTHROPIC_API_KEY  Claude API key
  DAYS               optional, default 7
"""
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

import anthropic

GRAPH = "https://graph.instagram.com/" + os.environ.get("IG_API_VERSION", "v23.0")
TOKEN = os.environ["IG_ACCESS_TOKEN"]
DAYS = int(os.environ.get("DAYS", "7"))
SINCE = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=DAYS)
OUT = os.path.join(os.path.dirname(__file__), "..", "content-engine", "insights.md")


def get(path, **params):
    params["access_token"] = TOKEN
    url = path if path.startswith("http") else f"{GRAPH}/{path}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def pages(path, **params):
    data = get(path, **params)
    while True:
        yield from data.get("data", [])
        nxt = data.get("paging", {}).get("next")
        if not nxt:
            return
        data = get(nxt)


def when(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")


def fetch_comments(me):
    """Comments (and replies) left by other people on posts, last DAYS days."""
    out = []
    cutoff_posts = SINCE - dt.timedelta(days=30)  # older posts still get comments
    for m in pages("me/media", fields="id,caption,timestamp,comments_count", limit=50):
        if when(m["timestamp"]) < cutoff_posts:
            break
        if not m.get("comments_count"):
            continue
        post = (m.get("caption") or "")[:80].replace("\n", " ")
        for c in pages(f"{m['id']}/comments", fields="text,username,timestamp,replies{text,username,timestamp}", limit=50):
            for x in [c] + c.get("replies", {}).get("data", []):
                if x.get("username") != me and when(x["timestamp"]) >= SINCE:
                    out.append({"post": post, "text": x.get("text", "")})
    return out


def fetch_dms(me):
    """Incoming DM text, last DAYS days. Returns [] if messaging isn't set up."""
    out = []
    try:
        for conv in pages("me/conversations", platform="instagram",
                          fields="updated_time,messages.limit(25){message,from,created_time}"):
            if when(conv["updated_time"]) < SINCE:
                continue
            for msg in conv.get("messages", {}).get("data", []):
                if (msg.get("from", {}).get("username") != me and msg.get("message")
                        and when(msg["created_time"]) >= SINCE):
                    out.append(msg["message"])
    except Exception as e:  # missing permission etc. Comments still work.
        print(f"DMs skipped: {e}", file=sys.stderr)
    return out


def refresh_token():
    """Keeps the 60-day token alive. Returns days left, or None."""
    try:
        r = get(f"https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token={TOKEN}")
        return round(r.get("expires_in", 0) / 86400)
    except Exception as e:
        print(f"Token refresh failed: {e}", file=sys.stderr)
        return None


PROMPT = """You are helping Coach Kimi, a Malaysian fitness and weight-loss coach (Instagram @transformwithkimi), plan next week's posts.
Below are the comments and DMs people sent in the last {days} days (Malay, English or mixed).
Ignore spam, emojis-only, "nice", tags of friends and bot messages.

Write a short weekly report in English, in markdown, with exactly these sections:

# Comment and DM insights, week ending {date}
_{n_comments} comments, {n_dms} DMs analysed._

## Top questions
Up to 8, most asked first, each as "- **Question in plain words** (about N times): one line on what they really want to know"

## Objections and worries
Up to 5 reasons people hesitate (price, time, "I've tried before", food, etc.), same format with rough counts.

## Requested topics
Topics people want more of, with rough counts.

## Post ideas for next week
5 ideas, each "- **Hook** (format: carousel / reel / story): which question or objection it answers"

## Buying signals
One or two lines: how many messages looked like people ready to join (asking price, how to start), and what they asked. No names.

Rules: never include usernames, names, phone numbers, or quote a DM word for word (paraphrase). Keep the whole report under 450 words. If there is very little data, say so and keep it short.

COMMENTS (post caption | comment):
{comments}

DMS:
{dms}
"""


def main():
    me = get("me", fields="username").get("username")
    comments = fetch_comments(me)
    dms = fetch_dms(me)
    days_left = refresh_token()
    print(f"Collected {len(comments)} comments and {len(dms)} DMs")

    today = dt.date.today().isoformat()
    prompt = PROMPT.format(
        days=DAYS, date=today, n_comments=len(comments), n_dms=len(dms),
        comments="\n".join(f"{c['post']} | {c['text']}" for c in comments) or "(none)",
        dms="\n".join(f"- {d}" for d in dms) or "(none, or DM access not set up yet)",
    )
    client = anthropic.Anthropic()
    resp = client.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": prompt}],
    )
    if resp.stop_reason == "refusal":
        sys.exit("Claude declined the request; no report written.")
    report = "".join(b.text for b in resp.content if b.type == "text").strip()
    if days_left is not None and days_left < 20:
        report += f"\n\n> Instagram token expires in about {days_left} days. Make a new one in the Meta app and update the IG_ACCESS_TOKEN secret.\n"

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"Wrote {os.path.normpath(OUT)} ({resp.usage.input_tokens} in / {resp.usage.output_tokens} out tokens)")


if __name__ == "__main__":
    main()
