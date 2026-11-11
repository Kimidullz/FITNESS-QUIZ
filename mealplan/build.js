// Builds the free fat-loss meal plan PDFs (4 calorie levels x BM/EN) into ../pdf/
// and writes mealplan/days.json (used by the calculator on index.html).
// Run: node mealplan/build.js   (needs a local server on :8765 for fonts/images? no: fonts load from Google)
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');

// [ms, en, kcal, protein g] rough estimates per portion (MyFCD/USDA-style, rounded)
const FOOD = {
  B1: ["Roti canai kosong 1 keping + telur rebus 1 + teh O kosong", "1 plain roti canai + 1 boiled egg + teh O kosong", 375, 12],
  B2: ["Oat 40g + susu rendah lemak 200ml + pisang", "40g oats + 200ml low-fat milk + banana", 350, 14],
  B3: ["Roti wholemeal 2 keping + telur 2 biji + kopi O kosong", "2 slices wholemeal bread + 2 eggs + black coffee", 320, 20],
  B4: ["Nasi lemak separuh nasi + telur rebus, tanpa ayam goreng", "Nasi lemak, half the rice + boiled egg, no fried chicken", 400, 13],
  B5: ["Yogurt Greek 170g + buah + granola 2 sudu", "170g Greek yogurt + fruit + 2 tbsp granola", 300, 18],
  B6: ["Mee hoon sup ayam 1 mangkuk", "1 bowl chicken mee hoon soup", 350, 18],
  B7: ["Thosai 2 keping + dhal", "2 thosai + dhal", 300, 10],
  B8: ["Roti canai 1 + telur 2 biji + teh tarik kurang manis", "1 roti canai + 2 eggs + teh tarik less sugar", 550, 21],
  B9: ["Oat 60g + susu rendah lemak + pisang + telur rebus 2 biji", "60g oats + low-fat milk + banana + 2 boiled eggs", 580, 28],
  L1: ["Nasi campur: nasi ½ cawan + ayam bakar + 2 sayur", "Nasi campur: ½ cup rice + grilled chicken + 2 vegetables", 450, 33],
  L2: ["Nasi 1 cawan + ikan bakar + sayur + ulam", "1 cup rice + grilled fish + vegetables + ulam", 500, 35],
  L3: ["Nasi ayam panggang (buang kulit) + sayur", "Roasted chicken rice (skin off) + vegetables", 600, 33],
  L4: ["Nasi 1 cawan + dada ayam 150g + salad", "1 cup rice + 150g chicken breast + salad", 530, 50],
  L5: ["Wrap tortilla + ayam + salad", "Tortilla wrap + chicken + salad", 420, 30],
  L6: ["Yong tau foo sup 6 keping + mee hoon sikit", "Yong tau foo soup, 6 pieces + a little mee hoon", 400, 22],
  L7: ["Nasi ½ cawan + daging masak kicap + sayur", "½ cup rice + beef in soy sauce + vegetables", 480, 28],
  L8: ["Nasi 1 cawan + ayam bakar + 2 sayur", "1 cup rice + grilled chicken + 2 vegetables", 550, 35],
  S1: ["Pisang + susu rendah lemak 1 gelas", "Banana + 1 glass low-fat milk", 190, 9],
  S2: ["Yogurt Greek + epal", "Greek yogurt + apple", 210, 16],
  S3: ["Kacang badam/tanah 1 genggam (25g)", "A handful of almonds/peanuts (25g)", 150, 6],
  S4: ["Telur rebus 2 biji", "2 boiled eggs", 150, 12],
  S5: ["Buah potong 1 cawan", "1 cup cut fruit", 80, 1],
  S6: ["Roti wholemeal + peanut butter 1 sudu", "Wholemeal toast + 1 tbsp peanut butter", 250, 9],
  D1: ["Ikan kembung bakar + nasi ½ cawan + sayur", "Grilled mackerel + ½ cup rice + vegetables", 350, 34],
  D2: ["Sup ayam + nasi ½ cawan + sayur", "Chicken soup + ½ cup rice + vegetables", 400, 30],
  D3: ["Telur dadar 2 biji + roti wholemeal 2 keping + salad", "2-egg omelette + 2 slices wholemeal bread + salad", 390, 22],
  D4: ["Kentang 1 biji + dada ayam 150g + sayur", "1 potato + 150g chicken breast + vegetables", 480, 52],
  D5: ["Spaghetti 1 cawan + sos daging tomato + salad", "1 cup spaghetti + tomato meat sauce + salad", 520, 28],
  D6: ["Tom yam campur (kurang santan) + nasi ½ cawan", "Tom yam campur (less coconut milk) + ½ cup rice", 400, 30],
  D7: ["Ayam atau ikan bakar + sayur, tanpa nasi", "Grilled chicken or fish + vegetables, no rice", 300, 35],
  D8: ["Nasi 1 cawan + ikan bakar + sayur + sup sayur", "1 cup rice + grilled fish + vegetables + vegetable soup", 550, 38],
};
// each day = [breakfast, lunch, snack(s), dinner]
const TIERS = {
  1200: [["B1","L1",["S5"],"D7"], ["B5","L6",["S4"],"D1"], ["B3","L5",["S5"],"D2"]],
  1500: [["B4","L1",["S2"],"D2"], ["B3","L4",["S1"],"D6"], ["B7","L2",["S4"],"D4"]],
  1800: [["B1","L3",["S1","S2"],"D2"], ["B2","L4",["S6","S5"],"D5"], ["B4","L2",["S2","S4"],"D5"]],
  2000: [["B8","L3",["S1","S2"],"D4"], ["B9","L4",["S6","S2"],"D5"], ["B4","L4",["S1","S6"],"D8"]],
  2300: [["B8","L8",["S6","S2","S4"],"D5"], ["B9","L3",["S1","S6","S4"],"D4"], ["B8","L2",["S2","S6","S4"],"D8"]],
};
const dayTotal = d => { const ids=[d[0],d[1],...d[2],d[3]]; return ids.reduce((t,i)=>[t[0]+FOOD[i][2], t[1]+FOOD[i][3]],[0,0]); };
for (const [k, days] of Object.entries(TIERS)) for (const d of days) {
  const [kc] = dayTotal(d); console.assert(Math.abs(kc - k) <= 120, `tier ${k} day ${d} = ${kc}`);
}

