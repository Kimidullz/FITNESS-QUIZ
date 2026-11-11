// Grocery page data for the meal plan PDF (nutritionist draft, 11 Nov 2026).
// Quantities are tallied from TIERS in build.js with the week rotation
//   Isnin/Khamis/Ahad = Hari 1, Selasa/Jumaat = Hari 2, Rabu/Sabtu = Hari 3.
// Each PDF is one tier, so print ONLY that tier's quantity column ("Kuantiti untuk 1,500 kcal").
// "-" = item not needed at that tier: hide the row. ★ = stock item, lasts 3-4+ weeks.
// Prices: rough estimates, Klang Valley hypermarket + pasar pagi, late 2026. Not quotes.

const GROCERY = {
  // [ms, en, {1200,1500,1800,2000,2300}, "RM range for that row"]
  groups: [
    { ms:"Protein", en:"Protein", rows:[
      ["Dada ayam (atau ayam seekor, buang kulit)", "Chicken breast (or whole chicken, skin off)", {1200:"1 kg",1500:"1 kg",1800:"750 g",2000:"1 kg",2300:"750 g"}, "RM12-20"],
      ["Ikan kembung", "Mackerel (kembung)", {1200:"2 ekor",1500:"2 ekor",1800:"4 ekor",2000:"2 ekor",2300:"4 ekor"}, "RM4-12"],
      ["Telur", "Eggs", {1200:"12 biji",1500:"10 biji",1800:"10 biji",2000:"6 biji",2300:"20 biji"}, "RM3-10"],
      ["Daging kisar (lembu atau ayam)", "Minced beef or chicken", {1200:"-",1500:"-",1800:"200 g",2000:"200 g",2300:"300 g"}, "RM5-14"],
    ]},
    { ms:"Tenusu", en:"Dairy", rows:[
      ["Yogurt Greek tanpa gula (atau tapis yogurt biasa, tip 2)", "Plain Greek yogurt, no sugar (or strain plain yogurt, tip 2)", {1200:"500 g",1500:"500 g",1800:"750 g",2000:"750 g",2300:"750 g"}, "RM15-28"],
      ["Susu rendah lemak", "Low-fat milk", {1200:"-",1500:"1 L",1800:"1 L",2000:"2 L",2300:"1 L"}, "RM7-17"],
    ]},
    { ms:"Karbo", en:"Carbs", rows:[
      ["Beras (mentah, guna stok rumah)", "Rice (uncooked, from home stock)", {1200:"150 g",1500:"350 g",1800:"500 g",2000:"400 g",2300:"450 g"}, "RM1-2"],
      ["Roti wholemeal (simpan dalam freezer)", "Wholemeal bread (keep in freezer)", {1200:"4 keping",1500:"4 keping",1800:"4 keping",2000:"8 keping",2300:"1 buku"}, "RM4-6"],
      ["Oat ★", "Oats ★", {1200:"-",1500:"-",1800:"500 g",2000:"500 g",2300:"500 g"}, "RM6-9"],
      ["Spaghetti ★", "Spaghetti ★", {1200:"-",1500:"-",1800:"500 g",2000:"500 g",2300:"500 g"}, "RM4-6"],
      ["Kentang", "Potatoes", {1200:"1 biji",1500:"4 biji",1800:"2 biji",2000:"3 biji",2300:"2 biji"}, "RM1-3"],
      ["Tortilla wrap (atau guna roti wholemeal)", "Tortilla wraps (or use wholemeal bread)", {1200:"1 paket",1500:"-",1800:"-",2000:"-",2300:"-"}, "RM0-9"],
      ["Granola (tanpa gula tambahan) ★", "Granola, no added sugar ★", {1200:"1 paket kecil",1500:"-",1800:"-",2000:"-",2300:"-"}, "RM10-18"],
    ]},
    { ms:"Sayur (sama untuk semua: makan sebanyak mana pun)", en:"Vegetables (same for everyone: eat as much as you like)", rows:[
      ["Sawi / kangkung / bayam 4 ikat · kubis 1 kecil · lobak merah 3 · timun 2 · tomato 5 · daun salad 1 paket · ulam 1 ikat · bawang besar 3",
       "Leafy greens 4 bunches · 1 small cabbage · 3 carrots · 2 cucumbers · 5 tomatoes · 1 pack lettuce · 1 bunch ulam · 3 onions", {1200:"✓",1500:"✓",1800:"✓",2000:"✓",2300:"✓"}, "RM15-22"],
    ]},
    { ms:"Buah", en:"Fruit", rows:[
      ["Pisang", "Bananas", {1200:"-",1500:"2 biji",1800:"1 sikat",2000:"1 sikat",2300:"1 sikat"}, "RM1-6"],
      ["Epal (atau jambu batu, lebih murah)", "Apples (or guava, cheaper)", {1200:"-",1500:"3 biji",1800:"5 biji",2000:"5 biji",2300:"5 biji"}, "RM3-8"],
      ["Betik (untuk buah potong)", "Papaya (for cut fruit)", {1200:"1 biji",1500:"-",1800:"-",2000:"-",2300:"-"}, "RM2-8"],
      ["Limau nipis", "Limes", {1200:"6 biji",1500:"6 biji",1800:"6 biji",2000:"6 biji",2300:"6 biji"}, "RM1-2"],
    ]},
    { ms:"Dapur & sos ★", en:"Pantry & sauces ★", rows:[
      ["Garam, lada hitam, kunyit serbuk, bawang putih, halia, serai, cili padi, kicap, sos tiram, minyak masak (1 sudu sehari cukup). Tambah ikut menu: rempah sup (1,200-1,800) · pes tom yam (1,500, kalau masak sendiri) · tomato tin / sos pasta + peanut butter tanpa gula (1,800+)",
       "Salt, black pepper, turmeric, garlic, ginger, lemongrass, bird's-eye chilli, soy sauce, oyster sauce, cooking oil (1 tbsp a day is enough). Plus by menu: soup spice (1,200-1,800) · tom yam paste (1,500, if cooking) · canned tomato / pasta sauce + no-sugar peanut butter (1,800+)",
       {1200:"✓",1500:"✓",1800:"✓",2000:"✓",2300:"✓"}, "RM20-35 minggu 1, ~RM5 lepas tu"],
    ]},
    { ms:"Minuman", en:"Drinks", rows:[
      ["Teh / kopi O (uncang atau serbuk) ★ · air kosong 2-3 L sehari (botol isi semula) · air limau tanpa gula. Tiada air manis dalam senarai ini.",
       "Tea / black coffee ★ · 2-3 L plain water a day (refill a bottle) · lime water, no sugar. No sweet drinks on this list.",
       {1200:"✓",1500:"✓",1800:"✓",2000:"✓",2300:"✓"}, "RM5-8"],
    ]},
  ],
  // meals in the sample days that are bought outside, per tier
  eatOut: {
    1200: { ms:"Roti canai + teh O ×3 · nasi campur ×3 · yong tau foo ×2", en:"Roti canai + teh O ×3 · nasi campur ×3 · yong tau foo ×2", rm:"RM50-65" },
    1500: { ms:"Nasi lemak ×3 · nasi campur ×3 · thosai ×2 · tom yam ×2", en:"Nasi lemak ×3 · nasi campur ×3 · thosai ×2 · tom yam ×2", rm:"RM60-90" },
    1800: { ms:"Roti canai + teh O ×3 · nasi ayam panggang ×3 · nasi lemak ×2", en:"Roti canai + teh O ×3 · roasted chicken rice ×3 · nasi lemak ×2", rm:"RM40-55" },
    2000: { ms:"Roti canai + 2 telur ×3 · nasi ayam panggang ×3 · nasi lemak ×2", en:"Roti canai + 2 eggs ×3 · roasted chicken rice ×3 · nasi lemak ×2", rm:"RM45-65" },
    2300: { ms:"Roti canai + 2 telur ×5 · nasi ayam panggang ×2", en:"Roti canai + 2 eggs ×5 · roasted chicken rice ×2", rm:"RM40-57" },
  },
  // weekly grocery (excl. ★ first-week stock) and per-day incl. eating out
  totals: {
    1200: { dapur:"RM70-100", sehari:"RM17-24" },
    1500: { dapur:"RM70-100", sehari:"RM19-27" },
    1800: { dapur:"RM90-125", sehari:"RM19-26" },
    2000: { dapur:"RM95-130", sehari:"RM20-28" },
    2300: { dapur:"RM95-130", sehari:"RM19-27" },
  },
  ms: {
    h:"Senarai barang dapur 1 minggu",
    sub:"Untuk 1 orang · ikut menu Hari 1-3 pelan ini · Isnin/Khamis/Ahad = Hari 1 · Selasa/Jumaat = Hari 2 · Rabu/Sabtu = Hari 3",
    qtyH:"Kuantiti untuk {k} kcal",
    outH:"Beli di luar (ikut menu anda)",
    totalH:"Anggaran kos seminggu",
    totalLine:"Barang dapur {dapur} + makan luar {out}. Purata lebih kurang {sehari} sehari.",
    stock:"★ Barang stok: beli sekali, tahan 3-4 minggu. Tambah ~RM25-45 pada minggu pertama sahaja.",
    priceNote:"Harga anggaran pasar raya besar & pasar pagi, Lembah Klang, 2026. Harga sebenar berbeza ikut tempat & musim.",
    family:"Masak untuk keluarga? Gandakan sayur & nasi ikut bilangan orang. Tambah ~150 g ayam/ikan untuk setiap orang, setiap hidangan.",
    tipsH:"5 tip jimat",
    tips:[
      "Beli ayam seekor, minta peniaga potong & buang kulit. Biasanya lebih murah sekilo daripada dada ayam. Bahagi 150 g setiap bekas, simpan dalam freezer.",
      "Yogurt Greek mahal? Tapis yogurt biasa tanpa gula dalam penapis + tisu dapur semalaman dalam peti sejuk. Atau tukar snek yogurt dengan 2 telur rebus.",
      "Buah tempatan ikut musim (betik, pisang, jambu batu, nanas) ganti epal import.",
      "Sayur & ikan di pasar pagi. Telur (1 papan 30 biji), beras, oat & susu di pasar raya besar: beli sekali seminggu sahaja ikut senarai.",
      "Tauhu & tempe: protein murah. Tukar 2 hidangan ayam seminggu dengan tauhu/tempe bakar.",
    ],
    prepH:"Meal prep Ahad: 30 minit",
    prep:[
      ["0-5 min","Hidupkan rice cooker. Periuk 1: rebus semua telur untuk minggu ini (10 min). Periuk 2: sup ayam atau sos daging tomato, biar reneh."],
      ["5-10 min","Perap ayam: kunyit, lada hitam, garam, bawang putih, limau. Bahagi 150 g."],
      ["10-25 min","Bakar 3 hidangan ayam (air fryer, oven atau kuali leper). Bakinya simpan mentah berperap dalam freezer untuk Khamis-Sabtu. Sambil tunggu: basuh & potong lobak, kubis, timun, salad; potong buah untuk 3 hari."],
      ["25-30 min","Bahagi nasi ikut cawan dalam bekas & sejukkan cepat. Isi semua dalam bekas, tulis hari. Rabu malam: pindah ayam untuk Khamis & Jumaat ke peti sejuk. Jumaat malam: pindah bahagian Sabtu."],
    ],
    safety:"Keselamatan makanan: lauk yang dah masak (ayam, sup, sos daging) habiskan dalam 3 hari; bahagian untuk Khamis ke atas, bekukan. Ayam mentah yang dah cair: masak dalam 1-2 hari. Nasi: sejukkan cepat, simpan dalam freezer, panaskan sampai betul-betul panas. Telur rebus yang belum dikupas tahan ~1 minggu dalam peti sejuk. Sayur daun (sawi, kangkung) masak segar, jangan potong awal-awal.",
  },
  en: {
    h:"1-week grocery list",
    sub:"For 1 person · matches Day 1-3 of this plan · Mon/Thu/Sun = Day 1 · Tue/Fri = Day 2 · Wed/Sat = Day 3",
    qtyH:"Amount for {k} kcal",
    outH:"Bought outside (from your menu)",
    totalH:"Rough cost per week",
    totalLine:"Groceries {dapur} + eating out {out}. About {sehari} a day on average.",
    stock:"★ Stock items: buy once, last 3-4 weeks. Add ~RM25-45 in week 1 only.",
    priceNote:"Rough hypermarket & morning market prices, Klang Valley, 2026. Real prices vary by place and season.",
    family:"Cooking for the family? Multiply veg and rice by the number of people. Add ~150 g chicken/fish per person per meal.",
    tipsH:"5 money-saving tips",
    tips:[
      "Buy a whole chicken and ask the seller to cut it and remove the skin. Usually cheaper per kg than breast. Portion 150 g per box and freeze.",
      "Greek yogurt pricey? Strain plain no-sugar yogurt through a sieve + kitchen paper overnight in the fridge. Or swap the yogurt snack for 2 boiled eggs.",
      "Local fruit in season (papaya, banana, guava, pineapple) instead of imported apples.",
      "Veg and fish at the morning market. Eggs (tray of 30), rice, oats and milk at the hypermarket: one trip a week, list only.",
      "Tofu and tempeh are cheap protein. Swap 2 chicken meals a week for grilled tofu/tempeh.",
    ],
    prepH:"30-minute Sunday meal prep",
    prep:[
      ["0-5 min","Rice cooker on. Pot 1: boil all the week's eggs (10 min). Pot 2: chicken soup or tomato meat sauce, simmer."],
      ["5-10 min","Marinate chicken: turmeric, black pepper, salt, garlic, lime. Portion 150 g."],
      ["10-25 min","Grill 3 chicken portions (air fryer, oven or flat pan). Freeze the rest raw in its marinade for Thu-Sat. Meanwhile wash and cut carrot, cabbage, cucumber, salad; cut fruit for 3 days."],
      ["25-30 min","Portion rice by the cup and cool it fast. Box everything, write the day. Wednesday night: move Thu & Fri chicken to the fridge. Friday night: move Saturday's."],
    ],
    safety:"Food safety: eat cooked chicken, soup and meat sauce within 3 days; freeze anything meant for Thursday onwards. Thawed raw chicken: cook within 1-2 days. Rice: cool fast, freeze, reheat until piping hot. Unpeeled boiled eggs keep ~1 week in the fridge. Cook leafy greens fresh; don't cut them early.",
  },
  // optional: closing CTA for page 3 (only if weekly check-ins are really in the RM259 package)
  cta: {
    ms:{ h:"Ini versi percuma, untuk semua orang.", p:"Dalam program penuh, coach semak progress anda setiap minggu dan ubah menu & senarai ini ikut badan, bajet dan keluarga anda. Results berbeza ikut individu.", btn:"Jawab kuiz 2 minit →" },
    en:{ h:"This is the free version, for everyone.", p:"In the full program a coach checks your progress every week and adjusts this menu and list to your body, budget and family. Results vary.", btn:"Take the 2-minute quiz →" },
  },
};
module.exports = GROCERY;
