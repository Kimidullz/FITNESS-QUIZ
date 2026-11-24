"""English versions of the two free tools (no API; run after build5.py, before polish.py):

  en/food-check/   "Check what you ate yesterday" -> WhatsApp to coach   (Malay: semak/)
  en/workout/      "7-day home workout" generator -> Day 7 WhatsApp      (Malay: workout/)
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build2  # noqa: E402
from build import BASE, E  # noqa: E402

SEO, ROOT = build2.SEO, build2.ROOT
CATS_EN = {"sarapan": "Breakfast", "nasi": "Rice & sides", "mee": "Noodles", "mamak": "Mamak", "minuman": "Drinks",
           "kuih": "Kuih & desserts", "barat": "Western & fast food", "buah": "Fruit", "snek": "Snacks"}


def food_check():
    src = json.loads((SEO / "foods.json").read_text())
    al = json.loads((SEO / "aliases.json").read_text()) if (SEO / "aliases.json").exists() else {}
    data = []
    for f in src["foods"]:
        p, pe = SEO / "data" / f"{f['slug']}.json", SEO / "data-en" / f"{f['slug']}.json"
        if not (p.exists() and pe.exists()):
            continue
        d, de = json.loads(p.read_text()), json.loads(pe.read_text())
        name = de["name_en"].split("(")[0].strip()
        data.append([f["slug"], name, f["cat"], de["serving_en"], f["kcal"], d["protein_g"], de["swap"]["name"], de["swap"]["kcal"],
                     " ".join([name.lower(), f["name"].lower()] + al.get(f["slug"], []))])
    chips = '<button class="on" data-c="">All</button>' + "".join(f'<button data-c="{c}">{E(CATS_EN.get(c, l))}</button>' for c, l in src["categories"].items())
    js = """<script>
const F=__DATA__, CO=__COACH__;
const st={q:{},c:"",s:"",sex:""};
try{Object.assign(st.q,JSON.parse(localStorage.getItem("semak")||"{}"))}catch(e){}
const $=id=>document.getElementById(id);
const nz=s=>s.toLowerCase().replace(/[^a-z0-9]/g,"");
function list(){const v=nz($("q").value);
 $("pick").innerHTML=F.filter(f=>(!st.c||f[2]===st.c)&&(!v||nz(f[8]).includes(v)||f[8].split(" ").some(w=>nz(w).includes(v)))).map(f=>{const n=st.q[f[0]]||0;
  return `<div class="it"><span>${f[1]}<small>${f[3]} · ~${f[4]} kcal</small></span><div class="q">${n?`<button data-m="${f[0]}" aria-label="Less">−</button><b>${n}</b>`:""}<button class="add" data-p="${f[0]}" aria-label="Add">+</button></div></div>`}).join("")||"<p>Not found. Try another name or pick the closest one.</p>";tot()}
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
 let verdict=t.k<lo-300?"Your calories are quite low. Eating too little usually leads to bad hunger at night and is hard to keep up.":t.k<=hi?"This is still within the usual range for fat loss. What matters now: enough protein and being consistent every day.":"This is above the usual range for fat loss. No need to give up your favourite food, just swap 2-3 things.";
 const pro=Math.round(t.p);
 $("r").innerHTML=`<div class="answer"><div class="k">${t.k.toLocaleString()}<small>kcal</small></div><div class="s">estimate for yesterday<span>${t.n} items · protein ~${pro} g</span></div>
 <div class="walk">Usual range for fat loss: ~${lo.toLocaleString()}-${hi.toLocaleString()} kcal a day (${st.sex==="f"?"women":"men"}, rough estimate).</div></div>
 <p class="lead" style="margin-top:14px">${verdict}${pro<60?" Your protein is low (~"+pro+" g). Most people need more, to stay full longer and protect muscle.":""}</p>
 <h2>Your 3 highest-calorie items</h2>${top.map(x=>`<div class="menu"><span class="n">~${x.k} kcal</span><b>${x.f[1]}${x.n>1?" ×"+x.n:""}</b>Swap: ${x.f[6]} (~${x.f[7]} kcal)</div>`).join("")}
 ${save>50?`<p><b>Swap just these 3 and you save about ${save} kcal a day.</b></p>`:""}`;
 const c=CO[st.sex], lines=items.map(x=>`- ${x.f[1]}${x.n>1?" x"+x.n:""}`).join("\\n");
 const msg=`Hi ${c[0]}! I used "Check what you ate yesterday" on your website.\\nYesterday I ate:\\n${lines}\\nTotal: ~${t.k} kcal, protein ~${pro} g.\\nCould you check it and tell me what I should change?`;
 $("wa").href=`https://wa.me/${c[1]}?text=${encodeURIComponent(msg)}`;$("wa").textContent=`Send to ${c[0]} for a check →`;
 $("res").classList.add("on");$("res").scrollIntoView({behavior:"smooth"})};
