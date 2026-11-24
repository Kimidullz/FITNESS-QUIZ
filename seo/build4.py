"""English guide pages (no API; run after build.py, build2.py, build3.py). Data from seo/generate6.py en:

  en/women/<slug_en>/      English versions of wanita/<slug>/
  en/exercises/<slug_en>/  English versions of senaman/<slug>/
  en/ramadan/              English version of ramadan/

Each English page links to its Malay twin (hreflang both ways; polish.py adds the Malay side).
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
ZARA = build2.COACH["f"][1]
FINE = "General guidance only, not medical advice. If you have a health condition, are pregnant or take medicine, talk to your doctor first."


def load(kind):
    d0 = SEO / "en" / kind
    return [json.loads(p.read_text()) for p in sorted(d0.glob("*.json"))] if d0.exists() else []


def en_map():
    """Malay path -> English path, for every English page that exists."""
    m = {f"wanita/{d['slug']}": f"en/women/{d['slug_en']}" for d in load("women")}
    m.update({f"senaman/{d['slug']}": f"en/exercises/{d['slug_en']}" for d in load("exercises")})
    if (SEO / "en" / "ramadan.json").exists():
        m["ramadan"] = "en/ramadan"
    return m


def en_title(path, women, ex):
    for d in women + ex:
        if path.endswith("/" + d["slug_en"]):
            return d["title"]
    return {"en/ramadan": "Ramadan guide", "semak": "Check what you ate yesterday (BM)", "workout": "7-day home workout (BM)"}.get(path, path)


def rel_en(ms_paths, m, women, ex):
    out = []
    for p in ms_paths:
        if p in m:
            out.append(f'<a href="{BASE}{m[p]}/">{E(en_title(m[p], women, ex))}</a>')
        elif p.startswith("kalori/") and (SEO / "data-en" / f"{p[7:]}.json").exists():
            n = json.loads((SEO / "data-en" / f"{p[7:]}.json").read_text())["name_en"].split("(")[0].strip()
            out.append(f'<a href="{BASE}calories/{p[7:]}/">{E(n)} calories</a>')
    return "".join(out)


def faq_ld(d):
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in d["faq"]]}, ensure_ascii=False) + "</script>"


def zara_box(topic):
    msg = urllib.parse.quote(f"Hi Coach Zara, I read your guide \"{topic}\". I'd like to ask about losing weight.")
    return f"""<div class="box"><h2>Tired of trying alone?</h2><p>Coach Zara helps working women lose fat without crash diets, around your work schedule and everyday food.</p>
<a class="btn y" href="https://wa.me/{ZARA}?text={msg}" target="_blank" rel="noopener">WhatsApp Coach Zara →</a>
<a class="btn w2" href="{BASE}kuiz/?src=women&amp;lang=en">Take the 2-minute quiz first</a>
<p class="price">{build2.PRICE_EN}</p></div>"""


def main():
    women, ex, m = load("women"), load("exercises"), en_map()
    urls = []
    rel_src = json.loads((SEO / "related.json").read_text()) if (SEO / "related.json").exists() else {}
    faqs = lambda d: "".join(f'<details><summary>{E(q["q"])}</summary><p>{E(q["a"])}</p></details>' for q in d["faq"])
    for d in women:
        path = f"en/women/{d['slug_en']}/"
        r = rel_src.get(f"wanita/{d['slug']}", {})
        rel = rel_en(r.get("same", []) + r.get("other", []), m, women, ex) or "".join(
            [f'<a href="{BASE}en/women/{x["slug_en"]}/">{E(x["title"])}</a>' for x in women if x is not d][:6])
        build2.write(path.rstrip("/"), build2.head(d["title"] if len(d["title"]) > 50 else f"{d['title']} | Coach Zara", d["intro"][:155], path, "en", faq_ld(d),
                                                   {"ms": f"wanita/{d['slug']}/", "en": path}) + f"""<main class="w">
