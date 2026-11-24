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


# ---------- English versions (data from generate7.py en2: seo/en/compare|eat-out|over-50, same file names as BM) ----------

def load_en(kind):
    return load(f"en/{kind}")


def en_map5():
    """Malay path -> English path for round 2 pages that have an English version."""
    m = {}
    for kind, sec, key in (("compare", "banding", "id"), ("eat-out", "makan-luar", "slug"), ("over-50", "umur-50", "slug")):
        pages = load_en(kind)
        for d in pages:
            m[f"{sec}/{d[key]}"] = f"en/{kind}/{d['id'] if kind == 'compare' else d['slug_en']}"
        if pages:
            m[sec] = f"en/{kind}"
    return m


def short_en(slug):
    p = SEO / "data-en" / f"{slug}.json"
    return json.loads(p.read_text())["name_en"].split("(")[0].strip() if p.exists() else short(slug)


def serving_en(slug):
    p = SEO / "data-en" / f"{slug}.json"
    return json.loads(p.read_text())["serving_en"] if p.exists() else FOODS[slug]["serving"]


def cta_en(src, h, p):
    return f"""<div class="box"><h2>{E(h)}</h2><p>{E(p)}</p>
<a class="btn y" href="{BASE}kuiz/?src={src}&amp;lang=en">Take the 2-minute quiz →</a>
<a class="btn w2" href="{BASE}?src={src}&amp;lang=en#kalori">Work out my calories + free meal plan</a>
<p class="price">{build2.PRICE_EN}</p></div>"""


def compare_en():
    pages, urls = load_en("compare"), []
    win = {d["id"]: d["winner"] for d in load("banding")}
    for d in pages:
        a, b = d["id"].split("-vs-")
        w = win.get(d["id"], "seri")
        da, db = (json.loads((SEO / "data" / f"{x}.json").read_text()) for x in (a, b))
        na, nb = short_en(a), short_en(b)
        card = lambda s, n, dd: f"""<div class="f{' win' if w == s else ''}">{'<span class="tag">Better pick</span>' if w == s else ''}<b>{E(n)}</b><div class="k">{FOODS[s]['kcal']}</div><small>kcal · {E(serving_en(s))}</small><small>protein {dd['protein_g']} g · fat {dd['fat_g']} g</small></div>"""
        path = f"en/compare/{d['id']}/"
        others = [x for x in pages if x is not d and (a in x["id"] or b in x["id"])][:4] or [x for x in pages if x is not d][:4]
        build2.write(path.rstrip("/"), build2.head(f"{na} vs {nb}: which is better for weight loss?", d["verdict"][:155], path, "en", faq_ld(d) + CSS5,
                                                   {"ms": f"banding/{d['id']}/", "en": path}) + f"""<main class="w">
<p class="crumb"><a href="../">Food comparisons</a></p><h1>{E(na)} vs {E(nb)}</h1><p class="lead">{E(d['verdict'])}</p>
<p class="lang">Read in Malay: <a href="{BASE}banding/{d['id']}/">versi Bahasa Melayu</a></p>
<div class="vs">{card(a, na, da)}<div class="x">VS</div>{card(b, nb, db)}</div>
<h2>Why?</h2><ul class="tips">{''.join(f'<li>{E(x)}</li>' for x in d['why'])}</ul>
<h2>When {E(na)} is still fine</h2><div class="card">{E(d['when_a'])}</div>
<h2>When {E(nb)} is still fine</h2><div class="card">{E(d['when_b'])}</div>
<h2>A smarter way</h2><div class="card">{E(d['tip'])}</div>
{cta_en('compare', "It's not the food, it's the routine", 'Take the 2-minute quiz to find what is really holding your results back.')}
<h2>FAQ</h2>{faqs(d)}
<h2>More comparisons</h2><div class="rel">{''.join(f'<a href="{BASE}en/compare/{x["id"]}/">{E(short_en(x["id"].split("-vs-")[0]))} vs {E(short_en(x["id"].split("-vs-")[1]))}</a>' for x in others)}</div>
<div class="rel" style="margin-top:8px"><a href="{BASE}calories/{a}/">{E(na)} calories</a><a href="{BASE}calories/{b}/">{E(nb)} calories</a></div>
<p class="fine">All numbers are estimates for a normal Malaysian serving. General guide only, not medical advice.</p></main>""" + build2.foot("en"))
        urls.append(path)
    if pages:
        build2.write("en/compare", build2.head("Malaysian food comparisons: which is better for weight loss?",
            "Nasi lemak vs roti canai, teh tarik vs kopi O, fried chicken vs satay and more. Compare calories, protein and which is better for weight loss.",
            "en/compare/", "en", CSS5, {"ms": "banding/", "en": "en/compare/"}) + f"""<main class="w">
<p class="crumb"><a href="{BASE}?lang=en">Coach Kimi &amp; Coach Zara</a> › Food comparisons</p><h1>Food comparisons</h1>
<p class="lead">Two choices in front of you, which one is better when you want to lose weight? Tap to see calories, protein and the coach's answer.</p>
<div class="list">{''.join(f'<a href="{x["id"]}/"><span>{E(short_en(x["id"].split("-vs-")[0]))} vs {E(short_en(x["id"].split("-vs-")[1]))}</span><b>→</b></a>' for x in pages)}</div>
<p class="lang">Read in Malay: <a href="{BASE}banding/">Banding makanan</a></p></main>""" + build2.foot("en"))
        urls.append("en/compare/")
    return urls


