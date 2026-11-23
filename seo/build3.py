"""Third batch of pages (no API): wanita/<slug>/ guides for working women (Coach Zara's audience).
PUBLISH3 = False keeps them noindex and out of the sitemap until Kimi approves.
"""
import json
import pathlib
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build2  # noqa: E402
from build import BASE, E  # noqa: E402

PUBLISH3 = False
build2.PUBLISH2 = PUBLISH3  # head() reads this for the noindex tag
SEO = build2.SEO
ZARA = build2.COACH["f"][1]


def zara_box(topic):
    msg = urllib.parse.quote(f"Hi Coach Zara, saya baca panduan \"{topic}\". Saya nak tanya pasal turun berat.")
    return f"""<div class="box"><h2>Penat cuba sendiri?</h2><p>Coach Zara bantu wanita bekerja turun lemak tanpa diet ekstrem, ikut jadual kerja dan makanan harian anda.</p>
<a class="btn y" href="https://wa.me/{ZARA}?text={msg}" target="_blank" rel="noopener">WhatsApp Coach Zara →</a>
<a class="btn w2" href="{BASE}kuiz/?src=wanita">Jawab kuiz 2 minit dulu</a>
<p class="price">{build2.PRICE_MS}</p></div>"""


def main():
    d0 = SEO / "wanita"
    pages = [json.loads(p.read_text()) for p in sorted(d0.glob("*.json"))] if d0.exists() else []
    for d in pages:
        faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in d["faq"]]}
        rel = [x for x in pages if x["slug"] != d["slug"]][:6]
        build2.write(f"wanita/{d['slug']}", build2.head(f"{d['title']} | Coach Zara", d["intro"][:155], f"wanita/{d['slug']}/", "ms",
            f'<script type="application/ld+json">{json.dumps(faq, ensure_ascii=False)}</script>') + f"""<main class="w">
<p class="crumb"><a href="../">Turun lemak untuk wanita bekerja</a></p><h1>{E(d['title'])}</h1><p class="lead">{E(d['intro'])}</p>
{''.join(f'<h2>{E(s["h"])}</h2><p>{E(s["p"])}</p>' for s in d['sections'])}
<h2>Cuba minggu ini</h2><ul class="tips">{''.join(f'<li>{E(a)}</li>' for a in d['action'])}</ul>
<div class="card"><b>Mitos:</b> {E(d['myth'])}</div>
{zara_box(d['title'])}
<h2>Soalan lazim</h2>{''.join(f'<details><summary>{E(q["q"])}</summary><p>{E(q["a"])}</p></details>' for q in d['faq'])}
<h2>Baca juga</h2><div class="rel">{''.join(f'<a href="../{x["slug"]}/">{E(x["title"])}</a>' for x in rel)}</div>
<p class="fine">Panduan am sahaja, bukan nasihat perubatan. Ada masalah kesihatan, sedang mengandung atau ambil ubat: bincang dengan doktor dulu.</p></main>""" + build2.foot())
    if pages:
        build2.write("wanita", build2.head("Turun lemak untuk wanita bekerja | Coach Zara",
            "Panduan turun lemak untuk wanita bekerja: bekal, snek pejabat, lapar petang, stress, tiada masa bersenam dan banyak lagi.", "wanita/") + f"""<main class="w">
<p class="crumb"><a href="{BASE}">Coach Kimi &amp; Coach Zara</a> › Wanita bekerja</p><h1>Turun lemak untuk wanita bekerja</h1>
<p class="lead">Sibuk kerja, makan ikut masa yang ada, dah cuba macam-macam tapi berat tak bergerak? Mula di sini.</p>
<div class="list">{''.join(f'<a href="{x["slug"]}/"><span>{E(x["title"])}</span><b>→</b></a>' for x in pages)}</div>
{zara_box("Turun lemak untuk wanita bekerja")}</main>""" + build2.foot())
    urls = [f"wanita/{d['slug']}/" for d in pages] + (["wanita/"] if pages else [])
    sm = build2.ROOT / "sitemap.xml"
    if PUBLISH3 and sm.exists() and urls and f"{BASE}wanita/</loc>" not in sm.read_text():
        sm.write_text(sm.read_text().replace("</urlset>", "".join(f"<url><loc>{BASE}{u}</loc></url>\n" for u in urls) + "</urlset>"))
    print(f"build3: {len(urls)} pages (publish={PUBLISH3})")


if __name__ == "__main__":
    main()