<p class="crumb"><a href="../">Fat loss for working women</a></p><h1>{E(d['title'])}</h1><p class="lead">{E(d['intro'])}</p>
<p class="lang">Read in Malay: <a href="{BASE}wanita/{d['slug']}/">versi Bahasa Melayu</a></p>
{''.join(f'<h2>{E(s["h"])}</h2><p>{E(s["p"])}</p>' for s in d['sections'])}
<h2>Try this week</h2><ul class="tips">{''.join(f'<li>{E(a)}</li>' for a in d['action'])}</ul>
<div class="card"><b>Myth:</b> {E(d['myth'])}</div>
{zara_box(d['title'])}
<h2>FAQ</h2>{faqs(d)}
<h2>Read next</h2><div class="rel">{rel}</div>
<p class="fine">{FINE}</p></main>""" + build2.foot("en"))
        urls.append(path)
    if women:
        build2.write("en/women", build2.head("Fat loss for working women | Coach Zara",
            "Fat loss guides for working women in Malaysia: packed lunch, office snacks, afternoon hunger, stress, no time to exercise and more.",
            "en/women/", "en", alt={"ms": "wanita/", "en": "en/women/"}) + f"""<main class="w">
<p class="crumb"><a href="{BASE}?lang=en">Coach Kimi &amp; Coach Zara</a> › Working women</p><h1>Fat loss for working women</h1>
<p class="lead">Busy at work, eating whenever you can, tried everything but the scale won't move? Start here.</p>
<div class="list">{''.join(f'<a href="{x["slug_en"]}/"><span>{E(x["title"])}</span><b>→</b></a>' for x in women)}</div>
{zara_box("Fat loss for working women")}
<p class="lang">Read in Malay: <a href="{BASE}wanita/">Turun lemak untuk wanita bekerja</a></p></main>""" + build2.foot("en"))
        urls.append("en/women/")
    for d in ex:
        path = f"en/exercises/{d['slug_en']}/"
        src = json.loads((SEO / "exercises" / f"{d['slug']}.json").read_text())
        vid = f'<div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/{src["video"]}" title="{E(d["title"])}" loading="lazy" allowfullscreen></iframe></div>' if src.get("video") else ""
        r = rel_src.get(f"senaman/{d['slug']}", {})
        rel = rel_en(r.get("same", []) + r.get("other", []), m, women, ex) or "".join(
            [f'<a href="{BASE}en/exercises/{x["slug_en"]}/">{E(x["title"])}</a>' for x in ex if x is not d][:6])
        build2.write(path.rstrip("/"), build2.head(d["title"] if len(d["title"]) > 50 else f"{d['title']} | Exercise guide", d["intro"][:155], path, "en", faq_ld(d),
                                                   {"ms": f"senaman/{d['slug']}/", "en": path}) + f"""<main class="w">
<p class="crumb"><a href="../">Home workouts</a></p><h1>{E(d['title'])}</h1><p class="lead">{E(d['intro'])}</p>
<p class="lang">Read in Malay: <a href="{BASE}senaman/{d['slug']}/">versi Bahasa Melayu</a></p>{vid}
<div class="card"><b>Works:</b> {E(d['muscles'])}<br><b>For beginners:</b> {E(d['dose'])}</div>
<h2>How to do it</h2><ol class="steps">{''.join(f'<li>{E(s)}</li>' for s in d['steps'])}</ol>
<h2>Common mistakes</h2><ul class="tips">{''.join(f'<li>{E(s)}</li>' for s in d['mistakes'])}</ul>
<h2>Easier version</h2><div class="card">{E(d['easier'])}</div>
<h2>Harder version</h2><div class="card">{E(d['harder'])}</div>
<div class="box"><h2>Want a plan made for you?</h2><p>Take the 2-minute quiz to find what's holding your results back. Your coach then builds a plan around your schedule.</p>
<a class="btn y" href="{BASE}kuiz/?src=exercises&amp;lang=en">Take the free quiz →</a><a class="btn w2" href="{BASE}?src=exercises&amp;lang=en#kalori">Work out my calories + free meal plan</a><p class="price">{build2.PRICE_EN}</p></div>
<h2>FAQ</h2>{faqs(d)}
<h2>Read next</h2><div class="rel">{rel}</div>
<p class="fine">{E(d['safety'])} {FINE}</p></main>""" + build2.foot("en"))
        urls.append(path)
    if ex:
        build2.write("en/exercises", build2.head("Home workouts: exercise guides for beginners",
            "No-equipment home exercise guides: squats, push-ups, plank, core, arms, legs and more. How to do them, common mistakes and videos.",
            "en/exercises/", "en", alt={"ms": "senaman/", "en": "en/exercises/"}) + f"""<main class="w">
