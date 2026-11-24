"""Sixth batch (24 Nov 2026, after the 5-tester site check). Needs ANTHROPIC_API_KEY; output is plain JSON, so pages keep working after the credit ends.

  python seo/generate6.py en       -> seo/en/women/<slug>.json, seo/en/exercises/<slug>.json, seo/en/ramadan.json (English versions)
  python seo/generate6.py health   -> results/starter.json, goal "health" keys rewritten safe for joint pain / older / not office-only
  python seo/generate6.py aliases  -> seo/aliases.json   {food slug: [search words]}
  python seo/generate6.py related  -> seo/related.json   {"wanita/<slug>": [...], "senaman/<slug>": [...]} hand-picked links
  python seo/generate6.py all      -> everything above (skips what already exists)
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate import call  # noqa: E402
from generate2 import S, arr, clean, obj  # noqa: E402
import generate4  # noqa: E402

SEO = pathlib.Path(__file__).resolve().parent
ROOT = SEO.parent
EN_RULE = ("Translate into simple, natural Malaysian English for Malaysian readers (keep Malaysian food names like nasi lemak, "
           "teh tarik, kuih, mamak as they are). Keep the meaning, numbers and safety notes exactly; do not add claims, "
           "products, supplements or brand names. slug_en = short lowercase English URL slug with hyphens.")

FAQ = arr(obj({"q": S(), "a": S()}))
SCHEMAS = {
    "women": obj({"slug": S(), "slug_en": S(), "title": S(), "intro": S(), "sections": arr(obj({"h": S(), "p": S()})),
                  "action": arr(S()), "myth": S(), "faq": FAQ}),
    "exercises": obj({"slug": S(), "slug_en": S(), "title": S(), "intro": S(), "muscles": S(), "steps": arr(S()),
                      "mistakes": arr(S()), "easier": S(), "harder": S(), "dose": S(), "safety": S(), "faq": FAQ}),
}


def run_en():
    for kind, src in (("women", SEO / "wanita"), ("exercises", SEO / "exercises")):
        out = SEO / "en" / kind; out.mkdir(parents=True, exist_ok=True)
        todo = [p for p in sorted(src.glob("*.json")) if not (out / p.name).exists()]
        for i in range(0, len(todo), 6):
            batch = [json.loads(p.read_text()) for p in todo[i:i + 6]]
            for b in batch:
                b.pop("video", None)
            prompt = EN_RULE + " Keep each slug exactly as given.\n\n" + json.dumps(batch, ensure_ascii=False)
            for d in call(prompt, obj({"pages": arr(SCHEMAS[kind])}))["pages"]:
                if any(d["slug"] == b["slug"] for b in batch) and clean(d):
                    (out / f"{d['slug']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
            print(f"en {kind} {min(i + 6, len(todo))}/{len(todo)}", flush=True)
    p = SEO / "en" / "ramadan.json"
    if not p.exists():
        d = json.loads((SEO / "ramadan.json").read_text())
        menu = arr(obj({"name": S(), "items": S(), "why": S(), "kcal": {"type": "integer"}, "protein_g": {"type": "integer"}}))
        rows = arr(obj({"name": S(), "serving": S(), "kcal": {"type": "integer"}}))
        sch = obj({"title": S(), "intro": S(), "why_gain": arr(S()), "sahur": menu, "berbuka": menu, "bazar": rows,
                   "kuih_raya": rows, "exercise": S(), "tips": arr(S()), "raya": arr(S()), "faq": FAQ})
        r = call(EN_RULE + " Keep every list in the same order and length. Keep sahur, berbuka, Raya and food names.\n\n"
                 + json.dumps(d, ensure_ascii=False), sch)
        if clean(r):
            p.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print("en ramadan done", flush=True)


def run_health():
    """Goal 'health' (blood sugar, blood pressure, joint pain): plans safe for older adults, retirees and sore knees."""
    p = ROOT / "results" / "starter.json"
    have = json.loads(p.read_text())
    done_flag = SEO / "en" / ".health-done"
    if done_flag.exists():
        return
    todo = [c for c in generate4.combos() if c[0].startswith("loss|5|")]
    new = {}
    for i in range(0, len(todo), 8):
        batch = todo[i:i + 8]
        lines = "\n".join(f"- key {k}: goal \"{g}\"; " + (f"biggest problem habit ({sh}): asked \"{qq}\", answered \"{an}\"" if sh
                          else "no bad habit, wants to go further") for k, pa, g, sh, qq, an in batch)
        prompt = ("Quiz result page for Coach Kimi & Coach Zara (Malaysia). These people picked the goal HEALTH (blood sugar, "
                  "blood pressure, cholesterol, joint pain). Many are 45-65, some retired or at home, some still working, some "
                  "have sore knees or take medicine. For each key write a 3-DAY STARTER PLAN that fixes their biggest problem "
                  "habit first. Each day: a short focus and exactly 3 small, concrete tasks. Day 1 easiest. Fit ANY daily "
                  "routine: say 'hari anda' not 'pejabat', no LRT or office-only examples. Movement must be joint-friendly: "
                  "walking, chair sit-to-stand, wall push-up, marching in place, stretching; NO jumping, deep squats, lunges, "
                  "burpees or plank holds. Food: Malaysian (nasi campur, kopitiam, home cooking), less sugar in drinks, "
                  "half-plate vegetables, protein each meal; no crash diets, no calorie targets, no fasting advice. If they "
                  "take medicine for diabetes or blood pressure, one task on day 1 may say to tell their doctor they are "
                  "changing how they eat. day3 = one line asking them to WhatsApp their coach on day 3 with what they noticed. "
                  "Every text in casual BM ('anda') as ms and simple Malaysian English as en. No products, supplements, brand "
                  "names or kg promises.\n\n" + lines)
        for d in call(prompt, generate4.SCHEMA)["plans"]:
            if any(d["key"] == b[0] for b in batch) and clean(d) and len(d["days"]) == 3:
                new[d["key"]] = {"t": d["title"], "d": [{"f": x["focus"], "x": x["tasks"][:3]} for x in d["days"]], "e": d["day3"]}
        print(f"health {len(new)}/{len(todo)}", flush=True)
    have.update(new)
    p.write_text(json.dumps(have, ensure_ascii=False, separators=(",", ":")))
    if len(new) == len(todo):
        done_flag.parent.mkdir(parents=True, exist_ok=True); done_flag.write_text("ok")


def run_aliases():
    p = SEO / "aliases.json"
    if p.exists():
        return
    foods = json.loads((SEO / "foods.json").read_text())["foods"]
    lst = "\n".join(f"- {f['slug']}: {f['name']}" for f in foods)
    sch = obj({"foods": arr(obj({"slug": S(), "words": arr(S(description="lowercase search word"))}))})
    r = call("Search box for a Malaysian food calorie list. For each food give 3-8 extra lowercase words people might type "
             "to find it: English name, short forms, common misspellings and joined-up spellings (e.g. 'nasilemak', "
             "'nasi lmk'), Chinese/Indian/Western names Malaysians use (e.g. 'chicken rice', 'roti prata'), and the "
             "main ingredient. Do not repeat the food's own name.\n\n" + lst, sch)
    out = {x["slug"]: sorted({w.strip().lower() for w in x["words"] if w.strip()}) for x in r["foods"]}
    p.write_text(json.dumps(out, ensure_ascii=False, indent=0))
    print("aliases", len(out), flush=True)


def run_related():
    p = SEO / "related.json"
    if p.exists():
        return
    pages = []
    for sec, d0 in (("wanita", SEO / "wanita"), ("senaman", SEO / "exercises")):
        for f in sorted(d0.glob("*.json")):
            pages.append((f"{sec}/{f.stem}", json.loads(f.read_text())["title"]))
    foods = json.loads((SEO / "foods.json").read_text())["foods"]
    tools = [("semak", "Semak makan semalam (kira kalori semalam)"), ("workout", "Workout 7 Hari di rumah (pelan senaman)"),
             ("ramadan", "Panduan Ramadan")]
    sch = obj({"pages": arr(obj({"id": S(), "same": arr(S()), "other": arr(S())}))})
    out = {}
    ids = [x[0] for x in pages]
    for i in range(0, len(pages), 30):
        batch = pages[i:i + 30]
        prompt = ("Pick related links for guide pages on a Malaysian fat-loss coaching site. For each page id: 'same' = the 4 "
                  "most useful OTHER pages from the guide list for someone reading it (prefer the same section, mix sections "
                  "when it helps); 'other' = 2 links from the food or tool lists that fit the topic (food ids look like "
                  "kalori/<slug>, tools are semak, workout, ramadan). Use ids exactly as listed.\n\nGUIDES:\n"
                  + "\n".join(f"{a}: {b}" for a, b in pages) + "\n\nFOODS:\n" + "\n".join(f"kalori/{f['slug']}: {f['name']}" for f in foods)
                  + "\n\nTOOLS:\n" + "\n".join(f"{a}: {b}" for a, b in tools) + "\n\nPAGES TO DO:\n" + "\n".join(a for a, _ in batch))
        valid = set(ids) | {f"kalori/{f['slug']}" for f in foods} | {t[0] for t in tools}
        for d in call(prompt, sch)["pages"]:
            if d["id"] in ids:
                out[d["id"]] = {"same": [x for x in d["same"] if x in ids and x != d["id"]][:4],
                                "other": [x for x in d["other"] if x in valid and x not in ids][:2]}
        print(f"related {len(out)}/{len(pages)}", flush=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=0))


JOBS = {"en": run_en, "health": run_health, "aliases": run_aliases, "related": run_related}

if __name__ == "__main__":
    job = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn in JOBS.items():
        if job in (name, "all"):
            fn()
