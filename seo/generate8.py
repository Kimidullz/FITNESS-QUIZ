"""27 Nov 2026: 20 MORE guide pages for working women (Coach Zara's audience), Malay + English.
Kept apart from seo/wanita/ until Kimi approves, so they stay hidden (see build7.py).

  python seo/generate8.py wanita3  -> seo/wanita-new/<slug>.json (BM) then seo/en/women-new/<slug>.json (EN)
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate import call  # noqa: E402
from generate2 import S, arr, clean, obj  # noqa: E402
from generate3 import SCHEMA  # noqa: E402
from generate6 import EN_RULE, SCHEMAS  # noqa: E402

SEO = pathlib.Path(__file__).resolve().parent

TOPICS = [
    ("kerja-shift-turun-berat", "Kerja shift (jururawat, kilang, keselamatan): cara turun berat ikut jadual yang berubah"),
    ("outstation-dan-kursus", "Outstation, kursus dan seminar di hotel: cara jaga progress bila jauh dari rumah"),
    ("berat-naik-lepas-kahwin", "Berat naik lepas kahwin: kenapa jadi dan cara urus berdua"),
    ("puasa-sunat-turun-berat", "Puasa sunat Isnin dan Khamis: boleh bantu turun berat?"),
    ("intermittent-fasting-wanita-bekerja", "Intermittent fasting untuk wanita bekerja: sesuai ke dengan jadual kerja?"),
    ("skip-sarapan-turun-berat", "Skip sarapan supaya kalori kurang: idea baik atau tidak?"),
    ("order-grabfood-foodpanda", "Selalu order GrabFood atau foodpanda tapi nak turun berat: cara pilih menu"),
    ("meal-prep-hujung-minggu", "Meal prep hujung minggu: 2 jam untuk bekal 5 hari kerja"),
    ("makan-sihat-bajet", "Makan sihat dengan bajet RM15 sehari untuk wanita bekerja"),
    ("cheat-day-perlu-ke", "Cheat day: perlu ke, dan cara buat tanpa rosakkan progress"),
    ("berapa-kerap-timbang-berat", "Berapa kerap patut timbang berat? Harian, mingguan atau bulanan"),
    ("penat-lesu-bila-diet", "Selalu penat dan lesu bila diet: tanda anda makan terlalu sikit?"),
    ("langkah-harian-kerja-duduk", "7,000 hingga 10,000 langkah sehari bila kerja duduk: cara capai tanpa ke gym"),
    ("craving-manis-waktu-malam", "Craving manis waktu malam: cara kawal tanpa rasa terseksa"),
    ("minum-air-kosong-cukup", "Cukup minum air ke? Air kosong, lapar palsu dan berat badan"),
    ("makan-rumah-family-mertua", "Makan di rumah family atau mertua: cara jaga makan tanpa kecil hati sesiapa"),
    ("umur-40-an-berat-naik", "Umur 40-an, berat naik walaupun makan sama: apa yang berubah dan apa nak buat"),
    ("cikgu-turun-berat", "Cikgu dan pensyarah: turun berat dengan jadual sekolah, kantin dan kerja bawa balik"),
    ("ibu-bekerja-masa-tak-cukup", "Kerja, anak dan rumah: cara turun berat bila masa memang tak cukup"),
    ("mula-semula-lepas-gagal", "Dah gagal diet banyak kali: cara mula semula yang berbeza kali ini"),
]

SCHEMA_REL = obj({"pages": arr(obj({**SCHEMA["properties"]["pages"]["items"]["properties"],
                                    "related": arr(S(description="slug from the EXISTING list"))}))})


def run_bm():
    out = SEO / "wanita-new"; out.mkdir(exist_ok=True)
    existing = sorted(p.stem for p in (SEO / "wanita").glob("*.json"))
    todo = [t for t in TOPICS if not (out / f"{t[0]}.json").exists()]
    for i in range(0, len(todo), 5):
        batch = todo[i:i + 5]
        prompt = ("Write BM guide pages for Malaysian WORKING WOMEN (20s-40s, office/field/shift/WFH, busy) who struggle with fat loss. "
                  "Casual but clear BM, use 'anda'. Malaysian food and work life (mamak, nasi campur, bekal, meeting kuih, traffic). "
                  "3-5 sections, 3-5 action steps, 1 myth, 3 FAQ. Realistic: about 0.5-1 kg a week, no crash diets, no spot reduction, "
                  "no products or supplements named. Where health conditions or religious rulings matter (PCOS, thyroid, perimenopause, "
                  "pregnancy, fasting rules), keep it general and say to check with a doctor or ustazah. "
                  "Do NOT write about postpartum or breastfeeding. "
                  "related = 4 slugs from this EXISTING list that a reader of this page would want next: " + ", ".join(existing)
                  + "\n\n" + "\n".join(f"- slug {s}: {t}" for s, t in batch))
        for d in call(prompt, SCHEMA_REL)["pages"]:
            if any(d["slug"] == b[0] for b in batch) and clean(d):
                d["related"] = [r for r in d.get("related", []) if r in existing][:4]
                (out / f"{d['slug']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
        print(f"bm {min(i + 5, len(todo))}/{len(todo)}", flush=True)


def run_en():
    src = SEO / "wanita-new"
    out = SEO / "en" / "women-new"; out.mkdir(parents=True, exist_ok=True)
    todo = [p for p in sorted(src.glob("*.json")) if not (out / p.name).exists()]
    for i in range(0, len(todo), 5):
        batch = [json.loads(p.read_text()) for p in todo[i:i + 5]]
        for b in batch:
            b.pop("related", None)
        prompt = EN_RULE + " Keep each slug exactly as given.\n\n" + json.dumps(batch, ensure_ascii=False)
        for d in call(prompt, obj({"pages": arr(SCHEMAS["women"])}))["pages"]:
            if any(d["slug"] == b["slug"] for b in batch) and clean(d):
                (out / f"{d['slug']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
        print(f"en {min(i + 5, len(todo))}/{len(todo)}", flush=True)


if __name__ == "__main__":
    job = sys.argv[1] if len(sys.argv) > 1 else "wanita3"
    if job in ("wanita3", "bm"):
        run_bm()
    if job in ("wanita3", "en"):
        run_en()
