"""Last build step (no API; run after build.py, build2.py, build3.py, build4.py). Safe to run twice.

Adds to every generated guide page (kalori, calories, semak, workout, senaman, wanita, ramadan, en/...):
  - site icon + apple-touch-icon
  - a section menu under the header, in the page's language
  - BM<->EN hreflang both ways + a "Read in English" link on Malay pages that have a twin
  - a small "who writes this" coaches card above the first call-to-action box
  - the program + RM259 strip right before the footer
  - food search: extra search words (seo/aliases.json), spaces ignored, "not found" message
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build2  # noqa: E402
import build4  # noqa: E402
import build5  # noqa: E402
from build import BASE  # noqa: E402

ROOT = build2.ROOT
SEO = build2.SEO
MARK = "<!--polish-->"
ICON_SVG = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%230B0B0B'/%3E"
            "%3Cpath d='M38 64 64 30v14L52 64z' fill='%23E30613'/%3E%3Cpath d='M50 64 64 46v10l-6 8z' fill='%23FFD200'/%3E%3Ctext x='8' y='40' "
            "font-family='Arial Black,Arial' font-weight='900' font-style='italic' font-size='20' fill='%23fff'%3EWDT%3C/text%3E%3C/svg%3E")
ICONS = f'<link rel="icon" href="{ICON_SVG}"><link rel="apple-touch-icon" href="{BASE}img/icon-180.png">'
SECTIONS = ["kalori", "calories", "semak", "workout", "senaman", "wanita", "ramadan", "en", "banding", "makan-luar", "umur-50"]

CSS = """<style>
.snav{background:#111;border-bottom:3px solid var(--yellow)}
.snav{position:relative}.snav:after{content:'';position:absolute;right:0;top:0;bottom:0;width:28px;background:linear-gradient(90deg,transparent,#111);pointer-events:none}
.snav .w{display:flex;gap:6px;overflow-x:auto;padding-top:8px;padding-bottom:8px;scrollbar-width:none}
.snav a{flex:none;color:#fff;text-decoration:none;font:700 13px Montserrat,sans-serif;padding:7px 12px;border-radius:99px;border:1px solid #333}
.snav a.on{background:var(--yellow);color:#000;border-color:var(--yellow)}
.coaches{display:flex;gap:12px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin:30px 0 -16px}
.coaches img{width:46px;height:46px;border-radius:50%;object-fit:cover;object-position:top;flex:none}
.coaches img+img{margin-left:-22px;border:2px solid #fff}
.coaches p{margin:0;font-size:14px;line-height:1.45}.coaches b{display:block}
.pstrip{background:#000;color:#fff;margin-top:28px}
.pstrip .w{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;padding-top:16px;padding-bottom:16px}
.pstrip p{margin:0;font-size:14px;font-weight:600;flex:1 1 260px}.pstrip b{color:var(--yellow)}
.pstrip a{background:var(--red);color:#fff;text-decoration:none;font-weight:800;font-size:14px;padding:10px 16px;border-radius:99px;white-space:nowrap}
.nores{display:none;background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px;font-size:15px}
:focus-visible{outline:3px solid var(--yellow);outline-offset:2px;box-shadow:0 0 0 6px #000}
.fine{font-size:14px}
/* dark WDT look, same family as the home page (24 Nov round 2) */
:root{--ink:#f2f2f2;--muted:#a9a9a9;--line:#2b2b2b;--bg:#0b0b0b;--card:#161616}
body{background:var(--bg);color:var(--ink)}
h1{color:#fff;font-size:38px}h1:after{content:"";display:block;width:72px;height:7px;margin-top:12px;background:linear-gradient(90deg,var(--red) 0 55%,var(--yellow) 55% 100%);transform:skewX(-24deg)}
h2{color:#fff}h2:before{content:"";display:inline-block;width:8px;height:.8em;background:var(--yellow);margin-right:10px;transform:skewX(-18deg)}
.box h2:before,.answer h2:before{display:none}
.lead{color:#ddd}.crumb,.crumb a{color:var(--muted)}
.card,table,details,ul.tips li,.rel a,.list a,.menu,.day,.pick .it,.coaches,.vid,.nores{background:var(--card)!important;color:var(--ink);border-color:var(--line)!important}
ul.tips li{border-left:5px solid var(--red)!important}
.rel a:hover,.list a:hover{border-color:var(--yellow)!important}
.answer{border:1px solid var(--line)}
.search{background:var(--card);color:#fff;border-color:#444}.search::placeholder{color:#888}
.chips button,.seg button{background:var(--card);color:#fff;border-color:#444}
.chips button.on,.seg button.on{background:var(--yellow);color:#000;border-color:var(--yellow)}
.q button{background:#262626;color:#fff}.q button.add{background:var(--red)}
.coaches{border-left:5px solid var(--yellow)!important}
.lang a,.rel a span,.list a b,.swap .n,.menu .n{color:var(--yellow)}
.btn.w2{background:#fff;color:#000}
.day .chk,label.l{color:#fff}
.fine{color:var(--muted)}
footer{border-top:1px solid #222}
@media (min-width:700px){h1{font-size:48px}}
</style>"""


def nav(lang, sec):
    if lang == "en":
        items = [("calories", "calories/", "Food calories"), ("en/women", "en/women/", "Working women"),
                 ("en/compare", "en/compare/", "Food comparisons"), ("en/eat-out", "en/eat-out/", "Eating out"),
                 ("en/exercises", "en/exercises/", "Exercises"), ("en/over-50", "en/over-50/", "Age 50+"), ("en/ramadan", "en/ramadan/", "Ramadan"),
                 ("semak", "semak/", "Food check (BM)"), ("workout", "workout/", "7-day workout (BM)")]
    else:
        items = [("kalori", "kalori/", "Kalori makanan"), ("semak", "semak/", "Semak makan"), ("workout", "workout/", "Workout 7 hari"),
                 ("banding", "banding/", "Banding makanan"), ("makan-luar", "makan-luar/", "Makan luar"),
                 ("senaman", "senaman/", "Senaman"), ("wanita", "wanita/", "Wanita bekerja"), ("umur-50", "umur-50/", "Umur 50+"), ("ramadan", "ramadan/", "Ramadan")]
    lab = "Menu" if lang == "en" else "Menu bahagian"
    return f'<nav class="snav" aria-label="{lab}"><div class="w">' + "".join(
        f'<a href="{BASE}{h}"{" class=on aria-current=page" if k == sec else ""}>{t}</a>' for k, h, t in items) + "</div></nav>" + \
        "<script>(()=>{const a=document.querySelector('.snav a.on');if(a)a.parentNode.scrollLeft=a.offsetLeft-16})()</script>"


def coaches(lang):
    if lang == "en":
        t = "<b>Coach Kimi &amp; Coach Zara · WeDoTransformations</b>Husband-and-wife online coaches in Malaysia. Kimi coaches men, Zara coaches women."
    else:
        t = "<b>Coach Kimi &amp; Coach Zara · WeDoTransformations</b>Pasangan coach online di Malaysia. Kimi bantu lelaki, Zara bantu wanita."
    return f'<div class="coaches"><img src="{BASE}img/kimi.jpg" alt="Coach Kimi" width="46" height="46" loading="lazy"><img src="{BASE}img/zara.jpg" alt="Coach Zara" width="46" height="46" loading="lazy"><p>{t}</p></div>'


def strip(lang):
    if lang == "en":
        return (f'<div class="pstrip"><div class="w"><p>Want a coach to do this with you? <b>Programs from RM259 a month, supplements included.</b> '
                f'One payment, no contract.</p><a href="{BASE}kuiz/?lang=en&amp;src=strip">Take the quiz →</a></div></div>')
    return (f'<div class="pstrip"><div class="w"><p>Nak coach teman sampai berjaya? <b>Program coaching dari RM259 sebulan, termasuk supplement.</b> '
            f'Bayar sekali, tiada kontrak.</p><a href="{BASE}kuiz/?src=strip">Jawab kuiz →</a></div></div>')


SEARCH_JS = """<script>(()=>{const q=document.getElementById('q'),nr=document.getElementById('nores'),n=s=>s.toLowerCase().replace(/[^a-z0-9]/g,'');
q.addEventListener('input',()=>{const v=n(q.value);let any=false;
document.querySelectorAll('.list a').forEach(a=>{const ok=!v||n(a.dataset.n).includes(v)||a.dataset.n.split('|').some(w=>n(w).includes(v));a.style.display=ok?'':'none';if(ok)any=true});
document.querySelectorAll('.cat').forEach(s=>s.style.display=[...s.querySelectorAll('.list a')].some(a=>a.style.display!=='none')?'':'none');
nr.style.display=any?'none':'block'})})();</script>"""


def fix_search(html, lang):
    al = json.loads((SEO / "aliases.json").read_text()) if (SEO / "aliases.json").exists() else {}
    html = re.sub(r'<a href="([a-z0-9-]+)/" data-n="([^"]*)"',
                  lambda m: f'<a href="{m.group(1)}/" data-n="{m.group(2)}{"|" + "|".join(al.get(m.group(1), [])) if al.get(m.group(1)) else ""}"', html)
    html = re.sub(r"<script>document\.getElementById\('q'\)\.addEventListener\('input'.*?</script>", lambda m: SEARCH_JS, html, flags=re.S)
    msg = ("Not found. Try another name, or <a href=\"" + BASE + "semak/\">check a whole day's food</a>." if lang == "en"
           else "Tak jumpa. Cuba nama lain, atau tanya coach di WhatsApp lepas <a href=\"" + BASE + "kuiz/?src=kalori\">jawab kuiz</a>.")
    return html.replace('aria-label="Search food">', f'aria-label="Search food"><p class="nores" id="nores">{msg}</p>', 1).replace(
        'aria-label="Cari makanan">', f'aria-label="Cari makanan"><p class="nores" id="nores">{msg}</p>', 1)


def twin(rel):
    """Malay page path (e.g. 'kalori/nasi-lemak-biasa') -> English twin path, if it exists."""
    if rel.startswith("kalori/") and (ROOT / "calories" / rel[7:] / "index.html").exists():
        return "calories/" + rel[7:]
    if rel == "kalori":
        return "calories"
    m = build4.en_map()
    m.update({"wanita": "en/women", "senaman": "en/exercises"})
    m.update(build5.en_map5())
    t = m.get(rel)
    return t if t and (ROOT / t / "index.html").exists() else None


def polish(p):
    html = p.read_text()
    if MARK in html:
        return False
    rel = str(p.parent.relative_to(ROOT))
    lang = "en" if '<html lang="en"' in html else "ms"
    sec = rel.split("/")[0]
    if sec == "en":
        sec = "/".join(rel.split("/")[:2])
    html = html.replace("</head>", ICONS + CSS + "</head>", 1)
    html = re.sub(r"(</header>)", lambda m: m.group(1) + nav(lang, sec), html, count=1)
    if lang == "ms":
        t = twin(rel)
        if t and 'hreflang="en"' not in html:
            html = html.replace('<meta property="og:title"', f'<link rel="alternate" hreflang="ms" href="{BASE}{rel}/"><link rel="alternate" hreflang="en" href="{BASE}{t}/"><meta property="og:title"', 1)
            html = re.sub(r"(<h1>.*?</h1>)", lambda m: m.group(1) + f'<p class="lang">Read in English: <a href="{BASE}{t}/">English version</a></p>', html, count=1, flags=re.S)
    if '<div class="box">' in html and "Coach Zara bantu wanita bekerja" not in html and "Coach Zara helps working women" not in html:
        html = html.replace('<div class="box">', coaches(lang) + '<div class="box">', 1)
    html = html.replace("<footer>", strip(lang) + "<footer>", 1)
    if p.parent in (ROOT / "kalori", ROOT / "calories"):
        html = fix_search(html, lang)
    html = html.replace("</body>", MARK + "</body>", 1)
    p.write_text(html)
    return True


def main():
    n = 0
    for sec in SECTIONS:
        for p in sorted((ROOT / sec).rglob("index.html")) if (ROOT / sec).exists() else []:
            n += polish(p)
    print(f"polish: {n} pages")


if __name__ == "__main__":
    main()
