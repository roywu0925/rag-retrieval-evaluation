"""Roy's blind labelling worksheets for the stale-fact hand audit (rule section 6).

  .venv/bin/python scripts/make_audit_worksheets.py
    -> reports/audit/worksheet_1.md   all 36 MIXED / OLD_FLAGGED / OTHER answers
       reports/audit/worksheet_2.md   the 22 random answers (seed 0 draw, already fixed by analyze_stale.py)
       eval/stale_audit_worksheet_key.json   item -> answer record (NOT for Roy)

Blind: no fact id, condition, arm or rule class appears. Order is shuffled with SEED (recorded in the freeze log),
not grouped by fact, condition or arm. The answer shown is the text the rule classified, without the "Sources:"
line, which the rule never reads and which can reveal the condition.
Labels are the three headline buckets, because the 0.85 threshold is on buckets. X1 items (hallucination probe)
get X1's own three outcomes and are scored separately.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SEED = 20261106
OUT = ROOT / "reports/audit"
KEY = ROOT / "eval/stale_audit_worksheet_key.json"

# One-line value summaries for the labeller, from eval/stale_facts.json (old / current); SF4 and SF5 phrased to
# match their questions, X1 per its rule.
VALUES = {
 "SF1": ("No numeric accuracy spec is published; the measured positions are quantised to 0.01 yd, with no detectable noise above that step.",
         "A \"published accuracy range\" of 0.15-0.30 yd (also the uncited 0.17 yd and 0.25 yd figures)."),
 "SF2": ("p99 latency is 76-102 ms (76.2-101.7 ms).", "p99 latency is 68.9 ms."),
 "SF3": ("0.31 yd at the 1.9 s primary horizon; 1.51 yd at 3 s (full 18 weeks).",
         "About 0.9 yd (0.887 yd; week 1 only, 3 s horizon, 4.6% coverage)."),
 "SF4": ("The table values are week-1 only; on the full 18 weeks every value moves by less than 0.3 yd and the ordering is unchanged.",
         "The same week-1 values presented as if they were full-data values (no week-1 scope)."),
 "SF5": ("constant_acceleration, damped_velocity AND constant_position.",
         "Only constant_acceleration and damped_velocity."),
 "SF6": ("0.103 yd (floor) -> 0.147 (quadrature); the headline crossing is now 0.075 (tbl_kalman_speed vs constant_velocity).",
         "0.029 (week 1, 3 s horizon)."),
 "SF7": ("3.5% (394 of 11,254 tracks, full data).", "4.6% (24 of 526 tracks, week 1)."),
 "SF8": ("58% (25.68 vs 40.62 yd, primary horizon).", "51% (39.37 vs 59.57, week 1, 3 s horizon)."),
 "SF9": ("Signal 1 (input PSI) works as a monitor for K5; \"none is deployment-ready\" holds for K3 only.",
         "None of the four signals is deployment-ready."),
 "SF10": ("Tier 2 / Part 3 is complete: SageMaker endpoint latency was measured in us-west-2 and us-east-1.",
          "Tier 2 \"not started\"."),
 "SF11": ("K1-K5 have been trained and evaluated.", "Task K (the learned-model part) \"not started\"."),
 "X1": ("The documentation does not say what the 0.23 figure was corrected to.", "(none: nothing to supersede)"),
}

HEADER = """# Stale-fact answer audit: worksheet {w} of 2 ({n} answers)

{intro}

## How to label

Each block shows a question, what the documentation **currently** says, what it **used to** say, and one
model answer. Decide what a reader of the answer would come away believing, and tick **exactly one** box by
changing `[ ]` to `[x]`.

- **propagated**: a reader of this answer would come away believing the superseded value is current.
- **current**: a reader would come away with the right value.
- **neither**: the answer gives neither value clearly, or declines to answer.

If none of the three fits, tick the closest and say why on the `Note:` line. Notes are read, not scored.
Some answers may look alike or repeat; label each one on its own. Fact, model and condition are hidden on
purpose. Please don't look them up.

{x1}
---
"""
X1_NOTE = ("A few blocks ask about \"the 0.23 lag figure\". The documentation never says what it was corrected to, "
           "so those blocks have different boxes: **invents a replacement**, **says it isn't given**, or **other**.\n")


def block(i, n, rec, fact, question):
    cur, old = VALUES[fact]
    label = ("[ ] invents a replacement   [ ] says it isn't given   [ ] other" if fact == "X1"
             else "[ ] propagated   [ ] current   [ ] neither")
    return (f"### {i} of {n}\n\nQuestion: {question}\n\nCurrent value: {cur}\n\nSuperseded value: {old}\n\n"
            f"Answer:\n\n{rec}\n\nYour label: {label}\n\nNote:\n\n---\n")


def main():
    if KEY.exists():
        raise SystemExit(f"{KEY} exists; refusing to overwrite (worksheets may already be with Roy)")
    blind = [json.loads(l) for l in open(ROOT / "eval/stale_audit_blind.jsonl")]
    key = json.load(open(ROOT / "eval/stale_audit_key.json"))
    fragile = [i for i, k in enumerate(key) if k["rule_class"] in ("MIXED", "OLD_FLAGGED", "OTHER")]
    rest = [i for i in range(len(key)) if i not in fragile]
    assert (len(fragile), len(rest)) == (36, 22), (len(fragile), len(rest))
    rng = np.random.default_rng(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    wkey = []
    for w, ids, intro in (
        (1, fragile, "Do this one first."),
        (2, rest, "Do this one after worksheet 1."),
    ):
        order = [ids[j] for j in rng.permutation(len(ids))]
        has_x1 = any(blind[a]["fact"] == "X1" for a in order)
        txt = HEADER.format(w=w, n=len(order), intro=intro, x1=X1_NOTE if has_x1 else "")
        for pos, a in enumerate(order, 1):
            b = blind[a]
            txt += "\n" + block(pos, len(order), b["answer"], b["fact"], b["question"])
            wkey.append({"worksheet": w, "item": pos, "audit_id": a, "fact": b["fact"], **key[a]})
        (OUT / f"worksheet_{w}.md").write_text(txt)
    KEY.write_text(json.dumps(wkey, indent=1))
    for p in (OUT / "worksheet_1.md", OUT / "worksheet_2.md", KEY):
        print(p.relative_to(ROOT), hashlib.sha256(p.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
