"""Third batch (23 Nov 2026): BM guide pages for working women struggling with fat loss (Coach Zara's audience).

  python seo/generate3.py wanita  -> seo/wanita/<slug>.json
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate import call  # noqa: E402
from generate2 import S, arr, clean, obj  # noqa: E402

SEO = pathlib.Path(__file__).resolve().parent

TOPICS = [
    ("kenapa-susah-turun-berat-wanita-bekerja", "Kenapa susah turun berat bila dah bekerja?"),
    ("dah-diet-tapi-berat-tak-turun", "Dah diet tapi berat tak turun: 7 sebab biasa"),
    ("lemak-perut-wanita", "Lemak perut wanita: kenapa susah hilang dan apa yang betul-betul berkesan"),
    ("duduk-lama-di-pejabat", "Duduk lama di pejabat buat berat naik? Ini cara imbangkan"),
    ("bekal-ke-pejabat-turun-berat", "Idea bekal ke pejabat untuk turun berat (5 hari)"),
    ("lunch-luar-pejabat", "Makan tengah hari di luar tapi nak turun berat: cara pilih"),
    ("snek-pejabat-sihat", "Snek pejabat: yang selamat dan yang buat berat naik diam-diam"),
    ("kuih-dan-makanan-free-di-pejabat", "Kuih meeting, birthday cake dan makanan free di pejabat: cara handle"),
    ("lapar-petang-3-petang", "Lapar teruk pukul 3-4 petang: kenapa jadi dan cara elak"),
    ("makan-malam-lewat-balik-kerja", "Balik kerja lewat dan makan malam lewat: masih boleh turun berat?"),
    ("stress-kerja-makan-banyak", "Stress kerja buat makan banyak: cara putuskan kitaran ni"),
    ("tidur-tak-cukup-berat-naik", "Tidur tak cukup buat berat naik? Apa kaitannya"),
    ("tiada-masa-bersenam", "Tiada masa bersenam: pelan 20 minit untuk wanita bekerja"),
    ("senaman-sebelum-atau-lepas-kerja", "Senam sebelum kerja atau lepas kerja: mana lebih sesuai?"),
    ("air-manis-kopi-pejabat", "Kopi, teh tarik dan air manis pejabat: berapa banyak kalori sebenarnya"),
    ("hujung-minggu-rosak-diet", "Hujung minggu rosakkan progress? Cara jaga tanpa rasa terkongkong"),
    ("kitaran-haid-dan-berat", "Berat naik sebelum datang bulan: normal ke?"),
    ("pcos-turun-berat", "PCOS dan turun berat: apa yang boleh dibantu dengan makan dan senaman"),
    ("umur-30-an-metabolisme", "Umur 30-an, metabolisme dah perlahan? Fakta sebenar"),
    ("protein-untuk-wanita", "Berapa banyak protein wanita perlu untuk turun lemak?"),
    ("nasi-untuk-wanita-turun-berat", "Wanita nak turun berat kena berhenti makan nasi?"),
    ("kalori-wanita-sehari", "Berapa kalori wanita perlu sehari untuk turun berat?"),
    ("berat-tak-turun-tapi-baju-longgar", "Berat tak turun tapi baju longgar: apa maksudnya"),
    ("diet-ekstrem-kesan", "Diet ekstrem dan 'turun 5 kg seminggu': kenapa berat naik balik"),
    ("angkat-beban-wanita-jadi-besar", "Wanita angkat beban nanti badan jadi besar? Mitos vs fakta"),
    ("lengan-dan-peha-wanita", "Lengan dan peha besar: boleh kecilkan bahagian tu sahaja?"),
    ("makan-luar-dengan-kawan", "Keluar makan dengan kawan dan family tanpa rosakkan progress"),
    ("motivasi-hilang-minggu-kedua", "Motivasi hilang lepas 2 minggu: cara terus konsisten"),
    ("wfh-berat-naik", "Kerja dari rumah (WFH) dan berat naik: cara susun hari anda"),
    ("rutin-pagi-wanita-bekerja", "Rutin pagi 15 minit untuk wanita bekerja yang nak turun lemak"),
]

SCHEMA = obj({"pages": arr(obj({
    "slug": S(), "title": S(description="H1 in BM, the way women search it"),
    "intro": S(description="2 sentences: direct, warm answer first"),
    "sections": arr(obj({"h": S(description="short subheading"), "p": S(description="2-4 sentences, practical")})),
    "action": arr(S(description="small step she can do this week")),
    "myth": S(description="one common belief and the truth, 1-2 sentences"),
    "faq": arr(obj({"q": S(), "a": S()}))}))})


def run_wanita():
    out = SEO / "wanita"; out.mkdir(exist_ok=True)
    todo = [t for t in TOPICS if not (out / f"{t[0]}.json").exists()]
    for i in range(0, len(todo), 5):
        batch = todo[i:i + 5]
        prompt = ("Write BM guide pages for Malaysian WORKING WOMEN (20s-40s, office/field/WFH, busy) who struggle with fat loss. "
                  "Casual but clear BM, use 'anda'. Malaysian food and work life (mamak, nasi campur, bekal, meeting kuih, traffic). "
                  "3-5 sections, 3-5 action steps, 1 myth, 3 FAQ. Realistic: about 0.5-1 kg a week, no crash diets, no spot reduction, "
                  "no products or supplements named. Where health conditions matter (PCOS, thyroid, pregnancy), say to check with a doctor. "
                  "Do NOT write about postpartum or breastfeeding.\n\n" + "\n".join(f"- slug {s}: {t}" for s, t in batch))
        for d in call(prompt, SCHEMA)["pages"]:
            if any(d["slug"] == b[0] for b in batch) and clean(d):
                (out / f"{d['slug']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
        print(f"done {min(i + 5, len(todo))}/{len(todo)}", flush=True)


if __name__ == "__main__":
    {"wanita": run_wanita}[sys.argv[1] if len(sys.argv) > 1 else "wanita"]()
