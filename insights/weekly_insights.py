"""Weekly comment insights for Coach Kimi (Instagram @coachkimii_, TikTok @transformwithkimi).

Uses Apify to read the last 7 days of public comments, asks Claude what people
ask and want, and writes content-engine/insights.md (read by the content engine).

Instagram comments are mostly CTA keywords ("Plan", "Serat"), so they are
counted per post as a demand signal; real questions are passed to Claude.
DMs are private and can't be read this way.

Privacy: the repo is public, so the output never has usernames, names or
phone numbers. Raw comments are never printed or saved.

Env:
  APIFY_TOKEN        Apify API token (console.apify.com > Settings > API & Integrations)
  ANTHROPIC_API_KEY  Claude API key
  IG_USERNAME        default coachkimii_
  TIKTOK_USERNAME    default transformwithkimi
  DAYS               default 7
  COMMENTS_PER_POST  default 30 (keeps Apify cost to about US$0.30 a week)
"""
import collections
import datetime as dt
import json
import os
import re
import sys
import urllib.request

import anthropic

APIFY = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
IG_USER = os.environ.get("IG_USERNAME", "coachkimii_")
TT_USER = os.environ.get("TIKTOK_USERNAME", "transformwithkimi")
DAYS = int(os.environ.get("DAYS", "7"))
PER_POST = int(os.environ.get("COMMENTS_PER_POST", "30"))
NOW = dt.datetime.now(dt.timezone.utc)
SINCE = NOW - dt.timedelta(days=DAYS)
OUT = os.path.join(os.path.dirname(__file__), "..", "content-engine", "insights.md")


def apify(actor, run_input):
    req = urllib.request.Request(
        APIFY.format(actor=actor.replace("/", "~")),
        data=json.dumps(run_input).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + os.environ["APIFY_TOKEN"]},
    )
    with urllib.request.urlopen(req, timeout=330) as r:
        return json.load(r)


def when(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def is_keyword(text):
    """One short word, like "Plan" or "Serat": a CTA reply, not a question."""
    return bool(re.fullmatch(r"[^\W\d_]{2,12}[!.\s]*", text.strip()))


def instagram():
    profile = apify("apify/instagram-profile-scraper", {"usernames": [IG_USER]})[0]
    posts = [p for p in profile.get("latestPosts", []) if when(p["timestamp"]) >= SINCE]
    with_comments = [p["url"] for p in posts if p.get("commentsCount")]
    comments = apify("apify/instagram-comment-scraper", {
        "directUrls": with_comments, "resultsLimit": PER_POST,
        "includeNestedComments": False}) if with_comments else []
    by_post = collections.defaultdict(list)
    for c in comments:
        if c.get("ownerUsername") != IG_USER and c.get("text"):
            by_post[c.get("postUrl", "").rstrip("/") + "/"].append(c["text"])
    rows = []
    for p in posts:
        texts = by_post.get(p["url"].rstrip("/") + "/", [])
        rows.append({
            "platform": "Instagram", "type": p.get("type"),
            "date": p["timestamp"][:10],
            "caption": (p.get("caption") or "")[:90].replace("\n", " "),
            "likes": p.get("likesCount"), "comments": p.get("commentsCount"),
            "views": p.get("videoViewCount"),
            "keywords": collections.Counter(t.strip().lower().strip("!. ") for t in texts if is_keyword(t)),
            "other": [t for t in texts if not is_keyword(t)],
        })
    return rows, profile.get("followersCount")


def tiktok():
    items = apify("clockworks/tiktok-comments-scraper", {
        "profiles": [TT_USER], "resultsPerPage": 10, "commentsPerPost": PER_POST,
        "maxRepliesPerComment": 0,
        "oldestPostDateUnified": SINCE.date().isoformat()})
    by_video = collections.defaultdict(list)
    for c in items:
        if c.get("uniqueId") != TT_USER and c.get("text") and when(c["createTimeISO"]) >= SINCE:
            by_video[c.get("videoWebUrl")].append(c["text"])
    return [{"platform": "TikTok", "video": i + 1,
             "keywords": collections.Counter(t.strip().lower() for t in t_ if is_keyword(t)),
             "other": [t for t in t_ if not is_keyword(t)]}
            for i, t_ in enumerate(by_video.values())]


PROMPT = """You are helping Coach Kimi, a Malaysian fitness and weight-loss coach, plan next week's posts.
Below is the last {days} days of Instagram and TikTok activity. Most Instagram comments are CTA keywords
(people commenting a word like "Plan" to get a DM), so keyword counts show which TOPICS pulled the most leads.
"Other comments" are real questions and reactions (Malay, English or mixed). Ignore spam, emojis-only and other coaches promoting themselves.

Write a short weekly report in English, in markdown, with exactly these sections:

# Comment insights, week ending {date}
_Instagram @{ig} ({followers} followers) and TikTok. Public comments only, DMs not included._

## What pulled the most leads
Rank the posts by keyword comments and engagement. One line each: topic, format, comments, what it tells us.

## Top questions
Up to 8 real questions people asked, most common first, "- **Question in plain words** (about N times): what they really want to know". If there are few, say so.

## Objections and worries
Up to 5, same format. Skip the section body with "None seen this week" if there are none.

## Requested topics
Topics people want more of, with rough counts.

## Post ideas for next week
5 ideas, each "- **Hook** (format): which demand, question or objection it answers". Lean on what pulled the most leads.

Rules: never include usernames, names or phone numbers, and paraphrase instead of quoting. Keep it under 450 words.

DATA:
{data}
"""


def main():
    ig, followers = instagram()
    try:
        tt = tiktok()
    except Exception as e:  # TikTok scrape can fail; Instagram still useful
        print(f"TikTok skipped: {e}", file=sys.stderr)
        tt = []
    n = sum(len(r["other"]) + sum(r["keywords"].values()) for r in ig + tt)
    print(f"{len(ig)} Instagram posts, {len(tt)} TikTok videos, {n} comments read")

    def fmt(r):
        head = {k: v for k, v in r.items() if k not in ("keywords", "other")}
        return (json.dumps(head, ensure_ascii=False)
                + f"\n  keyword comments in sample: {dict(r['keywords']) or 'none'}"
                + "\n  other comments:\n" + ("\n".join(f"  - {t}" for t in r["other"]) or "  (none)"))

    today = NOW.date().isoformat()
    prompt = PROMPT.format(days=DAYS, date=today, ig=IG_USER, followers=followers,
                           data="\n\n".join(fmt(r) for r in ig + tt) or "(no posts this week)")
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
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"Wrote {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
