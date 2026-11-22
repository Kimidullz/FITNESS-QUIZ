"""Writes the "Kalori makanan" food pages and the personal quiz notes with the Claude API.

Runs in GitHub Actions (.github/workflows/api-build.yml) with the ANTHROPIC_API_KEY secret.
Built once while Kimi's API credit lasts (expires 12 Dec 2026); the output is plain JSON
committed to the repo, so the site keeps working without the API afterwards.

  python seo/generate.py foods [--limit N]   -> seo/data/<slug>.json (skips foods already done)
  python seo/generate.py notes               -> results/notes.json (skips groups already done)
"""
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEO = ROOT / "seo"
DATA = SEO / "data"
NOTES = ROOT / "results" / "notes.json"
MODEL = os.environ.get("CONTENT_MODEL", "claude-opus-5-5")
BATCH = 8

SYSTEM = """You write for Coach Kimi and Coach Zara, a Malaysian husband-and-wife online fitness coaching team (WeDoTransformations).
Audience: busy Malaysian working adults and mums who want to lose 3-10 kg without crash diets, still eating rice and eating out.
Language: natural, friendly Bahasa Malaysia the way Malaysians write on social media (standard spelling, light everyday words like "okay", "lepak" are fine, no slang overload). English only where asked.
Rules:
- Calorie and macro numbers are ESTIMATES for a typical Malaysian serving. Say "anggaran" where it matters. Never claim lab precision.
- Never shame food. Every food can fit; the point is portion, frequency and what you pair it with.
- No medical diagnosis, no promises of results, no "detox", no weight-loss claims for any product or supplement. Do not mention supplements, shakes or any brand.
- Practical tips must be things a busy person can do at a mamak, warung, office or home kitchen in Malaysia.
- Keep sentences short and easy for a phone screen."""

FOOD_SCHEMA = {
    "type": "object",
    "properties": {"foods": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "slug": {"type": "string"},
            "intro": {"type": "string", "description": "2 sentences. Sentence 1 answers directly: about N kcal per serving. Sentence 2: what makes most of the calories."},
            "protein_g": {"type": "integer"}, "carbs_g": {"type": "integer"}, "fat_g": {"type": "integer"},
            "breakdown": {"type": "array", "description": "3-5 parts of the dish with their share, e.g. nasi santan 1 cawan ~250 kcal", "items": {
                "type": "object", "properties": {"part": {"type": "string"}, "kcal": {"type": "integer"}},
                "required": ["part", "kcal"], "additionalProperties": False}},
            "variants": {"type": "array", "description": "2-4 common versions or add-ons and their kcal", "items": {
                "type": "object", "properties": {"name": {"type": "string"}, "kcal": {"type": "integer"}},
                "required": ["name", "kcal"], "additionalProperties": False}},
            "diet": {"type": "string", "description": "Paragraph answering 'Boleh makan masa nak turun berat?' honestly, 3-4 sentences."},
            "tips": {"type": "array", "items": {"type": "string"}, "description": "3 practical tips to enjoy it with fewer calories or more protein"},
            "swap": {"type": "object", "properties": {"name": {"type": "string"}, "kcal": {"type": "integer"}, "why": {"type": "string"}},
                     "required": ["name", "kcal", "why"], "additionalProperties": False},
            "faq": {"type": "array", "description": "3 questions people really search about this food (not about its calories, that is answered above)", "items": {
                "type": "object", "properties": {"q": {"type": "string"}, "a": {"type": "string"}},
                "required": ["q", "a"], "additionalProperties": False}},
            "check": {"type": "string", "description": "Empty string, unless the given kcal looks wrong by more than 25% for a typical Malaysian serving: then say what you would use and why (English)."},
        },
        "required": ["slug", "intro", "protein_g", "carbs_g", "fat_g", "breakdown", "variants", "diet", "tips", "swap", "faq", "check"],
        "additionalProperties": False}}},
    "required": ["foods"], "additionalProperties": False,
}


def call(prompt: str, schema: dict) -> dict:
    import anthropic
    client = anthropic.Anthropic()
    with client.beta.messages.stream(
        model=MODEL, max_tokens=64000, system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "adaptive"},
        output_config={"effort": os.environ.get("CONTENT_EFFORT", "medium"),
                       "format": {"type": "json_schema", "schema": schema}},
        betas=["server-side-fallback-2026-07-01"], fallbacks="default",
    ) as stream:
        msg = stream.get_final_message()
    u = msg.usage
    print(f"  tokens in {u.input_tokens} out {u.output_tokens} ({msg.model})", flush=True)
    if msg.stop_reason in ("refusal", "max_tokens"):
        raise RuntimeError("stopped: " + msg.stop_reason)
    return json.loads("".join(b.text for b in msg.content if b.type == "text"))


def check_food(f: dict, d: dict) -> list:
    """Problems that mean the batch should be redone."""
    errs = []
    macro = 4 * d["protein_g"] + 4 * d["carbs_g"] + 9 * d["fat_g"]
    if abs(macro - f["kcal"]) > 0.2 * f["kcal"] + 15:
        errs.append(f"macros give {macro} kcal, page says {f['kcal']}")
    if len(d["tips"]) < 3 or len(d["faq"]) < 3:
        errs.append("too few tips or faq")
    bad = [w for w in ("herbalife", "detox", "shake", "supplement", "suplemen") if w in json.dumps(d, ensure_ascii=False).lower()]
    if bad:
        errs.append("banned words: " + ", ".join(bad))
    return errs


