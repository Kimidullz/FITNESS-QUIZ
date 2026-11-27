"""Eighth batch (27 Nov 2026): PRIVATE sales role-play trainer for Kimi's team (coaches / downlines).

  python seo/generate8.py  -> private-out/roleplay.json  (NOT committed: uploaded as an Actions artifact,
                              then encrypted by plans-relay.yml, because these are private sales scripts)

Makes 30 practice leads (24 client calls + 6 recruit invites), each a scripted call with 3 reply choices per
turn (best / okay / weak + why), and 40 quick objection drills. Every text has ms (rojak) + en.
"""
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate2 import S, arr, obj  # noqa: E402
from generate5 import SYSTEM as PITCH_SYSTEM  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "private-out" / "roleplay.json"
MODEL = os.environ.get("CONTENT_MODEL", "claude-opus-5-5")

SYSTEM = PITCH_SYSTEM + """

THIS JOB: you write PRACTICE material for a sales role-play trainer. New coaches in Kimi's team (his downlines, e.g. Coach Mel) read the lead's line, pick one of 3 replies, and learn from the "why". It must feel like a REAL Malaysian WhatsApp/phone call: leads talk naturally (ms: rojak, lah/kan/tu, short; en: simple Malaysian English), they dodge, joke, go quiet, change topic.
The call follows Kimi's 10-step co-pilot: 1 warm open + frame (YES or NO both okay), 2 goal and history, 3 go 3 levels deeper (why), 4 a normal day, 5 pain and the cost of waiting, 6 vision, 7 the triangle (Nutrition, Workout, Mindset & Method; visceral fat, scale lies), 8 commitment 1-10, 9 the program + recommend inside budget + close (YES or NO), 10 after YES: RM50 deposit, balance before start, onboarding.
Reply options: exactly 3 per turn, in random order, scores 2 (what a top coach says: asks, listens, mirrors their words, stays calm, closes clearly), 1 (okay but misses something: talks too much, pitches too early, vague), 0 (a common mistake: pushy, desperate, discount too fast, promises results, argues, shames, lectures, info-dumps, medical claims). The 0 option must be a TEMPTING mistake a new coach really makes, not a silly one. "why" = 1 short sentence teaching the point. Option texts are what the coach SAYS (1-3 sentences).
Recruit-invite leads (kind "recruit") are a DIFFERENT conversation: a happy client or a contact, invited by Kimi's downline to look at becoming a coach. Follow Eric Worre's invite: be in a hurry, compliment, invite to look (a short video, then a 1-on-1 Zoom with the upline team), "if I send you a video, will you watch it?", book a time. NEVER mention income figures, never promise money, never hide that it is Herbalife/WDT; no pressure; it is fine if they say no and stay a client. Top replies here lead to the video + Zoom booking, not to explaining the whole business."""

BI = obj({"ms": S(), "en": S()})
OPT = obj({"text": BI, "score": {"type": "integer", "enum": [0, 1, 2]}, "why": BI})
LEAD = obj({
    "id": S(),
    "card": BI,      # what the coach knows before the call: 2-3 short lines (source, goal, budget, quiz zone)
    "secret": BI,    # the lead's hidden truth (real fear / motivation / real objection), revealed at the end
    "turns": arr(obj({"step": BI, "lead": BI, "options": arr(OPT), "tip": BI})),
    "end_yes": BI,   # what the lead says when the coach did well (score high)
    "end_no": BI,    # what the lead says when the coach did badly
    "lesson": BI,    # the one big lesson of this lead
})
DRILL = obj({"id": S(), "objection": BI, "context": BI, "options": arr(OPT)})

