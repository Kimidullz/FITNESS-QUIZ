"""Coach Kimi content engine.

Weekly:  python content-engine/generate.py weekly
         -> content-engine/output/weekly/<monday>.md
Bulk:    python content-engine/generate.py bulk 12   (12 weekly batches in a row)
Monthly: python content-engine/generate.py monthly
         -> content-engine/output/monthly/<yyyy-mm>.md and .csv (columns match the
            "Plan" tab of the WDT 30-Day Content Planner Google Sheet)

Needs ANTHROPIC_API_KEY in the environment (a GitHub secret in the Action).
Add --dry-run to print the prompt without calling the API (free).
"""

import csv
import datetime as dt
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "output"
MODEL = os.environ.get("CONTENT_MODEL", "claude-opus-5-5")
MYT = dt.timezone(dt.timedelta(hours=8))

PLAN_COLUMNS = [
    "Day", "Week", "Date", "Time (MYT)", "Platforms", "Format", "Goal", "Topic",
    "Hook (first 3 seconds)", "What to say or show", "Caption", "CTA keyword",
    "Hashtags", "Film batch", "Status",
]


def read(name: str) -> str:
    path = HERE / name
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8").strip()
    if name == "topics.md":  # only real bullet lines count
        text = "\n".join(l for l in text.splitlines() if re.match(r"^\s*-\s*\S", l))
    return text


def recent_titles(limit_files: int = 16) -> str:
    """Headings from recent batches so the model does not repeat topics."""
    files = sorted((OUT / "weekly").glob("*.md")) + sorted((OUT / "monthly").glob("*.md"))
    files = sorted(files, key=lambda p: p.stat().st_mtime)[-limit_files:]
    titles = []
    for f in files:
        for line in f.read_text(encoding="utf-8").splitlines():
            # weekly: post headings only (reel script tables would crowd them out);
            # monthly: the plan table rows
            is_row = f.parent.name == "monthly" and line.startswith("| ") and "---" not in line
            if line.startswith("## ") or is_row:
                titles.append(line.strip()[:140])
    return "\n".join(titles[-250:])


def system_prompt() -> str:
    return (
        "You are the content strategist and copywriter for Coach Kimi, a Malaysian "
        "fitness coach. Write exactly in Kimi's voice as described in the voice guide. "
        "Write in English unless the voice guide or topic list says otherwise. Every "
        "number you use must be realistic for Malaysia, rounded, and marked approximate; "
        "never invent studies, prices you can't stand behind, or medical claims. If you "
        "are unsure of a number, use a softer range or leave the number out.\n\n"
        "<voice_guide>\n" + read("voice.md") + "\n</voice_guide>"
    )


def context_block() -> str:
    parts = []
    topics = read("topics.md")
    if topics:
        parts.append("<kimi_topic_requests>\nUse these first.\n" + topics + "\n</kimi_topic_requests>")
    insights = read("insights.md")
    if insights:
        parts.append(
            "<audience_insights>\nWhat followers asked or said in comments and DMs "
            "recently. Answer the most common questions and objections with posts.\n"
            + insights + "\n</audience_insights>"
        )
    titles = recent_titles()
    if titles:
        parts.append("<already_made>\nDo not repeat these topics or hooks.\n" + titles + "\n</already_made>")
    return "\n\n".join(parts)


def next_monday(today: dt.date) -> dt.date:
    return today + dt.timedelta(days=(7 - today.weekday()) % 7 or 7)