<p class="crumb"><a href="{BASE}?lang=en">Coach Kimi &amp; Coach Zara</a> › Exercises</p><h1>Home workouts</h1>
<p class="lead">Short guides for beginners, no equipment needed.</p>
<div class="list">{''.join(f'<a href="{x["slug_en"]}/"><span>{E(x["title"])}</span><b>→</b></a>' for x in ex)}</div>
<p class="lang">Read in Malay: <a href="{BASE}senaman/">Senaman di rumah</a></p></main>""" + build2.foot("en"))
        urls.append("en/exercises/")
    rp = SEO / "en" / "ramadan.json"
    if rp.exists():
        d = json.loads(rp.read_text())
        menus = lambda xs: "".join(f'<div class="menu"><span class="n">~{x["kcal"]} kcal · {x["protein_g"]} g protein</span><b>{E(x["name"])}</b>{E(x["items"])}<br><small>{E(x["why"])}</small></div>' for x in xs)
        rows = lambda xs: "".join(f"<tr><td>{E(x['name'])} <small style='color:var(--muted)'>({E(x['serving'])})</small></td><td>~{x['kcal']} kcal</td></tr>" for x in xs)
        build2.write("en/ramadan", build2.head(d["title"] + " | Coach Kimi & Coach Zara", d["intro"][:155], "en/ramadan/", "en", faq_ld(d),
                                               {"ms": "ramadan/", "en": "en/ramadan/"}) + f"""<main class="w">
<p class="crumb"><a href="{BASE}?lang=en">Coach Kimi &amp; Coach Zara</a> › Ramadan</p><h1>{E(d['title'])}</h1><p class="lead">{E(d['intro'])}</p>
<p class="lang">Read in Malay: <a href="{BASE}ramadan/">Panduan Ramadan</a></p>
<h2>Why many people gain weight while fasting</h2><ul class="tips">{''.join(f'<li>{E(x)}</li>' for x in d['why_gain'])}</ul>
<h2>5 sahur menus</h2>{menus(d['sahur'])}
<h2>5 berbuka menus</h2>{menus(d['berbuka'])}
<h2>Ramadan bazaar calories</h2><table>{rows(d['bazar'])}</table>
<h2>Raya cookie calories</h2><table>{rows(d['kuih_raya'])}</table>
<h2>Exercising while fasting</h2><div class="card">{E(d['exercise'])}</div>
<h2>Tips to fast without gaining weight</h2><ul class="tips">{''.join(f'<li>{E(x)}</li>' for x in d['tips'])}</ul>
<h2>Raya open houses without the guilt</h2><ul class="tips">{''.join(f'<li>{E(x)}</li>' for x in d['raya'])}</ul>
<div class="box"><h2>Want a coach with you through Ramadan?</h2><p>Take the 2-minute quiz to find what's holding your results back.</p>
<a class="btn y" href="{BASE}kuiz/?src=ramadan&amp;lang=en">Take the free quiz →</a><p class="price">{build2.PRICE_EN}</p></div>
<h2>FAQ</h2>{faqs(d)}
<p class="fine">All calories are estimates. If you have diabetes or high blood pressure, or are pregnant or breastfeeding, talk to your doctor before changing how you fast or eat. General guidance only.</p>
</main>""" + build2.foot("en"))
        urls.append("en/ramadan/")
    sm = ROOT / "sitemap.xml"
    if build2.PUBLISH2 and sm.exists() and urls:
        s = sm.read_text()
        add = "".join(f"<url><loc>{BASE}{u}</loc></url>\n" for u in urls if f"{BASE}{u}</loc>" not in s)
        sm.write_text(s.replace("</urlset>", add + "</urlset>"))
    print(f"build4: {len(urls)} English pages")


if __name__ == "__main__":
    main()
