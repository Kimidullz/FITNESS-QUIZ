"""20 more working-women guides (27 Nov 2026), Malay + English, from seo/generate8.py. No API.

While PUBLISH7 = False they are HIDDEN: noindex, not in the sitemap, not on the /wanita/ or /en/women/ lists,
and not linked from anywhere except the private review list at wanita/baru/ (also noindex).

To publish after Kimi's OK: move seo/wanita-new/*.json into seo/wanita/ and seo/en/women-new/*.json into
seo/en/women/ (drop the "related" key or keep it, both work), delete wanita/baru/, then run the normal build
(build.py .. build6.py, polish.py). They then join the existing lists, sitemap and hreflang.
"""
import json
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build2  # noqa: E402
import build3  # noqa: E402  (sets build2.PUBLISH2 = True on import)
import build4  # noqa: E402
from build import BASE, E  # noqa: E402

PUBLISH7 = False
SEO, ROOT = build2.SEO, build2.ROOT


def load(d0):
    return [json.loads(p.read_text()) for p in sorted(d0.glob("*.json"))] if d0.exists() else []


def faqs(d):
    return "".join(f'<details><summary>{E(q["q"])}</summary><p>{E(q["a"])}</p></details>' for q in d["faq"])


def main():
    if PUBLISH7:
        print("build7: PUBLISH7 is True; move the JSON into seo/wanita and seo/en/women instead (see top of file)")
        return
    build2.PUBLISH2 = False  # noindex on every page below
    bm, en = load(SEO / "wanita-new"), {d["slug"]: d for d in load(SEO / "en" / "women-new")}
    m = build4.en_map()
    for d in bm:
        t = en.get(d["slug"])
        ms_path, en_path = f"wanita/{d['slug']}/", (f"en/women/{t['slug_en']}/" if t else None)
        rel = [f"wanita/{r}" for r in d.get("related", [])] or [f"wanita/{p.stem}" for p in sorted((SEO / "wanita").glob("*.json"))][:4]
        build2.write(ms_path.rstrip("/"), build2.head(f"{d['title']} | Coach Zara", d["intro"][:155], ms_path, "ms",
            build4.faq_ld(d), {"ms": ms_path, "en": en_path} if t else None) + f"""<main class="w">
<p class="crumb"><a href="../">Turun lemak untuk wanita bekerja</a></p><h1>{E(d['title'])}</h1>
{f'<p class="lang">Read in English: <a href="{BASE}{en_path}">English version</a></p>' if t else ''}<p class="lead">{E(d['intro'])}</p>
{''.join(f'<h2>{E(s["h"])}</h2><p>{E(s["p"])}</p>' for s in d['sections'])}
<h2>Cuba minggu ini</h2><ul class="tips">{''.join(f'<li>{E(a)}</li>' for a in d['action'])}</ul>
<div class="card"><b>Mitos:</b> {E(d['myth'])}</div>
{build3.zara_box(d['title'])}
<h2>Soalan lazim</h2>{faqs(d)}
<h2>Baca juga</h2><div class="rel">{build2.rel_html(rel)}</div>
<p class="fine">Panduan am sahaja, bukan nasihat perubatan. Ada masalah kesihatan, sedang mengandung atau ambil ubat: bincang dengan doktor dulu.</p></main>""" + build2.foot())
        if not t:
            continue
        rel_en = "".join(f'<a href="{BASE}{m[p]}/">{E(build4.en_title(m[p], build4.load("women"), []))}</a>' for p in rel if p in m)
        build2.write(en_path.rstrip("/"), build2.head(f"{t['title']} | Coach Zara", t["intro"][:155], en_path, "en",
            build4.faq_ld(t), {"ms": ms_path, "en": en_path}) + f"""<main class="w">
<p class="crumb"><a href="../">Fat loss for working women</a></p><h1>{E(t['title'])}</h1><p class="lead">{E(t['intro'])}</p>
<p class="lang">Read in Malay: <a href="{BASE}{ms_path}">versi Bahasa Melayu</a></p>
{''.join(f'<h2>{E(s["h"])}</h2><p>{E(s["p"])}</p>' for s in t['sections'])}
<h2>Try this week</h2><ul class="tips">{''.join(f'<li>{E(a)}</li>' for a in t['action'])}</ul>
<div class="card"><b>Myth:</b> {E(t['myth'])}</div>
{build4.zara_box(t['title'])}
<h2>FAQ</h2>{faqs(t)}
<h2>Read next</h2><div class="rel">{rel_en}</div>
<p class="fine">{build4.FINE}</p></main>""" + build2.foot("en"))
    if bm:
        rows = "".join(f'<a href="{BASE}wanita/{d["slug"]}/"><span>{E(d["title"])}</span><b>BM →</b></a>'
                       + (f'<a href="{BASE}en/women/{en[d["slug"]]["slug_en"]}/"><span>{E(en[d["slug"]]["title"])}</span><b>EN →</b></a>' if d["slug"] in en else "")
                       for d in bm)
        build2.write("wanita/baru", build2.head("Semakan: 20 panduan baru (tersembunyi)", "Untuk semakan Kimi sahaja.", "wanita/baru/")
            + f"""<main class="w"><h1>20 panduan baru untuk semakan</h1>
<p class="lead">Halaman ini tersembunyi: tiada link dari laman, tiada dalam sitemap, Google diminta tidak index. {len(bm)} BM + {len(en)} English.</p>
<div class="list">{rows}</div></main>""" + build2.foot())
    elif (ROOT / "wanita" / "baru").exists():
        shutil.rmtree(ROOT / "wanita" / "baru")
    build2.PUBLISH2 = True
    print(f"build7: {len(bm)} BM + {len(en)} EN hidden pages")


if __name__ == "__main__":
    main()