$("reset").onclick=()=>{st.q={};list();$("res").classList.remove("on");scrollTo(0,0)};
list();
</script>"""
    js = js.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__COACH__", json.dumps(build2.COACH))
    build2.write("en/food-check", build2.head("Check what you ate yesterday: how many calories do you eat a day?",
        "Pick what you ate yesterday from 120 Malaysian foods. Get your total calories, protein, your 3 highest-calorie items and easy swaps. Free.",
        "en/food-check/", "en", alt={"ms": "semak/", "en": "en/food-check/"}) + f"""<main class="w">
<p class="crumb"><a href="{BASE}?lang=en">Coach Kimi &amp; Coach Zara</a> › Food check</p>
<h1>Check what you ate yesterday</h1>
<p class="lead">Tap <b>+</b> for everything you ate and drank yesterday, from morning to night. In 1 minute you'll know your total calories, protein, and the 3 easiest things to swap.</p>
<p class="lang">Read in Malay: <a href="{BASE}semak/">Semak makan semalam</a></p>
<input class="search" id="q" type="search" placeholder="Search, e.g. nasi lemak, teh tarik" aria-label="Search food">
<div class="chips">{chips}</div><div class="pick" id="pick"></div>
<div id="sexbox"><label class="l">You are</label><div class="seg"><button data-sex="f">Female</button><button data-sex="m">Male</button></div></div>
<div class="bar"><div class="t"><b id="tk">0</b> kcal · <span id="tn">0</span> items</div><button id="go">Check →</button></div>
<section class="res" id="res"><h2>Your result</h2><div id="r"></div>
<a class="btn r" id="wa" target="_blank" rel="noopener"></a>
<p style="font-size:14px;margin:8px 0 0">Your coach will check what you ate and give you 1-2 of the easiest changes for you. Free, no pressure.</p>
<button class="btn" id="reset" style="border:2px solid var(--ink);background:#fff;width:100%;font:800 15px Montserrat">Start again</button>
<p class="price" style="color:var(--muted)">{build2.PRICE_EN}</p></section>
<p class="fine">All numbers are estimates for normal Malaysian servings. The calorie range is a rough guide, not medical advice. Not for under 18s, or if you are pregnant or breastfeeding: see a doctor first.</p>
</main>{js}""" + build2.foot("en"))
    return ["en/food-check/"]


def workout():
    plan_js = (ROOT / "pelan14" / "plan.js").read_text()
    lib = plan_js[plan_js.index("const EX = {"):plan_js.index("const WORK_DAYS")]
    js = """<script>
""" + lib + """
const CO=__COACH__;const $=id=>document.getElementById(id);
const st={lvl:"",min:"",sex:"",knee:false,back:false};
document.addEventListener("click",e=>{const b=e.target.closest("button[data-k]");if(!b)return;st[b.dataset.k]=b.dataset.v;
 document.querySelectorAll(`button[data-k="${b.dataset.k}"]`).forEach(x=>x.classList.toggle("on",x===b))});
const DOSE={10:[2,30,20],20:[3,40,20],30:[4,45,15]};
function sess(list){return [...new Set(list.map(k=>st.knee&&SWAP_KNEE[k]?SWAP_KNEE[k]:k).map(k=>st.back&&SWAP_BACK[k]?SWAP_BACK[k]:k))]}
$("go").onclick=()=>{st.knee=$("knee").checked;st.back=$("back").checked;
 const miss=["lvl","min","sex"].find(k=>!st[k]);if(miss){$("f-"+miss).scrollIntoView({behavior:"smooth",block:"center"});$("f-"+miss).style.outline="3px solid #E30613";$("miss").textContent="Pick first: "+{lvl:"your level",min:"time per day",sex:"male or female"}[miss]+" ↑";$("miss").hidden=false;return}$("miss").hidden=true;
 const [r,on,off]=DOSE[st.min], A=sess(SESS[st.lvl][0]), B=sess(SESS[st.lvl][1]);
 const walk={10:15,20:20,30:30}[st.min];
 const ex=list=>`<ol>${list.map(k=>`<li><b>${EX[k].en}</b>: ${EX[k].c_en} <a href="https://www.youtube.com/watch?v=${EX[k].v}" target="_blank" rel="noopener">Watch video →</a></li>`).join("")}</ol>`;
 const days=[["Day 1","Workout A",ex(A)],["Day 2","Walk",`<p>Brisk walk for ${walk} minutes. You can split it in 2 (morning + evening).</p>`],["Day 3","Workout B",ex(B)],["Day 4","Walk",`<p>Brisk walk for ${walk} minutes, or 10 minutes up and down the stairs.</p>`],["Day 5","Workout A",ex(A)],["Day 6","Workout B (optional) or walk",ex(B)],["Day 7","Rest + check-in","<p>Rest. Measure your waist and ask yourself: more energy? sleeping better?</p>"]];
 let done={};try{done=JSON.parse(localStorage.getItem("wk7")||"{}")}catch(e){}
 $("plan").innerHTML=`<div class="card" style="margin-bottom:12px"><b>How to do it:</b> each exercise ${on} seconds, rest ${off} seconds. All of them = 1 round. Do <b>${r} rounds</b> (~${st.min} minutes). Start with 2-3 minutes of marching in place.</div>`+
  days.map((d,i)=>`<div class="day"><h3>${d[0]} · ${d[1]}</h3>${d[2]}<label class="chk"><input type="checkbox" data-d="${i}" ${done[i]?"checked":""}> Done</label></div>`).join("");
 const c=CO[st.sex];
 const go=()=>{const n=Object.values(done).filter(Boolean).length;
  const msg=`Hi ${c[0]}! I did the 7-Day Home Workout from your website.\\nLevel: ${{new:"just starting",some:"exercise sometimes",active:"active"}[st.lvl]}, ${st.min} minutes.\\nDone: ${n} of 7 days.\\nWhat's my next step?`;
  $("wa").href=`https://wa.me/${c[1]}?text=${encodeURIComponent(msg)}`;$("wa").textContent=`Send my progress to ${c[0]} →`};
 go();document.querySelectorAll("[data-d]").forEach(x=>x.onchange=()=>{done[x.dataset.d]=x.checked;try{localStorage.setItem("wk7",JSON.stringify(done))}catch(e){};go()});
 $("res").classList.add("on");$("res").scrollIntoView({behavior:"smooth"})};
