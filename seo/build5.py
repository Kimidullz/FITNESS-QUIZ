"""Round 2 pages (no API; run after build.py..build4.py, before polish.py). Data from seo/generate7.py:

  banding/<a>-vs-<b>/   50 food comparisons     banding/     index
  makan-luar/<slug>/    20 "what to order" guides makan-luar/ index
  umur-50/<slug>/       10 guides for 50+       umur-50/     index
"""
import json
import pathlib
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build2  # noqa: E402
from build import BASE, E  # noqa: E402

SEO = build2.SEO
ROOT = build2.ROOT
FOODS = {f["slug"]: f for f in json.loads((SEO / "foods.json").read_text())["foods"]}
KIMI = build2.COACH["m"][1]


def short(slug):
    return FOODS[slug]["name"].split("(")[0].strip()


def faq_ld(d):
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in d["faq"]]}, ensure_ascii=False) + "</script>"


def faqs(d):
    return "".join(f'<details><summary>{E(q["q"])}</summary><p>{E(q["a"])}</p></details>' for q in d["faq"])


def load(sec):
    d0 = SEO / sec
    return [json.loads(p.read_text()) for p in sorted(d0.glob("*.json"))] if d0.exists() else []


CSS5 = """<style>
.vs{display:grid;grid-template-columns:1fr auto 1fr;gap:8px;align-items:stretch;margin:6px 0 16px}
.vs .f{background:#161616;border:1px solid #2b2b2b;border-radius:14px;padding:14px;text-align:center}
.vs .f.win{border:2px solid var(--yellow)}
.vs .f b{display:block;font-size:15px;line-height:1.3}.vs .f .k{font:italic 40px/1.1 Anton,sans-serif;color:var(--yellow)}
.vs .f small{display:block;color:#a9a9a9;font-size:12.5px}.vs .x{align-self:center;font:italic 26px Anton,sans-serif;color:var(--red)}
.vs .tag{display:inline-block;background:var(--yellow);color:#000;font-weight:800;font-size:11px;border-radius:99px;padding:2px 8px;margin-bottom:6px}
.pick2{display:grid;gap:8px}.pick2 div{background:#161616;border:1px solid #2b2b2b;border-radius:12px;padding:12px 14px}
.pick2 .n{float:right;color:var(--yellow);font-weight:800}.pick2.bad .n{color:#ff6b6b}
.doc{background:#2a1214;border:1px solid #5a2228;border-radius:12px;padding:12px 14px;margin:10px 0 0}
</style>"""


def cta_box(src, h, p):
    return f"""<div class="box"><h2>{E(h)}</h2><p>{E(p)}</p>
<a class="btn y" href="{BASE}kuiz/?src={src}">Jawab kuiz 2 minit →</a>
<a class="btn w2" href="{BASE}semak/?src={src}">Semak makan semalam saya</a>
<p class="price">{build2.PRICE_MS}</p></div>"""


