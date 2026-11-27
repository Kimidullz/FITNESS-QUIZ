"""Second batch made with Kimi's Claude API credit (23 Nov 2026). Same pattern as generate.py.

  python seo/generate2.py foods-en    -> seo/data-en/<slug>.json   (English versions of the food pages)
  python seo/generate2.py exercises   -> seo/exercises/<slug>.json (BM exercise guide pages)
  python seo/generate2.py ramadan     -> seo/ramadan.json          (BM Ramadan guide)
  python seo/generate2.py plans       -> private-out/plans.json    (coach-only starting plans; NOT committed,
                                                                   uploaded as a workflow artifact)
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate import SYSTEM, call  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEO = ROOT / "seo"
S = lambda **p: {"type": "string", **p}
I = {"type": "integer"}


def obj(props: dict, req=None) -> dict:
    return {"type": "object", "properties": props, "required": req or list(props), "additionalProperties": False}


def arr(items) -> dict:
    return {"type": "array", "items": items}


BANNED = ("herbalife", "detox", "supplement", "suplemen")


def clean(d) -> bool:
    t = json.dumps(d, ensure_ascii=False).lower()
    return not any(w in t for w in BANNED)


# ---------- English food pages ----------
FOOD_EN = obj({"foods": arr(obj({
    "slug": S(), "name_en": S(description="English page name Malaysians would search, keep Malay dish names, e.g. 'Nasi lemak (plain)'"),
    "serving_en": S(), "intro": S(), "breakdown": arr(obj({"part": S(), "kcal": I})),
    "variants": arr(obj({"name": S(), "kcal": I})), "diet": S(), "tips": arr(S()),
    "swap": obj({"name": S(), "kcal": I, "why": S()}), "faq": arr(obj({"q": S(), "a": S()}))}))})


def run_foods_en():
    out = SEO / "data-en"; out.mkdir(exist_ok=True)
    foods = json.loads((SEO / "foods.json").read_text())["foods"]
    todo = [f for f in foods if not (out / f"{f['slug']}.json").exists()]
    print(len(todo), "to translate")
    for i in range(0, len(todo), 10):
        batch = todo[i:i + 10]
        src = [{"slug": f["slug"], "name": f["name"], "serving": f["serving"], "kcal": f["kcal"],
                **{k: v for k, v in json.loads((SEO / "data" / f"{f['slug']}.json").read_text()).items()
                   if k in ("intro", "breakdown", "variants", "diet", "tips", "swap", "faq")}} for f in batch]
        prompt = ("Rewrite these Malaysian food calorie pages in natural, simple Malaysian English (for Malaysians searching "
                  "e.g. 'roti canai calories'). Keep every number exactly the same. Keep Malay food names as they are "
                  "(nasi lemak, kuah dal, teh tarik). Same meaning, not word-for-word.\n\n" + json.dumps(src, ensure_ascii=False))
        got = call(prompt, FOOD_EN)["foods"]
        for d in got:
            if any(d["slug"] == f["slug"] for f in batch) and clean(d):
                (out / f"{d['slug']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
        print(f"done {min(i + 10, len(todo))}/{len(todo)}", flush=True)


# ---------- exercise guide pages ----------
EXERCISES = [
    ("squat", "Squat", "m0GcZ24pK6k"), ("duduk-bangun-kerusi", "Duduk-bangun dari kerusi (sit to stand)", "5yxfzyzEzBY"),
    ("push-up", "Push-up", "I9fsqKE5XHo"), ("push-up-lutut", "Push-up lutut (untuk beginner)", "WcHtt6zT3Go"),
    ("push-up-dinding", "Push-up dinding", "5NPvv40gd3Q"), ("glute-bridge", "Glute bridge", "XLXGydU5DdU"),
    ("plank", "Plank", "rerKy2AEHz4"), ("side-plank", "Side plank", "N_s9em1xTqU"), ("lunge", "Lunge", "FOXMtZ2dqow"),
    ("bird-dog", "Bird dog", "oKKutQk8QVE"), ("dead-bug", "Dead bug", "GbSC02oU3To"), ("calf-raise", "Calf raise", "k8ipHzKeAkQ"),
    ("step-up-tangga", "Step-up guna tangga", "VJtMb2im41c"), ("jalan-setempat", "Jalan setempat (march in place)", "u1gmWFvEluM"),
    ("jumping-jack", "Jumping jack", ""), ("mountain-climber", "Mountain climber", ""), ("burpee-beginner", "Burpee untuk beginner", ""),
    ("senaman-perut-buncit", "Senaman untuk perut buncit (dan kenapa sit-up sahaja tak cukup)", ""),
    ("senaman-lengan-bergelambir", "Senaman lengan bergelambir di rumah", ""), ("senaman-peha-punggung", "Senaman peha dan punggung di rumah", ""),
    ("senaman-10-minit-pejabat", "Senaman 10 minit di pejabat", ""), ("regangan-sebelum-tidur", "Regangan 5 minit sebelum tidur", ""),
    ("jalan-kaki-turun-berat", "Jalan kaki untuk turun berat: berapa langkah sehari?", ""),
    ("senaman-20-minit-rumah", "Senaman 20 minit di rumah tanpa alat", ""), ("hiit-beginner", "HIIT untuk beginner (15 minit)", ""),
    ("skipping", "Skipping untuk turun berat", ""), ("senaman-tangga", "Senaman naik tangga", ""),
    ("senaman-wanita-beginner", "Senaman wanita untuk beginner di rumah", ""),
    ("cardio-vs-angkat-beban", "Cardio atau angkat beban: mana lebih bagus untuk turun lemak?", ""),
    ("senaman-orang-gemuk", "Senaman untuk orang berat badan tinggi (selamat untuk lutut)", ""),
    # 28 Nov: gentle / injury set (big body, sore joints, after injury)
    ("senaman-duduk-kerusi", "Senaman sambil duduk di kerusi (untuk badan besar atau sendi sakit)", ""),
    ("senaman-sakit-lutut", "Senaman bila lutut sakit: apa yang selamat di rumah", ""),
    ("senaman-sakit-belakang", "Senaman ringan bila sakit belakang (bawah)", ""),
    ("senaman-sakit-bahu", "Senaman ringan bila bahu sakit atau kaku", ""),
    ("senaman-100kg-mula", "Berat 100kg ke atas: cara mula bersenam di rumah", ""),
    ("senaman-tanpa-lompat", "Senaman tanpa lompat (low impact) 15 minit", ""),
    ("jalan-kaki-badan-besar", "Jalan kaki untuk badan besar: cara mula tanpa sakit lutut", ""),
    ("senaman-atas-katil", "Senaman ringan atas katil (untuk yang susah bangun atau baru sembuh)", ""),
    ("senaman-lepas-cedera", "Mula bersenam semula lepas cedera: langkah selamat", ""),
    ("regangan-pinggul-ketat", "Regangan untuk pinggul ketat dan sakit duduk lama", ""),
]
EX_SCHEMA = obj({"pages": arr(obj({
    "slug": S(), "title": S(description="H1 in BM, the way people search"), "intro": S(description="2 sentences, direct answer"),
    "muscles": S(description="otot/bahagian yang dilatih, or what this routine targets"),
    "steps": arr(S()), "mistakes": arr(S()), "easier": S(), "harder": S(),
    "dose": S(description="berapa set/ulangan/minit dan berapa kali seminggu untuk beginner"),
    "safety": S(description="1-2 sentences: when to stop or see a doctor/physio"),
    "faq": arr(obj({"q": S(), "a": S()}))}))})


def run_exercises():
    out = SEO / "exercises"; out.mkdir(exist_ok=True)
    todo = [e for e in EXERCISES if not (out / f"{e[0]}.json").exists()]
    for i in range(0, len(todo), 6):
        batch = todo[i:i + 6]
        prompt = ("Write BM exercise guide pages for busy Malaysian beginners exercising at home with no equipment. "
                  "Steps: 4-6 short numbered cues. Mistakes: 3. FAQ: 3 real questions. Never promise spot reduction "
                  "(fat loss comes from overall eating + movement); say so kindly on belly/arm/thigh pages. Pages about a big body (100kg+), knee/back/shoulder pain, bed or chair exercise, "
                  "or coming back after injury: low impact only (no jumping, no deep squats), short sessions, seated or wall options, "
                  "pain-free range; stop if pain is sharp, and see a doctor/physio first after surgery, a recent injury, "
                  "chest pain or dizziness. Never diagnose.\n\n"
                  + "\n".join(f"- slug {s}: {t}" for s, t, _ in batch))
        got = call(prompt, EX_SCHEMA)["pages"]
        for d in got:
            m = [e for e in batch if e[0] == d["slug"]]
            if m and clean(d):
                d["video"] = m[0][2]
                (out / f"{d['slug']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
        print(f"done {min(i + 6, len(todo))}/{len(todo)}", flush=True)


# ---------- Ramadan guide ----------
MENU = obj({"name": S(), "items": S(), "kcal": I, "protein_g": I, "why": S()})
RAM_SCHEMA = obj({
    "title": S(), "intro": S(), "why_gain": arr(S(description="why many people gain weight in Ramadan")),
    "sahur": arr(MENU), "berbuka": arr(MENU), "bazar": arr(obj({"name": S(), "serving": S(), "kcal": I})),
    "kuih_raya": arr(obj({"name": S(), "serving": S(), "kcal": I})),
    "exercise": S(description="when and how to exercise while fasting, 3-4 sentences"),
    "tips": arr(S()), "raya": arr(S(description="tips for Hari Raya open houses")), "faq": arr(obj({"q": S(), "a": S()}))})


def run_ramadan():
    p = SEO / "ramadan.json"
    if p.exists():
        return print("ramadan exists")
    prompt = ("Write a free BM guide: 'Panduan Ramadan: puasa tanpa naik berat' for Malaysian working adults and mums. "
              "5 sahur menus and 5 berbuka menus (Malaysian food, realistic, with anggaran kcal and protein), "
              "15 popular bazar Ramadan foods with kcal, 15 kuih raya with kcal per serving, 3 why_gain points, "
              "8 tips, 5 raya open-house tips, 6 FAQ (e.g. boleh senam masa puasa, minum air berapa, kurma). "
              "People with diabetes, pregnant or breastfeeding: check with their doctor before changing how they fast or eat.")
    d = call(prompt, RAM_SCHEMA)
    if clean(d):
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1))
        print("ramadan written")


# ---------- private starting plans for coaches ----------
ROUTINES = {"office": "office job 9-5, sits most of the day", "shift": "shift worker (factory/security/nurse), rotating hours",
            "active": "on their feet all day (retail, delivery, field work)", "home": "homemaker or works from home, with kids"}
FOOD = {"out": "mostly eats out (mamak, warung, delivery)", "cook": "mostly cooks or eats home food"}
PLAN_SCHEMA = obj({"plans": arr(obj({
    "key": S(), "title": S(description="short label, e.g. 'Lelaki · pejabat · makan luar · turun lemak'"),
    "summary": S(description="2 sentences for the coach: what this person usually struggles with"),
    "day": arr(obj({"time": S(), "meal": S(), "kcal": I})),
    "swaps": arr(S()), "week1_habits": arr(S()), "workout": S(description="20-min x 3 per week plan that fits their routine"),
    "checkin": arr(S(description="questions the coach asks at the week-1 check-in")),
    "pitfalls": arr(S()), "message": S(description="welcome WhatsApp message in casual BM, 'awak', from the coach")}))})


def run_plans():
    out = ROOT / "private-out"; out.mkdir(exist_ok=True)
    p = out / "plans.json"
    have = json.loads(p.read_text()) if p.exists() else {}
    combos = []
    for sex in ("m", "f"):
        for r in ROUTINES:
            for fd in FOOD:
                for goal in ("loss", "gain"):
                    combos.append((f"{sex}|{r}|{fd}|{goal}", sex, r, fd, goal, ""))
            combos.append((f"{sex}|{r}|any|loss50", sex, r, "any", "loss", "aged 50+, may have joint stiffness"))
    todo = [c for c in combos if c[0] not in have]
    print(len(todo), "plans to write")
    for i in range(0, len(todo), 5):
        batch = todo[i:i + 5]
        lines = "\n".join(
            f"- key {k}: {'man' if s == 'm' else 'woman'}; {ROUTINES[r]}; {FOOD.get(fd, 'mixed eating')}; "
            f"goal {'lose fat (about 0.5-1 kg a week)' if g == 'loss' else 'gain weight, mostly muscle'}{'; ' + extra if extra else ''}"
            for k, s, r, fd, g, extra in batch)
        prompt = ("These are PRIVATE first-week starting plans for our coaches (Coach Kimi, Coach Zara) to adapt for a new "
                  "client of this type. The written plan is food-first. Sample day: 5-7 rows (times that fit their routine, "
                  "Malaysian meals, kcal; total around 1,500-1,800 for women losing, 1,800-2,200 men losing, +300-400 for gain). "
                  "5 swaps, 3 week-1 habits, workout plan, 5 check-in questions, 3 pitfalls. Coaches adjust numbers after the "
                  "body assessment, so say 'anggaran' where needed.\n\n" + lines)
        for d in call(prompt, PLAN_SCHEMA)["plans"]:
            if d["key"] in [b[0] for b in batch]:
                have[d["key"]] = d
        p.write_text(json.dumps(have, ensure_ascii=False, indent=1))
        print(f"done {len(have)}/{len(combos)}", flush=True)


if __name__ == "__main__":
    jobs = {"foods-en": run_foods_en, "exercises": run_exercises, "ramadan": run_ramadan, "plans": run_plans}
    for j in (sys.argv[1:] or jobs):
        if j == "extras":
            for f in jobs.values():
                f()
        else:
            jobs[j]()