def weekly_prompt(start: dt.date) -> str:
    days = [(start + dt.timedelta(days=i)).strftime("%a %-d %b %Y") for i in range(7)]
    return (
        context_block()
        + f"\n\nWrite next week's content batch for {days[0]} to {days[-1]}.\n\n"
        "These posts go on both Instagram and TikTok (same 4:5 carousel images on both). "
        "Make 7 posts, one per day, in this order of days: " + ", ".join(days) + ".\n"
        "- 5 photo carousels (IG 4:5, 6 slides) and 2 short reels (20 to 35 seconds).\n"
        "- Use the winning formula from the voice guide. Mix pillars: cheap protein / money, "
        "Malaysian food ranked, body inside view, habits and excuses, Kimi's story or a client win.\n"
        "- Suggested time: 6:00 PM on weekdays, 10:00 AM on weekends (MYT).\n\n"
        "Format the answer as Markdown, exactly like this for each post:\n\n"
        "## <Day date> | <Carousel or Reel> | <SERIES NAME #N if any>: <topic>\n"
        "**Why it should work:** one line.\n"
        "**Hook options:** 3 numbered hooks (the first is the pick).\n"
        "For carousels, **Slides:** numbered 1 to 6, each with the exact headline and the short body text on that slide.\n"
        "For reels, **Script:** a table with columns Time | On screen | Voiceover / what Kimi says | Shot. Gentle pace.\n"
        "**Caption:** ready to paste.\n"
        "**TikTok title:** \n"
        "**Pinned comment:** \n"
        "**Numbers to double-check:** list each number used and its rough source, or 'none'.\n\n"
        "After the 7 posts, add '## Bonus: 10 spare hooks' with 10 one-line hooks for future posts, "
        "and '## Threads / Stories ideas' with 5 one-liners.\n"
        "Start directly with the first post heading. No intro text."
    )


MONTH_SCHEMA = {
    "type": "object",
    "properties": {
        "rows": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "e.g. Mon 7 Dec"},
                    "time": {"type": "string"},
                    "platforms": {"type": "string"},
                    "format": {"type": "string", "enum": ["Carousel", "Video"]},
                    "goal": {"type": "string", "enum": ["Awareness", "Connection", "Trust", "Leads"]},
                    "topic": {"type": "string"},
                    "hook": {"type": "string"},
                    "what_to_show": {"type": "string"},
                    "caption": {"type": "string"},
                    "cta_keyword": {"type": "string"},
                    "hashtags": {"type": "string"},
                },
                "required": ["date", "time", "platforms", "format", "goal", "topic", "hook",
                             "what_to_show", "caption", "cta_keyword", "hashtags"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["rows"],
    "additionalProperties": False,
}


def monthly_prompt(first: dt.date, n_days: int) -> str:
    last = first + dt.timedelta(days=n_days - 1)
    return (
        context_block()
        + f"\n\nFill a content plan for every day from {first:%a %-d %b %Y} to {last:%a %-d %b %Y} "
        f"({n_days} rows, one per day, in date order).\n"
        "- About two thirds carousels (they perform best), one third short videos Kimi can film "
        "in one batch on Sundays.\n"
        "- Goals: mostly Awareness, plus Connection (Kimi's story, behind the scenes), Trust "
        "(client results, only if generic, no names), and about one Leads post a week (quiz).\n"
        "- Time: 6:00 PM weekdays, 10:00 AM weekends. Platforms: 'IG + TikTok photo post' for "
        "carousels, 'TikTok + IG Reels' for videos.\n"
        "- what_to_show: for carousels, the 6 slide headlines; for videos, the beats in 2 to 4 short steps.\n"
        "- Keep series numbering going (e.g. CHEAP PROTEIN #7). 0 to 3 hashtags.\n"
        "- Spread similar topics apart (no two money/protein posts on back-to-back days)."
    )


