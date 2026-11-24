"""Fifth batch (24 Nov 2026): PRIVATE call pitch + likely objections for the coaches' call co-pilot.

  python seo/generate5.py pitch  -> private-out/pitch.json  (NOT committed: uploaded as an Actions artifact,
                                    then encrypted by plans-relay.yml, because it is a private sales script)
Key: "<path>|<zone 0-2>|<weakest side 0-2>|<budget 0-4>|<sex m/f/x>"  (gain: budget 0-2, sex x only)
"""
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate2 import S, arr, obj  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "private-out" / "pitch.json"
MODEL = os.environ.get("CONTENT_MODEL", "claude-opus-5-5")

SYSTEM = """You write PRIVATE sales-call scripts for Coach Kimi and Coach Zara (Malaysian husband-and-wife online fitness coaches, WeDoTransformations, Herbalife distributors). Only the coach sees these lines; the coach says them to a lead on a 15-30 minute call after the lead did the "Kenapa Berat Tak Turun?" quiz.
Voice (ms): Malaysian rojak the way Kimi talks on calls: "I" and "you", short sentences, BM with natural English words (plan, coach, check-in, goal, result, okay). Example: "Dari apa you cerita tadi, side you yang paling lemah ialah makan. Tu bukan sebab you malas." en: the same lines in simple, warm Malaysian English.
The program: 1-1 + group coaching, meal plan with normal Malaysian food (nasi, lauk, eating out), 20-minute home workouts, weekly check-in. Coaching is the SAME in every package; packages only differ in nutrition support (Herbalife):
- Starter RM259: 1x Formula 1 shake, 1 month (the price on the website, the floor, never go lower)
- Basic RM459: 2x Formula 1, 1 month
- Advance RM859: 2x F1 + Tea Mix + Aloe, up to 2 months (about RM430 a month)
- Premium RM1,259: 2x F1 + Tea Mix + Aloe + F3 + Fibre, up to 2 months (about RM630 a month)
- 4-month transformation RM3,259: normally RM5,000+, discounted when they start today; 4 months coaching + supplements (about RM27 a day); for big goals and commitment 8+
Payment: RM50 deposit today to lock a place, balance before the start date (DuitNow).
Rules:
- Pitch inside the lead's budget. Use the per-month or per-day figure where it helps. Compare with what they already spend (teh tarik, delivery) only lightly.
- Results differ person to person: never promise kg, a date or a result. No medical claims; health conditions -> check with their doctor first.
- Never claim the shake itself makes you lose or gain weight; it is a convenient, protein-rich meal or extra meal. The system (plan + coach + consistency) gives the result.
- Weight gain leads: shake = extra meal between meals with milk; do NOT push Tea Mix (caffeine blunts appetite); never say "gemuk".
- Never talk about income, the business opportunity or recruiting on a client call.
- If asked "MLM?": honest yes, Herbalife is direct selling, but they come as a coaching client, no selling targets.
- Never shame. No "gemuk" about the person. Women: privacy, no comments on looks. Men: ego-safe, numbers like waist and energy.
- Objections must be the ones THIS lead is most likely to raise given their zone, weakest side, budget and sex, each with 2-3 short lines the coach can say, ending by moving back to the close (YES or NO both okay)."""

BI = obj({"ms": S(), "en": S()})
SCHEMA = obj({"items": arr(obj({
    "key": S(),
    "angle": BI,                 # one-line frame for this lead (coach note)
    "pitch": arr(BI),            # 4 lines to say at step 8, in order: mirror their problem, the fix, the package + price, the close question
    "objections": arr(obj({"tag": BI, "lines": arr(BI)})),  # exactly 3
    "stepdown": BI,              # what to say if they hesitate on price
}))})

ZONES = ["On track (score 0-5): decent habits, no structure, weekends undo the week",
         "Running on empty (6-10): eats on the go or skips meals, sweet drinks, ~6 h sleep, lost weight then regained",
         "Burnout zone (11-15): skips meals then overeats at night, little water, lots of sweet drinks, under 6 h sleep, daily stress, gave up quickly before"]