const T = {
  ms: { title:"Meal Plan Turun Lemak", sub:"Pelan asas percuma · makanan Malaysia + makanan harian", kcal:"kalori sehari", pro:"protein sehari", water:"air sehari",
        plateH:"Pinggan sihat (setiap kali makan)", plate:["½ pinggan sayur","¼ protein: ayam, ikan, telur, tauhu, daging","¼ nasi, roti atau mee"],
        rulesH:"5 peraturan mudah", rules:["Protein dalam setiap hidangan.","Air manis tukar ke kosong atau kurang manis.","Bakar, rebus, kukus, sup: kurangkan goreng dan santan.","Tidur 7 jam. Kurang tidur = lebih lapar.","Jalan 7,000+ langkah sehari."],
        daysH:"3 contoh menu sehari", day:"Hari", meals:["Sarapan","Tengah hari","Snek","Makan malam"], total:"Jumlah",
        mix:"Boleh tukar hidangan antara hari, asalkan kalori lebih kurang sama.",
        swapH:"Tukar ini, jimat kalori", swaps:[["Teh tarik","Teh O kosong / kurang manis","~100"],["Ayam goreng","Ayam bakar / panggang","~100"],["Nasi sepinggan penuh","Separuh nasi + tambah sayur","~150"],["Mee goreng mamak","Mee hoon sup","~300"],["Air manis / soda","Air kosong / air limau tanpa gula","~140"],["Kerepek","Kacang 1 genggam / buah","~100"]],
        outH:"Makan di luar", out:["Mamak: roti canai kosong, telur separuh masak, teh O.","Nasi campur: 1 lauk protein + 2 sayur, kuah sikit.","Fast food: burger ayam bakar, tanpa air manis.","Pilih sup dan bakar dulu."],
        shiftH:"Kerja syif?", shift:"Makan ikut waktu jaga, bukan waktu jam. Syif malam: makan malam sebelum masuk kerja, snek protein kecil sekitar 2 pagi (telur, yogurt), sarapan ringan sebelum tidur. Elak snek manis tengah malam dan tidur siang dalam bilik gelap.",
        ctaH:"Nak program penuh dengan coach?", cta:"Jawab kuiz 2 minit di website. Kalau sesuai, coach akan WhatsApp anda untuk consultation percuma.", ctaBtn:"Jawab kuiz →",
        note:"Anggaran sahaja, bukan nasihat perubatan. Result berbeza mengikut individu. Tidak sesuai untuk bawah 18 tahun, ibu mengandung atau menyusu, kurang berat badan, pernah ada eating disorder, atau penghidap diabetes, buah pinggang atau jantung: jumpa doktor dulu." },
  en: { title:"Fat-Loss Meal Plan", sub:"Free basic plan · Malaysian + everyday food", kcal:"calories a day", pro:"protein a day", water:"water a day",
        plateH:"Healthy plate (every meal)", plate:["½ plate vegetables","¼ protein: chicken, fish, eggs, tofu, meat","¼ rice, bread or noodles"],
        rulesH:"5 simple rules", rules:["Protein at every meal.","Swap sweet drinks for plain or less sugar.","Grill, boil, steam or soup: less frying and santan.","Sleep 7 hours. Less sleep = more hunger.","Walk 7,000+ steps a day."],
        daysH:"3 sample days", day:"Day", meals:["Breakfast","Lunch","Snack","Dinner"], total:"Total",
        mix:"Swap meals between days as long as the calories are about the same.",
        swapH:"Swap this, save calories", swaps:[["Teh tarik","Teh O kosong / less sugar","~100"],["Fried chicken","Grilled / roasted chicken","~100"],["Full plate of rice","Half the rice + more vegetables","~150"],["Mee goreng mamak","Mee hoon soup","~300"],["Sweet drink / soda","Plain water / lime, no sugar","~140"],["Crisps","A handful of nuts / fruit","~100"]],
        outH:"Eating out", out:["Mamak: plain roti canai, half-boiled eggs, teh O.","Nasi campur: 1 protein + 2 vegetables, little gravy.","Fast food: grilled chicken burger, no sweet drink.","Choose soup and grilled first."],
        shiftH:"Working shifts?", shift:"Eat by your waking hours, not the clock. Night shift: eat dinner before your shift, a small protein snack around 2am (eggs, yogurt), and a light breakfast before you sleep. Skip sweet midnight snacks and sleep in a dark room.",
        ctaH:"Want the full program with a coach?", cta:"Take the 2-minute quiz on the website. If it's a fit, a coach will WhatsApp you for a free consultation.", ctaBtn:"Take the quiz →",
        note:"Estimate only, not medical advice. Results vary. Not for under 18s, pregnant or breastfeeding mums, people who are underweight, have had an eating disorder, or have diabetes, kidney or heart problems: see your doctor first." },
};
// Other coaches (e.g. Coach Mel) reuse this with env: BRAND, BRAND_SUB, SITE, OUT
const SITE = process.env.SITE || "https://kimidullz.github.io/FITNESS-QUIZ/";
const BRAND = process.env.BRAND || "ARAMI", BRAND_SUB = process.env.BRAND_SUB || "Coach Kimi &amp; Coach Zara";
const proRange = k => ({1200:"80-100",1500:"90-110",1800:"100-130",2000:"110-140",2300:"120-150"})[k];
const esc = s => s.replace(/&/g,"&amp;").replace(/</g,"&lt;");

