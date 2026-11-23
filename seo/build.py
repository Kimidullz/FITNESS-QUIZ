"""Builds the 'Kalori makanan Malaysia' pages from seo/foods.json + seo/data/*.json (no API needed).

  python seo/build.py        -> kalori/index.html, kalori/<slug>/index.html, sitemap.xml, robots.txt

PUBLISH = True keeps the pages out of Google (noindex, no sitemap) until Kimi approves them.
"""
import html
import json
import pathlib

PUBLISH = True

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEO = ROOT / "seo"
OUT = ROOT / "kalori"
BASE = "https://kimidullz.github.io/FITNESS-QUIZ/"
WALK_KCAL_MIN = 4.5   # brisk walk, about 65 kg adult
E = html.escape

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">'
CSS = """
:root{--red:#E30613;--yellow:#FFD200;--ink:#111;--muted:#555;--line:#e6e3dc;--bg:#f6f4ef}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 Montserrat,system-ui,sans-serif}
a{color:inherit}
.top{background:#000;color:#fff;position:sticky;top:0;z-index:5}
.top .w{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:58px}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none}
.logo{font:italic 22px Anton,sans-serif;background:#fff;color:#000;padding:0 8px;border-radius:4px;border-left:6px solid var(--red);box-shadow:inset 3px 0 0 var(--yellow)}
.brand small{display:block;font-size:11px;opacity:.75;line-height:1.2}.brand b{font-size:14px;letter-spacing:.5px}
.top .cta{background:var(--red);color:#fff;text-decoration:none;font-weight:800;font-size:13px;padding:9px 14px;border-radius:99px;white-space:nowrap}
.w{max-width:760px;margin:0 auto;padding:0 16px}
.crumb{font-size:13px;color:var(--muted);margin:18px 0 6px}.crumb a{text-decoration:none;border-bottom:1px solid var(--line)}
h1{font:italic 34px/1.08 Anton,sans-serif;text-transform:uppercase;margin:6px 0 12px;letter-spacing:.3px}
h2{font:italic 24px/1.15 Anton,sans-serif;text-transform:uppercase;margin:34px 0 10px}
.lead{font-size:17px;margin:0 0 18px}
.answer{background:#000;color:#fff;border-radius:16px;padding:20px;display:grid;grid-template-columns:auto 1fr;gap:6px 18px;align-items:center}
.answer .k{font:italic 64px/1 Anton,sans-serif;color:var(--yellow)}.answer .k small{font-size:22px;color:#fff;margin-left:4px}
.answer .s{font-weight:600}.answer .s span{display:block;font-weight:500;opacity:.75;font-size:14px}
.macros{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.macros span{background:#1d1d1d;border:1px solid #333;border-radius:99px;padding:5px 12px;font-size:14px}
.macros b{color:var(--yellow)}
.walk{grid-column:1/-1;font-size:14px;opacity:.85;margin-top:4px}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;font-size:15px}
td{padding:11px 14px;border-bottom:1px solid var(--line)}td:last-child{text-align:right;font-weight:700;white-space:nowrap}
tr:last-child td{border-bottom:0}
.card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 18px}
ul.tips{padding:0;margin:0;list-style:none;display:grid;gap:10px}
ul.tips li{background:#fff;border:1px solid var(--line);border-left:5px solid var(--red);border-radius:10px;padding:12px 14px}
.swap{display:flex;gap:14px;align-items:center}.swap .n{font:italic 30px Anton,sans-serif;color:var(--red);white-space:nowrap}
details{background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin-bottom:8px}
summary{font-weight:700;cursor:pointer}details p{margin:8px 0 2px}
.box{background:var(--red);color:#fff;border-radius:18px;padding:22px 20px;margin:36px 0 10px}
.box h2{margin:0 0 6px;color:#fff}.box p{margin:0 0 14px}
.btn{display:block;text-align:center;text-decoration:none;font-weight:800;border-radius:99px;padding:14px 16px;margin-top:10px}
.btn.y{background:var(--yellow);color:#000}.btn.w2{background:#fff;color:#000}.btn.o{border:2px solid #fff;color:#fff}
.price{font-size:14px;font-weight:700;margin:12px 0 0;opacity:.95}
.rel{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px}
.rel a{background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 12px;text-decoration:none;font-size:14px;font-weight:600}
.rel a span{display:block;color:var(--red);font-weight:800}
.fine{font-size:12.5px;color:var(--muted);margin:22px 0 40px}
footer{background:#000;color:#bbb;font-size:13px;padding:22px 0 40px;text-align:center}footer a{color:#fff}
.search{width:100%;font:inherit;padding:14px 16px;border:2px solid var(--ink);border-radius:12px;margin:6px 0 18px}
.cat h2{margin-top:26px}
.list{display:grid;gap:6px}
.list a{display:flex;justify-content:space-between;gap:12px;background:#fff;border:1px solid var(--line);border-radius:10px;padding:11px 14px;text-decoration:none}
.list a b{white-space:nowrap;color:var(--red)}.list a small{color:var(--muted);display:block;font-size:12.5px}
@media (min-width:700px){h1{font-size:44px}.answer .k{font-size:80px}}
"""