SIDES = ["Nutrition (meals, drinks)", "Workout (no time, starts then stops)", "Mindset & Method (sleep, stress, no plan, gave up before)"]
BUDGETS = ["Under RM300", "RM300-RM500", "RM500-RM900", "RM900-RM1,300", "Above RM1,300 (wants the full transformation)"]
SEX = {"m": "a man", "f": "a woman", "x": "unknown sex (keep it neutral)"}


def package(path, zone, budget):
    if path == "gain":
        return ["Starter RM259", "Basic RM459 (fits most gainers)", "Basic RM459, Advance only if they ask for more"][budget]
    return ["Starter RM259 (floor)", "Basic RM459, step down to Starter",
            "Advance RM859 (~RM430/month), step down to Basic", "Premium RM1,259 (~RM630/month), step down to Advance",
            ("4-month transformation RM3,259 (~RM27/day), step down to Premium" if zone else "Premium RM1,259, or the 4-month RM3,259 if their goal is big")][budget]


def combos():
    out = []
    for z in range(3):
        for s in range(3):
            for b in range(5):
                for x in "mfx":
                    out.append((f"loss|{z}|{s}|{b}|{x}", "loss", z, s, b, x))
            for b in range(3):
                out.append((f"gain|{z}|{s}|{b}|x", "gain", z, s, b, "x"))
    return out


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


def ok(d):
    t = json.dumps(d, ensure_ascii=False).lower()
    return (len(d["pitch"]) >= 3 and len(d["objections"]) >= 3 and all(o["lines"] for o in d["objections"])
            and "gemuk" not in t and "jamin" not in t and "guarantee" not in t)


def run():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    have = json.loads(OUT.read_text()) if OUT.exists() else {}
    todo = [c for c in combos() if c[0] not in have]
    print(len(todo), "of", len(combos()), "to write", flush=True)
    for i in range(0, len(todo), 6):
        batch = todo[i:i + 6]
        lines = "\n".join(f"- key {k}: {'FAT LOSS' if p == 'loss' else 'WEIGHT GAIN (muscle)'} lead; {SEX[x]}; zone {ZONES[z]}; "
                          f"weakest side {SIDES[s]}; monthly budget {BUDGETS[b] if p == 'loss' else ['Under RM300', 'RM300-RM500', 'RM500 or more'][b]}; "
                          f"package to pitch: {package(p, z, b)}" for k, p, z, s, b, x in batch)
        prompt = ("For each key write the step-8 offer for the coach's call: angle (1 line, coach note), pitch (exactly 4 lines "
                  "to say, in order: mirror their problem in their life, how the program fixes their weakest side, the package "
                  "and price inside their budget, a YES-or-NO close question), objections (exactly 3 most likely for THIS lead, "
                  "tag = what the lead says in their words, lines = 2-3 replies), stepdown (1-2 lines if they hesitate on price; "
                  "for Starter-budget leads offer the RM50 deposit + balance before start instead of a cheaper package). "
                  "Make leads with different profiles really different. Every text has ms and en.\n\n" + lines)
        for attempt in range(2):
            try:
                res = call(prompt, SCHEMA)["items"]
                break
            except Exception as e:  # one retry per batch
                print("  retry:", e, flush=True)
                res = []
        for d in res:
            if any(d["key"] == b[0] for b in batch) and ok(d):
                have[d["key"]] = {"a": d["angle"], "p": d["pitch"][:4], "o": [{"t": o["tag"], "l": o["lines"][:3]} for o in d["objections"][:3]], "s": d["stepdown"]}
        OUT.write_text(json.dumps(have, ensure_ascii=False, separators=(",", ":")))
        print(f"done {len(have)}", flush=True)


if __name__ == "__main__":
    run()
