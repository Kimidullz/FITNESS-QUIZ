// Pelan Digital 14 Hari: data + generator (no DOM). Used by pelan14/index.html; node can require() it for tests.
// Food numbers are rough per-portion estimates (MyFCD/USDA style, rounded). Prices: rough Klang Valley estimates, late 2026, not quotes.
(function(){
"use strict";

// ---------- calories + protein (same formulas as the calculator in ../index.html) ----------
const tdee = (sex, age, cm, kg, act) => (10*kg + 6.25*cm - 5*age + (sex==="m" ? 5 : -161)) * [1.2,1.375,1.45,1.55,1.725][act];
const lossCal = (...a) => { const t = tdee(...a); return Math.max(a[0]==="m" ? 1500 : 1200, t - Math.min(500, t*0.2)); };
const gainCal = (...a) => { const t = tdee(...a); return t + Math.min(400, Math.max(250, t*0.12)); };
const GAIN_PROTEIN = [1.6,1.7,1.8,1.9,2.0];
const r5 = x => Math.round(x/5)*5, r50 = x => Math.round(x/50)*50;

// ---------- foods ----------
// id | slots (B breakfast, L lunch, D dinner, S snack, A add-on) | ms | en | kcal | protein g | RM | tier 1 jimat 2 sederhana 3 selesa
// | src h home / b bought | tags (c ayam, b daging lembu, f ikan, s udang/sotong, e telur, d susu/yogurt/keju, n kacang) | recipe | grocery | g = weight gain only
const F_RAW = [
// breakfast
["B01","B","Oat 40g + susu rendah lemak 200ml + pisang","40g oats + 200ml low-fat milk + banana",350,14,2.5,1,"h","d","overnight-oats","oat:40,susu:200,pisang:1"],
["B02","B","Roti wholemeal 2 keping + telur 2 biji + kopi O kosong","2 slices wholemeal bread + 2 eggs + black coffee",320,20,2.5,1,"h","e","","roti:2,telur:2"],
["B03","B","Roti canai kosong 1 + telur rebus 1 + teh O kosong","1 plain roti canai + 1 boiled egg + teh O kosong",375,12,4.5,1,"b","e"],
["B04","B","Nasi lemak separuh nasi + telur rebus, tanpa ayam goreng","Nasi lemak, half the rice + boiled egg, no fried chicken",400,13,4,1,"b","en"],
["B05","B","Thosai 2 keping + dhal","2 thosai + dhal",300,10,4,1,"b",""],
["B06","B","Mee hoon sup ayam 1 mangkuk","1 bowl chicken mee hoon soup",350,18,6,1,"b","c"],
["B07","BD","Telur dadar sayur + roti wholemeal 1 keping","Vegetable omelette + 1 slice wholemeal bread",370,24,3,1,"h","e","omelette","telur:3,roti:1,sayur:0.5"],
["B08","B","Bubur oat telur & ikan bilis","Savoury oats with egg & anchovies",300,17,2.5,1,"h","ef","savoury-oats","oat:40,telur:1,bilis:1,sayur:0.5"],
["B09","B","Ubi keledek rebus 1 biji + telur rebus 2 biji","1 boiled sweet potato + 2 boiled eggs",300,14,3,1,"h","e","","keledek:1,telur:2"],
["B10","B","Bihun goreng ½ pinggan + telur mata (minta kurang minyak)","½ plate fried bihun + fried egg (ask for less oil)",420,13,4.5,1,"b","e"],
["B11","B","Roti wholemeal 2 keping + sardin ½ tin kecil + timun","2 slices wholemeal bread + ½ small can sardines + cucumber",300,18,3,1,"h","f","sardin","roti:2,sardin:0.5"],
["B12","B","Pancake oat pisang","Banana oat pancakes",380,18,2.5,1,"h","e","oat-pancake","oat:40,pisang:1,telur:2"],
["B13","B","Chapati 2 keping + dhal","2 chapati + dhal",360,13,4,1,"b",""],
["B14","B","Roti wholemeal 2 keping + peanut butter 1 sudu besar + pisang","2 slices wholemeal bread + 1 tbsp peanut butter + banana",340,12,2,1,"h","n","","roti:2,pb:1,pisang:1"],
["B15","B","Yogurt Greek 170g + buah + granola 2 sudu besar","170g Greek yogurt + fruit + 2 tbsp granola",300,18,6,2,"h","d","","yogG:170,buah:1,granola:2"],
["B16","B","Sandwich telur & tuna (roti wholemeal)","Egg & tuna wholemeal sandwich",380,26,5,2,"h","ef","","roti:2,telur:1,tuna:0.5"],
["B17","B","Roti bakar (kaya sikit, tanpa mentega) + telur separuh masak 2 + kopi O kosong","Toast (a little kaya, no butter) + 2 half-boiled eggs + black coffee",330,18,6.5,2,"b","e"],
["B18","B","Smoothie pisang oat","Banana oat smoothie",380,17,4,2,"h","dn","smoothie","susu:250,pisang:1,oat:20,pb:1"],
["B19","B","Bubur ayam 1 mangkuk","1 bowl chicken porridge",350,18,7,2,"b","c"],
["B20","B","Roti wholemeal 2 keping + ½ avokado + telur 2 biji","2 slices wholemeal bread + ½ avocado + 2 eggs",450,20,9,3,"h","e","","roti:2,avo:0.5,telur:2"],
["B21","B","Overnight oats + chia + beri + yogurt Greek","Overnight oats with chia, berries & Greek yogurt",380,22,8,3,"h","d","overnight-oats","oat:40,susu:150,yogG:100,chia:1,beri:0.5"],
["B22","B","Brunch kafe: telur hancur 2 + roti sourdough 1 + salad, tanpa sos","Café brunch: 2 scrambled eggs + 1 sourdough toast + salad, no sauce",420,20,18,3,"b","ed"],
["B23","B","Yogurt Greek 200g + beri + badam 15g + chia","200g Greek yogurt + berries + 15g almonds + chia",360,24,10,3,"h","dn","","yogG:200,beri:0.5,kacang:15,chia:1"],
["B24","B","Roti canai 1 + telur 2 biji + teh tarik kurang manis","1 roti canai + 2 eggs + teh tarik less sugar",550,21,6,1,"b","ed"],
["B25","B","Oat 60g + susu rendah lemak + pisang + telur rebus 2 biji","60g oats + low-fat milk + banana + 2 boiled eggs",580,28,4.5,1,"h","de","","oat:60,susu:200,pisang:1,telur:2"],
["B26","B","Nasi lemak + telur rebus + ayam bakar","Nasi lemak + boiled egg + grilled chicken",700,36,9,1,"b","cen","","",1],
["B27","B","Oat 60g + susu penuh krim 250ml + pisang + peanut butter 1 sudu besar","60g oats + 250ml full-cream milk + banana + 1 tbsp peanut butter",590,21,4,1,"h","dn","","oat:60,susuF:250,pisang:1,pb:1",1],
["B28","B","Roti wholemeal 3 keping + telur hancur 3 biji + susu penuh krim 1 gelas","3 slices wholemeal toast + 3 scrambled eggs + 1 glass full-cream milk",670,39,5,1,"h","ed","","roti:3,telur:3,susuF:250",1],
["B29","B","Oat 60g + susu penuh krim 200ml + pisang + telur rebus 2 biji","60g oats + 200ml full-cream milk + banana + 2 boiled eggs",620,28,4.5,1,"h","de","","oat:60,susuF:200,pisang:1,telur:2",1],
// lunch / dinner
["L01","L","Nasi campur: nasi ½ cawan + ayam bakar + 2 sayur","Nasi campur: ½ cup rice + grilled chicken + 2 vegetables",450,33,8,1,"b","c"],
["L02","L","Nasi campur: nasi 1 cawan + ikan bakar/goreng kunyit + 2 sayur","Nasi campur: 1 cup rice + grilled or turmeric fish + 2 vegetables",500,30,8,1,"b","f"],
["L03","LD","Nasi 1 cawan + dada ayam 150g + salad","1 cup rice + 150g chicken breast + salad",530,40,5,1,"h","c","dada-ayam","beras:55,ayam:150,sayur:1"],
["L04","L","Nasi goreng kampung versi sihat","Healthier kampung fried rice",420,35,4,1,"h","cef","nasi-goreng","beras:40,ayam:80,telur:1,bilis:1,sayur:1"],
["L05","L","Yong tau foo sup 6 keping + mee hoon sikit","Yong tau foo soup, 6 pieces + a little mee hoon",400,22,9,1,"b","f"],
["L06","LD","Ayam kicap kurang manis + nasi ½ cawan + timun","Less-sweet soy sauce chicken + ½ cup rice + cucumber",430,38,5,1,"h","c","ayam-kicap","ayam:150,beras:28,sayur:0.5"],
["L07","LD","Ikan bakar sambal kurang minyak + nasi ½ cawan + ulam","Low-oil grilled fish with sambal + ½ cup rice + ulam",360,27,5,1,"h","f","ikan-bakar","ikan:1,beras:28,sayur:0.5"],
["L08","LD","Tauhu & tempe tumis sayur + nasi ½ cawan","Tofu & tempeh vegetable stir-fry + ½ cup rice",480,32,3.5,1,"h","","tauhu-tempe","tauhu:100,tempe:80,beras:28,sayur:1.5"],
["L09","LD","Sardin masak tomato + nasi ½ cawan + timun","Sardines in tomato + ½ cup rice + cucumber",390,26,3.5,1,"h","f","sardin","sardin:1,beras:28,sayur:0.5"],
["L10","LD","Asam pedas ikan + nasi ½ cawan","Asam pedas fish + ½ cup rice",380,32,5,1,"h","f","asam-ikan","ikanF:150,beras:28,sayur:0.5"],
["L11","LD","Ikan kukus halia + nasi ½ cawan + sayur","Ginger steamed fish + ½ cup rice + vegetables",340,32,5.5,1,"h","f","ikan-kukus","ikanF:150,beras:28,sayur:1"],
["L12","LD","Tauhu kukus telur + nasi ½ cawan + sayur","Steamed egg tofu + ½ cup rice + vegetables",380,22,3,1,"h","e","tauhu-kukus","tauhuL:150,telur:2,beras:28,sayur:1"],
["L13","LD","Kuey teow sup ayam / bebola ikan","Kuey teow soup with chicken or fish balls",420,22,7,1,"b","cf"],
["L14","L","Nasi ayam panggang (buang kulit) + sayur","Roasted chicken rice (skin off) + vegetables",600,33,8,1,"b","c"],
["L15","L","Nasi kerabu separuh nasi + ikan bakar + ulam, tanpa keropok","Nasi kerabu, half rice + grilled fish + ulam, no crackers",480,28,9,1,"b","f"],
["L16","LD","Sup bebola ikan + bihun sikit","Fish ball soup + a little bihun",350,22,5,1,"h","f","sup-bebola","bebola:8,bihun:40,sayur:1"],
["L17","LD","Sup sayur ayam + nasi ½ cawan","Chicken vegetable soup + ½ cup rice",390,33,4.5,1,"h","c","sup-ayam","ayam:120,kentang:0.5,sayur:1.5,beras:28"],
["L18","LD","Capati 1 + kari ayam (ambil isi, kuah sikit) + dhal","1 chapati + chicken curry (meat, little gravy) + dhal",450,28,8,1,"b","c"],
["L19","L","Wrap ayam","Chicken wrap",360,35,6,2,"h","cd","wrap","tortilla:1,ayam:120,yogG:30,sayur:1"],
["L20","LD","Nasi ½ cawan + daging masak kicap + sayur","½ cup rice + beef in soy sauce + vegetables",480,28,12,2,"b","b"],
["L21","LD","Tom yam campur kuah jernih + nasi ½ cawan","Clear tom yam campur + ½ cup rice",400,30,13,2,"b","fsc"],
["L22","LD","Udang tumis bawang putih & sayur + nasi ½ cawan","Garlic prawns & vegetables + ½ cup rice",330,33,10,2,"h","s","udang","udang:150,sayur:1,beras:28"],
["L23","LD","Daging tumis brokoli + nasi ½ cawan","Beef & broccoli stir-fry + ½ cup rice",360,34,10,2,"h","b","daging-brokoli","daging:120,sayur:1,beras:28"],
["L24","LD","Chicken chop bakar (tanpa kulit) + salad + kentang sikit","Grilled chicken chop (skin off) + salad + a little potato",550,40,16,2,"b","c"],
["L25","LD","Ikan bakar gerai + sayur + nasi ½ cawan","Grilled fish from a stall + vegetables + ½ cup rice",450,35,15,2,"b","f"],
["L26","LD","Spaghetti 1 cawan + sos daging tomato + salad","1 cup spaghetti + tomato meat sauce + salad",520,28,7,2,"h","b","","spag:80,daging:80,sayur:1"],
["L27","LD","Salmon panggang lemon + kentang + sayur","Lemon baked salmon + potato + vegetables",460,33,20,3,"h","f","salmon","salmon:150,kentang:1,sayur:1"],
["L28","L","Salad bowl kafe: nasi perang + salmon atau ayam + sayur","Café bowl: brown rice + salmon or chicken + vegetables",550,35,28,3,"b","fc"],
["L29","L","Sandwich 6 inci roti gandum + ayam panggang + sayur, sos rendah lemak","6-inch wheat sub + roast chicken + vegetables, low-fat sauce",380,26,17,3,"b","c"],
["L30","LD","Steak daging tanpa lemak 150g + kentang + salad","150g lean beef steak + potato + salad",560,42,35,3,"b","b"],
["L31","L","Set teriyaki ayam (nasi separuh) + sup miso + salad","Chicken teriyaki set (half rice) + miso soup + salad",550,35,22,3,"b","c"],
["L32","LD","Nasi perang ½ cawan + ayam panggang + salad avokado","½ cup brown rice + roast chicken + avocado salad",520,38,14,3,"h","c","dada-ayam","beras:28,ayam:150,avo:0.5,sayur:1"],
["L33","L","Nasi 1½ cawan + ayam bakar + 2 sayur + kuah sikit","1½ cups rice + grilled chicken + 2 veg + a little gravy",720,39,10,1,"b","c","","",1],
["L34","L","Nasi 1½ cawan + ikan bakar + telur dadar + sayur","1½ cups rice + grilled fish + omelette + vegetables",710,40,10,1,"b","fe","","",1],
["L35","L","Nasi 2 cawan + ayam bakar + 2 sayur + kuah sikit","2 cups rice + grilled chicken + 2 veg + a little gravy",820,41,11,1,"b","c","","",1],
["D01","D","Ikan kembung bakar + nasi ½ cawan + sayur","Grilled mackerel + ½ cup rice + vegetables",350,28,5,1,"h","f","ikan-bakar","ikan:1,beras:28,sayur:1"],
["D02","D","Telur dadar 2 biji + roti wholemeal 2 keping + salad","2-egg omelette + 2 slices wholemeal bread + salad",390,22,3,1,"h","e","omelette","telur:2,roti:2,sayur:1"],
["D03","D","Kentang 1 biji + dada ayam 150g + sayur","1 potato + 150g chicken breast + vegetables",480,41,6,1,"h","c","dada-ayam","kentang:1,ayam:150,sayur:1"],
["D04","D","Ayam bakar + sayur, tanpa nasi","Grilled chicken + vegetables, no rice",300,35,9,1,"b","c"],
["D05","D","Ubi keledek + ikan kukus halia + sayur","Sweet potato + ginger steamed fish + vegetables",400,31,6,1,"h","f","ikan-kukus","keledek:1,ikanF:150,sayur:1"],
["D06","D","Bubur nasi ayam (rumah)","Home-made chicken rice porridge",330,24,4,1,"h","c","","beras:35,ayam:100,sayur:0.5"],
["D07","D","Wantan mee sup (bukan kering)","Wantan mee soup (not dry)",420,22,8,1,"b","c"],
["D08","D","Sate ayam 10 cucuk + timun bawang, kuah sikit, tanpa nasi impit","10 chicken satay + cucumber & onion, a little sauce, no rice cakes",450,35,11,2,"b","cn"],
["D09","D","Salad ayam panggang + telur + dressing ringan","Grilled chicken salad + egg + light dressing",380,35,15,2,"b","ce"],
["D10","D","Salmon panggang lemon + sayur, tanpa kentang","Lemon baked salmon + vegetables, no potato",360,32,19,3,"h","f","salmon","salmon:150,sayur:1.5"],
["D11","D","Nasi 1½ cawan + daging masak kicap + sayur","1½ cups rice + beef in soy sauce + vegetables",660,38,14,1,"b","b","","",1],
["D12","D","Nasi 1 cawan + ayam masak merah + sayur + telur rebus","1 cup rice + ayam masak merah + vegetables + boiled egg",640,35,10,1,"b","ce","","",1],
["D13","D","Mee sup daging + telur rebus 1 biji","Beef noodle soup + 1 boiled egg",550,31,11,1,"b","be","","",1],
// snacks
["S01","S","Pisang + susu rendah lemak 1 gelas","Banana + 1 glass low-fat milk",190,9,2,1,"h","d","","pisang:1,susu:250"],
["S02","S","Yogurt Greek 150g + epal","150g Greek yogurt + apple",210,16,5,2,"h","d","","yogG:150,buah:1"],
["S03","S","Kacang tanah/badam 1 genggam (25g)","A handful of peanuts or almonds (25g)",150,6,1.5,1,"h","n","","kacang:25"],
["S04","S","Telur rebus 2 biji","2 boiled eggs",150,12,1.2,1,"h","e","","telur:2"],
["S05","S","Buah 1 cawan (betik, tembikai, jambu batu)","1 cup fruit (papaya, watermelon, guava)",80,1,2,1,"h","","","buah:1"],
["S06","S","Roti wholemeal 2 keping + peanut butter 1 sudu besar","2 slices wholemeal toast + 1 tbsp peanut butter",250,11,1.5,1,"h","n","","roti:2,pb:1"],
["S07","S","Susu soya kurang manis 1 kotak (250ml)","1 carton less-sweet soy milk (250ml)",100,7,2,1,"b",""],
["S08","S","Jagung rebus 1 tongkol","1 boiled corn on the cob",150,5,2.5,1,"b",""],
["S09","S","Tuna ½ tin + biskut krim crackers 3 keping","½ can tuna + 3 cream crackers",200,15,3,1,"h","f","","tuna:0.5"],
["S10","S","Yogurt tanpa gula 1 cawan kecil (140g)","1 small cup plain yogurt (140g)",90,5,2,1,"h","d","","yog:140"],
["S11","S","Edamame 1 cawan","1 cup edamame",190,17,5,2,"h","","","edamame:1"],
["S12","S","Kurma 3 biji + badam 10 biji","3 dates + 10 almonds",160,4,3,2,"h","n","","kurma:3,kacang:12"],
["S13","S","Yogurt Greek 150g + beri ½ cawan","150g Greek yogurt + ½ cup berries",170,15,8,3,"h","d","","yogG:150,beri:0.5"],
["S14","S","½ avokado + telur rebus 1 biji","½ avocado + 1 boiled egg",190,8,6,3,"h","e","","avo:0.5,telur:1"],
["S15","S","Hummus 3 sudu besar + timun & lobak","3 tbsp hummus + cucumber & carrot",150,5,6,3,"h","","","hummus:3,sayur:1"],
["S16","S","Smoothie: susu penuh krim + pisang + oat 30g + peanut butter","Smoothie: full-cream milk + banana + 30g oats + peanut butter",475,17,4,1,"h","dn","smoothie","susuF:250,pisang:1,oat:30,pb:1",1],
["S17","S","Kacang campur 40g + kurma 3 biji","40g mixed nuts + 3 dates",310,9,4,1,"h","n","","kacang:40,kurma:3",1],
["S18","S","Yogurt Greek 170g + granola 4 sudu besar + madu 1 sudu kecil","170g Greek yogurt + 4 tbsp granola + 1 tsp honey",290,20,7,2,"h","d","","yogG:170,granola:4",1],
["S19","S","Sandwich 2 telur & keju (roti wholemeal)","2-egg & cheese wholemeal sandwich",370,24,4,1,"h","ed","","roti:2,telur:2,keju:1",1],
["S20","S","Pisang + susu penuh krim 1 gelas","Banana + 1 glass full-cream milk",265,10,2,1,"h","d","","pisang:1,susuF:250",1],
// add-ons, attached to a meal
["A1","A","+ nasi ½ cawan","+ ½ cup rice",100,2,0.5,1,"h","","","beras:28"],
["A2","A","+ telur rebus 1 biji","+ 1 boiled egg",75,6,0.6,1,"h","e","","telur:1"],
["A3","A","+ susu rendah lemak 1 gelas","+ 1 glass low-fat milk",110,8,1.5,1,"h","d","","susu:250"],
["A4","A","+ buah 1 biji (pisang/epal)","+ 1 fruit (banana/apple)",80,1,1,1,"h","","","buah:1"],
["A5","A","+ peanut butter 1 sudu besar","+ 1 tbsp peanut butter",95,4,0.5,1,"h","n","","pb:1"],
["A6","A","+ susu penuh krim 1 gelas","+ 1 glass full-cream milk",160,8,1.5,1,"h","d","","susuF:250",1],
["A7","A","+ nasi 1 cawan","+ 1 cup rice",200,4,1,1,"h","","","beras:55",1],
];
const FOODS = F_RAW.map(r => ({ id:r[0], slots:r[1], ms:r[2], en:r[3], kcal:r[4], p:r[5], rm:r[6], tier:r[7], src:r[8], tags:r[9]||"", recipe:r[10]||"",
  groc:(r[11]||"").split(",").filter(Boolean).map(x => { const [k,q] = x.split(":"); return [k, +q]; }), gain:!!r[12] }));
const FOOD = Object.fromEntries(FOODS.map(f => [f.id, f]));
// add-ons go with these meals
const ADDON_TO = { A1:"LD", A2:"BLD", A3:"B", A4:"B", A5:"B", A6:"B", A7:"LD" };

// grocery units: [ms, en, unit ms, unit en, divide by, round step]
const GROC = {
  telur:["Telur","Eggs","biji","",1,1], roti:["Roti wholemeal","Wholemeal bread","keping","slices",1,1], oat:["Oat","Oats","g","g",1,50],
  susu:["Susu rendah lemak","Low-fat milk","L","L",1000,0.5], susuF:["Susu penuh krim","Full-cream milk","L","L",1000,0.5],
  yogG:["Yogurt Greek tanpa gula","Plain Greek yogurt","g","g",1,100], yog:["Yogurt tanpa gula","Plain yogurt","g","g",1,100],
  pisang:["Pisang","Bananas","biji","",1,1], buah:["Buah (epal, betik, jambu batu, tembikai)","Fruit (apple, papaya, guava, watermelon)","hidangan","servings",1,1],
  beri:["Beri (beku pun boleh)","Berries (frozen is fine)","cawan","cups",1,0.5], avo:["Avokado","Avocado","biji","",1,1],
  ayam:["Dada ayam","Chicken breast","g","g",1,100], ikan:["Ikan kembung / selar","Mackerel (kembung/selar)","ekor","",1,1],
  ikanF:["Isi ikan (siakap, tilapia, tenggiri)","Fish fillet (seabass, tilapia, mackerel)","g","g",1,50], salmon:["Salmon","Salmon","g","g",1,50],
  daging:["Daging lembu tanpa lemak","Lean beef","g","g",1,50], udang:["Udang","Prawns","g","g",1,50],
  sardin:["Sardin tin kecil (155g)","Small can sardines (155g)","tin","cans",1,1], tuna:["Tuna dalam air (tin)","Tuna in water (can)","tin","cans",1,1],
  tauhu:["Tauhu keras","Firm tofu","g","g",1,100], tauhuL:["Tauhu sutera / tauhu telur","Silken or egg tofu","batang","tubes",150,1], tempe:["Tempe","Tempeh","g","g",1,100],
  bebola:["Bebola ikan","Fish balls","biji","",1,1], bihun:["Bihun","Rice vermicelli","g","g",1,50], beras:["Beras (mentah)","Rice (uncooked)","g","g",1,100],
  sayur:["Sayur campur (sawi, kangkung, kubis, brokoli, lobak, timun, tomato)","Mixed vegetables (greens, cabbage, broccoli, carrot, cucumber, tomato)","cawan","cups",1,1],
  kentang:["Kentang","Potatoes","biji","",1,1], keledek:["Ubi keledek","Sweet potatoes","biji","",1,1], spag:["Spaghetti","Spaghetti","g","g",1,100],
  tortilla:["Tortilla wrap","Tortilla wraps","keping","",1,1], kacang:["Kacang tanah / badam","Peanuts or almonds","g","g",1,25],
  pb:["Peanut butter","Peanut butter","sudu besar","tbsp",1,1], granola:["Granola tanpa gula tambahan","Granola, no added sugar","sudu besar","tbsp",1,1],
  chia:["Biji chia","Chia seeds","sudu besar","tbsp",1,1], bilis:["Ikan bilis","Anchovies","sudu besar","tbsp",1,1],
  kurma:["Kurma","Dates","biji","",1,1], keju:["Keju slice","Cheese slices","keping","slices",1,1], hummus:["Hummus","Hummus","sudu besar","tbsp",1,1],
  edamame:["Edamame beku","Frozen edamame","cawan","cups",1,1],
};

// ---------- recipes (first 8 copied from mealplan/recipes.json) ----------
const RECIPES = {
"overnight-oats":{ms:"Overnight oats pisang",en:"Banana overnight oats",time:"5 min",kcal:350,p:20,
 ing_ms:["Oat 40g (½ cawan)","Susu rendah lemak 150ml","Yogurt Greek tanpa gula 100g (½ cawan)","Pisang ½ biji, hiris","Kayu manis serbuk secubit (pilihan)"],
 ing_en:["40g oats (½ cup)","150ml low-fat milk","100g plain Greek yogurt (½ cup)","½ banana, sliced","A pinch of cinnamon (optional)"],
 st_ms:["Masukkan oat, susu dan yogurt dalam balang bertutup. Kacau rata.","Simpan dalam peti sejuk semalaman (sekurang-kurangnya 4 jam).","Pagi esok, tambah pisang dan kayu manis. Makan sejuk."],
 st_en:["Put oats, milk and yogurt in a lidded jar. Stir well.","Refrigerate overnight (at least 4 hours).","In the morning, top with banana and cinnamon. Eat cold."]},
"omelette":{ms:"Telur dadar sayur",en:"Vegetable omelette",time:"10 min",kcal:370,p:24,
 ing_ms:["Telur 3 biji","Bawang besar ¼ biji + tomato ½ biji, potong kecil","Sawi atau kubis ½ cawan, hiris halus","Cili merah ½ biji + daun bawang (pilihan)","Minyak 1 sudu kecil, garam & lada sulah","Roti wholemeal 1 keping"],
 ing_en:["3 eggs","¼ onion + ½ tomato, finely chopped","½ cup mustard greens or cabbage, finely sliced","½ red chilli + spring onion (optional)","1 tsp oil, salt & white pepper","1 slice wholemeal bread"],
 st_ms:["Pukul telur dengan garam dan lada. Masukkan semua sayur.","Panaskan minyak dalam kuali tidak melekat, api sederhana. Tuang telur.","Masak 2-3 minit setiap belah sampai masak. Makan dengan roti."],
 st_en:["Beat the eggs with salt and pepper. Add all the vegetables.","Heat the oil in a non-stick pan on medium. Pour in the eggs.","Cook 2-3 minutes each side until set. Eat with the bread."]},
"nasi-goreng":{ms:"Nasi goreng kampung versi sihat",en:"Healthier kampung fried rice",time:"15 min",kcal:420,p:35,
 ing_ms:["Nasi sejuk ¾ cawan (nasi semalam pun boleh)","Dada ayam 80g, potong kecil","Telur 1 biji","Kangkung atau sawi 1 cawan, potong","Ikan bilis 1 sudu besar + bawang merah 2 biji + bawang putih 1 ulas + cili padi 2 biji","Kicap masin 1 sudu kecil, minyak 1 sudu kecil"],
 ing_en:["¾ cup cold rice (yesterday's rice is fine)","80g chicken breast, diced","1 egg","1 cup water spinach or mustard greens, cut","1 tbsp anchovies + 2 shallots + 1 garlic clove + 2 bird's eye chillies","1 tsp light soy sauce, 1 tsp oil"],
 st_ms:["Tumbuk bawang, cili dan ikan bilis. Tumis dengan minyak sampai wangi.","Masukkan ayam, masak sampai putih. Pecahkan telur, kacau.","Masukkan nasi, sayur dan kicap. Goreng 3 minit."],
 st_en:["Pound the shallots, garlic, chillies and anchovies. Fry in the oil until fragrant.","Add the chicken and cook until white. Crack in the egg and stir.","Add the rice, greens and soy sauce. Fry for 3 minutes."]},
"wrap":{ms:"Wrap ayam",en:"Chicken wrap",time:"15 min",kcal:360,p:35,
 ing_ms:["Tortilla 1 keping (8 inci), gandum penuh jika ada","Dada ayam 120g, hiris nipis","Serbuk cili ½ sudu kecil, lada hitam, garam","Minyak ½ sudu kecil","Daun salad 1 cawan + timun & tomato, hiris","Sos: yogurt Greek 2 sudu besar + sos cili 1 sudu kecil"],
 ing_en:["1 tortilla (8 inch), wholemeal if you can","120g chicken breast, thinly sliced","½ tsp chilli powder, black pepper, salt","½ tsp oil","1 cup lettuce + sliced cucumber & tomato","Sauce: 2 tbsp Greek yogurt + 1 tsp chilli sauce"],
 st_ms:["Gaul ayam dengan serbuk cili, lada dan garam.","Masak dalam kuali dengan minyak 5-6 minit sampai masak.","Panaskan tortilla, sapu sos, isi salad dan ayam, gulung."],
 st_en:["Toss the chicken with chilli powder, pepper and salt.","Cook in a pan with the oil for 5-6 minutes until done.","Warm the tortilla, spread the sauce, fill with salad and chicken, roll up."]},
"ayam-kicap":{ms:"Ayam kicap kurang manis (air fryer)",en:"Less-sweet soy sauce chicken (air fryer)",time:"20 min",kcal:430,p:38,
 ing_ms:["Dada ayam 150g, potong dadu","Kicap masin 1 sudu besar + kicap manis 1 sudu besar","Bawang putih 2 ulas, cincang","Bawang besar ½ biji, hiris","Minyak 1 sudu kecil, lada hitam secubit","Nasi ½ cawan + timun"],
 ing_en:["150g chicken breast, cubed","1 tbsp light soy sauce + 1 tbsp sweet soy sauce","2 garlic cloves, minced","½ onion, sliced","1 tsp oil, a pinch of black pepper","½ cup rice + cucumber"],
 st_ms:["Perap ayam dengan kicap, bawang putih dan lada 10 minit.","Air fryer 180°C, 12-14 minit, goncang separuh jalan.","Tumis bawang besar sekejap, gaul dengan ayam. Makan dengan nasi."],
 st_en:["Marinate the chicken in soy sauce, garlic and pepper for 10 minutes.","Air fry at 180°C for 12-14 minutes, shake halfway.","Quickly fry the onion, toss with the chicken. Serve with rice."]},
"ikan-bakar":{ms:"Ikan bakar sambal kurang minyak",en:"Low-oil grilled fish with sambal",time:"20 min",kcal:360,p:27,
 ing_ms:["Ikan kembung atau selar 1 ekor sederhana (~180g)","Kunyit serbuk ½ sudu kecil + garam secubit","Cili kisar 1 sudu besar","Bawang merah 3 biji + bawang putih 1 ulas, kisar","Air asam jawa 2 sudu besar, gula ½ sudu kecil","Minyak 1 sudu kecil","Nasi ½ cawan + ulam atau timun"],
 ing_en:["1 medium mackerel or scad (~180g)","½ tsp turmeric + a pinch of salt","1 tbsp blended chilli","3 shallots + 1 garlic clove, blended","2 tbsp tamarind water, ½ tsp sugar","1 tsp oil","½ cup rice + ulam or cucumber"],
 st_ms:["Lumur ikan dengan kunyit dan garam. Bakar dalam oven/air fryer 200°C, 15 minit.","Tumis cili dan bawang dengan minyak sampai garing, masukkan air asam dan gula.","Sapu sambal atas ikan. Makan dengan nasi dan ulam."],
 st_en:["Rub the fish with turmeric and salt. Bake or air fry at 200°C for 15 minutes.","Fry the chilli and shallots in the oil until cooked, add tamarind and sugar.","Spread the sambal on the fish. Serve with rice and ulam."]},
"sup-ayam":{ms:"Sup sayur ayam",en:"Chicken vegetable soup",time:"20 min",kcal:290,p:31,
 ing_ms:["Dada ayam 120g, hiris nipis","Kentang ½ biji + lobak merah ½ batang, potong dadu","Kubis 1 cawan, hiris","Bawang merah 3 biji + bawang putih 2 ulas + halia 1 inci, ketuk","Rempah sup 1 sudu kecil","Air 2 cawan, garam & lada sulah","Daun sup & daun bawang"],
 ing_en:["120g chicken breast, thinly sliced","½ potato + ½ carrot, diced","1 cup cabbage, sliced","3 shallots + 2 garlic cloves + 1 inch ginger, bruised","1 tsp soup spice","2 cups water, salt & white pepper","Celery leaves & spring onion"],
 st_ms:["Rebus air dengan bawang, halia dan rempah sup.","Masukkan ayam, kentang dan lobak. Masak 10 minit.","Masukkan kubis, garam dan lada. Masak 3 minit, tabur daun sup."],
 st_en:["Boil the water with shallots, garlic, ginger and soup spice.","Add the chicken, potato and carrot. Cook 10 minutes.","Add the cabbage, salt and pepper. Cook 3 minutes, top with the leaves."]},
"tauhu-tempe":{ms:"Tauhu & tempe tumis sayur",en:"Tofu & tempeh vegetable stir-fry",time:"20 min",kcal:380,p:30,
 ing_ms:["Tauhu keras 100g, potong dadu","Tempe 80g, potong nipis","Sayur campur 1½ cawan (kacang buncis, lobak merah, sawi)","Bawang putih 2 ulas + cili merah 1 biji, hiris","Sos tiram 1 sudu besar + kicap masin 1 sudu kecil + air 3 sudu besar","Minyak 1 sudu kecil"],
 ing_en:["100g firm tofu, cubed","80g tempeh, thinly sliced","1½ cups mixed vegetables (green beans, carrot, mustard greens)","2 garlic cloves + 1 red chilli, sliced","1 tbsp oyster sauce + 1 tsp light soy sauce + 3 tbsp water","1 tsp oil"],
 st_ms:["Bakar tauhu dan tempe dalam air fryer 200°C, 10 minit (atau pan tanpa minyak).","Tumis bawang putih dan cili dengan minyak. Masukkan sayur dan sos.","Masukkan tauhu dan tempe, gaul 2 minit."],
 st_en:["Air fry the tofu and tempeh at 200°C for 10 minutes (or dry-pan).","Fry the garlic and chilli in the oil. Add the vegetables and sauce.","Add the tofu and tempeh, toss for 2 minutes."]},
"savoury-oats":{ms:"Bubur oat telur & ikan bilis",en:"Savoury oats with egg & anchovies",time:"10 min",kcal:300,p:17,
 ing_ms:["Oat 40g (½ cawan)","Air 1½ cawan","Telur 1 biji","Ikan bilis 1 sudu besar, basuh","Sawi atau bayam ½ cawan, potong","Bawang putih 1 ulas, lada sulah, minyak ½ sudu kecil"],
 ing_en:["40g oats (½ cup)","1½ cups water","1 egg","1 tbsp anchovies, rinsed","½ cup greens or spinach, cut","1 garlic clove, white pepper, ½ tsp oil"],
 st_ms:["Tumis bawang putih dan ikan bilis dengan minyak sekejap.","Masukkan air dan oat, masak 4-5 minit sambil kacau.","Masukkan sayur, pecahkan telur dan kacau sampai masak. Tabur lada."],
 st_en:["Briefly fry the garlic and anchovies in the oil.","Add water and oats, cook 4-5 minutes, stirring.","Add the greens, crack in the egg and stir until cooked. Add pepper."]},
"oat-pancake":{ms:"Pancake oat pisang",en:"Banana oat pancakes",time:"15 min",kcal:380,p:18,
 ing_ms:["Oat 40g (kisar jadi tepung)","Pisang 1 biji, lenyek","Telur 2 biji","Kayu manis secubit (pilihan)","Minyak ½ sudu kecil untuk pan"],
 ing_en:["40g oats (blend into flour)","1 banana, mashed","2 eggs","A pinch of cinnamon (optional)","½ tsp oil for the pan"],
 st_ms:["Gaul oat, pisang dan telur jadi adunan.","Panaskan pan tidak melekat, api perlahan. Tuang 2 sudu besar adunan setiap satu.","Masak 2 minit setiap belah. Dapat 4-5 keping."],
 st_en:["Mix the oats, banana and eggs into a batter.","Heat a non-stick pan on low. Pour 2 tbsp of batter per pancake.","Cook 2 minutes each side. Makes 4-5."]},
"sardin":{ms:"Sardin masak tomato",en:"Sardines in tomato",time:"10 min",kcal:390,p:26,
 ing_ms:["Sardin tin kecil 1 tin (155g)","Bawang besar ½ biji, hiris","Cili merah 1 biji, hiris","Perahan limau nipis","Minyak 1 sudu kecil","Nasi ½ cawan + timun"],
 ing_en:["1 small can sardines (155g)","½ onion, sliced","1 red chilli, sliced","A squeeze of lime","1 tsp oil","½ cup rice + cucumber"],
 st_ms:["Tumis bawang dan cili dengan minyak sampai layu.","Masukkan sardin dengan sosnya, pecahkan sikit. Masak 3 minit.","Perah limau. Makan dengan nasi atau roti wholemeal."],
 st_en:["Fry the onion and chilli in the oil until soft.","Add the sardines with their sauce, break them up a little. Cook 3 minutes.","Add the lime. Eat with rice or wholemeal bread."]},
"ikan-kukus":{ms:"Ikan kukus halia",en:"Ginger steamed fish",time:"20 min",kcal:340,p:32,
 ing_ms:["Isi ikan siakap atau tilapia 150g","Halia 2 inci, hiris halus","Kicap masin 1 sudu besar + air 2 sudu besar","Minyak bijan 1 sudu kecil","Daun bawang & ketumbar","Nasi ½ cawan + sayur rebus"],
 ing_en:["150g seabass or tilapia fillet","2 inches ginger, finely sliced","1 tbsp light soy sauce + 2 tbsp water","1 tsp sesame oil","Spring onion & coriander","½ cup rice + boiled vegetables"],
 st_ms:["Letak ikan atas pinggan, tabur halia.","Kukus 10-12 minit sampai isi putih.","Siram kicap, air dan minyak bijan. Tabur daun bawang."],
 st_en:["Put the fish on a plate, top with ginger.","Steam 10-12 minutes until the flesh is white.","Pour over the soy sauce, water and sesame oil. Top with spring onion."]},
"tauhu-kukus":{ms:"Tauhu kukus telur",en:"Steamed egg tofu",time:"15 min",kcal:380,p:22,
 ing_ms:["Tauhu sutera atau tauhu telur 1 batang (150g)","Telur 2 biji","Sos tiram 1 sudu besar + kicap masin 1 sudu kecil","Bawang putih goreng 1 sudu kecil (dengan minyaknya)","Daun bawang","Nasi ½ cawan + sayur"],
 ing_en:["1 tube silken or egg tofu (150g)","2 eggs","1 tbsp oyster sauce + 1 tsp light soy sauce","1 tsp fried garlic (with its oil)","Spring onion","½ cup rice + vegetables"],
 st_ms:["Hiris tauhu, susun dalam mangkuk. Pukul telur dengan sedikit air, tuang atas tauhu.","Kukus 10 minit, api sederhana.","Siram sos, tabur bawang putih goreng dan daun bawang."],
 st_en:["Slice the tofu into a bowl. Beat the eggs with a little water, pour over.","Steam 10 minutes on medium heat.","Pour over the sauce, top with fried garlic and spring onion."]},
"asam-ikan":{ms:"Asam pedas ikan",en:"Asam pedas fish",time:"25 min",kcal:380,p:32,
 ing_ms:["Ikan tenggiri atau pari 150g","Cili kisar 1 sudu besar + bawang merah 3 biji + bawang putih 1 ulas, kisar","Asam keping 2 atau air asam jawa ¼ cawan","Bendi 4 batang + tomato 1 biji","Daun kesum, garam, minyak 1 sudu kecil","Nasi ½ cawan"],
 ing_en:["150g mackerel or stingray","1 tbsp blended chilli + 3 shallots + 1 garlic clove, blended","2 pieces asam keping or ¼ cup tamarind water","4 okra + 1 tomato","Vietnamese mint, salt, 1 tsp oil","½ cup rice"],
 st_ms:["Tumis bahan kisar dengan minyak sampai garing.","Masukkan 1½ cawan air, asam, garam dan daun kesum. Didihkan.","Masukkan ikan, bendi dan tomato. Masak 8-10 minit."],
 st_en:["Fry the blended paste in the oil until cooked.","Add 1½ cups water, tamarind, salt and mint. Bring to the boil.","Add the fish, okra and tomato. Cook 8-10 minutes."]},
"salmon":{ms:"Salmon panggang lemon",en:"Lemon baked salmon",time:"20 min",kcal:460,p:33,
 ing_ms:["Salmon 150g","Lemon ½ biji, perah + hiris","Bawang putih 1 ulas, lada hitam, garam","Brokoli & lobak merah 1 cawan","Kentang 1 biji kecil (pilihan)"],
 ing_en:["150g salmon","½ lemon, squeezed + sliced","1 garlic clove, black pepper, salt","1 cup broccoli & carrot","1 small potato (optional)"],
 st_ms:["Perap salmon dengan lemon, bawang putih, lada dan garam 10 minit.","Bakar dalam oven/air fryer 200°C, 10-12 minit bersama sayur dan kentang.","Tanpa kentang: ~360 kcal."],
 st_en:["Marinate the salmon with lemon, garlic, pepper and salt for 10 minutes.","Bake or air fry at 200°C for 10-12 minutes with the vegetables and potato.","Without the potato: ~360 kcal."]},
"daging-brokoli":{ms:"Daging tumis brokoli",en:"Beef & broccoli stir-fry",time:"15 min",kcal:360,p:34,
 ing_ms:["Daging lembu tanpa lemak 120g, hiris nipis","Brokoli 1 cawan","Sos tiram 1 sudu besar + kicap masin 1 sudu kecil","Bawang putih 2 ulas + halia sedikit","Minyak 1 sudu kecil","Nasi ½ cawan"],
 ing_en:["120g lean beef, thinly sliced","1 cup broccoli","1 tbsp oyster sauce + 1 tsp light soy sauce","2 garlic cloves + a little ginger","1 tsp oil","½ cup rice"],
 st_ms:["Celur brokoli 1 minit.","Tumis bawang putih dan halia, masukkan daging. Masak 2-3 minit api besar.","Masukkan brokoli dan sos, gaul 1 minit."],
 st_en:["Blanch the broccoli for 1 minute.","Fry the garlic and ginger, add the beef. Cook 2-3 minutes on high.","Add the broccoli and sauce, toss for 1 minute."]},
"udang":{ms:"Udang tumis bawang putih & sayur",en:"Garlic prawns & vegetables",time:"15 min",kcal:330,p:33,
 ing_ms:["Udang 150g, buang kulit","Sayur campur 1 cawan (kacang buncis, lobak, cendawan)","Bawang putih 3 ulas, cincang","Cili padi 1 biji (pilihan), garam, lada","Minyak 1 sudu kecil","Nasi ½ cawan"],
 ing_en:["150g prawns, peeled","1 cup mixed vegetables (green beans, carrot, mushroom)","3 garlic cloves, minced","1 bird's eye chilli (optional), salt, pepper","1 tsp oil","½ cup rice"],
 st_ms:["Tumis bawang putih dengan minyak sampai wangi.","Masukkan udang, masak 2 minit sampai merah.","Masukkan sayur, garam dan lada. Masak 2 minit."],
 st_en:["Fry the garlic in the oil until fragrant.","Add the prawns, cook 2 minutes until pink.","Add the vegetables, salt and pepper. Cook 2 minutes."]},
"dada-ayam":{ms:"Dada ayam perap (air fryer / pan)",en:"Marinated chicken breast (air fryer or pan)",time:"20 min",kcal:220,p:34,
 ing_ms:["Dada ayam 150g, nipiskan","Kunyit ½ sudu kecil + serbuk cili ½ sudu kecil","Lada hitam, garam, perahan limau","Minyak 1 sudu kecil","Hidang dengan nasi/kentang dan salad ikut menu"],
 ing_en:["150g chicken breast, flattened","½ tsp turmeric + ½ tsp chilli powder","Black pepper, salt, a squeeze of lime","1 tsp oil","Serve with rice or potato and salad as in your menu"],
 st_ms:["Perap ayam 15 minit (atau semalaman).","Air fryer 190°C, 14-16 minit, atau pan 5-6 minit setiap belah.","Rehatkan 2 minit sebelum potong. Masak 3-4 keping sekali untuk 2-3 hari."],
 st_en:["Marinate the chicken for 15 minutes (or overnight).","Air fry at 190°C for 14-16 minutes, or pan-fry 5-6 minutes each side.","Rest 2 minutes before slicing. Cook 3-4 at once for 2-3 days."]},
"sup-bebola":{ms:"Sup bebola ikan & bihun",en:"Fish ball & bihun soup",time:"15 min",kcal:350,p:22,
 ing_ms:["Bebola ikan 8 biji","Bihun 40g (kering), rendam","Sawi 1 cawan","Bawang putih 2 ulas, goreng dengan minyak 1 sudu kecil","Air 2 cawan, garam, lada sulah, daun bawang"],
 ing_en:["8 fish balls","40g dry bihun, soaked","1 cup mustard greens","2 garlic cloves, fried in 1 tsp oil","2 cups water, salt, white pepper, spring onion"],
 st_ms:["Didihkan air dengan garam dan lada.","Masukkan bebola ikan, masak 5 minit sampai terapung.","Masukkan bihun dan sawi 2 minit. Tabur bawang putih goreng."],
 st_en:["Boil the water with salt and pepper.","Add the fish balls, cook 5 minutes until they float.","Add bihun and greens for 2 minutes. Top with fried garlic."]},
"smoothie":{ms:"Smoothie pisang oat",en:"Banana oat smoothie",time:"5 min",kcal:380,p:17,
 ing_ms:["Susu rendah lemak 250ml (naik berat: susu penuh krim)","Pisang 1 biji (beku lagi sedap)","Oat 20g","Peanut butter 1 sudu besar","Ais sikit"],
 ing_en:["250ml low-fat milk (weight gain: full-cream milk)","1 banana (frozen is nicer)","20g oats","1 tbsp peanut butter","A little ice"],
 st_ms:["Masukkan semua dalam blender.","Kisar 30-40 saat sampai licin.","Minum terus. Naik berat: tambah oat jadi 30g."],
 st_en:["Put everything in a blender.","Blend 30-40 seconds until smooth.","Drink straight away. Weight gain: use 30g oats."]},
};

// ---------- 14 topics, alternating Makan / Gerak / Minda ----------
const TOPICS = [
{k:"makan", ms:{t:"Pinggan sihat",p:["Separuh pinggan sayur, suku protein (ayam, ikan, telur, tauhu), suku karbo (nasi, roti, ubi).","Protein satu tapak tangan, nasi satu genggam penumbuk.","Tak perlu buang nasi. Cuma susun semula pinggan."],a:"Ambil gambar pinggan makan tengah hari. Betul ke separuh sayur?"},
 en:{t:"The healthy plate",p:["Half the plate vegetables, a quarter protein (chicken, fish, egg, tofu), a quarter carbs (rice, bread, sweet potato).","Protein the size of your palm, rice the size of your fist.","You don't have to drop rice. Just rearrange the plate."],a:"Snap a photo of your lunch plate. Is half of it vegetables?"},
 gms:{t:"Pinggan naik berat",p:["Suku protein, suku hingga separuh karbo, sayur sikit sahaja supaya perut tak cepat kenyang.","Makan 4-5 kali sehari. Jangan skip sarapan.","Tambah kalori yang mudah: nasi lebih, telur, susu, kacang, peanut butter."],a:"Hari ini pastikan 3 makan utama + 1-2 snek, ikut menu."},
 gen:{t:"The weight-gain plate",p:["A quarter protein, a quarter to half carbs, only a few vegetables so you don't fill up too fast.","Eat 4-5 times a day. Don't skip breakfast.","Add easy calories: more rice, eggs, milk, nuts, peanut butter."],a:"Today, get 3 main meals + 1-2 snacks, as in your menu."}},
{k:"gerak", ms:{t:"Langkah harian",p:["Berjalan ialah cara paling mudah bakar tenaga tanpa rasa letih.","Sasaran you ada di tab Senaman. Naik sedikit-sedikit, bukan sekali gus.","Jalan 10 minit lepas makan pun sudah banyak membantu."],a:"Jalan 10 minit lepas makan malam."},
 en:{t:"Daily steps",p:["Walking is the easiest way to burn energy without feeling drained.","Your target is in the Workout tab. Go up a little at a time, not all at once.","Even a 10-minute walk after a meal helps a lot."],a:"Take a 10-minute walk after dinner."}},
{k:"minda", ms:{t:"Pinggang lebih jujur dari penimbang",p:["Berat boleh naik turun 1-2 kg sehari sebab air, garam dan makanan dalam perut.","Ukur pinggang di paras pusat, pagi, sebelum makan. Ini lebih tepat tunjuk lemak turun.","Timbang seminggu sekali sahaja, hari dan masa yang sama."],a:"Ukur pinggang pagi esok dan tulis di tab Progress."},
 en:{t:"Your waist is more honest than the scale",p:["Weight can swing 1-2 kg a day from water, salt and food in your stomach.","Measure your waist at the belly button, in the morning, before eating. It shows fat loss better.","Weigh yourself once a week only, same day and time."],a:"Measure your waist tomorrow morning and note it in Progress."},
 gms:{t:"Timbang dengan betul",p:["Berat naik turun ikut air dan makanan. Jangan panik dengan satu nombor.","Timbang seminggu sekali, pagi, lepas tandas, sebelum makan.","Sasaran sihat: naik perlahan, lebih kurang 0.25-0.5 kg seminggu."],a:"Timbang pagi esok dan tulis di tab Progress."},
 gen:{t:"Weigh yourself the right way",p:["Weight swings with water and food. Don't panic over one number.","Weigh once a week, in the morning, after the toilet, before eating.","A healthy pace: slow, about 0.25-0.5 kg a week."],a:"Weigh yourself tomorrow morning and note it in Progress."}},
{k:"makan", ms:{t:"Protein setiap kali makan",p:["Protein buat you kenyang lebih lama dan jaga otot.","Setiap makan, ada satu sumber protein: telur, ayam, ikan, tauhu, tempe, susu atau yogurt.","Pilihan murah: telur, tauhu, tempe, sardin, ikan kembung."],a:"Semak menu hari ini. Setiap makan ada protein?"},
 en:{t:"Protein at every meal",p:["Protein keeps you full longer and protects your muscle.","At each meal, have one protein: egg, chicken, fish, tofu, tempeh, milk or yogurt.","Cheap picks: eggs, tofu, tempeh, sardines, mackerel."],a:"Check today's menu. Does every meal have protein?"}},
{k:"gerak", ms:{t:"Gerakan Asas buat betul",p:["Perlahan dan betul lebih baik dari laju dan salah.","Tengok video setiap gerakan sekali sebelum mula.","Penat itu normal. Sakit tajam di sendi bukan normal: berhenti dan tukar ke versi lebih mudah."],a:"Buat sesi senaman hari ini, tengok video dulu."},
 en:{t:"Doing the basic moves right",p:["Slow and correct beats fast and sloppy.","Watch each move's video once before you start.","Feeling tired is normal. Sharp joint pain is not: stop and switch to the easier version."],a:"Do today's workout, watch the videos first."}},
{k:"minda", ms:{t:"Hujung minggu & kenduri",p:["Satu hari makan lebih tak rosakkan semuanya. Yang penting hari esok kembali ke menu.","Di kenduri: ambil lauk dulu, nasi separuh, kurangkan kuah santan.","Air sirap dan teh tarik: pilih satu sahaja, atau air kosong."],a:"Ada majlis minggu ini? Rancang dulu apa you akan ambil."},
 en:{t:"Weekends & kenduri",p:["One big day doesn't ruin everything. What matters is going back to the menu the next day.","At a kenduri: take the dishes first, half the rice, less coconut gravy.","Sirap and teh tarik: pick just one, or plain water."],a:"Any event this week? Plan what you'll take first."}},
{k:"makan", ms:{t:"Air manis senyap-senyap",p:["Teh tarik, sirap, kopi 3 dalam 1 dan air kotak boleh tambah 150-250 kcal setiap gelas.","Tukar kepada kosong atau kurang manis, satu minuman sehari dulu.","Hari ini juga check-in Hari 7: ukur pinggang dan timbang di tab Progress."],a:"Check-in Hari 7 di tab Progress, kemudian Salin untuk group."},
 en:{t:"The hidden sugar in drinks",p:["Teh tarik, sirap, 3-in-1 coffee and packet drinks can add 150-250 kcal per glass.","Switch to kosong or less sweet, one drink a day to start.","Today is also the Day 7 check-in: measure your waist and weigh in, in Progress."],a:"Do the Day 7 check-in in Progress, then Copy for group."},
 gms:{t:"Kalori cair yang membantu",p:["Kalau susah makan banyak, minum kalori: susu penuh krim, smoothie pisang oat.","Minum di antara waktu makan, bukan sebelum makan, supaya tak kenyang awal.","Hari ini juga check-in Hari 7: timbang dan ukur di tab Progress."],a:"Check-in Hari 7 di tab Progress, kemudian Salin untuk group."},
 gen:{t:"Liquid calories that help",p:["If eating a lot is hard, drink some calories: full-cream milk, banana oat smoothie.","Drink between meals, not before, so you don't fill up early.","Today is also the Day 7 check-in: weigh in and measure, in Progress."],a:"Do the Day 7 check-in in Progress, then Copy for group."}},
{k:"gerak", ms:{t:"Naik 1,000 langkah",p:["Minggu ini sasaran langkah naik 1,000 lagi.","Cara mudah: parking jauh sikit, naik tangga, jalan masa telefon.","Pergerakan harian selain senaman bakar lebih banyak tenaga dari yang orang sangka."],a:"Pilih satu cara tambah langkah hari ini."},
 en:{t:"Add 1,000 steps",p:["This week your step target goes up by another 1,000.","Easy ways: park further, take the stairs, walk while on the phone.","Everyday movement outside workouts burns more energy than most people think."],a:"Pick one way to add steps today."}},
{k:"minda", ms:{t:"Craving: lapar atau penat?",p:["Lapar betul datang perlahan, apa-apa makanan pun okay. Craving datang tiba-tiba, nak satu makanan sahaja.","Craving selalu datang bila penat, stress atau bosan.","Cuba: minum air, tunggu 10 minit. Masih lapar? Makan snek dari menu."],a:"Bila craving datang hari ini, tanya: lapar atau penat?"},
 en:{t:"Craving: hungry or tired?",p:["Real hunger builds slowly and any food will do. A craving hits suddenly and wants one food.","Cravings often come when you're tired, stressed or bored.","Try: drink water, wait 10 minutes. Still hungry? Have a snack from your menu."],a:"When a craving hits today, ask: hungry or tired?"}},
{k:"makan", ms:{t:"Makan luar tanpa rasa bersalah",p:["Mamak: roti kosong + telur, teh O kosong. Elak mee goreng + teh tarik.","Nasi campur: nasi separuh, lauk bakar atau rebus, 2 sayur, kuah sikit.","Kedai ayam goreng: ambil 1 ketul, buang kulit, tukar air kepada air kosong."],a:"Kalau makan luar hari ini, guna satu tip di atas."},
 en:{t:"Eating out without guilt",p:["Mamak: plain roti + egg, teh O kosong. Skip mee goreng + teh tarik.","Nasi campur: half rice, grilled or boiled dishes, 2 vegetables, little gravy.","Fried chicken place: one piece, skin off, plain water instead of soda."],a:"If you eat out today, use one tip above."}},
{k:"gerak", ms:{t:"Tidur juga sebahagian latihan",p:["Kurang tidur buat lapar lebih dan craving lebih kuat esoknya.","Sasaran 7 jam. Tutup telefon 30 minit sebelum tidur.","Kerja syif: tidur di bilik gelap dan sejuk, waktu yang sama setiap hari bekerja."],a:"Malam ini, letak telefon jauh 30 minit sebelum tidur."},
 en:{t:"Sleep is part of training",p:["Short sleep makes you hungrier and cravings stronger the next day.","Aim for 7 hours. Phone away 30 minutes before bed.","Shift work: sleep in a dark, cool room, at the same time each work day."],a:"Tonight, put your phone away 30 minutes before bed."}},
{k:"minda", ms:{t:"Berat tak turun? Itu normal",p:["Berat badan turun macam tangga, bukan garisan lurus. Ada minggu nampak tak bergerak.","Tengok juga pinggang, baju, tenaga dan tidur.","Yang buat result: ikut menu lebih kurang 80% masa, minggu demi minggu."],a:"Tulis satu perubahan selain berat yang you rasa minggu ini."},
 en:{t:"Weight not moving? That's normal",p:["Weight comes down like stairs, not a straight line. Some weeks look flat.","Look at your waist, clothes, energy and sleep too.","What gets results: following the menu about 80% of the time, week after week."],a:"Write down one change besides weight you've felt this week."},
 gms:{t:"Naik perlahan itu normal",p:["Badan perlukan masa. Ada minggu berat naik, ada minggu kekal.","Kalau 2 minggu tak naik langsung, tambah satu snek atau satu gelas susu sehari.","Tengok juga tenaga, kekuatan dan selera makan."],a:"Tulis satu perubahan yang you rasa minggu ini."},
 gen:{t:"Slow gain is normal",p:["Your body needs time. Some weeks go up, some stay the same.","If nothing moves for 2 weeks, add one snack or one glass of milk a day.","Look at your energy, strength and appetite too."],a:"Write down one change you've felt this week."}},
{k:"makan", ms:{t:"Serat & sayur",p:["Serat buat kenyang lama dan bagus untuk perut.","Sumber mudah: sayur hijau, ulam, jambu batu, oat, kacang dal, ubi keledek.","Mula makan dengan sayur dulu, kemudian lauk dan nasi."],a:"Hari ini, mula setiap makan dengan sayur."},
 en:{t:"Fibre & vegetables",p:["Fibre keeps you full longer and is good for your gut.","Easy sources: leafy greens, ulam, guava, oats, dal, sweet potato.","Start each meal with the vegetables, then the protein and rice."],a:"Today, start every meal with vegetables."}},
{k:"minda", ms:{t:"Apa lepas ni?",p:["14 hari ini bina asas: pinggan, protein, langkah dan senaman ringkas.","Program penuh tambah: meal review oleh coach, workout dalam app, coaching 1-ke-1 dan group, check-in mingguan.","Isi Progress Hari 14 dan tengok tawaran untuk you."],a:"Isi Progress Hari 14, kemudian hantar kepada coach."},
 en:{t:"What's next?",p:["These 14 days built the base: the plate, protein, steps and a short workout.","The full program adds: meal reviews by a coach, workouts in the app, 1-to-1 and group coaching, weekly check-ins.","Fill in Day 14 Progress and see your offer."],a:"Fill in Day 14 Progress, then send it to your coach."}},
];

// ---------- workouts ----------
const YT = id => "https://www.youtube.com/watch?v=" + id;
const EX = {
  march:{ms:"Jalan setempat",en:"March in place",v:"u1gmWFvEluM",c_ms:"Angkat lutut, hayun tangan, bernafas biasa.",c_en:"Lift your knees, swing your arms, breathe normally."},
  sts:{ms:"Duduk-bangun dari kerusi",en:"Sit to stand",v:"5yxfzyzEzBY",c_ms:"Kaki selebar bahu, bangun tanpa tolak dengan tangan, duduk perlahan.",c_en:"Feet hip-width, stand up without pushing with your hands, sit down slowly."},
  squat:{ms:"Squat",en:"Squat",v:"m0GcZ24pK6k",c_ms:"Punggung ke belakang macam nak duduk, dada tegak, lutut ikut arah jari kaki.",c_en:"Hips back like sitting down, chest up, knees in line with your toes."},
  wallpu:{ms:"Push-up dinding",en:"Wall push-up",v:"5NPvv40gd3Q",c_ms:"Tangan di dinding paras bahu, badan lurus, bengkok siku perlahan.",c_en:"Hands on the wall at shoulder height, body straight, bend your elbows slowly."},
  kneepu:{ms:"Push-up lutut",en:"Knee push-up",v:"WcHtt6zT3Go",c_ms:"Lutut di lantai, badan lurus dari lutut ke kepala.",c_en:"Knees on the floor, body straight from knees to head."},
  pu:{ms:"Push-up",en:"Push-up",v:"I9fsqKE5XHo",c_ms:"Badan lurus macam papan, dada turun hampir ke lantai.",c_en:"Body straight like a plank, chest down close to the floor."},
  bridge:{ms:"Glute bridge",en:"Glute bridge",v:"XLXGydU5DdU",c_ms:"Baring, lutut bengkok, angkat punggung, picit punggung di atas 2 saat.",c_en:"Lie down, knees bent, lift your hips, squeeze your glutes at the top for 2 seconds."},
  plank:{ms:"Plank",en:"Plank",v:"rerKy2AEHz4",c_ms:"Siku bawah bahu, badan lurus, perut ketat. Jangan tahan nafas.",c_en:"Elbows under shoulders, body straight, tummy tight. Don't hold your breath."},
  kplank:{ms:"Plank lutut",en:"Knee plank",v:"rerKy2AEHz4",c_ms:"Macam plank, tapi lutut di lantai.",c_en:"Like a plank, but with your knees on the floor."},
  side:{ms:"Side plank",en:"Side plank",v:"N_s9em1xTqU",c_ms:"Baring mengiring, siku bawah bahu, angkat pinggul. Lutut boleh di lantai.",c_en:"Lie on your side, elbow under shoulder, lift your hips. Knees down is fine."},
  lunge:{ms:"Lunge",en:"Lunge",v:"FOXMtZ2dqow",c_ms:"Langkah ke depan, turun sampai dua lutut bengkok, tolak balik.",c_en:"Step forward, lower until both knees bend, push back."},
  birddog:{ms:"Bird dog",en:"Bird dog",v:"oKKutQk8QVE",c_ms:"Merangkak, hulur tangan dan kaki bertentangan, perlahan, belakang rata.",c_en:"On all fours, reach the opposite arm and leg, slowly, back flat."},
  deadbug:{ms:"Dead bug",en:"Dead bug",v:"GbSC02oU3To",c_ms:"Baring, tangan dan lutut ke atas, turunkan tangan dan kaki bertentangan, belakang rapat lantai.",c_en:"Lie down, arms and knees up, lower the opposite arm and leg, back pressed to the floor."},
  calf:{ms:"Calf raise",en:"Calf raise",v:"k8ipHzKeAkQ",c_ms:"Berdiri, jengket perlahan, turun perlahan. Pegang dinding kalau perlu.",c_en:"Stand, rise onto your toes slowly, lower slowly. Hold a wall if needed."},
  stepup:{ms:"Step-up (tangga)",en:"Step-up (stairs)",v:"VJtMb2im41c",c_ms:"Naik satu anak tangga dengan satu kaki, turun perlahan, tukar kaki.",c_en:"Step up one stair with one foot, step down slowly, switch legs."},
  // gentle level (28 Nov, Kimi: bigger bodies + sore joints): seated or holding a support, no jumping, no floor
  smarch:{ms:"Jalan setempat sambil duduk",en:"Seated march",v:"",c_ms:"Duduk tegak di kerusi, angkat lutut bergilir, hayun tangan.",c_en:"Sit tall on a chair, lift your knees in turn, swing your arms."},
  legext:{ms:"Luruskan kaki sambil duduk",en:"Seated leg extension",v:"",c_ms:"Duduk tegak, luruskan satu kaki perlahan, tahan 2 saat, turun. Tukar kaki.",c_en:"Sit tall, straighten one leg slowly, hold 2 seconds, lower. Switch legs."},
  armraise:{ms:"Angkat tangan sambil duduk",en:"Seated arm raise",v:"",c_ms:"Duduk tegak, angkat dua tangan ke atas perlahan, turun perlahan. Berhenti kalau bahu sakit.",c_en:"Sit tall, raise both arms overhead slowly, lower slowly. Stop if your shoulder hurts."},
  sidestep:{ms:"Langkah ke tepi",en:"Side step",v:"",c_ms:"Berdiri dekat dinding atau meja, langkah ke kiri dan kanan perlahan. Pegang kalau perlu.",c_en:"Stand near a wall or table, step left and right slowly. Hold on if you need to."},
};
const SESS = {
  gentle:[["smarch","sts","wallpu","legext","calf"], ["armraise","legext","wallpu","sidestep","smarch"]],
  new:   [["sts","wallpu","bridge","birddog","calf"], ["deadbug","stepup","kplank","bridge","wallpu"]],
  some:  [["squat","kneepu","bridge","plank"], ["lunge","birddog","stepup","side"]],
  active:[["squat","pu","lunge","plank","bridge"], ["stepup","pu","deadbug","side","calf"]],
};
const SWAP_KNEE = { squat:"sts", lunge:"bridge", stepup:"calf" };   // sts: high chair, half range
const SWAP_BACK = { plank:"deadbug", kplank:"deadbug", side:"birddog", pu:"wallpu" };
const WORK_DAYS = [2,4,6,9,11,13];

function workout(a, day){
  const i = WORK_DAYS.indexOf(day); if (i < 0) return null;
  let moves = SESS[a.level][i % 2].slice();
  const swap = m => (a.knee && SWAP_KNEE[m]) || (a.back && SWAP_BACK[m]) || m;
  const n = moves.length;
  moves = moves.map(swap).filter((m, k, all) => all.indexOf(m) === k);   // no duplicates after swaps
  for (const f of ["deadbug","birddog","calf","wallpu"]) if (moves.length < n && !moves.includes(f) && swap(f) === f) moves.push(f);
  const wk2 = day > 7, gain = a.goal === "naik";
  return { session: i % 2 ? "B" : "A", warm: "march", moves,
    rounds: gain ? 3 : (wk2 ? 3 : 2), work: gain ? null : (a.level === "new" ? 30 : 40), reps: gain ? "10-12" : null,
    rest: gain ? 60 : (a.level === "new" ? 30 : 20) };
}

// ---------- targets ----------
const STEP_NOW = { lt3:2500, s3:4000, s5:6500, s8:9000, tt:null };
function targets(a){
  const args = [a.sex, a.age, a.cm, a.kg, a.act];
  const gain = a.goal === "naik";
  const kcal = r50(gain ? gainCal(...args) : lossCal(...args));
  const pFull = gain ? a.kg * GAIN_PROTEIN[a.act] : 1.6 * Math.min(a.kg, 27*(a.cm/100)**2);
  const protein = r5(Math.min(pFull, kcal * (gain ? 0.25 : 0.3) / 4));
  const now = STEP_NOW[a.steps];
  const steps = now == null ? [5000, 6000] : [Math.min(12000, now + 1000), Math.min(12000, now + 2000)];
  const water = Math.round(a.kg * 0.033 * 4);   // 250ml glasses
  return { kcal, protein, steps, water, gain };
}

// who can't get a plan, or needs a doctor note
function check(a){
  const bmi = a.kg / (a.cm/100)**2;
  if (a.age < 18) return { stop:"age" };
  if (a.health.includes("preg")) return { stop:"preg" };
  if (a.goal === "turun" && bmi < 18.5) return { stop:"lowbmi" };
  if (a.goal === "naik" && bmi < 16) return { stop:"verylow" };
  if (a.goal === "naik" && bmi >= 23) return { stop:"gainhigh" };
  return { stop:null, doctor: a.health.includes("med"), bmi };
}

// ---------- generator ----------
function mulberry32(s){ return function(){ s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const fnv = s => { let h = 0x811c9dc5; for (const c of String(s)) { h ^= c.charCodeAt(0); h = Math.imul(h, 0x01000193) >>> 0; } return h; };
// daily RM caps grow with calories (a 2,900 kcal gain plan needs more food than 1,300)
const BUDGET = { jimat:{maxTier:1, cap:k => Math.max(22, k/80)}, sederhana:{maxTier:2, cap:k => Math.max(40, k/50)}, selesa:{maxTier:3, cap:k => Math.max(70, k/30)} };

function pools(a){
  const gain = a.goal === "naik", b = BUDGET[a.budget];
  const ok = f => (!f.gain || gain) && f.tier <= b.maxTier && ![...f.tags].some(t => a.avoid.includes(t));
  const pick = s => FOODS.filter(f => f.slots.includes(s) && ok(f));
  return { B:pick("B"), L:pick("L"), D:pick("D"), S:pick("S"), A:pick("A") };
}

function generate(a){
  const T = targets(a), P = pools(a), rnd = mulberry32(fnv(JSON.stringify([a.name, a.goal, a.sex, a.age, a.cm, a.kg, a.act, a.budget, a.cook, a.avoid, a.health, a.level])));
  const b = BUDGET[a.budget], gain = T.gain, cap = b.cap(T.kcal);
  const maxSnacks = gain ? 3 : T.kcal < 1500 ? 1 : T.kcal < 2000 ? 2 : 3, maxAdd = gain ? 4 : 2;
  const any = arr => arr[Math.floor(rnd() * arr.length)];
  const used = {}, days = [];
  for (let d = 0; d < 14; d++) {
    const recent = new Set(days.slice(-2).flatMap(x => x.ids));
    let best = null;
    for (let trial = 0; trial < 400; trial++) {
      if (!P.B.length || !P.L.length || !P.D.length) break;
      const m = { B:any(P.B), L:any(P.L), D:any(P.D) };
      if (m.L.id === m.D.id) continue;
      const snacks = [], adds = [];
      let kcal = m.B.kcal + m.L.kcal + m.D.kcal, p = m.B.p + m.L.p + m.D.p;
      while (snacks.length < maxSnacks && kcal < T.kcal - 70) {
        const fit = P.S.filter(s => !snacks.includes(s) && kcal + s.kcal <= T.kcal + 60);
        if (!fit.length) break;
        const s = any(fit); snacks.push(s); kcal += s.kcal; p += s.p;
      }
      while (adds.length < maxAdd && kcal < T.kcal - 60) {
        const fit = P.A.filter(x => !adds.some(y => y.f === x) && kcal + x.kcal <= T.kcal + 60);
        if (!fit.length) break;
        const x = any(fit), to = any([...ADDON_TO[x.id]].filter(s => s === "B" || s === "L" || s === "D"));
        adds.push({ f:x, to }); kcal += x.kcal; p += x.p;
      }
      const all = [m.B, m.L, m.D, ...snacks, ...adds.map(x => x.f)];
      const cost = all.reduce((t, f) => t + f.rm, 0);
      const diff = Math.abs(kcal - T.kcal);
      let score = diff + Math.max(0, diff - 100) * 3 + Math.max(0, T.protein - p) * 3;
      if (cost > cap) score += (cost - cap) * 15;
      for (const f of [m.B, m.L, m.D]) {
        if (recent.has(f.id)) score += 80;
        score += (used[f.id] || 0) * 35;
        if (a.cook === "masak" && f.src === "b") score += 30;
        if (a.cook === "beli" && f.src === "h" && f.slots !== "B") score += 30;
        if (a.budget === "selesa" && f.tier < 3) score += 12;
        if (a.budget === "sederhana" && f.tier < 2) score += 6;
      }
      for (const s of snacks) if (recent.has(s.id)) score += 15;
      if (!best || score < best.score) best = { score, m, snacks, adds, kcal, p, cost };
    }
    if (!best) return { error:"pool", T };
    const ids = [best.m.B.id, best.m.L.id, best.m.D.id, ...best.snacks.map(s => s.id)];
    for (const id of ids) used[id] = (used[id] || 0) + 1;
    days.push({ day:d+1, B:best.m.B, L:best.m.L, D:best.m.D, S:best.snacks, adds:best.adds, kcal:best.kcal, p:best.p, cost:Math.round(best.cost), ids });
  }
  return { T, days, cap:Math.round(cap) };
}

// grocery list for one week (days 1-7 or 8-14), home-cooked items only
function grocery(days){
  const tot = {};
  let home = 0, out = 0;
  for (const d of days) for (const f of [d.B, d.L, d.D, ...d.S, ...d.adds.map(x => x.f)]) {
    if (f.src === "h") { home += f.rm; for (const [k, q] of f.groc) tot[k] = (tot[k] || 0) + q; } else out += f.rm;
  }
  const rows = Object.entries(tot).map(([k, q]) => {
    const g = GROC[k], v = Math.ceil(q / g[4] / g[5]) * g[5];
    return { k, ms:g[0], en:g[1], qty:+v.toFixed(1), u_ms:g[2], u_en:g[3] };
  });
  return { rows, home:Math.round(home), out:Math.round(out) };
}

function recipesUsed(days){
  const ids = new Set();
  for (const d of days) for (const f of [d.B, d.L, d.D, ...d.S]) if (f.recipe) ids.add(f.recipe);
  return [...ids];
}

// meal check: 4 ticks per meal, 3 meals = 12
function rate(score){ return score >= 10 ? "hebat" : score >= 7 ? "bagus" : "cuba"; }

const API = { FOODS, FOOD, RECIPES, TOPICS, EX, YT, WORK_DAYS, GROC, targets, check, generate, grocery, recipesUsed, workout, rate, fnv, tdee };
if (typeof module !== "undefined") module.exports = API; else window.PLAN = API;
})();