# id, label, brief
LEADS = [
    ("c01", "Aina, 27, admin exec, KL", "woman, fat loss, quiz Running on empty, budget RM300-500, works 9-6, skips breakfast, teh ais daily; friendly but says 'I nak fikir dulu' at the close"),
    ("c02", "Hafiz, 34, sales manager", "man, fat loss, waist 40in, budget RM500-900, busy, ego, 'I tahu nak buat apa, cuma tak ada masa'; tests if the coach knows their stuff"),
    ("c03", "Nurul, 31, teacher, mum of 2", "woman, fat loss after 2nd baby (baby is 2 years old now), budget under RM300, 'kena tanya suami dulu' is her real objection"),
    ("c04", "Daniel, 22, uni student", "man, WEIGHT GAIN, skinny, 52kg, eats once a day, budget under RM300, parents pay, shy, short answers"),
    ("c05", "Kak Ros, 52, clerk", "woman 50+, fat loss, has diabetes type 2 on medicine, budget RM300-500, asks 'shake ni boleh turunkan gula ke?' (coach must not make medical claims, refer to doctor)"),
    ("c06", "Siti, 29, nurse on shifts", "woman, fat loss, night shifts, eats at odd hours, budget RM500-900, tried keto and gained back; real fear: failing again in front of colleagues"),
    ("c07", "Arif, 40, lorry business owner", "man, fat loss, 98kg, snores, wife made him call, budget above RM1,300 but says 'mahal lah' to test; good fit for the 4-month RM3,259"),
    ("c08", "Mei Ling, 36, accountant (English speaker)", "woman, fat loss, skeptic, 'Isn't Herbalife an MLM?', wants facts, budget RM500-900"),
    ("c09", "Faizal, 26, gym bro", "man, WEIGHT GAIN muscle, goes to gym but no progress, thinks he knows everything, budget RM300-500, 'protein shake I boleh beli kat Shopee je'"),
    ("c10", "Farah, 24, new graduate", "woman, fat loss, wedding in 4 months, wants fast result, asks 'boleh turun 10kg dalam sebulan tak?' (coach must not promise)"),
    ("c11", "Encik Rahman, 47, government officer", "man, fat loss, high blood pressure, quiet, polite, budget RM500-900, decision maker is himself but slow; needs a clear YES/NO"),
    ("c12", "Liyana, 33, online seller", "woman, fat loss, eats late at night, stress, budget RM300-500, ghosted once before; came back from a follow-up message"),
    ("c13", "Kumar, 38, IT engineer", "man, fat loss, desk job, back pain, budget RM900-1,300, likes data and numbers (waist, visceral fat), English speaker"),
    ("c14", "Aishah, 30, housewife", "woman, fat loss, husband controls money, budget under RM300, wants it but scared to spend; the RM50 deposit + balance before start helps"),
    ("c15", "Zul, 28, Grab rider", "man, fat loss, eats mamak daily, budget under RM300, 'gaji tak tentu', asks for a discount below RM259 (floor, never lower)"),
    ("c16", "Dr. Hani, 35, dentist", "woman, fat loss, very busy, decisive, budget above RM1,300, hates long calls; test: coach must not over-talk"),
    ("c17", "Amir, 19, pre-university", "man, WEIGHT GAIN, mother is on the call too and asks most questions, budget RM300-500"),
    ("c18", "Sarah, 42, HR manager", "woman, fat loss, perimenopause, tried many slimming products, distrusts supplements, budget RM500-900"),
    ("c19", "Ikmal, 32, factory supervisor", "man, fat loss, says YES fast but has no money until payday (25th); coach must lock the deposit and balance date"),
    ("c20", "Wani, 26, bank teller", "woman, fat loss, friend of a current client (referral), excited but says 'nanti I join dengan kawan I sekali'"),
    ("c21", "Hakim, 45, contractor", "man, fat loss, wife is a client already with results, he is doubtful 'tu untuk perempuan je'"),
    ("c22", "Jess, 29, marketing executive (English speaker)", "woman, fat loss, compares prices with a gym PT and other coaches, 'Why are you more expensive than X?'"),
    ("c23", "Pak Cik Osman, 58, retired", "man 50+, fat loss + energy, knees hurt, budget RM300-500, children pay; slow speaker, needs patience"),
    ("c24", "Nadia, 31, teacher", "woman, fat loss, Ramadan coming in February, 'I start lepas raya lah'; cost of waiting"),
    ("r01", "Afiq, 30, client with results", "RECRUIT invite: happy client (lost 7kg), friends keep asking him how; open to side income but busy, worried 'I tak pandai jual'"),
    ("r02", "Dayang, 27, client, admin exec", "RECRUIT invite: loves the program, worried 'MLM ni kena cari downline kan?' and her parents dislike MLM"),
    ("r03", "Shah, 35, old school friend", "RECRUIT invite: not a client, sees Kimi's posts, asks 'berapa you dapat sebulan?' (never give figures, invite to look)"),
    ("r04", "Husna, 33, client, mum working from home", "RECRUIT invite: wants flexible work around kids, asks 'kena keluar modal banyak ke?' (start-up cost is explained on the Zoom, not on chat)"),
    ("r05", "Jason, 26, gym member (English speaker)", "RECRUIT invite: into fitness, likes coaching people, skeptical of Herbalife, says 'send me info, I'll read it'"),
    ("r06", "Alya, 24, client, fresh graduate", "RECRUIT invite: interested, says 'nanti I fikir' and goes quiet; the follow-up after 48h ('what did you like best?')"),
]

DRILL_TOPICS = [
    "Mahal lah", "Nak fikir dulu", "Kena tanya suami / isteri", "Tak ada masa", "Dah cuba dulu tak jadi", "MLM ke ni?",
    "Shake tu selamat ke? Ada steroid?", "Boleh turun berapa kilo sebulan?", "Nanti lepas gaji", "Boleh bagi diskaun?",
    "I boleh buat sendiri, YouTube banyak", "Kawan I makan je tak gemuk", "I tak suka shake", "Nak start lepas raya / cuti",
    "Dah join gym, tak perlu", "Kenapa tak jual kat Shopee lebih murah?", "Saya ada darah tinggi / kencing manis",
    "Saya tengah menyusu", "Nanti I contact you", "Hantar info je dulu", "Suami tak bagi", "I takut tak konsisten",
    "Dulu makan supplement lain kena side effect", "Coach lain lagi murah", "Tak percaya online coaching",
    "Kerja shift, susah", "I vegetarian", "Anak kecil, tak sempat masak", "Berat I naik sebab ubat", "Seen, no reply (ghost)",
    "RECRUIT: Berapa boleh dapat sebulan?", "RECRUIT: Kena cari downline ke?", "RECRUIT: I tak pandai jual",
    "RECRUIT: Kena modal banyak?", "RECRUIT: Family I tak suka MLM", "RECRUIT: Hantar info je, nanti I baca",
    "RECRUIT: I tak ada masa", "RECRUIT: Ni skim cepat kaya ke?", "RECRUIT: Kena jual kat kawan-kawan ke?",
    "RECRUIT: Nanti I fikir (after the Zoom)",
]


