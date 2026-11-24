"""Second batch of pages (no API needed; run after seo/build.py):

  calories/<slug>/   English food pages (from seo/data-en)
  semak/             "Semak makan semalam" checker -> WhatsApp to coach
  workout/           "Workout 7 Hari di Rumah" generator -> Day 7 WhatsApp
  senaman/<slug>/    BM exercise guides (from seo/exercises)
  ramadan/           BM Ramadan guide (from seo/ramadan.json)

PUBLISH2 = False keeps them noindex and out of the sitemap until Kimi approves.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build import BASE, CSS, E, FONTS, WALK_KCAL_MIN  # noqa: E402

PUBLISH2 = True
ROOT = pathlib.Path(__file__).resolve().parent.parent
SEO = ROOT / "seo"
COACH = {"m": ("Coach Kimi", "60127040268"), "f": ("Coach Zara", "60123520097")}
ALIASES = json.loads((SEO / "aliases.json").read_text()) if (SEO / "aliases.json").exists() else {}
PRICE_MS = "Program coaching bermula dari RM259 sebulan, termasuk supplement. Bayar sekali untuk 1 bulan, tiada kontrak."
PRICE_EN = "Coaching programs start from RM259 a month, supplements included. One payment for 1 month, no contract."

CSS2 = CSS + """
.chips{display:flex;gap:6px;overflow-x:auto;padding-bottom:6px;margin-bottom:10px}
.chips button{flex:none;font:600 13px Montserrat,sans-serif;border:1.5px solid var(--ink);background:#fff;border-radius:99px;padding:7px 12px}
.chips button.on{background:var(--ink);color:#fff}
.pick{display:grid;gap:6px}
.pick .it{display:flex;align-items:center;gap:10px;background:#fff;border:1px solid var(--line);border-radius:10px;padding:9px 10px 9px 14px}
.pick .it span{flex:1;font-size:14px;font-weight:600;line-height:1.3}.pick .it small{display:block;color:var(--muted);font-weight:500}
.q{display:flex;align-items:center;gap:6px}.q button{width:34px;height:34px;border-radius:50%;border:0;font:800 18px Montserrat;background:var(--bg)}
.q button.add{background:var(--red);color:#fff}.q b{min-width:16px;text-align:center}
.bar{position:sticky;bottom:0;background:#000;color:#fff;margin:16px -16px 0;padding:12px 16px calc(12px + env(safe-area-inset-bottom));display:flex;align-items:center;gap:12px;z-index:4}
.bar .t{flex:1;font-size:13px}.bar .t b{font:italic 26px Anton,sans-serif;color:var(--yellow)}
.bar button{background:var(--red);color:#fff;border:0;border-radius:99px;font:800 15px Montserrat;padding:12px 18px}
.res{display:none}.res.on{display:block}
.seg{display:grid;grid-template-columns:repeat(auto-fit,minmax(90px,1fr));gap:6px;margin:6px 0 14px}
.seg button{font:600 14px Montserrat;border:1.5px solid var(--ink);background:#fff;border-radius:10px;padding:11px 8px}
.seg button.on{background:var(--ink);color:#fff}
label.l{display:block;font-weight:700;margin-top:10px}
.day{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin-bottom:10px}
.day h3{margin:0 0 6px;font:italic 20px Anton,sans-serif;text-transform:uppercase}
.day ol{margin:6px 0 0;padding-left:20px}.day li{margin-bottom:6px}.day li a{font-size:13px;color:var(--red);font-weight:700}
.day .chk{display:flex;gap:8px;align-items:center;margin-top:8px;font-weight:700;font-size:14px}
.btn.r{background:var(--red);color:#fff}.btn.k{background:#000;color:#fff}
.vid{position:relative;padding-top:56.25%;border-radius:12px;overflow:hidden;background:#000;margin:10px 0}
.vid iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
ol.steps{padding-left:20px}ol.steps li{margin-bottom:8px}
.menu{background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin-bottom:8px}
.menu b{display:block}.menu .n{float:right;color:var(--red);font-weight:800}
.lang{font-size:13px;margin:10px 0 0}.lang a{font-weight:700}
"""


def head(title, desc, path, lang="ms", extra="", alt=None):
    robots = "" if PUBLISH2 else '<meta name="robots" content="noindex">'
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{BASE}{p}">' for l, p in (alt or {}).items())
    quiz = "Quiz 2 min" if lang == "en" else "Kuiz 2 minit"
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">{robots}
<link rel="canonical" href="{BASE}{path}">{alts}<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{BASE}img/share.jpg"><meta name="theme-color" content="#000">{FONTS}<style>{CSS2}</style>{extra}</head><body>
<header class="top"><div class="w"><a class="brand" href="{BASE}{'?lang=en' if lang == 'en' else ''}"><span class="logo">WDT</span><span><b>ARAMI</b><small>Coach Kimi &amp; Coach Zara</small></span></a>
<a class="cta" href="{BASE}kuiz/?src={path.split('/')[0]}{'&amp;lang=en' if lang == 'en' else ''}">{quiz}</a></div></header>"""


def foot(lang="ms"):
    if lang == "en":
        return f'<footer><div class="w">#WEDOTRANSFORMATIONS · <a href="{BASE}?lang=en">Coach Kimi &amp; Coach Zara</a> · <a href="{BASE}calories/">All foods</a></div></footer></body></html>'
    return f'<footer><div class="w">#WEDOTRANSFORMATIONS · <a href="{BASE}">Coach Kimi &amp; Coach Zara</a> · <a href="{BASE}kalori/">Kalori makanan</a> · <a href="{BASE}senaman/">Senaman</a></div></footer></body></html>'


def write(path, html):
    p = ROOT / path
    p.mkdir(parents=True, exist_ok=True)
    (p / "index.html").write_text(html)


def _title(path):
    """Display title for a site path like wanita/<slug>, senaman/<slug>, kalori/<slug>, semak."""
    sec, _, slug = path.partition("/")
    if sec == "wanita" and (SEO / "wanita" / f"{slug}.json").exists():
        return json.loads((SEO / "wanita" / f"{slug}.json").read_text())["title"]
    if sec == "senaman" and (SEO / "exercises" / f"{slug}.json").exists():
        return json.loads((SEO / "exercises" / f"{slug}.json").read_text())["title"]
    if sec == "kalori":
        for f in json.loads((SEO / "foods.json").read_text())["foods"]:
            if f["slug"] == slug:
                return "Kalori " + f["name"].split("(")[0].strip()
    return {"semak": "Semak makan semalam", "workout": "Workout 7 Hari di rumah", "ramadan": "Panduan Ramadan"}.get(path, path)


def related_for(sec, slug, pages):
    """Hand-picked links from seo/related.json (made by generate6.py related); falls back to the first pages A-Z."""
    rp = SEO / "related.json"
    r = json.loads(rp.read_text()).get(f"{sec}/{slug}") if rp.exists() else None
    if r and r["same"]:
        return r["same"] + r["other"]
    return [f"{sec}/{x['slug']}" for x in pages if x["slug"] != slug][:6]


def rel_html(paths):
    return "".join(f'<a href="{BASE}{p}/">{E(_title(p))}</a>' for p in paths)


def box_ms(h, p, src):
    return f"""<div class="box"><h2>{E(h)}</h2><p>{E(p)}</p>
<a class="btn y" href="{BASE}kuiz/?src={src}">Jawab kuiz percuma →</a>
<a class="btn w2" href="{BASE}semak/?src={src}">Semak makan semalam saya</a>
<p class="price">{PRICE_MS}</p></div>"""


# ---------- English food pages ----------
def calories(foods, cats_en):
    by_cat = {}
    done = []
    for f in foods:
        p = SEO / "data-en" / f"{f['slug']}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        bm = json.loads((SEO / "data" / f"{f['slug']}.json").read_text())
        done.append((f, d, bm))
        by_cat.setdefault(f["cat"], []).append((f, d))
    for f, d, bm in done:
        name = d["name_en"]; short = name.split("(")[0].strip()
        walk = round(f["kcal"] / WALK_KCAL_MIN)
        title = f"{short} calories: about {f['kcal']} kcal | Malaysian food calories"
        desc = f"{short}: about {f['kcal']} kcal per {d['serving_en']}, {bm['protein_g']} g protein. Calorie breakdown, other versions, diet tips and a lighter swap."
        faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f"How many calories in {short}?", "acceptedAnswer": {"@type": "Answer", "text": d["intro"]}}] + [
            {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in d["faq"]]}
        rows = lambda items: "".join(f"<tr><td>{E(x.get('part') or x.get('name'))}</td><td>~{x['kcal']} kcal</td></tr>" for x in items)
        rel = [r for r in by_cat[f["cat"]] if r[0]["slug"] != f["slug"]][:6]
        html = head(title, desc, f"calories/{f['slug']}/", "en", f'<script type="application/ld+json">{json.dumps(faq, ensure_ascii=False)}</script>',
                    {"ms": f"kalori/{f['slug']}/", "en": f"calories/{f['slug']}/"}) + f"""<main class="w">
<p class="crumb"><a href="../">Malaysian food calories</a> › {E(cats_en[f['cat']])}</p>
<h1>How many calories in {E(short)}?</h1><p class="lead">{E(d['intro'])}</p>
<div class="answer"><div class="k">{f['kcal']}<small>kcal</small></div><div class="s">estimate<span>{E(d['serving_en'])}</span></div>
<div class="macros"><span>Protein <b>{bm['protein_g']} g</b></span><span>Carbs <b>{bm['carbs_g']} g</b></span><span>Fat <b>{bm['fat_g']} g</b></span></div>
<div class="walk">About <b>{walk} minutes</b> of brisk walking (estimate for a 65 kg adult).</div></div>
<p class="lang">Read in Malay: <a href="{BASE}kalori/{f['slug']}/">{E(f['name'].split('(')[0].strip())}</a></p>
<h2>Where the calories come from</h2><table>{rows(d['breakdown'])}</table>
<h2>Other versions</h2><table>{rows(d['variants'])}</table>
<h2>Can I eat it while losing weight?</h2><div class="card"><p style="margin:0">{E(d['diet'])}</p></div>
<h2>3 smarter tips</h2><ul class="tips">{''.join(f'<li>{E(t)}</li>' for t in d['tips'])}</ul>
<h2>Smarter swap</h2><div class="card swap"><div class="n">~{d['swap']['kcal']}</div><div><b>{E(d['swap']['name'])}</b><br>{E(d['swap']['why'])}</div></div>
<div class="box"><h2>Want to lose weight without giving up {E(short.lower())}?</h2><p>It's not the food, it's the routine. Take the 2-minute quiz to find what's holding you back, or check what you ate yesterday.</p>
<a class="btn y" href="{BASE}kuiz/?src=calories&amp;lang=en">Take the free quiz →</a>
<a class="btn w2" href="{BASE}?src=calories&amp;lang=en#kalori">Work out my calories + free meal plan</a><p class="price">{PRICE_EN}</p></div>
<h2>FAQ</h2>{''.join(f'<details><summary>{E(q["q"])}</summary><p>{E(q["a"])}</p></details>' for q in d['faq'])}
<h2>More {E(cats_en[f['cat']].lower())}</h2><div class="rel">{''.join(f'<a href="../{r[0]["slug"]}/">{E(r[1]["name_en"].split("(")[0].strip())}<span>~{r[0]["kcal"]} kcal</span></a>' for r in rel)}</div>
<p class="fine">All numbers are estimates for a typical Malaysian serving. Real calories depend on the recipe, portion and cooking. General guidance only, not medical advice.</p></main>""" + foot("en")
        write(f"calories/{f['slug']}", html)
    secs = "".join(f"""<section class="cat" id="{c}"><h2>{E(cats_en[c])}</h2><div class="list">{''.join(
        f'<a href="{f["slug"]}/" data-n="{E((d["name_en"] + " " + f["name"]).lower())}"><span>{E(d["name_en"].split("(")[0].strip())}<small>{E(d["serving_en"])}</small></span><b>~{f["kcal"]} kcal</b></a>'
        for f, d in by_cat[c])}</div></section>""" for c in cats_en if by_cat.get(c))
    js = """<script>document.getElementById('q').addEventListener('input',e=>{const v=e.target.value.toLowerCase().trim();document.querySelectorAll('.list a').forEach(a=>a.style.display=!v||a.dataset.n.includes(v)?'':'none');document.querySelectorAll('.cat').forEach(s=>s.style.display=[...s.querySelectorAll('.list a')].some(a=>a.style.display!=='none')?'':'none')});</script>"""
    write("calories", head("Malaysian food calories: nasi lemak, roti canai, teh tarik & 100+ more",
                           "Calories in popular Malaysian food: breakfast, rice, noodles, mamak, drinks, kuih, fast food and fruit. Estimates with protein and diet tips.",
                           "calories/", "en", alt={"ms": "kalori/", "en": "calories/"}) + f"""<main class="w">
<p class="crumb"><a href="{BASE}?lang=en">Coach Kimi &amp; Coach Zara</a> › Food calories</p><h1>Malaysian food calories</h1>
<p class="lead">How many calories in nasi lemak, roti canai or teh tarik? Search your food. Each page has calories, protein, other versions and tips for losing weight.</p>
<input class="search" id="q" type="search" placeholder="Search, e.g. nasi lemak" aria-label="Search food">{secs}
<p class="lang">Read in Malay: <a href="{BASE}kalori/">Kalori makanan Malaysia</a></p></main>{js}""" + foot("en"))
    return [f"calories/{f['slug']}/" for f, _, _ in done] + (["calories/"] if done else [])


# ---------- Semak makan semalam ----------
def semak(foods, cats):
    data = []
    for f in foods:
        p = SEO / "data" / f"{f['slug']}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        data.append([f["slug"], f["name"].split("(")[0].strip(), f["cat"], f["serving"], f["kcal"], d["protein_g"], d["swap"]["name"], d["swap"]["kcal"],
                     " ".join([f["name"].lower()] + ALIASES.get(f["slug"], []))])
    chips = '<button class="on" data-c="">Semua</button>' + "".join(f'<button data-c="{c}">{E(l)}</button>' for c, l in cats.items())
    js = """<script>
const F=__DATA__, CO=__COACH__, PRICE=__PRICE__;
const st={q:{},c:"",s:"",sex:""};
try{Object.assign(st.q,JSON.parse(localStorage.getItem("semak")||"{}"))}catch(e){}
const $=id=>document.getElementById(id);
const nz=s=>s.toLowerCase().replace(/[^a-z0-9]/g,"");
function list(){const v=nz($("q").value);
 $("pick").innerHTML=F.filter(f=>(!st.c||f[2]===st.c)&&(!v||nz(f[8]).includes(v)||f[8].split(" ").some(w=>nz(w).includes(v)))).map(f=>{const n=st.q[f[0]]||0;
  return `<div class="it"><span>${f[1]}<small>${f[3]} · ~${f[4]} kcal</small></span><div class="q">${n?`<button data-m="${f[0]}" aria-label="Kurang">−</button><b>${n}</b>`:""}<button class="add" data-p="${f[0]}" aria-label="Tambah">+</button></div></div>`}).join("")||"<p>Tak jumpa. Cuba nama lain atau pilih yang paling hampir.</p>";tot()}
function tot(){let k=0,p=0,n=0;for(const s in st.q){const f=F.find(x=>x[0]===s);if(f){k+=f[4]*st.q[s];p+=f[5]*st.q[s];n+=st.q[s]}}
 $("tk").textContent=k.toLocaleString();$("tn").textContent=n;try{localStorage.setItem("semak",JSON.stringify(st.q))}catch(e){}return {k,p,n}}
document.addEventListener("click",e=>{const b=e.target.closest("button");if(!b)return;
 if(b.dataset.p){st.q[b.dataset.p]=(st.q[b.dataset.p]||0)+1;list()}
 else if(b.dataset.m){st.q[b.dataset.m]--;if(st.q[b.dataset.m]<=0)delete st.q[b.dataset.m];list()}
 else if(b.dataset.c!==undefined&&b.closest(".chips")){st.c=b.dataset.c;document.querySelectorAll(".chips button").forEach(x=>x.classList.toggle("on",x===b));list()}
 else if(b.dataset.sex){st.sex=b.dataset.sex;document.querySelectorAll("[data-sex]").forEach(x=>x.classList.toggle("on",x===b))}});
$("q").addEventListener("input",list);
$("go").onclick=()=>{const t=tot();if(!t.n){$("q").focus();return}
 if(!st.sex){$("sexbox").scrollIntoView({behavior:"smooth",block:"center"});$("sexbox").style.outline="3px solid #E30613";return}
 const lo=st.sex==="f"?1500:1800, hi=st.sex==="f"?1800:2200;
 const items=Object.keys(st.q).map(s=>{const f=F.find(x=>x[0]===s);return {f,n:st.q[s],k:f[4]*st.q[s]}}).sort((a,b)=>b.k-a.k);
 const top=items.slice(0,3), save=top.reduce((a,x)=>a+Math.max(0,(x.f[4]-x.f[7]))*x.n,0);
 let verdict=t.k<lo-300?"Kalori anda agak rendah. Makan terlalu sikit selalunya buat lapar teruk waktu malam dan susah kekal.":t.k<=hi?"Jumlah ni masih dalam julat biasa untuk turun lemak. Yang penting sekarang: protein cukup dan konsisten setiap hari.":"Jumlah ni lebih tinggi dari julat biasa untuk turun lemak. Tak perlu buang makanan kegemaran, cuma tukar 2-3 benda.";
 const pro=Math.round(t.p);
 $("r").innerHTML=`<div class="answer"><div class="k">${t.k.toLocaleString()}<small>kcal</small></div><div class="s">anggaran semalam<span>${t.n} item · protein ~${pro} g</span></div>
 <div class="walk">Julat biasa untuk turun lemak: ~${lo.toLocaleString()}-${hi.toLocaleString()} kcal sehari (${st.sex==="f"?"wanita":"lelaki"}, anggaran kasar).</div></div>
 <p class="lead" style="margin-top:14px">${verdict}${pro<60?" Protein anda rendah (~"+pro+" g). Kebanyakan orang perlukan lebih, supaya kenyang lama dan otot terjaga.":""}</p>
 <h2>3 item paling tinggi kalori</h2>${top.map(x=>`<div class="menu"><span class="n">~${x.k} kcal</span><b>${x.f[1]}${x.n>1?" ×"+x.n:""}</b>Tukar: ${x.f[6]} (~${x.f[7]} kcal)</div>`).join("")}
 ${save>50?`<p><b>Kalau tukar 3 benda ni je, jimat lebih kurang ${save} kcal sehari.</b></p>`:""}`;
 const c=CO[st.sex], lines=items.map(x=>`- ${x.f[1]}${x.n>1?" x"+x.n:""}`).join("\\n");
 const msg=`Hi ${c[0]}! Saya dah guna "Semak makan semalam" di website.\\nSemalam saya makan:\\n${lines}\\nJumlah: ~${t.k} kcal, protein ~${pro} g.\\nBoleh semak dan bagi tahu apa patut saya ubah?`;
 $("wa").href=`https://wa.me/${c[1]}?text=${encodeURIComponent(msg)}`;$("wa").textContent=`Hantar ke ${c[0]} untuk disemak →`;
 $("res").classList.add("on");$("res").scrollIntoView({behavior:"smooth"})};
$("reset").onclick=()=>{st.q={};list();$("res").classList.remove("on");scrollTo(0,0)};
list();
</script>"""
    js = js.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__COACH__", json.dumps(COACH)).replace("__PRICE__", json.dumps(PRICE_MS))
    write("semak", head("Semak makan semalam: berapa kalori anda makan sehari?",
                        "Pilih apa yang anda makan semalam dari 120 makanan Malaysia. Dapat jumlah kalori, protein, 3 item paling tinggi kalori dan pilihan tukar. Percuma.",
                        "semak/") + f"""<main class="w">
<p class="crumb"><a href="{BASE}">Coach Kimi &amp; Coach Zara</a> › Semak makan semalam</p>
<h1>Semak makan semalam</h1>
<p class="lead">Tekan <b>+</b> untuk semua yang anda makan dan minum semalam, dari pagi sampai malam. Dalam 1 minit anda tahu jumlah kalori, protein, dan 3 benda yang paling senang ditukar.</p>
<input class="search" id="q" type="search" placeholder="Cari, cth. nasi lemak, teh tarik" aria-label="Cari makanan">
<div class="chips">{chips}</div><div class="pick" id="pick"></div>
<div id="sexbox"><label class="l">Anda</label><div class="seg"><button data-sex="f">Perempuan</button><button data-sex="m">Lelaki</button></div></div>
<div class="bar"><div class="t"><b id="tk">0</b> kcal · <span id="tn">0</span> item</div><button id="go">Semak →</button></div>
<section class="res" id="res"><h2>Result anda</h2><div id="r"></div>
<a class="btn r" id="wa" target="_blank" rel="noopener"></a>
<p style="font-size:14px;margin:8px 0 0">Coach akan semak makan anda dan bagi 1-2 perubahan paling senang untuk anda. Percuma, tiada paksaan.</p>
<button class="btn" id="reset" style="border:2px solid var(--ink);background:#fff;width:100%;font:800 15px Montserrat">Mula semula</button>
<p class="price" style="color:var(--muted)">{PRICE_MS}</p></section>
<p class="fine">Semua nombor ialah anggaran untuk hidangan biasa di Malaysia. Julat kalori ialah panduan kasar, bukan nasihat perubatan. Tidak sesuai untuk bawah 18 tahun, ibu mengandung atau menyusu: jumpa doktor dulu.</p>
</main>{js}""" + foot())
    return ["semak/"]


# ---------- Workout 7 hari ----------
def workout():
    plan_js = (ROOT / "pelan14" / "plan.js").read_text()
    start = plan_js.index("const EX = {"); end = plan_js.index("const WORK_DAYS")
    lib = plan_js[start:end]
    js = """<script>
""" + lib + """
const CO=__COACH__;const $=id=>document.getElementById(id);
const st={lvl:"",min:"",sex:"",knee:false,back:false};
document.addEventListener("click",e=>{const b=e.target.closest("button[data-k]");if(!b)return;st[b.dataset.k]=b.dataset.v;
 document.querySelectorAll(`button[data-k="${b.dataset.k}"]`).forEach(x=>x.classList.toggle("on",x===b))});
const DOSE={10:[2,30,20],20:[3,40,20],30:[4,45,15]};
function sess(list){return [...new Set(list.map(k=>st.knee&&SWAP_KNEE[k]?SWAP_KNEE[k]:k).map(k=>st.back&&SWAP_BACK[k]?SWAP_BACK[k]:k))]}
$("go").onclick=()=>{st.knee=$("knee").checked;st.back=$("back").checked;
 const miss=["lvl","min","sex"].find(k=>!st[k]);if(miss){$("f-"+miss).scrollIntoView({behavior:"smooth",block:"center"});$("f-"+miss).style.outline="3px solid #E30613";$("miss").textContent="Pilih dulu: "+{lvl:"tahap anda",min:"masa sehari",sex:"lelaki atau perempuan"}[miss]+" ↑";$("miss").hidden=false;return}$("miss").hidden=true;
 const [r,on,off]=DOSE[st.min], A=sess(SESS[st.lvl][0]), B=sess(SESS[st.lvl][1]);
 const walk={10:15,20:20,30:30}[st.min];
 const ex=list=>`<ol>${list.map(k=>`<li><b>${EX[k].ms}</b>: ${EX[k].c_ms} <a href="https://www.youtube.com/watch?v=${EX[k].v}" target="_blank" rel="noopener">Tengok video →</a></li>`).join("")}</ol>`;
 const days=[["Hari 1","Senaman A",ex(A)],["Hari 2","Jalan kaki",`<p>Jalan laju ${walk} minit. Boleh pecah 2 kali (pagi + petang).</p>`],["Hari 3","Senaman B",ex(B)],["Hari 4","Jalan kaki",`<p>Jalan laju ${walk} minit, atau naik turun tangga 10 minit.</p>`],["Hari 5","Senaman A",ex(A)],["Hari 6","Senaman B (pilihan) atau jalan",ex(B)],["Hari 7","Rehat + semak","<p>Rehat. Ukur pinggang dan tanya diri: tenaga lebih baik? tidur lebih lena?</p>"]];
 let done={};try{done=JSON.parse(localStorage.getItem("wk7")||"{}")}catch(e){}
 $("plan").innerHTML=`<div class="card" style="margin-bottom:12px"><b>Cara buat:</b> setiap senaman ${on} saat, rehat ${off} saat. Habis semua = 1 pusingan. Buat <b>${r} pusingan</b> (~${st.min} minit). Mula dengan 2-3 minit jalan setempat.</div>`+
  days.map((d,i)=>`<div class="day"><h3>${d[0]} · ${d[1]}</h3>${d[2]}<label class="chk"><input type="checkbox" data-d="${i}" ${done[i]?"checked":""}> Siap</label></div>`).join("");
 const c=CO[st.sex];
 const go=()=>{const n=Object.values(done).filter(Boolean).length;
  const msg=`Hi ${c[0]}! Saya dah buat Workout 7 Hari di Rumah dari website.\\nTahap: ${{new:"baru mula",some:"kadang-kadang senam",active:"aktif"}[st.lvl]}, ${st.min} minit.\\nSiap: ${n} dari 7 hari.\\nApa langkah seterusnya untuk saya?`;
  $("wa").href=`https://wa.me/${c[1]}?text=${encodeURIComponent(msg)}`;$("wa").textContent=`Hantar progress ke ${c[0]} →`};
 go();document.querySelectorAll("[data-d]").forEach(x=>x.onchange=()=>{done[x.dataset.d]=x.checked;try{localStorage.setItem("wk7",JSON.stringify(done))}catch(e){};go()});
 $("res").classList.add("on");$("res").scrollIntoView({behavior:"smooth"})};
</script>"""
    js = js.replace("__COACH__", json.dumps(COACH))
    seg = lambda k, opts: "".join(f'<button data-k="{k}" data-v="{v}">{E(l)}</button>' for v, l in opts)
    write("workout", head("Workout 7 Hari di Rumah: pelan senaman percuma tanpa alat",
                          "Pelan senaman 7 hari di rumah ikut tahap dan masa anda (10, 20 atau 30 minit), tanpa alat, dengan video cara buat. Percuma.",
                          "workout/") + f"""<main class="w">
<p class="crumb"><a href="{BASE}">Coach Kimi &amp; Coach Zara</a> › Workout 7 Hari</p>
<h1>Workout 7 Hari di Rumah</h1>
<p class="lead">Jawab 3 soalan, dapat pelan 7 hari ikut tahap anda. Tanpa alat, tanpa gym, ada video cara buat setiap senaman.</p>
<div id="f-lvl"><label class="l">Tahap anda sekarang</label><div class="seg">{seg("lvl", [("new", "Baru mula"), ("some", "Kadang-kadang"), ("active", "Aktif")])}</div></div>
<div id="f-min"><label class="l">Masa sehari</label><div class="seg">{seg("min", [("10", "10 minit"), ("20", "20 minit"), ("30", "30 minit")])}</div></div>
<div id="f-sex"><label class="l">Anda</label><div class="seg">{seg("sex", [("f", "Perempuan"), ("m", "Lelaki")])}</div></div>
<label class="chk" style="display:flex;gap:8px;margin:6px 0"><input type="checkbox" id="knee"> Lutut saya selalu sakit</label>
<label class="chk" style="display:flex;gap:8px;margin:6px 0 14px"><input type="checkbox" id="back"> Belakang (pinggang) saya selalu sakit</label>
<p id="miss" hidden style="color:var(--red);font-weight:700;margin:0 0 6px"></p><button class="btn r" id="go" style="width:100%;border:0;font:800 16px Montserrat">Buat pelan saya →</button>
<section class="res" id="res"><h2>Pelan 7 hari anda</h2><div id="plan"></div>
<div class="box"><h2>Hari 7: hantar progress</h2><p>Tandakan hari yang siap, kemudian hantar ke coach. Coach akan bagi langkah seterusnya ikut progress anda.</p>
<a class="btn y" id="wa" target="_blank" rel="noopener"></a>
<a class="btn w2" href="{BASE}semak/?src=workout">Semak makan semalam saya</a><p class="price">{PRICE_MS}</p></div></section>
<p class="fine">Panduan am sahaja. Berhenti kalau rasa sakit tajam, pening atau sesak nafas. Ada masalah jantung, darah tinggi tak terkawal, baru bersalin atau sedang mengandung: tanya doktor dulu.</p>
</main>{js}""" + foot())
    return ["workout/"]


# ---------- exercise guides ----------
def senaman():
    pages = []
    for p in sorted((SEO / "exercises").glob("*.json")) if (SEO / "exercises").exists() else []:
        pages.append(json.loads(p.read_text()))
    for d in pages:
        vid = f'<div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/{d["video"]}" title="{E(d["title"])}" loading="lazy" allowfullscreen></iframe></div>' if d.get("video") else ""
        faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in d["faq"]]}
        rel = related_for("senaman", d["slug"], pages)
        write(f"senaman/{d['slug']}", head(f"{d['title']} | Panduan senaman", d["intro"][:155], f"senaman/{d['slug']}/", "ms",
                                           f'<script type="application/ld+json">{json.dumps(faq, ensure_ascii=False)}</script>') + f"""<main class="w">
<p class="crumb"><a href="../">Senaman di rumah</a></p><h1>{E(d['title'])}</h1><p class="lead">{E(d['intro'])}</p>{vid}
<div class="card"><b>Bahagian dilatih:</b> {E(d['muscles'])}<br><b>Untuk beginner:</b> {E(d['dose'])}</div>
<h2>Cara buat</h2><ol class="steps">{''.join(f'<li>{E(s)}</li>' for s in d['steps'])}</ol>
<h2>Kesilapan biasa</h2><ul class="tips">{''.join(f'<li>{E(s)}</li>' for s in d['mistakes'])}</ul>
<h2>Versi lebih mudah</h2><div class="card">{E(d['easier'])}</div>
<h2>Versi lebih mencabar</h2><div class="card">{E(d['harder'])}</div>
<div class="box"><h2>Nak pelan senaman 7 hari ikut tahap anda?</h2><p>Percuma, tanpa alat, 10 hingga 30 minit sehari, dengan video setiap senaman.</p>
<a class="btn y" href="{BASE}workout/?src=senaman">Buat pelan 7 hari saya →</a><a class="btn w2" href="{BASE}kuiz/?src=senaman">Jawab kuiz 2 minit</a><p class="price">{PRICE_MS}</p></div>
<h2>Soalan lazim</h2>{''.join(f'<details><summary>{E(q["q"])}</summary><p>{E(q["a"])}</p></details>' for q in d['faq'])}
<h2>Panduan lain</h2><div class="rel">{rel_html(rel)}</div>
<p class="fine">{E(d['safety'])} Panduan am sahaja, bukan nasihat perubatan.</p></main>""" + foot())
    if pages:
        write("senaman", head("Senaman di rumah: panduan untuk beginner", "Panduan senaman di rumah tanpa alat: squat, push-up, plank, senaman perut, lengan, peha dan banyak lagi. Cara buat, kesilapan biasa dan video.", "senaman/") + f"""<main class="w">
<p class="crumb"><a href="{BASE}">Coach Kimi &amp; Coach Zara</a> › Senaman</p><h1>Senaman di rumah</h1>
<p class="lead">Panduan ringkas untuk beginner, tanpa alat. Atau terus <a href="{BASE}workout/">buat pelan 7 hari ikut tahap anda</a>.</p>
<div class="list">{''.join(f'<a href="{x["slug"]}/"><span>{E(x["title"])}</span><b>→</b></a>' for x in pages)}</div></main>""" + foot())
    return [f"senaman/{d['slug']}/" for d in pages] + (["senaman/"] if pages else [])


# ---------- Ramadan ----------
def ramadan():
    p = SEO / "ramadan.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text())
    menus = lambda xs: "".join(f'<div class="menu"><span class="n">~{m["kcal"]} kcal · {m["protein_g"]} g protein</span><b>{E(m["name"])}</b>{E(m["items"])}<br><small>{E(m["why"])}</small></div>' for m in xs)
    rows = lambda xs: "".join(f"<tr><td>{E(x['name'])} <small style='color:var(--muted)'>({E(x['serving'])})</small></td><td>~{x['kcal']} kcal</td></tr>" for x in xs)
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in d["faq"]]}
    write("ramadan", head(d["title"] + " | Coach Kimi & Coach Zara", d["intro"][:155], "ramadan/", "ms",
                          f'<script type="application/ld+json">{json.dumps(faq, ensure_ascii=False)}</script>') + f"""<main class="w">
<p class="crumb"><a href="{BASE}">Coach Kimi &amp; Coach Zara</a> › Ramadan</p><h1>{E(d['title'])}</h1><p class="lead">{E(d['intro'])}</p>
<h2>Kenapa ramai naik berat masa puasa?</h2><ul class="tips">{''.join(f'<li>{E(x)}</li>' for x in d['why_gain'])}</ul>
<h2>5 menu sahur</h2>{menus(d['sahur'])}
<h2>5 menu berbuka</h2>{menus(d['berbuka'])}
<h2>Kalori juadah bazar Ramadan</h2><table>{rows(d['bazar'])}</table>
<h2>Kalori kuih raya</h2><table>{rows(d['kuih_raya'])}</table>
<h2>Bersenam masa puasa</h2><div class="card">{E(d['exercise'])}</div>
<h2>8 tips puasa tanpa naik berat</h2><ul class="tips">{''.join(f'<li>{E(x)}</li>' for x in d['tips'])}</ul>
<h2>Raya: open house tanpa rasa bersalah</h2><ul class="tips">{''.join(f'<li>{E(x)}</li>' for x in d['raya'])}</ul>
{box_ms("Nak coach teman sepanjang Ramadan?", "Jawab kuiz 2 minit untuk tahu apa yang paling menghalang result anda, atau semak apa anda makan semalam.", "ramadan")}
<h2>Soalan lazim</h2>{''.join(f'<details><summary>{E(q["q"])}</summary><p>{E(q["a"])}</p></details>' for q in d['faq'])}
<p class="fine">Semua kalori ialah anggaran. Ada diabetes, darah tinggi, sedang mengandung atau menyusu: bincang dengan doktor sebelum ubah cara puasa atau makan. Panduan am sahaja.</p>
</main>""" + foot())
    return ["ramadan/"]


def main():
    src = json.loads((SEO / "foods.json").read_text())
    cats_en = {"sarapan": "Breakfast", "nasi": "Rice & sides", "mee": "Noodles", "mamak": "Mamak", "minuman": "Drinks",
               "kuih": "Kuih & desserts", "barat": "Western & fast food", "buah": "Fruit", "snek": "Snacks"}
    urls = calories(src["foods"], cats_en) + semak(src["foods"], src["categories"]) + workout() + senaman() + ramadan()
    sm = ROOT / "sitemap.xml"
    if PUBLISH2 and sm.exists():
        s = sm.read_text().replace("</urlset>", "".join(f"<url><loc>{BASE}{u}</loc></url>\n" for u in urls) + "</urlset>")
        sm.write_text(s)
    print(f"build2: {len(urls)} pages (publish={PUBLISH2})")


if __name__ == "__main__":
    main()
