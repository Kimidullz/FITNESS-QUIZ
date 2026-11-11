// Builds the free "Kit Mula 7 Hari" meal plan PDFs (5 calorie levels x BM/EN, 8 pages) into ../pdf/,
// plus the weight-gain kit (3 levels x BM/EN, 6 pages: no eating-out or grocery page) as weight-gain-*.pdf.
// Data: FOOD/TIERS below, grocery.js (grocery page), recipes.json (recipes + eating out).
// Run: node mealplan/build.js [screenshotDir]
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');

// [ms, en, kcal, protein g] rough estimates per portion (MyFCD/USDA-style, rounded)
const FOOD = {
  B1: ["Roti canai kosong 1 keping + telur rebus 1 + teh O kosong", "1 plain roti canai + 1 boiled egg + teh O kosong", 375, 12],
  B2: ["Oat 40g + susu rendah lemak 200ml + pisang", "40g oats + 200ml low-fat milk + banana", 350, 14],
  B3: ["Roti wholemeal 2 keping + telur 2 biji + kopi O kosong", "2 slices wholemeal bread + 2 eggs + black coffee", 320, 20],
  B4: ["Nasi lemak separuh nasi + telur rebus, tanpa ayam goreng", "Nasi lemak, half the rice + boiled egg, no fried chicken", 400, 13],
  B5: ["Yogurt Greek 170g + buah + granola 2 sudu besar", "170g Greek yogurt + fruit + 2 tbsp granola", 300, 18],
  B6: ["Mee hoon sup ayam 1 mangkuk", "1 bowl chicken mee hoon soup", 350, 18],
  B7: ["Thosai 2 keping + dhal", "2 thosai + dhal", 300, 10],
  B8: ["Roti canai 1 + telur 2 biji + teh tarik kurang manis", "1 roti canai + 2 eggs + teh tarik less sugar", 550, 21],
  B9: ["Oat 60g + susu rendah lemak + pisang + telur rebus 2 biji", "60g oats + low-fat milk + banana + 2 boiled eggs", 580, 28],
  L1: ["Nasi campur: nasi ½ cawan + ayam bakar + 2 sayur", "Nasi campur: ½ cup rice + grilled chicken + 2 vegetables", 450, 33],
  L2: ["Nasi 1 cawan + ikan bakar + sayur + ulam", "1 cup rice + grilled fish + vegetables + ulam", 500, 30],
  L3: ["Nasi ayam panggang (buang kulit) + sayur", "Roasted chicken rice (skin off) + vegetables", 600, 33],
  L4: ["Nasi 1 cawan + dada ayam 150g + salad", "1 cup rice + 150g chicken breast + salad", 530, 40],
  L5: ["Wrap tortilla + ayam + salad", "Tortilla wrap + chicken + salad", 420, 30],
  L6: ["Yong tau foo sup 6 keping + mee hoon sikit", "Yong tau foo soup, 6 pieces + a little mee hoon", 400, 22],
  L7: ["Nasi ½ cawan + daging masak kicap + sayur", "½ cup rice + beef in soy sauce + vegetables", 480, 28],
  L8: ["Nasi 1 cawan + ayam bakar + 2 sayur", "1 cup rice + grilled chicken + 2 vegetables", 550, 35],
  S1: ["Pisang + susu rendah lemak 1 gelas", "Banana + 1 glass low-fat milk", 190, 9],
  S2: ["Yogurt Greek 150g + epal", "150g Greek yogurt + apple", 210, 16],
  S3: ["Kacang badam/tanah 1 genggam (25g)", "A handful of almonds/peanuts (25g)", 150, 6],
  S4: ["Telur rebus 2 biji", "2 boiled eggs", 150, 12],
  S5: ["Buah potong 1 cawan", "1 cup cut fruit", 80, 1],
  S6: ["Roti wholemeal 2 keping + peanut butter 1 sudu besar", "2 slices wholemeal toast + 1 tbsp peanut butter", 250, 11],
  D1: ["Ikan kembung bakar + nasi ½ cawan + sayur", "Grilled mackerel + ½ cup rice + vegetables", 350, 28],
  D2: ["Sup ayam + nasi ½ cawan + sayur", "Chicken soup + ½ cup rice + vegetables", 400, 30],
  D3: ["Telur dadar 2 biji + roti wholemeal 2 keping + salad", "2-egg omelette + 2 slices wholemeal bread + salad", 390, 22],
  D4: ["Kentang 1 biji + dada ayam 150g + sayur", "1 potato + 150g chicken breast + vegetables", 480, 41],
  D5: ["Spaghetti 1 cawan + sos daging tomato + salad", "1 cup spaghetti + tomato meat sauce + salad", 520, 28],
  D6: ["Tom yam campur kuah jernih + nasi ½ cawan", "Clear tom yam campur + ½ cup rice", 400, 30],
  D7: ["Ayam atau ikan bakar + sayur, tanpa nasi", "Grilled chicken or fish + vegetables, no rice", 300, 35],
  D8: ["Nasi 1 cawan + ikan bakar + sayur + sup sayur", "1 cup rice + grilled fish + vegetables + vegetable soup", 550, 31],
  // weight gain
  GB1: ["Nasi lemak + telur rebus + ayam bakar", "Nasi lemak + boiled egg + grilled chicken", 700, 36],
  GB2: ["Oat 60g + susu penuh krim 250ml + pisang + peanut butter 1 sudu besar", "60g oats + 250ml full-cream milk + banana + 1 tbsp peanut butter", 590, 21],
  GB3: ["3 roti wholemeal + 3 telur hancur + segelas susu penuh krim", "3 slices wholemeal toast + 3 scrambled eggs + full-cream milk", 670, 39],
  GL1: ["Nasi 1½ cawan + ayam bakar + 2 sayur + kuah sikit", "1½ cups rice + grilled chicken + 2 veg + a little gravy", 720, 39],
  GL2: ["Nasi 1½ cawan + ikan bakar + telur dadar + sayur", "1½ cups rice + grilled fish + omelette + vegetables", 710, 40],
  GL3: ["Nasi 2 cawan + ayam bakar + 2 sayur + kuah sikit", "2 cups rice + grilled chicken + 2 veg + a little gravy", 820, 41],
  GS1: ["Smoothie: susu penuh krim + pisang + oat 30g + peanut butter 1 sudu besar", "Smoothie: full-cream milk + banana + 30g oats + 1 tbsp peanut butter", 475, 17],   // 250ml milk
  GS2: ["Kacang campur 40g + kurma 3 biji", "40g mixed nuts + 3 dates", 310, 9],
  GS3: ["Yogurt Greek 170g + granola 4 sudu besar + madu 1 sudu kecil", "170g Greek yogurt + 4 tbsp granola + 1 tsp honey", 290, 20],
  GS4: ["Sandwich 2 telur & keju (roti wholemeal)", "2-egg & cheese wholemeal sandwich", 370, 24],
  GD1: ["Nasi 1½ cawan + daging masak kicap + sayur", "1½ cups rice + beef in soy sauce + vegetables", 660, 38],
  GD2: ["Nasi 1 cawan + ayam masak merah + sayur + telur rebus", "1 cup rice + ayam masak merah + vegetables + boiled egg", 640, 35],
  GD3: ["Mee sup daging + telur rebus 1 biji", "Beef noodle soup + 1 boiled egg", 550, 31],
};
// each day = [breakfast, lunch, snack(s), dinner]
const TIERS = {
  1200: [["B1","L1",["S5"],"D7"], ["B5","L6",["S4"],"D1"], ["B3","L5",["S5"],"D2"]],
  1500: [["B4","L1",["S2"],"D2"], ["B3","L4",["S1"],"D6"], ["B7","L2",["S4"],"D4"]],
  1800: [["B1","L3",["S1","S2"],"D2"], ["B2","L4",["S6","S4"],"D5"], ["B4","L2",["S2","S4"],"D8"]],
  2000: [["B8","L3",["S1","S2"],"D4"], ["B9","L4",["S6","S2"],"D5"], ["B4","L4",["S1","S6"],"D8"]],
  2300: [["B8","L8",["S6","S2","S4"],"D5"], ["B9","L3",["S1","S6","S4"],"D4"], ["B8","L2",["S2","S6","S4"],"D8"]],
};
const GTIERS = {
  2000: [["B9","L8",["S1","S4"],"D8"], ["GB3","L3",["S4","S5"],"GD3"], ["GB2","L8",["S4","S5"],"GD2"]],
  2500: [["GB1","L8",["GS1","S4"],"GD2"], ["GB3","GL2",["GS1","S5"],"GD1"], ["GB2","GL1",["GS3","S6"],"GD3"]],
  3000: [["GB1","GL3",["GS1","GS2"],"GD2"], ["GB3","GL2",["GS1","GS4"],"GD1"], ["GB2","GL3",["GS4","GS3","GS2"],"GD2"]],
};
const dayTotal = d => { const ids=[d[0],d[1],...d[2],d[3]]; return ids.reduce((t,i)=>[t[0]+FOOD[i][2], t[1]+FOOD[i][3]],[0,0]); };
for (const [k, days] of [...Object.entries(TIERS), ...Object.entries(GTIERS)]) for (const d of days) {
  const [kc] = dayTotal(d); console.assert(Math.abs(kc - k) <= 120, `tier ${k} day ${d} = ${kc}`);
}