def order_en():
    pages, urls = load_en("eat-out"), []
    rows = lambda xs, cls: f'<div class="pick2 {cls}">' + "".join(f'<div><span class="n">~{x["kcal"]} kcal</span><b>{E(x["name"])}</b><br><small>{E(x["why"])}</small></div>' for x in xs) + "</div>"
    for d in pages:
        path = f"en/eat-out/{d['slug_en']}/"
        build2.write(path.rstrip("/"), build2.head(d["title"], d["intro"][:155], path, "en", faq_ld(d) + CSS5,
                                                   {"ms": f"makan-luar/{d['slug']}/", "en": path}) + f"""<main class="w">
<p class="crumb"><a href="../">Eating out</a></p><h1>{E(d['title'])}</h1><p class="lead">{E(d['intro'])}</p>
<p class="lang">Read in Malay: <a href="{BASE}makan-luar/{d['slug']}/">versi Bahasa Melayu</a></p>
<h2>Best picks</h2>{rows(d['best'], '')}
<h2>Be careful with these</h2>{rows(d['careful'], 'bad')}
<h2>How to order</h2><ul class="tips">{''.join(f'<li>{E(x)}</li>' for x in d['hacks'])}</ul>
<h2>Drinks</h2><div class="card">{E(d['drink'])}</div>
{cta_en('eat-out', 'Eat out a lot?', 'Your coach can build a plan around the places you usually eat. Start with the 2-minute quiz.')}
<h2>FAQ</h2>{faqs(d)}
<h2>Other places</h2><div class="rel">{''.join([f'<a href="{BASE}en/eat-out/{x["slug_en"]}/">{E(x["title"])}</a>' for x in pages if x is not d][:6])}</div>
<p class="fine">Calories are estimates and change with the shop and portion size. General guide only.</p></main>""" + build2.foot("en"))
        urls.append(path)
    if pages:
        build2.write("en/eat-out", build2.head("Eating out but want to lose weight: what to order",
            "What to order at the mamak, kopitiam, nasi campur, McDonald's, KFC, 7-Eleven, pasar malam, kenduri and more when you want to lose weight.",
            "en/eat-out/", "en", CSS5, {"ms": "makan-luar/", "en": "en/eat-out/"}) + f"""<main class="w">
<p class="crumb"><a href="{BASE}?lang=en">Coach Kimi &amp; Coach Zara</a> › Eating out</p><h1>Eat out, still lose weight</h1>
<p class="lead">No need to stop eating out. Pick your place and see what's best to order.</p>
<div class="list">{''.join(f'<a href="{x["slug_en"]}/"><span>{E(x["title"])}</span><b>→</b></a>' for x in pages)}</div>
<p class="lang">Read in Malay: <a href="{BASE}makan-luar/">Makan luar</a></p></main>""" + build2.foot("en"))
        urls.append("en/eat-out/")
    return urls