def head(title, desc, path, extra=""):
    robots = "" if PUBLISH else '<meta name="robots" content="noindex">'
    return f"""<!doctype html><html lang="ms"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">{robots}
<link rel="canonical" href="{BASE}{path}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{BASE}img/share.jpg"><meta name="theme-color" content="#000">{FONTS}<style>{CSS}</style>{extra}</head><body>
<header class="top"><div class="w"><a class="brand" href="{BASE}"><span class="logo">WDT</span><span><b>ARAMI</b><small>Coach Kimi &amp; Coach Zara</small></span></a>
<a class="cta" href="{BASE}kuiz/?src=kalori">Kuiz 2 minit</a></div></header>"""


FOOT = f"""<footer><div class="w">#WEDOTRANSFORMATIONS · <a href="{BASE}">Coach Kimi &amp; Coach Zara</a> · <a href="{BASE}kalori/">Semua makanan</a></div></footer></body></html>"""


def cta(name):
    return f"""<div class="box"><h2>Nak turun berat tanpa tinggal {E(name.split('(')[0].strip().lower())}?</h2>
<p>Bukan makanan yang salah, tapi rutin. Jawab kuiz 2 minit untuk tahu apa yang paling menghalang result anda, atau kira kalori harian anda dan ambil meal plan percuma.</p>
<a class="btn y" href="{BASE}kuiz/?src=kalori">Jawab kuiz percuma →</a>
<a class="btn w2" href="{BASE}?src=kalori#kalori">Kira kalori saya + meal plan percuma</a>
<p class="price">Program coaching bermula dari RM259 sebulan, termasuk supplement. Bayar sekali untuk 1 bulan, tiada kontrak.</p></div>"""


def food_page(f, d, cats, by_cat):
    name = f["name"]
    short = name.split("(")[0].strip()
    title = f"Berapa kalori {short}? (~{f['kcal']} kcal) | Kalori makanan Malaysia"
    desc = f"{short}: anggaran {f['kcal']} kcal untuk {f['serving']}, {d['protein_g']} g protein. Pecahan kalori, versi lain, tips makan masa diet dan pilihan lebih ringan."
    walk = round(f["kcal"] / WALK_KCAL_MIN)
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f"Berapa kalori {short}?", "acceptedAnswer": {"@type": "Answer", "text": d["intro"]}}] + [
        {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in d["faq"]]}
    ld = f'<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>'
    rows = lambda items: "".join(f"<tr><td>{E(x.get('part') or x.get('name'))}</td><td>~{x['kcal']} kcal</td></tr>" for x in items)
    rel = [r for r in by_cat[f["cat"]] if r["slug"] != f["slug"]][:6]
    return head(title, desc, f"kalori/{f['slug']}/", ld) + f"""
<main class="w">
<p class="crumb"><a href="../">Kalori makanan</a> › <a href="../#{f['cat']}">{E(cats[f['cat']])}</a></p>
<h1>Berapa kalori {E(short)}?</h1>
<p class="lead">{E(d['intro'])}</p>
<div class="answer"><div class="k">{f['kcal']}<small>kcal</small></div><div class="s">anggaran<span>{E(f['serving'])}</span></div>
<div class="macros"><span>Protein <b>{d['protein_g']} g</b></span><span>Karbo <b>{d['carbs_g']} g</b></span><span>Lemak <b>{d['fat_g']} g</b></span></div>
<div class="walk">Sama dengan lebih kurang <b>{walk} minit</b> jalan laju (anggaran untuk orang 65 kg).</div></div>
<h2>Dari mana datang kalorinya?</h2><table>{rows(d['breakdown'])}</table>
<h2>Versi lain</h2><table>{rows(d['variants'])}</table>
<h2>Boleh makan masa nak turun berat?</h2><div class="card"><p style="margin:0">{E(d['diet'])}</p></div>
<h2>3 tips makan lebih bijak</h2><ul class="tips">{''.join(f'<li>{E(t)}</li>' for t in d['tips'])}</ul>
<h2>Pilihan lebih bijak</h2><div class="card swap"><div class="n">~{d['swap']['kcal']}</div><div><b>{E(d['swap']['name'])}</b><br>{E(d['swap']['why'])}</div></div>
{cta(short)}
<h2>Soalan lazim</h2>{''.join(f'<details><summary>{E(q["q"])}</summary><p>{E(q["a"])}</p></details>' for q in d['faq'])}
<h2>Makanan lain dalam {E(cats[f['cat']].lower())}</h2>
<div class="rel">{''.join(f'<a href="../{r["slug"]}/">{E(r["name"].split("(")[0].strip())}<span>~{r["kcal"]} kcal</span></a>' for r in rel)}</div>
<p class="fine">Semua nombor ialah anggaran untuk hidangan biasa di Malaysia. Kalori sebenar berbeza ikut resipi, saiz hidangan dan cara masak. Laman ini panduan am, bukan nasihat perubatan. Ada masalah kesihatan? Jumpa doktor dulu.</p>
</main>""" + FOOT