def call(prompt, schema):
    import anthropic
    client = anthropic.Anthropic()
    with client.beta.messages.stream(
        model=MODEL, max_tokens=64000, system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "adaptive"},
        output_config={"effort": os.environ.get("CONTENT_EFFORT", "medium"),
                       "format": {"type": "json_schema", "schema": schema}},
        betas=["server-side-fallback-2026-07-01"], fallbacks="default",
    ) as stream:
        msg = stream.get_final_message()
    u = msg.usage
    print(f"  tokens in {u.input_tokens} out {u.output_tokens} ({msg.model})", flush=True)
    if msg.stop_reason in ("refusal", "max_tokens"):
        raise RuntimeError("stopped: " + msg.stop_reason)
    return json.loads("".join(b.text for b in msg.content if b.type == "text"))


BAD = ("gemuk", "jamin", "guarantee", "dijamin", "pasti turun", "sure turun")


def good_opts(opts):
    return len(opts) == 3 and sorted(o["score"] for o in opts) == [0, 1, 2]


def ok_lead(d):
    t = json.dumps(d, ensure_ascii=False).lower()
    return 6 <= len(d["turns"]) <= 10 and all(good_opts(x["options"]) for x in d["turns"]) and not any(b in t for b in BAD)


def run():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    have = json.loads(OUT.read_text()) if OUT.exists() else {"leads": {}, "drills": {}}
    todo = [x for x in LEADS if x[0] not in have["leads"]]
    print(len(todo), "leads to write", flush=True)
    for i in range(0, len(todo), 2):
        batch = todo[i:i + 2]
        lines = "\n".join(f"- id {i_}: {label}. {brief}" for i_, label, brief in batch)
        prompt = ("Write one practice call per lead below. card = what the coach knows before the call (2-3 short lines). "
                  "secret = the lead's hidden truth, revealed after the call. turns = 7-9 turns that walk through the call "
                  "steps in order (client leads: steps 1-10 of the co-pilot, merging small steps; recruit leads: invite, "
                  "compliment, 'will you watch a video?', book the Zoom, follow-up), and the lead's REAL objection must show up. "
                  "Each turn: step (short name), lead (what the lead says, 1-3 sentences), options (exactly 3: scores 0, 1, 2 "
                  "in RANDOM order), tip (1 line coaching note after the turn). Then end_yes, end_no, lesson. "
                  "Every text has ms and en.\n\n" + lines)
        for attempt in range(2):
            try:
                res = call(prompt, obj({"leads": arr(LEAD)}))["leads"]
            except Exception as e:  # one retry per batch
                print("  retry:", e, flush=True)
                res = []
            for d in res:
                if any(d["id"] == b[0] for b in batch) and ok_lead(d):
                    have["leads"][d["id"]] = d
            if all(b[0] in have["leads"] for b in batch):
                break
        OUT.write_text(json.dumps(have, ensure_ascii=False, separators=(",", ":")))
        print(f"leads done {len(have['leads'])}", flush=True)

    todo = [(f"d{n + 1:02d}", t) for n, t in enumerate(DRILL_TOPICS) if f"d{n + 1:02d}" not in have["drills"]]
    for i in range(0, len(todo), 10):
        batch = todo[i:i + 10]
        prompt = ("Quick objection drills. For each id write: objection (what the lead/prospect says, natural, 1-2 sentences), "
                  "context (1 line: who says it and when in the call), options (exactly 3 coach replies, scores 0, 1, 2 in "
                  "RANDOM order, each with why). RECRUIT ones are a recruit invite chat, not a client call. "
                  "Every text has ms and en.\n\n" + "\n".join(f"- id {a}: {b}" for a, b in batch))
        for attempt in range(2):
            try:
                res = call(prompt, obj({"drills": arr(DRILL)}))["drills"]
            except Exception as e:
                print("  retry:", e, flush=True)
                res = []
            for d in res:
                if any(d["id"] == b[0] for b in batch) and good_opts(d["options"]):
                    have["drills"][d["id"]] = d
            if all(b[0] in have["drills"] for b in batch):
                break
        OUT.write_text(json.dumps(have, ensure_ascii=False, separators=(",", ":")))
        print(f"drills done {len(have['drills'])}", flush=True)
    meta = {i_: {"label": label, "brief": brief} for i_, label, brief in LEADS}
    have["meta"] = meta
    OUT.write_text(json.dumps(have, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    run()