</script>"""
    js = js.replace("__COACH__", json.dumps(build2.COACH))
    seg = lambda k, opts: "".join(f'<button data-k="{k}" data-v="{v}">{E(l)}</button>' for v, l in opts)
    build2.write("en/workout", build2.head("7-Day Home Workout: free no-equipment exercise plan",
        "A free 7-day home workout plan for your level and time (10, 20 or 30 minutes), no equipment, with how-to videos.",
        "en/workout/", "en", alt={"ms": "workout/", "en": "en/workout/"}) + f"""<main class="w">
<p class="crumb"><a href="{BASE}?lang=en">Coach Kimi &amp; Coach Zara</a> › 7-day workout</p>
<h1>7-Day Home Workout</h1>
<p class="lead">Answer 3 questions and get a 7-day plan for your level. No equipment, no gym, with a how-to video for every exercise.</p>
<p class="lang">Read in Malay: <a href="{BASE}workout/">Workout 7 Hari di Rumah</a></p>
<div id="f-lvl"><label class="l">Your level now</label><div class="seg">{seg("lvl", [("new", "Just starting"), ("some", "Sometimes"), ("active", "Active")])}</div></div>
<div id="f-min"><label class="l">Time per day</label><div class="seg">{seg("min", [("10", "10 min"), ("20", "20 min"), ("30", "30 min")])}</div></div>
<div id="f-sex"><label class="l">You are</label><div class="seg">{seg("sex", [("f", "Female"), ("m", "Male")])}</div></div>
<label class="chk" style="display:flex;gap:8px;margin:6px 0"><input type="checkbox" id="knee"> My knees often hurt</label>
<label class="chk" style="display:flex;gap:8px;margin:6px 0 14px"><input type="checkbox" id="back"> My lower back often hurts</label>
<p id="miss" hidden style="color:var(--red);font-weight:700;margin:0 0 6px"></p><button class="btn r" id="go" style="width:100%;border:0;font:800 16px Montserrat">Make my plan →</button>
<section class="res" id="res"><h2>Your 7-day plan</h2><div id="plan"></div>
<div class="box"><h2>Day 7: send your progress</h2><p>Tick the days you finished, then send them to your coach. Your coach will give you the next step based on your progress.</p>
<a class="btn y" id="wa" target="_blank" rel="noopener"></a>
<a class="btn w2" href="{BASE}en/food-check/?src=workout">Check what I ate yesterday</a><p class="price">{build2.PRICE_EN}</p></div></section>
<p class="fine">General guide only. Stop if you feel sharp pain, dizziness or shortness of breath. If you have heart problems, uncontrolled high blood pressure, just gave birth or are pregnant: ask your doctor first.</p>
</main>{js}""" + build2.foot("en"))
    return ["en/workout/"]


def main():
    urls = food_check() + workout()
    sm = ROOT / "sitemap.xml"
    if build2.PUBLISH2 and sm.exists():
        s = sm.read_text()
        add = "".join(f"<url><loc>{BASE}{u}</loc></url>\n" for u in urls if f"{BASE}{u}</loc>" not in s)
        sm.write_text(s.replace("</urlset>", add + "</urlset>"))
    print(f"build6: {len(urls)} pages")


if __name__ == "__main__":
    main()