def call_claude(prompt: str, schema: dict | None = None) -> str:
    import anthropic

    client = anthropic.Anthropic()
    kwargs = dict(
        model=MODEL,
        max_tokens=64000,
        system=system_prompt(),
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "adaptive"},
        output_config={"effort": os.environ.get("CONTENT_EFFORT", "medium")},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if schema:
        kwargs["output_config"]["format"] = {"type": "json_schema", "schema": schema}
    with client.beta.messages.stream(**kwargs) as stream:
        msg = stream.get_final_message()

    u = msg.usage
    print(f"Tokens: in {u.input_tokens}, out {u.output_tokens} (model {msg.model})", file=sys.stderr)
    if msg.stop_reason == "refusal":
        sys.exit("Claude declined this request. Try again or change topics.md.")
    if msg.stop_reason == "max_tokens":
        sys.exit("Output was cut off (max_tokens).")
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def run_weekly(dry: bool, start: dt.date | None = None) -> None:
    start = start or next_monday(dt.datetime.now(MYT).date())
    prompt = weekly_prompt(start)
    if dry:
        print(system_prompt(), "\n\n----\n\n", prompt)
        return
    body = call_claude(prompt)
    path = OUT / "weekly" / f"{start.isoformat()}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"# Content batch: week of {start:%-d %b %Y}\n\n"
        f"Made {dt.datetime.now(MYT):%-d %b %Y %H:%M} MYT by the content engine. "
        "Check every number before posting. Edit freely.\n\n"
    )
    path.write_text(header + body + "\n", encoding="utf-8")
    print(f"Wrote {path}")


def run_monthly(dry: bool) -> None:
    today = dt.datetime.now(MYT).date()
    first = (today.replace(day=1) + dt.timedelta(days=32)).replace(day=1)
    n_days = ((first + dt.timedelta(days=32)).replace(day=1) - first).days
    prompt = monthly_prompt(first, n_days)
    if dry:
        print(system_prompt(), "\n\n----\n\n", prompt)
        return
    rows = json.loads(call_claude(prompt, MONTH_SCHEMA))["rows"]

    stem = OUT / "monthly" / f"{first:%Y-%m}"
    stem.parent.mkdir(parents=True, exist_ok=True)
    with open(f"{stem}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(PLAN_COLUMNS)
        for i, r in enumerate(rows, 1):
            week = (i - 1) // 7 + 1
            batch = "Canva (no filming)" if r["format"] == "Carousel" else f"Batch {week} (film Sunday before)"
            status = "To design" if r["format"] == "Carousel" else "To film"
            w.writerow([i, week, r["date"], r["time"], r["platforms"], r["format"], r["goal"],
                        r["topic"], r["hook"], r["what_to_show"], r["caption"], r["cta_keyword"],
                        r["hashtags"], batch, status])

    def cell(s: str) -> str:
        return s.replace("|", "/").replace("\n", " ")

    lines = [f"# Content plan: {first:%B %Y}\n",
             "Made by the content engine. The same plan is in the .csv file next to this one "
             "(columns match the Plan tab of the content planner Sheet).\n",
             "| Date | Format | Goal | Topic | Hook |", "|---|---|---|---|---|"]
    lines += [f"| {cell(r['date'])} | {r['format']} | {r['goal']} | {cell(r['topic'])} | {cell(r['hook'])} |"
              for r in rows]
    pathlib.Path(f"{stem}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {stem}.md and {stem}.csv ({len(rows)} days)")


def run_bulk(dry: bool, weeks: int) -> None:
    """Many weekly batches in a row (e.g. 12 weeks = 3 months). Weeks that already
    have a file are skipped, so a re-run carries on where it stopped."""
    first = next_monday(dt.datetime.now(MYT).date())
    for i in range(weeks):
        start = first + dt.timedelta(weeks=i)
        if (OUT / "weekly" / f"{start.isoformat()}.md").exists():
            print(f"Skip {start} (already made)")
            continue
        run_weekly(dry, start)
        if dry:
            return


if __name__ == "__main__":
    args = sys.argv[1:]
    mode = next((a for a in args if a in ("weekly", "monthly", "bulk")), None)
    if not mode:
        sys.exit("Usage: python content-engine/generate.py weekly|monthly|bulk [weeks] [--dry-run]")
    dry = "--dry-run" in args
    if mode == "bulk":
        weeks = next((int(a) for a in args if a.isdigit()), 12)
        run_bulk(dry, weeks)
    elif mode == "weekly":
        # never overwrite a week that bulk (or an earlier run) already made
        run_bulk(dry, 1)
    else:
        run_monthly(dry)