def compare_pages():
    pages, urls = load("banding"), []
    for d in pages:
        a, b = d["id"].split("-vs-")
        da, db = (json.loads((SEO / "data" / f"{x}.json").read_text()) for x in (a, b))
        na, nb = short(a), short(b)
        card = lambda s, n, dd: f"""<div class="f{' win' if d['winner'] == s else ''}">{'<span class="tag">Lebih baik</span>' if d['winner'] == s else ''}<b>{E(n)}</b><div class="k">{FOODS[s]['kcal']}</div><small>kcal · {E(FOODS[s]['serving'])}</small><small>protein {dd['protein_g']} g · lemak {dd['fat_g']} g</small></div>"""
        title = f"{na} vs {nb}: mana lebih baik masa diet?"
        others = [x for x in pages if x is not d and (a in x["id"] or b in x["id"])][:4] or [x for x in pages if x is not d][:4]
        build2.write(f"banding/{d['id']}", build2.head(title, d["verdict"][:155], f"banding/{d['id']}/", "ms", faq_ld(d) + CSS5) + f"""<main class="w">
<p class="crumb"><a href="../">Banding makanan</a></p><h1>{E(na)} vs {E(nb)}</h1><p class="lead">{E(d['verdict'])}</p>
<div class="vs">{card(a, na, da)}<div class="x">VS</div>{card(b, nb, db)}</div>
<h2>Kenapa?</h2><ul class="tips">{''.join(f'<li>{E(x)}</li>' for x in d['why'])}</ul>
<h2>Bila {E(na)} masih okay</h2><div class="card">{E(d['when_a'])}</div>
<h2>Bila {E(nb)} masih okay</h2><div class="card">{E(d['when_b'])}</div>
<h2>Cara lebih bijak</h2><div class="card">{E(d['tip'])}</div>
{cta_box('banding', 'Bukan makanan yang salah, tapi rutin', 'Jawab kuiz 2 minit untuk tahu apa yang paling menghalang result anda.')}
<h2>Soalan lazim</h2>{faqs(d)}
<h2>Banding lagi</h2><div class="rel">{''.join(f'<a href="{BASE}banding/{x["id"]}/">{E(short(x["id"].split("-vs-")[0]))} vs {E(short(x["id"].split("-vs-")[1]))}</a>' for x in others)}</div>
<div class="rel" style="margin-top:8px"><a href="{BASE}kalori/{a}/">Kalori {E(na)}</a><a href="{BASE}kalori/{b}/">Kalori {E(nb)}</a></div>
<p class="fine">Semua nombor ialah anggaran untuk hidangan biasa di Malaysia. Panduan am sahaja, bukan nasihat perubatan.</p></main>""" + build2.foot())
        urls.append(f"banding/{d['id']}/")
    if pages:
        build2.write("banding", build2.head("Banding makanan Malaysia: mana lebih baik masa diet?",
            "Nasi lemak vs roti canai, teh tarik vs kopi o, KFC vs ayam goreng biasa dan banyak lagi. Banding kalori, protein dan mana lebih baik untuk turun berat.",
            "banding/", "ms", CSS5) + f"""<main class="w">
<p class="crumb"><a href="{BASE}">Coach Kimi &amp; Coach Zara</a> › Banding makanan</p><h1>Banding makanan</h1>
<p class="lead">Dua pilihan depan mata, mana satu lebih baik masa nak turun berat? Tekan untuk tengok kalori, protein dan jawapan coach.</p>
<div class="list">{''.join(f'<a href="{x["id"]}/"><span>{E(short(x["id"].split("-vs-")[0]))} vs {E(short(x["id"].split("-vs-")[1]))}</span><b>→</b></a>' for x in pages)}</div></main>""" + build2.foot())
        urls.append("banding/")
    return urls


def order_pages():
    pages, urls = load("makan-luar"), []
    rows = lambda xs, cls: f'<div class="pick2 {cls}">' + "".join(f'<div><span class="n">~{x["kcal"]} kcal</span><b>{E(x["name"])}</b><br><small>{E(x["why"])}</small></div>' for x in xs) + "</div>"
    for d in pages:
        build2.write(f"makan-luar/{d['slug']}", build2.head(d["title"], d["intro"][:155], f"makan-luar/{d['slug']}/", "ms", faq_ld(d) + CSS5) + f"""<main class="w">
<p class="crumb"><a href="../">Makan luar</a></p><h1>{E(d['title'])}</h1><p class="lead">{E(d['intro'])}</p>
<h2>Pilihan terbaik</h2>{rows(d['best'], '')}
<h2>Hati-hati dengan ni</h2>{rows(d['careful'], 'bad')}
<h2>Cara order</h2><ul class="tips">{''.join(f'<li>{E(x)}</li>' for x in d['hacks'])}</ul>
<h2>Minuman</h2><div class="card">{E(d['drink'])}</div>
{cta_box('makan-luar', 'Selalu makan luar?', 'Coach boleh susun pelan ikut tempat anda selalu makan. Mula dengan kuiz 2 minit.')}
<h2>Soalan lazim</h2>{faqs(d)}
<h2>Tempat lain</h2><div class="rel">{''.join([f'<a href="{BASE}makan-luar/{x["slug"]}/">{E(x["title"])}</a>' for x in pages if x is not d][:6])}</div>
<p class="fine">Kalori ialah anggaran dan berbeza ikut kedai dan saiz hidangan. Panduan am sahaja.</p></main>""" + build2.foot())
        urls.append(f"makan-luar/{d['slug']}/")
    if pages:
        build2.write("makan-luar", build2.head("Makan luar tapi nak turun berat: apa nak order",
            "Panduan apa nak order di mamak, kopitiam, nasi campur, McDonald's, KFC, 7-Eleven, pasar malam, kenduri dan banyak lagi bila nak turun berat.",
            "makan-luar/", "ms", CSS5) + f"""<main class="w">
<p class="crumb"><a href="{BASE}">Coach Kimi &amp; Coach Zara</a> › Makan luar</p><h1>Makan luar, tetap turun berat</h1>
<p class="lead">Tak perlu berhenti makan luar. Pilih tempat anda, tengok apa yang paling okay untuk diorder.</p>
<div class="list">{''.join(f'<a href="{x["slug"]}/"><span>{E(x["title"])}</span><b>→</b></a>' for x in pages)}</div></main>""" + build2.foot())
        urls.append("makan-luar/")
    return urls