function html(k, lang){
  const t = T[lang], L = i => esc(FOOD[i][lang==="ms"?0:1]);
  const dayCard = (d, n) => { const [kc, p] = dayTotal(d); const rows = [[0,[d[0]]],[1,[d[1]]],[2,d[2]],[3,[d[3]]]];
    return `<div class="day"><div class="dh"><b>${t.day} ${n}</b><span>${t.total}: ~${kc.toLocaleString()} kcal · ${p} g protein</span></div>
    ${rows.map(([m,ids])=>`<div class="row"><i>${t.meals[m]}</i><span>${ids.map(L).join(" + ")}</span><em>~${ids.reduce((a,i)=>a+FOOD[i][2],0)}</em></div>`).join("")}</div>`; };
  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
@page{size:A4;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Montserrat,sans-serif;color:#111;font-size:14px;line-height:1.45}
.page{width:210mm;height:297mm;padding:14mm 14mm 12mm;position:relative;overflow:hidden;page-break-after:always}
.page:last-child{page-break-after:auto}
.band{background:#0B0B0B;color:#fff;margin:-14mm -14mm 10mm;padding:12mm 14mm 9mm;position:relative}
.band:after{content:"";position:absolute;left:0;right:0;bottom:0;height:5px;background:linear-gradient(90deg,#E30613 0 65%,#FFD200 65%)}
.brand{font-family:Anton;font-size:18px;letter-spacing:.5px}.brand small{font-family:Montserrat;font-weight:700;font-size:11px;opacity:.7;margin-left:8px}
h1{font-family:Anton;font-style:italic;text-transform:uppercase;font-size:46px;line-height:1;margin-top:8px}
h1 em{color:#FFD200;font-style:italic}
.sub{opacity:.8;font-weight:700;margin-top:6px}
h2{font-family:Anton;font-style:italic;text-transform:uppercase;font-size:22px;margin:0 0 8px}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:10mm}
.stat{background:#F4F4F2;border-radius:10px;padding:12px 14px;border-top:5px solid #0B0B0B}
.stat:nth-child(2){border-top-color:#FFD200}
.stat b{display:block;font-family:Anton;font-style:italic;font-size:30px;line-height:1.05}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10mm;margin-bottom:9mm}
.plate{display:flex;gap:14px;align-items:center}
.pie{width:120px;height:120px;border-radius:50%;flex:none;background:conic-gradient(#6BBF59 0 50%,#E30613 50% 75%,#FFD200 75% 100%);border:4px solid #0B0B0B}
.plate li{list-style:none;margin-bottom:6px;padding-left:16px;position:relative;font-weight:700}
.plate li:before{content:"";position:absolute;left:0;top:4px;width:10px;height:10px;border-radius:2px}
.plate li:nth-child(1):before{background:#6BBF59}.plate li:nth-child(2):before{background:#E30613}.plate li:nth-child(3):before{background:#FFD200}
ol{padding-left:18px}ol li{margin-bottom:5px;font-weight:500}
.day{border:2px solid #E3E3E0;border-radius:10px;margin-bottom:5mm;overflow:hidden}
.dh{display:flex;justify-content:space-between;background:#0B0B0B;color:#fff;padding:7px 12px}
.dh b{font-family:Anton;font-style:italic;font-size:16px;letter-spacing:.5px}.dh span{font-weight:700;font-size:11.5px;align-self:center}
.row{display:grid;grid-template-columns:28mm 1fr 14mm;gap:8px;padding:7px 12px;border-top:1px solid #E3E3E0}
.row i{font-style:normal;font-weight:800;font-size:11px;text-transform:uppercase;letter-spacing:.4px}
.row em{font-style:normal;font-weight:700;text-align:right;color:#5E5E5E}
.mix{color:#5E5E5E;font-size:11.5px;margin-top:-2mm}
table{width:100%;border-collapse:collapse;margin-bottom:8mm}
td{padding:6px 8px;border-bottom:1px solid #E3E3E0}td:last-child{text-align:right;font-weight:800;white-space:nowrap}
td:nth-child(2){font-weight:700}td:nth-child(2):before{content:"→ ";color:#5E5E5E}
ul.out{list-style:none}ul.out li{margin-bottom:5px;padding-left:14px;position:relative}ul.out li:before{content:"✓";position:absolute;left:0;font-weight:800}
.box{background:#F4F4F2;border-radius:10px;padding:12px 14px}
.cta{background:#E30613;color:#fff;border-radius:12px;padding:14px 16px;margin-top:8mm;display:flex;justify-content:space-between;align-items:center;gap:14px}
.cta h3{font-family:Anton;font-style:italic;text-transform:uppercase;font-size:20px;line-height:1.1;margin-bottom:6px}
.cta a{background:#0B0B0B;color:#fff;text-decoration:none;font-weight:800;padding:10px 16px;border-radius:8px;white-space:nowrap}
.note{position:absolute;left:14mm;right:14mm;bottom:10mm;font-size:11px;color:#5E5E5E;border-top:1px solid #E3E3E0;padding-top:6px}
.foot{position:absolute;right:14mm;top:8mm;font-size:11px;color:#5E5E5E}
</style></head><body>
<div class="page">
  <div class="band"><div class="brand">${BRAND}<small>${BRAND_SUB}</small></div>
  <h1>${t.title} <em>~${k.toLocaleString()} kcal</em></h1><div class="sub">${t.sub}</div></div>
  <div class="stats"><div class="stat"><b>~${k.toLocaleString()}</b>${t.kcal}</div><div class="stat"><b>${proRange(k)} g</b>${t.pro}</div><div class="stat"><b>2-3 L</b>${t.water}</div></div>
  <div class="two"><div><h2>${t.plateH}</h2><div class="plate"><div class="pie"></div><ul>${t.plate.map(x=>`<li>${x}</li>`).join("")}</ul></div></div>
  <div><h2>${t.rulesH}</h2><ol>${t.rules.map(x=>`<li>${x}</li>`).join("")}</ol></div></div>
  <h2>${t.daysH}</h2>
  ${dayCard(TIERS[k][0],1)}${dayCard(TIERS[k][1],2)}
  <div class="note">${t.note}</div>
</div>
<div class="page"><div class="foot">${BRAND} · ${t.title} ~${k} kcal</div>
  ${dayCard(TIERS[k][2],3)}<p class="mix">${t.mix}</p>
  <h2 style="margin-top:6mm">${t.swapH}</h2>
  <table>${t.swaps.map(([a,b,c])=>`<tr><td>${a}</td><td>${b}</td><td>${c} kcal</td></tr>`).join("")}</table>
  <div class="two" style="margin-bottom:0"><div><h2>${t.outH}</h2><ul class="out">${t.out.map(x=>`<li>${x}</li>`).join("")}</ul></div>
  <div class="box"><h2>${t.shiftH}</h2><p>${t.shift}</p></div></div>
  <div class="cta"><div><h3>${t.ctaH}</h3><p>${t.cta}</p></div><a href="${SITE}${process.env.SITE ? "" : (lang==="en"?"?lang=en":"") + "#quiz-zone"}">${t.ctaBtn}</a></div>
  <div class="note">${t.note}</div>
</div></body></html>`;
}

(async () => {
  const out = process.env.OUT || path.join(__dirname, '..', 'pdf'); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(); const p = await b.newPage();
  for (const k of Object.keys(TIERS)) for (const lang of ['ms','en']) {
    await p.setContent(html(+k, lang), { waitUntil: 'networkidle' });
    await p.pdf({ path: path.join(out, `meal-plan-${k}-${lang}.pdf`), format: 'A4', printBackground: true });
    if (k === '1500' && process.argv[2]) await p.screenshot({ path: process.argv[2] + `/mp-${lang}.png`, fullPage: true });
  }
  await b.close();
  // calculator data: first day of each tier, with both languages
  const days = Object.fromEntries(Object.entries(TIERS).map(([k, ds]) => [k, ds[0].map(x => [].concat(x).map(i => FOOD[i]))]));
  fs.writeFileSync(path.join(__dirname, 'days.json'), JSON.stringify(days));
  console.log('ok', Object.entries(TIERS).map(([k, ds]) => k + ':' + ds.map(d => dayTotal(d)[0]).join('/')).join(' '));
})();
