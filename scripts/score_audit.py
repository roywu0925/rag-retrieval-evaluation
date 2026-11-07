"""Score Roy's filled-in worksheets against the rule (stale_fact_rule.md section 6). No API calls.

  .venv/bin/python scripts/score_audit.py            # scores whatever worksheets are filled; lists blanks

Per worksheet and combined, on the 11 stale facts (X1 scored separately):
  - raw agreement and Cohen's kappa on the three headline buckets (rule bucket vs Roy's bucket);
  - confusion matrix: rule's own 7 classes (rows) x Roy's 3 buckets (columns);
  - a population estimate of agreement over all 132 fact answers. Worksheet 1 is a census of the fragile
    classes and worksheet 2 a random sample of the rest, so the strata are weighted by their population sizes.
Threshold (pre-registered): headline-bucket agreement < 0.85 -> results are labelled "rule-dependent", with Roy's
rates shown beside them. The RULE's output stays the headline either way.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUCKET = {"CURRENT": "current", "CURRENT_FLAGGED": "current", "MIXED": "propagated", "PROPAGATED": "propagated",
          "OLD_FLAGGED": "neither", "ABSTAIN": "neither", "OTHER": "neither"}
X1MAP = {"invents a replacement": "HALLUCINATED", "says it isn't given": "CORRECT", "other": "OTHER"}
B3 = ["propagated", "current", "neither"]
QUESTIONS = {f: v["question"] for f, v in json.loads((ROOT / "eval/stale_patterns.json").read_text())["facts"].items()}
CLASSES = ["CURRENT", "CURRENT_FLAGGED", "MIXED", "PROPAGATED", "OLD_FLAGGED", "ABSTAIN", "OTHER"]


def parse(path):
    txt = Path(path).read_text()
    out = {}
    # tolerant of pasting: '### 1 of 36' or '1 of 22' headings; '[x]', '[ x]', '[x ]', '[X]' ticks
    head = r"^(?:#+\s*)?(\d+) of \d+\s*$"
    for m in re.finditer(head + r"\n(.*?)(?=" + head + r"|\Z)", txt, re.S | re.M):
        item, body = int(m.group(1)), m.group(2)
        lab = re.search(r"^Your label:\s*(.*)$", body, re.M).group(1)
        ticks = re.findall(r"\[\s*[xX]\s*\]\s*([^\[]+?)\s*(?=\[|$)", lab)
        note = re.search(r"^Note:(.*?)(?=^---|\Z)", body, re.S | re.M)
        q = re.search(r"^Question:\s*(.*)$", body, re.M)
        out[item] = {"ticks": [t.strip() for t in ticks], "note": note.group(1).strip() if note else "",
                     "question": q.group(1).strip() if q else None}
    return out


def kappa(pairs, cats):
    n = len(pairs)
    if n == 0:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[c] * cb[c] for c in cats) / n / n
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def main():
    key = json.load(open(ROOT / "eval/stale_audit_worksheet_key.json"))
    answers = [json.loads(l) for l in open(ROOT / "logs/stale_answers.jsonl")]
    n_fragile_pop = sum(a["class"] in ("MIXED", "OLD_FLAGGED", "OTHER") and a["fact"] != "X1" for a in answers)
    n_rest_pop = sum(a["class"] not in ("MIXED", "OLD_FLAGGED", "OTHER") and a["fact"] != "X1" for a in answers)
    rows, x1, problems, notes = {1: [], 2: []}, [], [], []
    for w in (1, 2):
        p = ROOT / f"reports/audit/worksheet_{w}.md"
        lab = parse(p)
        expect = {k["item"]: QUESTIONS[k["fact"]] for k in key if k["worksheet"] == w}
        for item, q in expect.items():  # guard: a reordered or mis-pasted block must not be scored silently
            if item in lab and lab[item]["question"] != q:
                raise SystemExit(f"worksheet {w} item {item}: question text does not match the key; refusing to score")
        for k in (k for k in key if k["worksheet"] == w):
            t = lab.get(k["item"], {"ticks": []})["ticks"]
            if len(t) != 1:
                problems.append(f"worksheet {w} item {k['item']}: {'no box ticked' if not t else 'more than one box ticked'}")
                continue
            if lab[k["item"]]["note"]:
                notes.append(f"w{w} #{k['item']}: {lab[k['item']]['note']}")
            if k["fact"] == "X1":
                x1.append((k["rule_class"], X1MAP[t[0]]))
            else:
                rows[w].append((k["rule_class"], t[0]))
    L = ["# Hand-audit agreement (scripts/score_audit.py)\n"]
    if problems:
        L.append(f"**{len(problems)} blocks not scorable yet** (exactly one box per block):")
        L += [f"- {p}" for p in problems[:60]]
        L.append("")
    for name, rs in (("Worksheet 1 (census of MIXED/OLD_FLAGGED/OTHER)", rows[1]), ("Worksheet 2 (random rest)", rows[2]),
                     ("Combined, unweighted", rows[1] + rows[2])):
        if not rs:
            continue
        pairs = [(BUCKET[c], r) for c, r in rs]
        agree = sum(a == b for a, b in pairs) / len(pairs)
        L.append(f"## {name}: n = {len(rs)}, agreement {agree:.2f}, Cohen's kappa {kappa(pairs, B3):.2f}\n")
        L.append("| rule class \\ Roy | " + " | ".join(B3) + " |")
        L.append("|---|" + "---|" * 3)
        for c in CLASSES:
            cnt = Counter(r for cc, r in rs if cc == c)
            if cnt:
                L.append(f"| {c} ({BUCKET[c]}) | " + " | ".join(str(cnt[b]) for b in B3) + " |")
        L.append("")
    if rows[1] and rows[2] and not problems:
        a1 = sum(BUCKET[c] == r for c, r in rows[1]) / len(rows[1])
        a2 = sum(BUCKET[c] == r for c, r in rows[2]) / len(rows[2])
        est = (a1 * n_fragile_pop + a2 * n_rest_pop) / (n_fragile_pop + n_rest_pop)
        L.append(f"**Population estimate of headline-bucket agreement over all {n_fragile_pop + n_rest_pop} fact answers "
                 f"(strata weighted {n_fragile_pop} / {n_rest_pop}): {est:.2f}.** Pre-registered threshold 0.85: "
                 + ("met; the rule's numbers stand as the headline." if est >= 0.85 else
                    "NOT met; the stale-fact results are labelled rule-dependent, with Roy's rates beside them.") + "\n")
    if x1:
        L.append(f"## X1 (scored separately): agreement {sum(a == b for a, b in x1)}/{len(x1)}; "
                 + ", ".join(f"rule {a} / Roy {b}" for a, b in x1) + "\n")
    if notes:
        L.append("## Roy's notes\n")
        L += [f"- {n}" for n in notes]
    (ROOT / "reports/audit/agreement.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