const G = require('./grocery.js'), R = require('./recipes.json');

const T = {
  ms: { kit:"Kit Mula 7 Hari · Percuma", title:"Meal Plan Turun Lemak", sub:"Menu 3 hari · Makan di luar · 8 resipi · Senarai barang + kos · Cabaran 7 hari", kcal:"kalori sehari", pro:"protein sehari", water:"air sehari",
        plateH:"Pinggan sihat (setiap kali makan)", plate:["½ pinggan sayur","¼ protein: ayam, ikan, telur, tauhu, daging","¼ nasi, roti atau mee"],
        rulesH:"5 peraturan mudah", rules:["Protein dalam setiap hidangan.","Air manis tukar ke kosong atau kurang manis.","Bakar, rebus, kukus, sup: kurangkan goreng dan santan.","Tidur 7 jam. Kurang tidur = lebih lapar.","Jalan 7,000+ langkah sehari."],
        daysH:"3 contoh menu sehari", day:"Hari", meals:["Sarapan","Tengah hari","Snek","Makan malam"], total:"Jumlah",
        mix:"Boleh tukar hidangan antara hari, atau dengan resipi dan pilihan makan luar dalam kit ini, asalkan kalori lebih kurang sama.",
        swapH:"Tukar ini, jimat kalori", swaps:[["Teh tarik","Teh O kosong / kurang manis","~100"],["Ayam goreng","Ayam bakar / panggang","~100"],["Nasi sepinggan penuh","Separuh nasi + tambah sayur","~150"],["Mee goreng mamak","Mee hoon sup","~300"],["Air manis / soda","Air kosong / air limau tanpa gula","~140"],["Kerepek sebungkus","Buah potong 1 cawan","~100"]],
        shiftH:"Kerja syif?", shift:"Makan ikut waktu jaga, bukan waktu jam. Syif malam: makan malam sebelum masuk kerja, snek protein kecil sekitar 2 pagi (telur, yogurt), sarapan ringan sebelum tidur. Elak snek manis tengah malam. Bila tidur siang, tidur dalam bilik yang gelap.",
        eoH:"Makan di luar? Pilih ini", eoSub:"Anggaran kalori untuk satu hidangan. Makan luar pun boleh turun lemak, asalkan pilih betul.", avoid:"Elak", say:"Cakap:",
        eoRule:"Di kedai mana pun: 1 protein (bakar, sup atau stim) + sayur + nasi separuh. Kuah sikit. Air kosong.",
        rcH:"Masak di rumah: 8 resipi mudah", rcH2:"Lagi 4 resipi",
        prepSub:"30 minit hari Ahad, makan sihat sampai Rabu. Ini yang paling banyak bantu orang yang sibuk.", safeH:"Keselamatan makanan:", famH:"Masak untuk keluarga?", rcSub:"Bawah 20 minit. Tukar mana-mana hidangan dalam menu dengan resipi yang kalorinya hampir sama.", ing:"Bahan", how:"Cara",
        slot:{"sarapan":"Sarapan","tengah hari":"Tengah hari","malam":"Makan malam","sarapan/malam":"Sarapan / malam","tengah hari/malam":"Tengah hari / malam"},
        trH:"Cabaran 7 Hari", trSub:"Tak perlu sempurna. Tick apa yang anda buat hari tu, dan tengok tick bertambah.", name:"Nama", start:"Tarikh mula",
        waistH:"Ukur pinggang, bukan berat je", waistHow:"Pagi, sebelum makan, pita di paras pusat. Berat boleh naik turun sebab air. Pinggang lebih jujur.",
        habits:["Protein tiap hidangan","Air kosong 2-3 L","7,000 langkah","Tidur 7 jam","Tiada air manis"], sum:"Tick",
        h7H:"Siap 7 hari? Hantar result anda", h7P:"Isi ukuran pinggang dan tick anda, terus hantar ke coach di WhatsApp. Percuma.", h7Btn:"Hantar result Hari 7 →", h7Wa:"Hi Coach! Saya dah siap Kit Mula 7 Hari ✓\nPinggang hari 1: ___ cm\nPinggang hari 7: ___ cm\nTick: ___/35\nBoleh semak result saya?",
        cmpH:"PDF ni peta. Program penuh: coach teman anda sepanjang jalan.", cmpFree:"Percuma (kit ini)", cmpPaid:"Program dengan coach",
        cmp:[["Menu ikut kalori, sama untuk semua","Menu ikut badan, kerja dan makanan kegemaran anda"],["Semak sendiri","Coach semak progress anda setiap minggu"],["Minggu kenduri? Teka sendiri","Pelan diubah, bukan dibuang"],["Tiada pelan senaman","Workout 20 minit ikut tahap anda"],["Buat seorang diri","Group WhatsApp: kawan yang sama-sama berusaha"],["Makanan biasa sahaja","Makanan biasa + supplement, dah termasuk dalam harga"]],
        price:"Program dari <b>RM259</b> sebulan, termasuk supplement",
        ctaH:"Kalau 7 hari sendiri pun dah rasa beza…", cta:"…bayangkan kalau ada coach yang semak progress anda setiap minggu. Jawab kuiz 2 minit: result terus ke WhatsApp coach untuk consultation percuma. Result berbeza mengikut individu.", ctaBtn:"Jawab kuiz 2 minit →",
        note:"Anggaran sahaja, bukan nasihat perubatan. Result berbeza mengikut individu. Tidak sesuai untuk bawah 18 tahun, ibu mengandung atau menyusu, kurang berat badan, pernah ada eating disorder, atau penghidap diabetes, buah pinggang atau jantung: jumpa doktor dulu." },
  en: { kit:"Free 7-Day Starter Kit", title:"Fat-Loss Meal Plan", sub:"3-day menu · Eating out · 8 recipes · Grocery list + cost · 7-day challenge", kcal:"calories a day", pro:"protein a day", water:"water a day",
        plateH:"Healthy plate (every meal)", plate:["½ plate vegetables","¼ protein: chicken, fish, eggs, tofu, meat","¼ rice, bread or noodles"],
        rulesH:"5 simple rules", rules:["Protein at every meal.","Swap sweet drinks for plain or less sugar.","Grill, boil, steam or soup: less frying and santan.","Sleep 7 hours. Less sleep = more hunger.","Walk 7,000+ steps a day."],
        daysH:"3 sample days", day:"Day", meals:["Breakfast","Lunch","Snack","Dinner"], total:"Total",
        mix:"Swap meals between days, or with the recipes and eating-out picks in this kit, as long as the calories are about the same.",
        swapH:"Swap this, save calories", swaps:[["Teh tarik","Teh O kosong / less sugar","~100"],["Fried chicken","Grilled / roasted chicken","~100"],["Full plate of rice","Half the rice + more vegetables","~150"],["Mee goreng mamak","Mee hoon soup","~300"],["Sweet drink / soda","Plain water / lime, no sugar","~140"],["A bag of crisps","1 cup cut fruit","~100"]],
        shiftH:"Working shifts?", shift:"Eat by your waking hours, not the clock. Night shift: eat dinner before your shift, a small protein snack around 2am (eggs, yogurt), and a light breakfast before you sleep. Skip sweet midnight snacks and sleep in a dark room.",
        eoH:"Eating out? Pick these", eoSub:"Rough calories for one serving. You can lose fat eating out, as long as you pick well.", avoid:"Avoid", say:"Say:",
        eoRule:"At any stall: 1 protein (grilled, soup or steamed) + vegetables + half rice. Little gravy. Plain water.",
        rcH:"Cook at home: 8 easy recipes", rcH2:"4 more recipes",
        prepSub:"30 minutes on Sunday, eat well until Wednesday. This is what helps busy people most.", safeH:"Food safety:", famH:"Cooking for the family?", rcSub:"Under 20 minutes. Swap any meal in your menu for a recipe with about the same calories.", ing:"You need", how:"How",
        slot:{"sarapan":"Breakfast","tengah hari":"Lunch","malam":"Dinner","sarapan/malam":"Breakfast / dinner","tengah hari/malam":"Lunch / dinner"},
        trH:"7-Day Challenge", trSub:"It doesn't need to be perfect. Tick what you did each day and watch the ticks add up.", name:"Name", start:"Start date",
        waistH:"Measure your waist, not just weight", waistHow:"Morning, before eating, tape at belly-button level. Weight moves with water. Your waist is more honest.",
        habits:["Protein every meal","2-3 L plain water","7,000 steps","7 hours sleep","No sweet drinks"], sum:"Ticks",
        h7H:"Done 7 days? Send your result", h7P:"Fill in your waist and ticks and send them to a coach on WhatsApp. Free.", h7Btn:"Send my Day 7 result →", h7Wa:"Hi Coach! I finished the 7-Day Starter Kit ✓\nWaist day 1: ___ cm\nWaist day 7: ___ cm\nTicks: ___/35\nCan you check my result?",
        cmpH:"This PDF is the map. The full program walks it with you.", cmpFree:"Free (this kit)", cmpPaid:"Program with a coach",
        cmp:[["Menu by calories, same for everyone","Menu built around your body, work and favourite food"],["Check yourself","A coach checks your progress every week"],["Kenduri week? Guess on your own","The plan gets adjusted, not abandoned"],["No workout plan","20-minute workouts at your level"],["On your own","WhatsApp group: people working on it with you"],["Normal food only","Normal food + supplements, already in the price"]],
        price:"Programs from <b>RM259</b> a month, supplements included",
        ctaH:"If 7 days on your own already feels different…", cta:"…imagine having a coach checking in every week. Take the 2-minute quiz: your result goes straight to a coach on WhatsApp for a free consultation. Results vary.", ctaBtn:"Take the 2-minute quiz →",
        note:"Estimate only, not medical advice. Results vary. Not for under 18s, pregnant or breastfeeding mums, people who are underweight, have had an eating disorder, or have diabetes, kidney or heart problems: see your doctor first." },
};
if (process.env.BRAND) {
  for (const l of ["ms","en"]) { T[l].cmp.pop(); T[l].price = ""; }
  T.ms.cmp[1][1] = "Coach follow-up progress anda"; T.ms.cmp[4][1] = "Coaching berkumpulan: kawan yang sama-sama berusaha";
  T.en.cmp[1][1] = "A coach follows up on your progress"; T.en.cmp[4][1] = "Group coaching: people working on it with you";
  T.ms.cta = T.ms.cta.replace("coach yang semak progress anda setiap minggu", "coach yang follow-up anda");
  T.en.cta = T.en.cta.replace("a coach checking in every week", "a coach who follows up with you");
}
// weight-gain kit: overrides on top of T (claims follow the co-pilot's gain mode: 0.25-0.5 kg a week, red flags to a doctor)
const GT = {
  ms: { kit:"Kit Naik Berat · Percuma", title:"Meal Plan Naik Berat", sub:"Menu 3 hari · Tambah kalori sihat · 8 resipi · Meal prep · Cabaran 7 hari",
        plateH:"Pinggan naik berat (setiap hidangan)", plate:["⅓ sayur","⅓ protein: ayam, ikan, telur, daging, tauhu","⅓ nasi, roti atau mee, boleh tambah"],
        rules:["Makan 5 kali sehari: 3 hidangan + 2 snek.","Protein setiap kali makan.","Tambah kalori sihat: susu, telur, kacang, pisang, peanut butter.","Latihan kekuatan 3 kali seminggu: naik otot, bukan lemak je.","Tidur 7 jam. Badan bina otot masa tidur."],
        mix:"Boleh tukar hidangan antara hari, atau dengan resipi dalam kit ini, asalkan kalori lebih kurang sama.",
        swapH:"Tambah ini, kalori naik cara sihat", swaps:[["Susu penuh krim 1 gelas","Masa sarapan atau sebelum tidur","+160"],["Peanut butter 1 sudu besar","Atas roti, oat atau pisang","+95"],["Kacang 1 genggam (30g)","Snek petang","+170"],["Pisang 1 biji","Dalam smoothie atau oat","+105"],["Telur 1 biji","Tambah pada nasi atau mee","+75"],["Nasi tambah ½ cawan","Tengah hari atau malam","+100"]],
        shiftH:"Susah nak makan banyak?", shift:"Makan setiap 3 jam walaupun tak lapar. Dapatkan kalori dari minuman: susu atau smoothie lebih senang daripada sepinggan nasi lagi. Jangan minum air banyak sebelum makan. Guna pinggan lebih besar. Simpan snek dalam beg: kacang, kurma, roti peanut butter.",
        rcSub:"Bawah 20 minit. Untuk naik berat, makan dengan sepinggan nasi penuh atau tambah telur dan segelas susu.",
        waistH:"Timbang berat, seminggu sekali", waistHow:"Pagi, lepas ke tandas, sebelum makan. Sasaran sihat: naik 0.25-0.5 kg seminggu. Lebih laju selalunya lemak.", unit:"kg",
        habits:["5 kali makan","Protein tiap hidangan","Latihan ikut jadual","Tidur 7 jam","Susu / smoothie"],
        h7H:"Siap 7 hari? Hantar berat anda", h7P:"Hantar berat hari 1, hari 7 dan tick anda ke coach di WhatsApp. Percuma.", h7Btn:"WhatsApp coach →",
        h7Wa:"Hi Coach! Saya dah siap 7 hari pelan naik berat ✓\nBerat hari 1: ___ kg\nBerat hari 7: ___ kg\nTick: ___/35\nBoleh semak result saya?",
        cmp:[["Menu ikut kalori, sama untuk semua","Menu ikut badan, selera dan jadual anda"],["Timbang sendiri","Coach semak progress anda setiap minggu"],["Tiada pelan senaman","Latihan kekuatan ikut tahap anda"],["Buat seorang diri","Group WhatsApp: kawan yang sama-sama berusaha"],["Makanan biasa sahaja","Makanan biasa + supplement, dah termasuk dalam harga"]],
        ctaH:"Kalau 7 hari sendiri pun dah rasa beza…", cta:"…bayangkan kalau ada coach yang semak progress anda setiap minggu. Mula dengan body assessment percuma: coach tengok badan anda dan bina pelan naik berat. Result berbeza mengikut individu.", ctaBtn:"Body assessment percuma →",
        note:"Anggaran sahaja, bukan nasihat perubatan. Result berbeza mengikut individu. Tidak sesuai untuk bawah 18 tahun, ibu mengandung atau menyusu, BMI bawah 16, pernah ada eating disorder, atau penghidap diabetes, buah pinggang atau jantung. Berat turun tanpa sebab? Jumpa doktor dulu." },
  en: { kit:"Free Weight Gain Kit", title:"Weight Gain Meal Plan", sub:"3-day menu · Healthy calorie add-ons · 8 recipes · Meal prep · 7-day challenge",
        plateH:"Weight gain plate (every meal)", plate:["⅓ vegetables","⅓ protein: chicken, fish, eggs, meat, tofu","⅓ rice, bread or noodles (seconds OK)"],
        rules:["Eat 5 times a day: 3 meals + 2 snacks.","Protein at every meal.","Add healthy calories: milk, eggs, nuts, bananas, peanut butter.","Strength training 3 times a week: gain muscle, not just fat.","Sleep 7 hours. Your body builds muscle while you sleep."],
        mix:"Swap meals between days, or with the recipes in this kit, as long as the calories are about the same.",
        swapH:"Add these for healthy calories", swaps:[["1 glass full-cream milk","At breakfast or before bed","+160"],["1 tbsp peanut butter","On toast, oats or a banana","+95"],["A handful of nuts (30g)","Afternoon snack","+170"],["1 banana","In a smoothie or oats","+105"],["1 egg","Add to rice or noodles","+75"],["Extra ½ cup rice","Lunch or dinner","+100"]],
        shiftH:"Hard to eat more?", shift:"Eat every 3 hours, even if you're not hungry. Drink your calories: milk or a smoothie is easier than another plate of rice. Don't drink lots of water right before meals. Use a bigger plate. Keep snacks in your bag: nuts, dates, peanut butter toast.",
        rcSub:"Under 20 minutes. To gain, eat them with a full plate of rice or add eggs and a glass of milk.",
        waistH:"Weigh yourself once a week", waistHow:"Morning, after the toilet, before eating. Healthy pace: 0.25-0.5 kg a week. Faster is usually fat.", unit:"kg",
        habits:["5 meals","Protein every meal","Training as planned","7 hours sleep","Milk / smoothie"],
        h7H:"Done 7 days? Send your weight", h7P:"Send your day 1 and day 7 weight and your ticks to a coach on WhatsApp. Free.", h7Btn:"WhatsApp a coach →",
        h7Wa:"Hi Coach! I finished 7 days of the weight gain plan ✓\nWeight day 1: ___ kg\nWeight day 7: ___ kg\nTicks: ___/35\nCan you check my result?",
        cmp:[["Menu by calories, same for everyone","Menu built around your body, taste and schedule"],["Weigh yourself","A coach checks your progress every week"],["No workout plan","Strength training at your level"],["On your own","WhatsApp group: people working on it with you"],["Normal food only","Normal food + supplements, already in the price"]],
        ctaH:"If 7 days on your own already feels different…", cta:"…imagine having a coach checking in every week. Start with the free body assessment: a coach looks at your body and builds your weight gain plan. Results vary.", ctaBtn:"Free body assessment →",
        note:"Estimate only, not medical advice. Results vary. Not for under 18s, pregnant or breastfeeding mums, a BMI under 16, a past eating disorder, or diabetes, kidney or heart problems. Losing weight without trying? See a doctor first." },
};
const KIMI_WA = "60127040268", ASSESS = "https://www.wedotransformations.com/coach/3e08ee09-9e41-403c-b54a-67a6b1d8e86c";   // keep in sync with CONFIG in index.html
// Other coaches (e.g. Coach Mel) reuse this with env: BRAND, BRAND_SUB, SITE, OUT, and HARI7_WA (WhatsApp number for the Day 7 button
// when their page has no #hari7 check-in)
const SITE = process.env.SITE || "https://kimidullz.github.io/FITNESS-QUIZ/";
const BRAND = process.env.BRAND || "ARAMI", BRAND_SUB = process.env.BRAND_SUB || "Coach Kimi &amp; Coach Zara";
const link = (lang, hash) => process.env.SITE ? SITE : SITE + (lang==="en" ? "?lang=en" : "") + hash;
const hari7 = lang => process.env.HARI7_WA ? `https://wa.me/${process.env.HARI7_WA}?text=${encodeURIComponent(T[lang].h7Wa)}` : link(lang, "#hari7");
const proRange = (k, gain) => (gain ? {2000:"90-120",2500:"110-140",3000:"130-160"} : {1200:"80-100",1500:"90-110",1800:"100-120",2000:"100-125",2300:"115-135"})[k];   // keep in sync with the cap maps in index.html runCalc
const esc = s => String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;");
const enQty = s => s.replace(/ (ekor|biji)$/,"").replace(" keping"," slices").replace(" paket"," pack").replace(" buku"," loaf").replace(" sikat"," bunch").replace("minggu 1, ~RM5 lepas tu","week 1, ~RM5 after");
const fill = (s, o) => s.replace(/\{(\w+)\}/g, (_, x) => o[x]);
function html(k, lang, gain){
  const PAGES = gain ? 6 : 8, DAYS = (gain ? GTIERS : TIERS)[k];
  let pn = 1;
  const note = gain ? GT[lang].note : T[lang].note + (k===1200 ? (lang==="en" ? " This 1,200 kcal plan is for women; men should not go below 1,500 kcal a day." : " Pelan 1,200 kcal ini untuk wanita; lelaki jangan makan bawah 1,500 kcal sehari.") : "");
  const t = gain ? { ...T[lang], ...GT[lang] } : T[lang], g = G[lang], en = lang === "en", L = i => esc(FOOD[i][en?1:0]);
  const foot = () => `<div class="foot">${BRAND} · ${t.title} ~${k.toLocaleString()} kcal · ${++pn}/${PAGES}</div>`;
  const dayCard = (d, n) => { const [kc, p] = dayTotal(d); const rows = [[0,[d[0]]],[1,[d[1]]],[2,d[2]],[3,[d[3]]]];
    return `<div class="day"><div class="dh"><b>${t.day} ${n}</b><span>${t.total}: ~${kc.toLocaleString()} kcal · ${p} g protein</span></div>
    ${rows.map(([m,ids])=>`<div class="row"><i>${t.meals[m]}${m===2&&ids.length>1?" ×"+ids.length:""}</i><span>${ids.map(L).join(m===2?" · ":" + ")}</span><em>~${ids.reduce((a,i)=>a+FOOD[i][2],0)}</em></div>`).join("")}</div>`; };
  const eo = R.eatout.map(e => `<div class="eo"><h4>${esc(en?e.place_en:e.place_ms)}</h4>
    ${e.picks.map(p=>`<div class="pk"><span>${esc(en?p.en:p.ms)}</span><em>~${p.kcal}</em></div>`).join("")}
    <div class="av"><b>✗ ${t.avoid}:</b> ${esc(en?e.avoid_en:e.avoid_ms)}</div>
    <div class="say"><b>${t.say}</b> “${esc(en?e.say_en:e.say)}”</div></div>`).join("");
  const rc = rs => rs.map(r => `<div class="rc"><div class="rh"><h4>${esc(en?r.en:r.ms)}</h4>
    <span class="meta">${t.slot[r.slot]||r.slot} · ${r.time} · ~${r.kcal} kcal · ${r.protein} g protein</span></div>
    <div class="rb"><div><b>${t.ing}</b><ul>${(en?r.ing_en:r.ing_ms).map(x=>`<li>${esc(x)}</li>`).join("")}</ul></div>
    <div><b>${t.how}</b><ol>${(en?r.steps_en:r.steps_ms).map(x=>`<li>${esc(x)}</li>`).join("")}</ol></div></div></div>`).join("");
  const q = s => en ? enQty(s) : s;
  const gl = gain ? "" : G.groups.map(grp => { const rows = grp.rows.filter(r => r[2][k] !== "-");
    return rows.length ? `<tr class="gh"><td colspan="4">${esc(grp[lang])}</td></tr>` + rows.map(r =>
      `<tr><td><span class="bx"></span></td><td>${esc(r[en?1:0])}</td><td>${r[2][k]==="✓" ? "" : esc(q(r[2][k]))}</td><td>${esc(q(r[3]))}</td></tr>`).join("") : ""; }).join("");
  const tot = G.totals[k], out = G.eatOut[k];
  const box5 = `<td><span class="bx"></span></td>`.repeat(5);
  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
@page{size:A4;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Montserrat,sans-serif;color:#111;font-size:14px;line-height:1.45}
.page{width:210mm;height:297mm;padding:14mm 14mm 12mm;position:relative;overflow:hidden;page-break-after:always}
.page:last-child{page-break-after:auto}
.band{background:#0B0B0B;color:#fff;margin:-14mm -14mm 8mm;padding:11mm 14mm 9mm;position:relative}
.band:after{content:"";position:absolute;left:0;right:0;bottom:0;height:5px;background:linear-gradient(90deg,#E30613 0 65%,#FFD200 65%)}
.brand{font-family:Anton;font-size:18px;letter-spacing:.5px}.brand small{font-family:Montserrat;font-weight:700;font-size:11px;opacity:.7;margin-left:8px}
.kit{float:right;font-family:Montserrat;background:#FFD200;color:#0B0B0B;font-weight:800;font-size:11px;letter-spacing:.6px;text-transform:uppercase;padding:3px 8px;border-radius:4px}
h1{font-family:Anton;font-style:italic;text-transform:uppercase;font-size:44px;line-height:1;margin-top:6px}
h1 em{color:#FFD200;font-style:italic}
.sub{opacity:.85;font-weight:700;margin-top:6px;font-size:12.5px}
h2{font-family:Anton;font-style:italic;text-transform:uppercase;font-size:22px;margin:0 0 8px}
.lead{color:#5E5E5E;font-weight:500;margin:-4px 0 5mm}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:7mm}
.stat{background:#F4F4F2;border-radius:10px;padding:12px 14px;border-top:5px solid #0B0B0B}
.stat:nth-child(2){border-top-color:#FFD200}
.stat b{display:block;font-family:Anton;font-style:italic;font-size:30px;line-height:1.05}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10mm;margin-bottom:6mm}
.plate{display:flex;gap:14px;align-items:center}
.pie{width:120px;height:120px;border-radius:50%;flex:none;background:conic-gradient(#6BBF59 0 50%,#E30613 50% 75%,#FFD200 75% 100%);border:4px solid #0B0B0B}
.plate li{list-style:none;margin-bottom:6px;padding-left:16px;position:relative;font-weight:700}
.plate li:before{content:"";position:absolute;left:0;top:4px;width:10px;height:10px;border-radius:2px}
.plate li:nth-child(1):before{background:#6BBF59}.plate li:nth-child(2):before{background:#E30613}.plate li:nth-child(3):before{background:#FFD200}
ol{padding-left:18px}ol li{margin-bottom:5px;font-weight:500}
.day{border:2px solid #E3E3E0;border-radius:10px;margin-bottom:5mm;overflow:hidden;break-inside:avoid}
.dh{display:flex;justify-content:space-between;background:#0B0B0B;color:#fff;padding:7px 12px}
.dh b{font-family:Anton;font-style:italic;font-size:16px;letter-spacing:.5px}.dh span{font-weight:700;font-size:11.5px;align-self:center}
.row{display:grid;grid-template-columns:28mm 1fr 14mm;gap:8px;padding:7px 12px;border-top:1px solid #E3E3E0}
.row i{font-style:normal;font-weight:800;font-size:11px;text-transform:uppercase;letter-spacing:.4px}
.row em{font-style:normal;font-weight:700;text-align:right;color:#5E5E5E}
.mix{color:#5E5E5E;font-size:11.5px;margin-top:-2mm}
table{width:100%;border-collapse:collapse}
.sw{margin-bottom:7mm}
.sw td{padding:5px 8px;border-bottom:1px solid #E3E3E0}.sw td:last-child{text-align:right;font-weight:800;white-space:nowrap}
.sw td:nth-child(2){font-weight:700}.sw td:nth-child(2):before{content:"→ ";color:#5E5E5E}
.box{background:#F4F4F2;border-radius:10px;padding:12px 14px}
.prep{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:6mm}
.prep div{border-top:4px solid #FFD200;background:#F4F4F2;border-radius:8px;padding:10px 12px;font-size:13px;line-height:1.45}
.prep b{display:block;font-family:Anton;font-style:italic;font-size:18px;margin-bottom:3px}
.small{font-size:11.5px;color:#5E5E5E}
.eog{display:grid;grid-template-columns:1fr 1fr;gap:5mm}
.eo{border:2px solid #E3E3E0;border-radius:10px;overflow:hidden;font-size:12.5px;break-inside:avoid}
.eo h4,.rc h4{font-family:Anton;font-style:italic;font-weight:400;text-transform:uppercase;font-size:16px;letter-spacing:.3px}
.eo h4{background:#0B0B0B;color:#fff;padding:6px 10px}
.pk{display:flex;justify-content:space-between;gap:8px;padding:6px 10px;border-bottom:1px solid #E3E3E0;font-weight:600}
.pk em{font-style:normal;font-weight:800;white-space:nowrap}
.av{padding:6px 10px;color:#5E5E5E;font-size:11.5px}.av b{color:#C00010}
.say{background:#FFF4BF;margin:0 10px 9px;border-radius:8px;padding:6px 9px;font-weight:600;font-size:12px}
.rule{background:#0B0B0B;color:#fff;border-radius:10px;padding:10px 14px;font-weight:700;margin-top:5mm}
.rc{border:2px solid #E3E3E0;border-radius:10px;overflow:hidden;font-size:12px;line-height:1.38;margin-bottom:4mm;break-inside:avoid}
.rc .rh{display:flex;justify-content:space-between;align-items:baseline;gap:10px;padding:7px 12px;border-bottom:3px solid #FFD200;background:#F4F4F2}
.rc h4{font-size:18px}
.rc .meta{font-weight:800;font-size:10.5px;color:#5E5E5E;text-transform:uppercase;letter-spacing:.3px;white-space:nowrap}
.rc .rb{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:8px 12px 9px}
.rc .rb b{display:block;font-size:10.5px;text-transform:uppercase;letter-spacing:.4px;margin-bottom:3px}
.rc ul{list-style:none}.rc ul li{padding-left:12px;position:relative;margin-bottom:1px}.rc ul li:before{content:"•";position:absolute;left:0;font-weight:800}
.rc ol{padding-left:16px}.rc ol li{margin-bottom:2px;font-weight:500}
.gl{font-size:12px;margin-bottom:4mm}
.gl td{padding:2px 6px;border-bottom:1px solid #E3E3E0;vertical-align:top}
.gl td:nth-child(1){width:7mm}.gl td:nth-child(3){font-weight:800;white-space:nowrap}.gl td:nth-child(4){text-align:right;color:#5E5E5E;white-space:nowrap}
.gl tr.gh td{font-family:Anton;font-style:italic;text-transform:uppercase;font-size:14px;padding-top:8px;border-bottom:2px solid #0B0B0B}
.bx{display:inline-block;width:12px;height:12px;border:2px solid #0B0B0B;border-radius:3px;vertical-align:middle}
.cost{background:#0B0B0B;color:#fff;border-radius:10px;padding:12px 14px;margin-bottom:3mm}
.cost b{color:#FFD200}
.tips{font-size:13.5px}.tips li{margin-bottom:7px}
.meet{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:5mm}
.meet div{border-bottom:2px solid #0B0B0B;padding:14px 0 4px;font-weight:800;font-size:12px}
.waist{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:10px;align-items:end;margin-bottom:4mm}
.waist .w{border:2px solid #0B0B0B;border-radius:10px;padding:8px 10px;font-weight:800;font-size:12px}
.waist .w span{display:block;font-family:Anton;font-style:italic;font-size:22px;color:#BDBDBD}
.tr{font-size:12px;margin-bottom:5mm}
.tr th{font-size:10.5px;text-transform:uppercase;letter-spacing:.3px;padding:5px 4px;text-align:center;background:#0B0B0B;color:#fff;font-weight:800}
.tr th:first-child{text-align:left;padding-left:8px}
.tr td{text-align:center;padding:3px 4px;border-bottom:1px solid #E3E3E0}
.tr td:first-child{text-align:left;font-weight:800;padding-left:8px}
.tr td:last-child{color:#BDBDBD;font-weight:800}
.h7{display:flex;justify-content:space-between;align-items:center;gap:12px;border:2px dashed #0B0B0B;border-radius:12px;padding:9px 14px;margin-bottom:5mm}
.h7 b{font-family:Anton;font-style:italic;text-transform:uppercase;font-size:17px}
.h7 a,.cta a{background:#0B0B0B;color:#fff;text-decoration:none;font-weight:800;padding:10px 14px;border-radius:8px;white-space:nowrap;font-size:13px}
.cmp{font-size:12.5px;margin-bottom:5mm}
.cmp th{text-align:left;padding:7px 10px;font-size:11px;text-transform:uppercase;letter-spacing:.4px}
.cmp th:first-child{background:#F4F4F2}.cmp th:last-child{background:#FFD200}
.cmp td{padding:5px 10px;border-bottom:1px solid #E3E3E0;width:38%}.cmp td:last-child{width:62%}.cmp td:first-child{color:#5E5E5E}.cmp td:last-child{font-weight:700}
.cta{background:#E30613;color:#fff;border-radius:12px;padding:14px 16px;display:flex;justify-content:space-between;align-items:center;gap:14px}
.cta h3{font-family:Anton;font-style:italic;text-transform:uppercase;font-size:20px;line-height:1.1;margin-bottom:6px}
.cta p{font-size:13px}
.cta .price{margin-top:6px;font-weight:700}.cta .price b{color:#FFD200;font-size:16px}
.note{position:absolute;left:14mm;right:14mm;bottom:10mm;font-size:11px;color:#5E5E5E;border-top:1px solid #E3E3E0;padding-top:6px}
.foot{position:absolute;right:14mm;top:7mm;font-size:10.5px;color:#5E5E5E}
</style></head><body>
<div class="page">
  <div class="band"><div class="brand">${BRAND}<small>${BRAND_SUB}</small><span class="kit">${t.kit}</span></div>
  <h1>${t.title} <em>~${k.toLocaleString()} kcal</em></h1><div class="sub">${t.sub}</div></div>
  <div class="stats"><div class="stat"><b>~${k.toLocaleString()}</b>${t.kcal}</div><div class="stat"><b>${proRange(k, gain)} g</b>${t.pro}</div><div class="stat"><b>2-3 L</b>${t.water}</div></div>
  <div class="two"><div><h2>${t.plateH}</h2><div class="plate"><div class="pie"${gain ? ' style="background:conic-gradient(#6BBF59 0 34%,#E30613 34% 67%,#FFD200 67% 100%)"' : ""}></div><ul>${t.plate.map(x=>`<li>${x}</li>`).join("")}</ul></div></div>
  <div><h2>${t.rulesH}</h2><ol>${t.rules.map(x=>`<li>${x}</li>`).join("")}</ol></div></div>
  <h2>${t.daysH}</h2>
  ${dayCard(DAYS[0],1)}${dayCard(DAYS[1],2)}
  <div class="note">${note}</div>
</div>
<div class="page">${foot()}
  ${dayCard(DAYS[2],3)}<p class="mix">${t.mix}</p>
  <h2 style="margin-top:6mm">${t.swapH}</h2>
  <table class="sw">${t.swaps.map(([a,b,c])=>`<tr><td>${a}</td><td>${b}</td><td>${c} kcal</td></tr>`).join("")}</table>
  <div class="box"><h2>${t.shiftH}</h2><p>${t.shift}</p></div>
</div>
${gain ? "" : `<div class="page">${foot()}
  <h2 style="font-size:28px">${t.eoH}</h2><p class="lead">${t.eoSub}</p>
  <div class="eog">${eo}</div>
  <div class="rule">${t.eoRule}</div>
</div>`}
<div class="page">${foot()}
  <h2 style="font-size:28px">${t.rcH}</h2><p class="lead">${t.rcSub}</p>
  ${rc(R.recipes.slice(0,4))}
</div>
<div class="page">${foot()}
  <h2 style="font-size:28px">${t.rcH2}</h2>
  ${rc(R.recipes.slice(4))}
</div>
${gain ? "" : `<div class="page">${foot()}
  <h2 style="font-size:28px">${esc(g.h)}</h2><p class="lead">${esc(g.sub)}<br><b style="color:#111">${fill(g.qtyH,{k:k.toLocaleString()})}</b></p>
  <table class="gl">${gl}</table>
  <div class="cost"><b>${g.totalH}:</b> ${fill(g.totalLine,{dapur:tot.dapur,out:out.rm,sehari:tot.sehari})}<br><span style="opacity:.75;font-size:12px">${g.outH}: ${esc(out[lang])}</span></div>
  <p class="small">${esc(g.stock)} ${esc(g.priceNote)}</p>
</div>`}
<div class="page">${foot()}
  <h2 style="font-size:28px">${g.prepH}</h2><p class="lead">${t.prepSub}</p>
  <div class="prep">${g.prep.map(([a,b])=>`<div><b>${a}</b>${esc(b)}</div>`).join("")}</div>
  <div class="box" style="margin-bottom:8mm"><b>${t.safeH}</b> ${esc(g.safety.replace(/^[^:]+: /,""))}</div>
  <h2>${g.tipsH}</h2><ol class="tips">${g.tips.map(x=>`<li>${esc(x)}</li>`).join("")}</ol>
  <div class="box" style="margin-top:6mm"><b>${t.famH}</b> ${esc(g.family.replace(/^[^?]+\? /,""))}</div>
</div>
<div class="page">${foot()}
  <h2 style="font-size:30px">${t.trH}</h2><p class="lead">${t.trSub}</p>
  <div class="meet"><div>${t.name}:</div><div>${t.start}:</div></div>
  <div class="waist"><div><b>${t.waistH}</b><p class="small">${t.waistHow}</p></div><div class="w">${t.day} 1<span>____ ${t.unit || "cm"}</span></div><div class="w">${t.day} 7<span>____ ${t.unit || "cm"}</span></div></div>
  <table class="tr"><tr><th>${t.day}</th>${t.habits.map(h=>`<th>${h}</th>`).join("")}<th>${t.sum}</th></tr>
  ${[1,2,3,4,5,6,7].map(n=>`<tr><td>${t.day} ${n}</td>${box5}<td>/5</td></tr>`).join("")}</table>
  <div class="h7"><div><b>${t.h7H}</b><p class="small">${t.h7P}</p></div><a href="${gain ? `https://wa.me/${KIMI_WA}?text=${encodeURIComponent(t.h7Wa)}` : hari7(lang)}">${t.h7Btn}</a></div>
  <h2>${t.cmpH}</h2>
  <table class="cmp"><tr><th>${t.cmpFree}</th><th>${t.cmpPaid}</th></tr>${t.cmp.map(([a,b])=>`<tr><td>${a}</td><td>${b}</td></tr>`).join("")}</table>
  <div class="cta"><div><h3>${t.ctaH}</h3><p>${t.cta}</p>${t.price ? `<p class="price">${t.price}</p>` : ""}</div><a href="${gain ? ASSESS : link(lang,"#quiz-zone")}">${t.ctaBtn}</a></div>
  <div class="note">${note}</div>
</div></body></html>`;
}

(async () => {
  const out = process.env.OUT || path.join(__dirname, '..', 'pdf'); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(); const p = await b.newPage();
  const sets = [[TIERS, false], ...(process.env.BRAND ? [] : [[GTIERS, true]])];   // the weight-gain kit is Kimi's only for now
  for (const [tiers, gain] of sets) for (const k of Object.keys(tiers)) for (const lang of ['ms','en']) {
    await p.setContent(html(+k, lang, gain), { waitUntil: 'networkidle' });
    // every page must fit on its own A4 sheet
    const over = await p.$$eval('.page', ps => ps.map((el, i) => {
      const kids = [...el.children].filter(c => !c.matches('.note,.foot')), note = el.querySelector('.note');
      const limit = note ? note.getBoundingClientRect().top - 4 : el.getBoundingClientRect().bottom - 30;
      const d = Math.max(...kids.map(c => c.getBoundingClientRect().bottom)) - limit; return d > 0 ? `p${i + 1}+${Math.round(d)}px` : 0; }).filter(Boolean));
    if (over.length) throw new Error(`overflow ${gain ? "gain " : ""}${k} ${lang} pages ${over}`);
    await p.pdf({ path: path.join(out, `${gain ? "weight-gain" : "meal-plan"}-${k}-${lang}.pdf`), format: 'A4', printBackground: true });
    if ((gain ? k === '2500' : k === '1500') && process.argv[2]) await p.screenshot({ path: process.argv[2] + `/${gain ? "wg" : "mp"}-${lang}.png`, fullPage: true });
  }
  await b.close();
  console.log('ok', [...Object.entries(TIERS), ...Object.entries(GTIERS)].map(([k, ds]) => k + ':' + ds.map(d => dayTotal(d)[0]).join('/')).join(' '));
})();