def run_foods(limit: int) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    foods = json.loads((SEO / "foods.json").read_text())["foods"]
    todo = [f for f in foods if not (DATA / f"{f['slug']}.json").exists()][:limit]
    print(f"{len(todo)} foods to write")
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i + BATCH]
        lines = "\n".join(f"- slug {f['slug']}: {f['name']}, serving {f['serving']}, about {f['kcal']} kcal" for f in batch)
        prompt = ("Write the content for these food pages on our 'Kalori makanan Malaysia' guide. "
                  "Use the given kcal as the page's number; your protein/carbs/fat must add up to roughly that "
                  "(4/4/9 kcal per gram). Keep breakdown parts adding up close to the total.\n\n" + lines)
        for attempt in range(2):
            try:
                got = {d["slug"]: d for d in call(prompt, FOOD_SCHEMA)["foods"]}
            except Exception as e:  # network / API hiccup: try once more
                print("  error:", e); got = {}
            for f in batch:
                d = got.get(f["slug"])
                if not d:
                    continue
                errs = check_food(f, d)
                if errs and attempt == 0:
                    print(f"  redo {f['slug']}: {errs}"); continue
                d["problems"] = errs
                (DATA / f"{f['slug']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
            batch = [f for f in batch if not (DATA / f"{f['slug']}.json").exists()]
            if not batch:
                break
            lines = "\n".join(f"- slug {f['slug']}: {f['name']}, serving {f['serving']}, about {f['kcal']} kcal" for f in batch)
            prompt = prompt.split("\n\n")[0] + "\n\n" + lines
        print(f"done {min(i + BATCH, len(todo))}/{len(todo)}", flush=True)


# ---------- personal quiz notes ----------
GOALS_LOSS = {"<5": "lose under 5 kg", "5-10": "lose 5 to 10 kg", "10-20": "lose 10 to 20 kg",
              "20+": "lose more than 20 kg", "health": "not about weight: more energy and better health"}
WHY_LOSS = ["their health (sugar, blood pressure, cholesterol, joint pain)", "to feel confident and fit old clothes again",
            "a big event coming (wedding, raya, holiday)", "more energy for family and work", "someone close (or their doctor) told them to"]
WHY_GAIN = ["health (doctor says underweight)", "to feel confident and fill out their clothes", "a big event coming",
            "more energy and strength for work and family", "someone close (or their doctor) told them to"]
WEAK_LOSS = {"Nutrition": "meals and drinks (skipping meals, quick oily food, sweet drinks, little water)",
             "Workout": "exercise (no time, starts then stops)",
             "Mindset & Method": "sleep, stress and past attempts that didn't stick",
             "none": "nothing stands out: their habits are already decent"}
WEAK_GAIN = {"Nutrition": "not eating enough meals and protein", "Workout": "little or no strength training",
             "Mindset & Method": "sleep, stress and past attempts that didn't stick", "none": "nothing stands out"}

NOTE_SCHEMA = {
    "type": "object",
    "properties": {"notes": {"type": "array", "items": {
        "type": "object",
        "properties": {"key": {"type": "string"}, "ms": {"type": "string"}, "en": {"type": "string"}},
        "required": ["key", "ms", "en"], "additionalProperties": False}}},
    "required": ["notes"], "additionalProperties": False,
}


def run_notes() -> None:
    NOTES.parent.mkdir(parents=True, exist_ok=True)
    have = json.loads(NOTES.read_text()) if NOTES.exists() else {}
    groups = [(g, GOALS_LOSS[g], WHY_LOSS, WEAK_LOSS) for g in GOALS_LOSS] + [("gain", "gain weight and look fuller", WHY_GAIN, WEAK_GAIN)]
    for g, goal, whys, weaks in groups:
        keys = [f"{g}|{w}|{k}" for w in range(len(whys)) for k in weaks]
        if all(k in have for k in keys):
            continue
        combos = "\n".join(f"- key {g}|{w}|{k}: goal = {goal}; main reason = {whys[w]}; weakest area = {weaks[k]}"
                           for w in range(len(whys)) for k in weaks)
        prompt = (
            "Our free 2-minute quiz ends with a short personal note from the coach. Write one note per key below, "
            "in Bahasa Malaysia (ms) and English (en).\n"
            "Each note: 2-3 short sentences, written as the coach speaking to 'anda'/'you'. Sentence 1 connects their goal "
            "with their reason in a warm, specific way (e.g. a wedding = a date to plan backwards from; doctor's advice = "
            "health first, scale second). Sentence 2 names the one thing to fix first for their weakest area, concrete "
            "and doable this week. Optional sentence 3: what a realistic pace looks like (about 0.5-1 kg a week for loss; "
            "slow, steady gain with strength training for gain). No price, no supplements, no brand, no medical claims. "
            "If the reason involves a doctor or health problem, say to keep following their doctor's advice. "
            "For 'more than 20 kg' be encouraging but realistic about it taking months. Make every note clearly different.\n\n"
            + combos)
        got = call(prompt, NOTE_SCHEMA)["notes"]
        for n in got:
            if n["key"] in keys:
                have[n["key"]] = {"ms": n["ms"].strip(), "en": n["en"].strip()}
        NOTES.write_text(json.dumps(have, ensure_ascii=False, indent=1))
        print(f"{g}: {sum(k in have for k in keys)}/{len(keys)} notes", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "foods"
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 10_000
    if mode in ("foods", "all"):
        run_foods(limit)
    if mode in ("notes", "all"):
        run_notes()