def senior_en():
    pages, urls = load_en("over-50"), []
    for d in pages:
        path = f"en/over-50/{d['slug_en']}/"
        msg = urllib.parse.quote(f"Hi Coach, I read your guide \"{d['title']}\". I'd like to ask about weight loss and my health.")
        build2.write(path.rstrip("/"), build2.head(d["title"], d["intro"][:155], path, "en", faq_ld(d) + CSS5,
                                                   {"ms": f"umur-50/{d['slug']}/", "en": path}) + f"""<main class="w">
<p class="crumb"><a href="../">Age 50 and above</a></p><h1>{E(d['title'])}</h1><p class="lead">{E(d['intro'])}</p>
<p class="lang">Read in Malay: <a href="{BASE}umur-50/{d['slug']}/">versi Bahasa Melayu</a></p>
<div class="doc"><b>See your doctor first if:</b> {E(d['doctor'])}</div>
{''.join(f'<h2>{E(s["h"])}</h2><p>{E(s["p"])}</p>' for s in d['sections'])}
<h2>Try this week</h2><ul class="tips">{''.join(f'<li>{E(a)}</li>' for a in d['action'])}</ul>
<div class="box"><h2>Want a coach who understands your situation?</h2><p>Your coach builds the plan around your age, medicine and joints, not an extreme diet. Got a question? Just ask.</p>
<a class="btn y" href="https://wa.me/{KIMI}?text={msg}" target="_blank" rel="noopener">WhatsApp a coach →</a>
<a class="btn w2" href="{BASE}kuiz/?src=over-50&amp;lang=en">Take the 2-minute quiz first</a><p class="price">{build2.PRICE_EN}</p></div>
<h2>FAQ</h2>{faqs(d)}
<h2>Read next</h2><div class="rel">{''.join([f'<a href="{BASE}en/over-50/{x["slug_en"]}/">{E(x["title"])}</a>' for x in pages if x is not d][:6])}</div>
<p class="fine">General guide only, not medical advice. Never change or stop your medicine without talking to your doctor.</p></main>""" + build2.foot("en"))
        urls.append(path)
    if pages:
        build2.write("en/over-50", build2.head("Age 50 and above: weight loss, blood sugar, blood pressure and knees",
            "Guides for age 50+: safe weight loss, blood sugar, high blood pressure, cholesterol, knee pain and chair exercises.",
            "en/over-50/", "en", CSS5, {"ms": "umur-50/", "en": "en/over-50/"}) + f"""<main class="w">
<p class="crumb"><a href="{BASE}?lang=en">Coach Kimi &amp; Coach Zara</a> › Age 50 and above</p><h1>Age 50 and above</h1>
<p class="lead">Your body changes after 50, but losing weight and staying healthy is still possible, in a way that is safe for your joints and follows your doctor's advice.</p>
<div class="list">{''.join(f'<a href="{x["slug_en"]}/"><span>{E(x["title"])}</span><b>→</b></a>' for x in pages)}</div>
<p class="lang">Read in Malay: <a href="{BASE}umur-50/">Umur 50 ke atas</a></p></main>""" + build2.foot("en"))
        urls.append("en/over-50/")
    return urls


def main():
    urls = compare_pages() + order_pages() + senior_pages() + compare_en() + order_en() + senior_en()
    sm = ROOT / "sitemap.xml"
    if build2.PUBLISH2 and sm.exists() and urls:
        s = sm.read_text()
        add = "".join(f"<url><loc>{BASE}{u}</loc></url>\n" for u in urls if f"{BASE}{u}</loc>" not in s)
        sm.write_text(s.replace("</urlset>", add + "</urlset>"))
    print(f"build5: {len(urls)} pages")


if __name__ == "__main__":
    main()
