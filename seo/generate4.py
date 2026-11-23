"""Fourth batch (23 Nov 2026): 3-day starter plans on the quiz result page.

  python seo/generate4.py starter  -> results/starter.json
Key: "<path>|<goal answer index>|<worst score question index>|<worst answer index>" (or "|none" when every answer scored 0).
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate import call  # noqa: E402
from generate2 import S, arr, clean, obj  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
Q = json.loads((ROOT / "seo" / "quizq.json").read_text())

BI = obj({"ms": S(), "en": S()})
SCHEMA = obj({"plans": arr(obj({
    "key": S(), "title": BI,
    "days": arr(obj({"focus": BI, "tasks": arr(BI)})),
    "day3": BI}))})


def combos():
    out = []
    for path in ("loss", "gain"):
        qs = Q[path]
        goals = [i for i, a in enumerate(qs[0]["a"]) if (a.get("v") == "gain") == (path == "gain")]
        for g in goals:
            for qi, q in enumerate(qs):
                if q["type"] != "score":
                    continue
                for ai, a in enumerate(q["a"]):
                    if a["s"]:
                        out.append((f"{path}|{g}|{qi}|{ai}", path, qs[0]["a"][g]["ms"], q["short"], q["q"], a["ms"]))
            out.append((f"{path}|{g}|none", path, qs[0]["a"][g]["ms"], "", "", "semua tabiat dah baik"))
    return out


def run():
    p = ROOT / "results" / "starter.json"
    have = json.loads(p.read_text()) if p.exists() else {}
    todo = [c for c in combos() if c[0] not in have]
    print(len(todo), "of", len(combos()), "to write", flush=True)
    for i in range(0, len(todo), 8):
        batch = todo[i:i + 8]
        lines = "\n".join(f"- key {k}: path {'fat loss' if pa == 'loss' else 'weight gain (muscle)'}; goal \"{g}\"; "
                          + (f"biggest problem habit ({sh}): asked \"{qq}\", answered \"{an}\"" if sh else "no bad habit, wants to go further")
                          for k, pa, g, sh, qq, an in batch)
        prompt = ("Quiz result page for Coach Kimi & Coach Zara (Malaysian working adults). For each key write a 3-DAY STARTER "
                  "PLAN that fixes their biggest problem habit first, fitted to their goal. Each day: a short focus and exactly 3 "
                  "small, concrete tasks (Malaysian food and life: mamak, nasi campur, teh tarik, bekal, office). Day 1 easiest. "
                  "day3 = one line asking them to WhatsApp their coach on day 3 with what they noticed. Give every text in casual "
                  "BM ('anda') as ms and simple Malaysian English as en. No products, supplements or brand names, no kg promises. "
                  "Weight gain: eat more often, protein, strength training; never say 'gemuk'.\n\n" + lines)
        for d in call(prompt, SCHEMA)["plans"]:
            if any(d["key"] == b[0] for b in batch) and clean(d) and len(d["days"]) == 3:
                have[d["key"]] = {"t": d["title"], "d": [{"f": x["focus"], "x": x["tasks"][:3]} for x in d["days"]], "e": d["day3"]}
        p.write_text(json.dumps(have, ensure_ascii=False, separators=(",", ":")))
        print(f"done {len(have)}", flush=True)


if __name__ == "__main__":
    run()