def index_page(foods, cats, by_cat):
    title = "Kalori makanan Malaysia: nasi lemak, roti canai, teh tarik & 100+ lagi"
    desc = "Senarai kalori makanan Malaysia yang popular: sarapan, nasi, mee, mamak, minuman, kuih, fast food dan buah. Anggaran kcal, protein dan tips makan masa diet."
    secs = "".join(f"""<section class="cat" id="{c}"><h2>{E(label)}</h2><div class="list">{''.join(
        f'<a href="{f["slug"]}/" data-n="{E(f["name"].lower())}"><span>{E(f["name"].split("(")[0].strip())}<small>{E(f["serving"])}</small></span><b>~{f["kcal"]} kcal</b></a>'
        for f in by_cat[c])}</div></section>""" for c, label in cats.items() if by_cat.get(c))
    js = """<script>document.getElementById('q').addEventListener('input',e=>{const v=e.target.value.toLowerCase().trim();
document.querySelectorAll('.list a').forEach(a=>a.style.display=!v||a.dataset.n.includes(v)?'':'none');
document.querySelectorAll('.cat').forEach(s=>s.style.display=[...s.querySelectorAll('.list a')].some(a=>a.style.display!=='none')?'':'none')});</script>"""
    return head(title, desc, "kalori/") + f"""<main class="w">
<p class="crumb"><a href="../">Coach Kimi &amp; Coach Zara</a> › Kalori makanan</p>
<h1>Kalori makanan Malaysia</h1>
<p class="lead">Berapa kalori nasi lemak, roti canai atau teh tarik? Cari makanan anda. Setiap satu ada anggaran kalori, protein, versi lain dan tips makan masa nak turun berat.</p>
<input class="search" id="q" type="search" placeholder="Cari makanan, cth. nasi lemak" aria-label="Cari makanan">
{secs}
{cta('makanan kegemaran anda')}
<p class="fine">Semua nombor ialah anggaran untuk hidangan biasa di Malaysia. Kalori sebenar berbeza ikut resipi, saiz hidangan dan cara masak.</p>
</main>{js}""" + FOOT


def main():
    src = json.loads((SEO / "foods.json").read_text())
    cats = src["categories"]
    foods = [f for f in src["foods"] if (SEO / "data" / f"{f['slug']}.json").exists()]
    by_cat = {}
    for f in foods:
        by_cat.setdefault(f["cat"], []).append(f)
    for f in foods:
        d = json.loads((SEO / "data" / f"{f['slug']}.json").read_text())
        p = OUT / f["slug"]
        p.mkdir(parents=True, exist_ok=True)
        (p / "index.html").write_text(food_page(f, d, cats, by_cat))
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(index_page(foods, cats, by_cat))
    if PUBLISH:
        urls = ["", "kuiz/", "kalori/"] + [f"kalori/{f['slug']}/" for f in foods]
        (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                          + "".join(f"<url><loc>{BASE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    print(f"built {len(foods)} food pages (publish={PUBLISH})")


if __name__ == "__main__":
    main()
