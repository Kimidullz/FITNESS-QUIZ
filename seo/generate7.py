"""Seventh batch (24 Nov 2026, round 2). Needs ANTHROPIC_API_KEY; output is plain JSON, pages keep working after the credit ends.

  python seo/generate7.py compare  -> seo/banding/<a>-vs-<b>.json   (50 "X vs Y, mana lebih baik masa diet?" pages)
  python seo/generate7.py order    -> seo/makan-luar/<slug>.json    (20 "apa nak order di ..." guides)
  python seo/generate7.py senior   -> seo/umur-50/<slug>.json       (10 guides for 50+, blood sugar, knees)
  python seo/generate7.py round2   -> all three (skips what already exists)
  python seo/generate7.py en2      -> English versions: seo/en/compare/, seo/en/eat-out/, seo/en/over-50/ (same file names as BM)
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate import call  # noqa: E402
from generate2 import S, arr, clean, obj  # noqa: E402

SEO = pathlib.Path(__file__).resolve().parent
FOODS = {f["slug"]: f for f in json.loads((SEO / "foods.json").read_text())["foods"]}

PAIRS = [
    ("nasi-lemak-biasa", "roti-canai-kosong"), ("roti-canai-kosong", "thosai-kosong"), ("roti-telur", "roti-planta"),
    ("nasi-lemak-biasa", "mee-hoon-goreng"), ("roti-bakar-kaya-mentega", "oat-dengan-susu"), ("nasi-lemak-ayam-goreng", "nasi-ayam"),
    ("nasi-ayam", "nasi-campur"), ("nasi-goreng-kampung", "nasi-goreng-pattaya"), ("nasi-kandar", "nasi-briyani-ayam"),
    ("nasi-ayam-penyet", "nasi-ayam"), ("nasi-putih", "nasi-goreng-kampung"), ("nasi-dagang", "nasi-kerabu"),
    ("mee-goreng-mamak", "maggi-goreng"), ("char-kuey-teow", "kuey-teow-sup"), ("laksa-penang", "laksa-kari"),
    ("mee-rebus", "mee-soto"), ("wantan-mee-kering", "pan-mee-sup"), ("bihun-sup", "mee-goreng-mamak"),
    ("mi-segera", "maggi-goreng"), ("mee-kari", "laksa-kari"), ("roti-tisu", "roti-canai-kosong"),
    ("murtabak-ayam", "roti-telur"), ("ayam-tandoori-dengan-naan", "nasi-briyani-ayam"), ("naan-cheese", "capati"),
    ("tosai-masala", "thosai-kosong"), ("teh-tarik", "kopi-o"), ("teh-tarik", "teh-o-ais"), ("milo-ais", "teh-tarik"),
    ("bubble-tea", "kopi-latte"), ("air-tebu", "air-kelapa"), ("jus-oren", "minuman-bergas"), ("sirap-bandung", "teh-ais-limau"),
    ("neslo-ais", "milo-ais"), ("cendol", "ais-kacang"), ("pisang-goreng", "cucur-udang"), ("kuih-seri-muka", "kuih-lapis"),
    ("donut-gula", "apam-balik"), ("karipap", "popia-goreng"), ("keropok-lekor", "pisang-goreng"),
    ("burger-ayam", "burger-daging"), ("ayam-goreng-fast-food-original", "ayam-goreng"), ("pizza", "burger-daging"),
    ("kentang-goreng", "nugget-ayam"), ("chicken-chop-dengan-kentang", "spaghetti-bolognese"), ("shawarma-ayam", "burger-ayam"),
    ("satay-ayam", "ayam-goreng"), ("pisang", "epal"), ("durian", "mangga"), ("kerepek-ubi", "kacang-tanah"), ("roti-putih", "capati"),
]

PLACES = [
    ("mamak", "Kedai mamak"), ("kopitiam", "Kopitiam"), ("nasi-campur", "Kedai nasi campur / nasi kandar"),
    ("mcdonalds", "McDonald's"), ("kfc", "KFC"), ("subway", "Subway"), ("pizza", "Pizza (Domino's, Pizza Hut)"),
    ("7-eleven", "7-Eleven / kedai serbaneka"), ("pasar-malam", "Pasar malam"), ("bazar-ramadan", "Bazar Ramadan"),
    ("kenduri", "Kenduri kahwin"), ("buffet-hotel", "Buffet hotel"), ("restoran-thai", "Restoran Thai / tomyam"),
    ("restoran-cina", "Restoran Cina / chap fan"), ("restoran-jepun", "Restoran Jepun / sushi"), ("kedai-kopi-moden", "Kafe kopi (Starbucks, ZUS, Tealive)"),
    ("steamboat", "Steamboat / BBQ"), ("warung-sarapan", "Warung sarapan pagi"), ("hentian-rnr", "Hentian R&R lebuhraya"),
    ("food-court", "Food court / medan selera"),
]

SENIOR = [
    ("turun-berat-umur-50", "Turun berat umur 50 ke atas: apa yang berubah dan apa yang masih berkesan"),
    ("gula-darah-tinggi-makan", "Gula dalam darah tinggi (pra-diabetes): cara susun pinggan harian"),
    ("diabetes-dan-nasi", "Ada diabetes, boleh makan nasi lagi? Cara makan yang lebih selamat"),
    ("darah-tinggi-garam", "Darah tinggi: kurangkan garam dalam makanan Malaysia tanpa hilang rasa"),
    ("kolesterol-tinggi-makan", "Kolesterol tinggi: apa nak kurangkan dan apa nak tambah"),
    ("sakit-lutut-bersenam", "Sakit lutut tapi nak bersenam: 6 senaman yang mesra lutut"),
    ("senaman-kerusi", "Senaman kerusi 15 minit untuk umur 50 ke atas"),
    ("otot-hilang-lepas-50", "Otot makin hilang lepas umur 50: kenapa protein dan latihan kekuatan penting"),
    ("jalan-kaki-warga-emas", "Jalan kaki untuk umur 50 ke atas: berapa lama, berapa laju, dan cara mula"),
    ("menopaus-berat-naik", "Menopaus dan berat naik: apa yang berlaku dan apa boleh dibuat"),
]

RULES = ("Casual but clear BM ('anda'), Malaysian food and life. Realistic: no crash diets, no kg promises, no products, "
         "supplements or brand names except the shop/restaurant names given. Numbers are estimates.")


def run_compare():
    out = SEO / "banding"; out.mkdir(exist_ok=True)
    todo = [p for p in PAIRS if not (out / f"{p[0]}-vs-{p[1]}.json").exists()]
    sch = obj({"pages": arr(obj({"id": S(), "winner": S(description="slug of the better pick for fat loss, or 'seri' if equal"),
                                 "verdict": S(description="1-2 sentence direct answer"), "why": arr(S(description="reason, with numbers")),
                                 "when_a": S(description="when the first food is still fine"), "when_b": S(description="when the second food is still fine"),
                                 "tip": S(description="one smarter way to eat either"), "faq": arr(obj({"q": S(), "a": S()}))}))})
    for i in range(0, len(todo), 10):
        batch = todo[i:i + 10]
        lines = []
        for a, b in batch:
            da, db = (json.loads((SEO / "data" / f"{x}.json").read_text()) for x in (a, b))
            lines.append(f"- id {a}-vs-{b}: A {FOODS[a]['name']} ({FOODS[a]['serving']}, ~{FOODS[a]['kcal']} kcal, protein {da['protein_g']} g, "
                         f"lemak {da['fat_g']} g) vs B {FOODS[b]['name']} ({FOODS[b]['serving']}, ~{FOODS[b]['kcal']} kcal, protein {db['protein_g']} g, lemak {db['fat_g']} g)")
        prompt = ("Write 'A vs B: mana lebih baik masa nak turun berat?' comparison pages for Malaysian readers. Judge on calories, "
                  "protein (keeps you full) and how easy it is to overeat. 3-4 'why' points using the numbers given, 2 FAQ. "
                  "Never shame any food; both can fit. " + RULES + "\n\n" + "\n".join(lines))
        for d in call(prompt, sch)["pages"]:
            if any(d["id"] == f"{a}-vs-{b}" for a, b in batch) and clean(d):
                (out / f"{d['id']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
        print(f"compare {min(i + 10, len(todo))}/{len(todo)}", flush=True)


def run_order():
    out = SEO / "makan-luar"; out.mkdir(exist_ok=True)
    todo = [p for p in PLACES if not (out / f"{p[0]}.json").exists()]
    sch = obj({"pages": arr(obj({"slug": S(), "title": S(description="BM H1, e.g. 'Apa nak order di kedai mamak bila nak turun berat'"),
                                 "intro": S(), "best": arr(obj({"name": S(), "kcal": {"type": "integer"}, "why": S()})),
                                 "careful": arr(obj({"name": S(), "kcal": {"type": "integer"}, "why": S()})),
                                 "hacks": arr(S(description="ordering trick, e.g. kurang manis, kuah asing")),
                                 "drink": S(description="best drink choice there"), "faq": arr(obj({"q": S(), "a": S()}))}))})
    for i in range(0, len(todo), 5):
        batch = todo[i:i + 5]
        prompt = ("Write 'what to order' guides for Malaysians who want to lose weight but still eat out. For each place: 5-6 "
                  "'best' picks with estimated kcal, 4-5 'careful' items with estimated kcal, 5 ordering hacks in Malaysian style, "
                  "the best drink, 2 FAQ. Real menu items people know at that kind of place. " + RULES + "\n\n"
                  + "\n".join(f"- slug {s}: {n}" for s, n in batch))
        for d in call(prompt, sch)["pages"]:
            if any(d["slug"] == b[0] for b in batch) and clean(d):
                (out / f"{d['slug']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
        print(f"order {min(i + 5, len(todo))}/{len(todo)}", flush=True)


def run_senior():
    out = SEO / "umur-50"; out.mkdir(exist_ok=True)
    todo = [t for t in SENIOR if not (out / f"{t[0]}.json").exists()]
    sch = obj({"pages": arr(obj({"slug": S(), "title": S(), "intro": S(), "sections": arr(obj({"h": S(), "p": S()})),
                                 "action": arr(S()), "doctor": S(description="when to see a doctor first, specific"),
                                 "faq": arr(obj({"q": S(), "a": S()}))}))})
    for i in range(0, len(todo), 5):
        batch = todo[i:i + 5]
        prompt = ("Write BM guide pages for Malaysians aged 50+ (working or retired) who want to lose weight or manage blood "
                  "sugar, blood pressure, cholesterol or sore knees. Warm, respectful, simple words (no gym jargon). 3-5 sections, "
                  "3-5 small action steps, a specific 'see your doctor first if...' note, 3 FAQ. Movement must be joint-friendly "
                  "(walking, chair exercises, wall push-ups, no jumping). Never tell anyone to change or stop medicine; say to "
                  "talk to their doctor. " + RULES + "\n\n" + "\n".join(f"- slug {s}: {t}" for s, t in batch))
        for d in call(prompt, sch)["pages"]:
            if any(d["slug"] == b[0] for b in batch) and clean(d):
                (out / f"{d['slug']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
        print(f"senior {min(i + 5, len(todo))}/{len(todo)}", flush=True)


EN_RULE = ("Translate into simple, natural Malaysian English for Malaysian readers (keep Malaysian food and place names like nasi "
           "lemak, teh tarik, kuih, mamak, kopitiam, kenduri, pasar malam as they are; ordering phrases like 'kurang manis' may stay "
           "in Malay with a short English gloss). Keep the meaning, numbers, kcal and doctor/safety notes exactly; keep every list in "
           "the same order and length; do not add claims, products, supplements or brand names. Keep id and slug exactly as given. "
           "slug_en = short lowercase English URL slug with hyphens.")
FAQ = arr(obj({"q": S(), "a": S()}))
ITEMS = arr(obj({"name": S(), "kcal": {"type": "integer"}, "why": S()}))
EN_JOBS = {
    "compare": ("banding", "id", 10, obj({"id": S(), "verdict": S(), "why": arr(S()), "when_a": S(), "when_b": S(), "tip": S(), "faq": FAQ})),
    "eat-out": ("makan-luar", "slug", 5, obj({"slug": S(), "slug_en": S(), "title": S(), "intro": S(), "best": ITEMS, "careful": ITEMS,
                                              "hacks": arr(S()), "drink": S(), "faq": FAQ})),
    "over-50": ("umur-50", "slug", 5, obj({"slug": S(), "slug_en": S(), "title": S(), "intro": S(), "sections": arr(obj({"h": S(), "p": S()})),
                                           "action": arr(S()), "doctor": S(), "faq": FAQ})),
}


def run_en2():
    for kind, (src, key, n, sch) in EN_JOBS.items():
        out = SEO / "en" / kind; out.mkdir(parents=True, exist_ok=True)
        todo = [p for p in sorted((SEO / src).glob("*.json")) if not (out / p.name).exists()]
        for i in range(0, len(todo), n):
            batch = [json.loads(p.read_text()) for p in todo[i:i + n]]
            for b in batch:
                b.pop("winner", None)
            for d in call(EN_RULE + "\n\n" + json.dumps(batch, ensure_ascii=False), obj({"pages": arr(sch)}))["pages"]:
                if any(d[key] == b[key] for b in batch) and clean(d):
                    (out / f"{d[key]}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
            print(f"en2 {kind} {min(i + n, len(todo))}/{len(todo)}", flush=True)


JOBS = {"compare": run_compare, "order": run_order, "senior": run_senior}

if __name__ == "__main__":
    job = sys.argv[1] if len(sys.argv) > 1 else "round2"
    if job == "en2":
        run_en2()
    for name, fn in JOBS.items():
        if job in (name, "round2"):
            fn()