def senior_pages():
    pages, urls = load("umur-50"), []
    for d in pages:
        msg = urllib.parse.quote(f"Hi Coach, saya baca panduan \"{d['title']}\". Saya nak tanya pasal turun berat dan kesihatan.")
        build2.write(f"umur-50/{d['slug']}", build2.head(d["title"], d["intro"][:155], f"umur-50/{d['slug']}/", "ms", faq_ld(d) + CSS5) + f"""<main class="w">
<p class="crumb"><a href="../">Umur 50 ke atas</a></p><h1>{E(d['title'])}</h1><p class="lead">{E(d['intro'])}</p>
<div class="doc"><b>Jumpa doktor dulu kalau:</b> {E(d['doctor'])}</div>
{''.join(f'<h2>{E(s["h"])}</h2><p>{E(s["p"])}</p>' for s in d['sections'])}
<h2>Cuba minggu ini</h2><ul class="tips">{''.join(f'<li>{E(a)}</li>' for a in d['action'])}</ul>
<div class="box"><h2>Nak coach yang faham keadaan anda?</h2><p>Coach susun pelan ikut umur, ubat dan sendi anda, bukan diet ekstrem. Ada soalan? Tanya terus.</p>
<a class="btn y" href="https://wa.me/{KIMI}?text={msg}" target="_blank" rel="noopener">WhatsApp coach →</a>
<a class="btn w2" href="{BASE}kuiz/?src=umur-50">Jawab kuiz 2 minit dulu</a><p class="price">{build2.PRICE_MS}</p></div>
<h2>Soalan lazim</h2>{faqs(d)}
<h2>Baca juga</h2><div class="rel">{''.join([f'<a href="{BASE}umur-50/{x["slug"]}/">{E(x["title"])}</a>' for x in pages if x is not d][:6])}<a href="{BASE}senaman/duduk-bangun-kerusi/">Senaman duduk bangun kerusi</a></div>
<p class="fine">Panduan am sahaja, bukan nasihat perubatan. Jangan ubah atau berhenti ubat tanpa bincang dengan doktor.</p></main>""" + build2.foot())
        urls.append(f"umur-50/{d['slug']}/")
    if pages:
        build2.write("umur-50", build2.head("Umur 50 ke atas: turun berat, gula, darah tinggi dan lutut",
            "Panduan untuk umur 50 ke atas: turun berat dengan selamat, gula dalam darah, darah tinggi, kolesterol, sakit lutut dan senaman kerusi.",
            "umur-50/", "ms", CSS5) + f"""<main class="w">
<p class="crumb"><a href="{BASE}">Coach Kimi &amp; Coach Zara</a> › Umur 50 ke atas</p><h1>Umur 50 ke atas</h1>
<p class="lead">Badan berubah lepas 50, tapi turun berat dan jaga kesihatan masih boleh, dengan cara yang selamat untuk sendi dan ikut nasihat doktor anda.</p>
<div class="list">{''.join(f'<a href="{x["slug"]}/"><span>{E(x["title"])}</span><b>→</b></a>' for x in pages)}</div></main>""" + build2.foot())
        urls.append("umur-50/")
    return urls


def main():
    urls = compare_pages() + order_pages() + senior_pages()
    sm = ROOT / "sitemap.xml"
    if build2.PUBLISH2 and sm.exists() and urls:
        s = sm.read_text()
        add = "".join(f"<url><loc>{BASE}{u}</loc></url>\n" for u in urls if f"{BASE}{u}</loc>" not in s)
        sm.write_text(s.replace("</urlset>", add + "</urlset>"))
    print(f"build5: {len(urls)} pages")


if __name__ == "__main__":
    main()
