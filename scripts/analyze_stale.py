"""Stale-fact analysis (no API calls). Implements reports/stale_fact_rule.md section 4 on logs/stale_answers.jsonl.

  .venv/bin/python scripts/analyze_stale.py      -> reports/stale_results.md + .json, and Roy's blind audit files

Unit = fact (SF1-SF11, n = 11; X1 is reported on its own). Denominator = ALL answers; the abstention rate is
reported separately. Test per mitigation versus baseline, within an arm: exact McNemar on the discordant facts,
Newcombe (method 10) 95% CI for the paired difference, and Holm-adjusted p-values over the 3 mitigations in the arm.
'corrections_doc' is reported as BASELINE REPEATS (its prompts equal baseline's) and is the per-arm noise floor.
It is not a mitigation test. Retrieval-limited facts SF3, SF10 and SF11 (fixed by the pre-run dry run) are excluded
in the second headline. S1 (MIXED -> neither) and S2 ("original" not a marker) are recomputed, and any change to
the mitigation ORDER within an arm is flagged as a finding.
"""
import json
from math import sqrt
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parent.parent
BUCKET = {"CURRENT": "current", "CURRENT_FLAGGED": "current", "MIXED": "propagated", "PROPAGATED": "propagated",
          "OLD_FLAGGED": "neither", "ABSTAIN": "neither", "OTHER": "neither"}
FACTS = [f"SF{i}" for i in range(1, 12)]
RETRIEVAL_LIMITED = {"SF3", "SF10", "SF11"}
MITIGATIONS = ["exclude_context", "recency_git"]          # tested; corrections_doc = repeats
CLASSES = ["CURRENT", "CURRENT_FLAGGED", "MIXED", "PROPAGATED", "OLD_FLAGGED", "ABSTAIN", "OTHER"]


def wilson(x, n, z=1.959964):
    if n == 0:
        return (np.nan, np.nan)
    p = x / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (c - h, c + h)


def newcombe10(a, b, c, d):
    """Paired difference p1 - p2 (baseline minus mitigation), where a = both propagated, b = base only,
    c = mitigation only, d = neither. Newcombe 1998 method 10."""
    n = a + b + c + d
    p1, p2 = (a + b) / n, (a + c) / n
    l1, u1 = wilson(a + b, n)
    l2, u2 = wilson(a + c, n)
    den = sqrt((a + b) * (c + d) * (a + c) * (b + d))
    phi = (a * d - b * c) / den if den else 0.0
    D = p1 - p2
    lo = D - sqrt(max(0.0, (p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2))
    hi = D + sqrt(max(0.0, (u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2))
    return D, lo, hi


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj


def main():
    A = [json.loads(l) for l in open(ROOT / "logs/stale_answers.jsonl")]
    arms = sorted({r["arm"] for r in A}, key=lambda a: ["haiku", "sonnet", "opus"].index(
        next(x for x in ["haiku", "sonnet", "opus"] if x in a)))
    conds = ["baseline", "exclude_context", "recency_git", "corrections_doc"]
    get = {(r["arm"], r["condition"], r["fact"]): r for r in A}
    out = {"rates": {}, "tests": {}, "noise": {}, "order_flags": [], "x1": {}, "crosstab": {}}
    L = ["# Stale-fact results (scripts/analyze_stale.py; rule: reports/stale_fact_rule.md, frozen)\n",
         "> **AUDIT VERDICT. Read this before any number below.** Every class, rate and test in this file is the "
         "frozen RULE's output. The pre-registered blind hand audit (reports/audit/agreement.md) found the rule wrong on "
         "31 of the 36 answers that drive its propagation count. Population agreement is 0.64, below the 0.85 threshold, so "
         "these results are RULE-DEPENDENT. The rule's pooled 39% propagation is about 10x the audited estimate of 4% "
         "(5/132; 95% upper bound 17%), and all 5 propagated answers are on the unmarked facts SF10 and SF11. "
         "See reports/finding_c_stale_facts.md.\n",
         "Descriptive by design (rule section 4): n = 11 facts per cell. A mitigation counts as an effect only if exact "
         "McNemar rejects. Abstention is measured under an explicit abstention instruction (upper bound).\n"]

    def bucket_of(r, line):
        if line == "S1":
            return "neither" if r["class"] == "MIXED" else BUCKET[r["class"]]
        if line == "S2":
            return BUCKET[r["S2_class"]]
        return BUCKET[r["class"]]

    # ---- rates
    L.append("## Rates per arm x condition (denominator = all answers)\n")
    L.append("| arm | condition | propagated (11) | propagated (8, excl. SF3/10/11) | current (11) | abstain (11) | S1 propagated | S2 propagated |")
    L.append("|---|---|---|---|---|---|---|---|")
    for arm in arms:
        for c in conds:
            rs = [get[(arm, c, f)] for f in FACTS]
            n = len(rs)
            prop = sum(bucket_of(r, "H") == "propagated" for r in rs)
            prop8 = sum(bucket_of(r, "H") == "propagated" for r in rs if r["fact"] not in RETRIEVAL_LIMITED)
            cur = sum(bucket_of(r, "H") == "current" for r in rs)
            ab = sum(r["class"] == "ABSTAIN" for r in rs)
            s1 = sum(bucket_of(r, "S1") == "propagated" for r in rs)
            s2 = sum(bucket_of(r, "S2") == "propagated" for r in rs)
            w = wilson(prop, n)
            out["rates"][f"{arm}|{c}"] = {"prop": prop, "prop8": prop8, "cur": cur, "abstain": ab, "S1": s1, "S2": s2,
                                         "n": n, "prop_wilson": w,
                                         "classes": {k: sum(r["class"] == k for r in rs) for k in CLASSES}}
            tag = " (repeats of baseline)" if c == "corrections_doc" else ""
            L.append(f"| {arm.split('.')[-1][:24]} | {c}{tag} | {prop}/11 [{100 * w[0]:.0f}-{100 * w[1]:.0f}%] | {prop8}/8 | "
                     f"{cur}/11 | {ab}/11 | {s1}/11 | {s2}/11 |")

    # ---- class counts
    L.append("\n## All seven classes\n")
    L.append("| arm | condition | " + " | ".join(CLASSES) + " |")
    L.append("|---|---|" + "---|" * len(CLASSES))
    for arm in arms:
        for c in conds:
            cl = out["rates"][f"{arm}|{c}"]["classes"]
            L.append(f"| {arm.split('.')[-1][:24]} | {c} | " + " | ".join(str(cl[k]) for k in CLASSES) + " |")

    # ---- paired tests
    L.append("\n## Mitigation vs baseline, paired over the 11 facts (exact McNemar; Newcombe CI; Holm within arm)\n")
    L.append("| arm | mitigation | fixed | broken | stayed prop. | stayed not | drop in propagation [95% CI] | p | p Holm | effect? |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for arm in arms:
        ps, rows = [], []
        for m in MITIGATIONS:
            a = b = c_ = d = 0
            for f in FACTS:
                x = BUCKET[get[(arm, "baseline", f)]["class"]] == "propagated"
                y = BUCKET[get[(arm, m, f)]["class"]] == "propagated"
                a += x and y; b += x and not y; c_ += (not x) and y; d += (not x) and (not y)
            p = binomtest(b, b + c_, 0.5).pvalue if b + c_ else 1.0
            D, lo, hi = newcombe10(a, b, c_, d)
            ps.append(p)
            rows.append((m, a, b, c_, d, D, lo, hi, p))
        for (m, a, b, c_, d, D, lo, hi, p), ph in zip(rows, holm(ps)):
            out["tests"][f"{arm}|{m}"] = {"fixed": b, "broken": c_, "both": a, "neither": d, "drop": D, "ci": [lo, hi],
                                         "p": p, "p_holm": ph}
            L.append(f"| {arm.split('.')[-1][:24]} | {m} | {b} | {c_} | {a} | {d} | {100 * D:+.0f} pts "
                     f"[{100 * lo:+.0f}, {100 * hi:+.0f}] | {p:.3f} | {ph:.3f} | {'YES' if ph < 0.05 else 'no (direction only)'} |")
    L.append("\nAt n = 11 the smallest rejecting outcome is 6 fixed / 0 broken. 'No' means this design could not "
             "detect it, not that there is no effect.")

    # ---- order flags (S1, S2)
    for arm in arms:
        def order(line):  # WEAK ordering: the sign of every pairwise comparison (ties stay ties)
            v = {c: sum(bucket_of(get[(arm, c, f)], line) == "propagated" for f in FACTS) for c in ["baseline"] + MITIGATIONS}
            cs = ["baseline"] + MITIGATIONS
            return [int(np.sign(v[x] - v[y])) for i, x in enumerate(cs) for y in cs[i + 1:]], v
        h, hv = order("H")
        for line in ("S1", "S2"):
            s, sv = order(line)
            if s != h:
                out["order_flags"].append({"arm": arm, "line": line, "headline": hv, "sensitivity": sv})
    L.append("\n## Sensitivity lines: does the mitigation ORDER change?\n")
    if out["order_flags"]:
        L.append("**FINDING: the ordering changes under a sensitivity line** (rule section 2, reported in the main text):")
        for f in out["order_flags"]:
            L.append(f"- {f['arm']}: {f['line']} gives {f['sensitivity']} vs headline {f['headline']}")
    else:
        L.append("No arm's mitigation ordering changes under S1 or S2.")

    # ---- noise floor
    L.append("\n## Noise floor: corrections_doc answers are repeats of baseline (identical prompts)\n")
    L.append("| arm | prompts identical | answers differ textually | answers change class |")
    L.append("|---|---|---|---|")
    for arm in arms:
        ids = sum(get[(arm, "baseline", f)]["prompt_sha256"] == get[(arm, "corrections_doc", f)]["prompt_sha256"] for f in FACTS + ["X1"])
        txt = sum(get[(arm, "baseline", f)]["answer"] != get[(arm, "corrections_doc", f)]["answer"] for f in FACTS + ["X1"])
        cls = sum(get[(arm, "baseline", f)]["class"] != get[(arm, "corrections_doc", f)]["class"] for f in FACTS + ["X1"])
        out["noise"][arm] = {"identical_prompts": ids, "text_diff": txt, "class_diff": cls}
        L.append(f"| {arm.split('.')[-1][:24]} | {ids}/12 | {txt}/12 | {cls}/12 |")
    L.append("\nThe Haiku stability check (two baseline runs before the main run): 0/12 textual, 0/12 class changes.")

    # ---- marked vs unmarked, retrieval cross-tab
    L.append("\n## Marked (SF1-SF9) vs unmarked (SF10, SF11) facts: propagated count\n")
    L.append("| arm | condition | marked (of 9) | unmarked (of 2) |")
    L.append("|---|---|---|---|")
    for arm in arms:
        for c in ["baseline"] + MITIGATIONS:
            mk = sum(BUCKET[get[(arm, c, f)]["class"]] == "propagated" for f in FACTS[:9])
            um = sum(BUCKET[get[(arm, c, f)]["class"]] == "propagated" for f in ("SF10", "SF11"))
            L.append(f"| {arm.split('.')[-1][:24]} | {c} | {mk} | {um} |")
    L.append("\n## Retrieval class x answer bucket (all arms, per condition)\n")
    for c in ["baseline"] + MITIGATIONS:
        tab = {}
        for r in A:
            if r["condition"] == c and r["fact"] in FACTS:
                k = (r["retrieval_class"], BUCKET[r["class"]])
                tab[k] = tab.get(k, 0) + 1
        out["crosstab"][c] = {f"{a}|{b}": v for (a, b), v in tab.items()}
        L.append(f"- {c}: " + ", ".join(f"{a}->{b}: {v}" for (a, b), v in sorted(tab.items())))

    # ---- X1 and per-fact
    L.append("\n## X1 (hallucination probe)\n")
    for arm in arms:
        L.append(f"- {arm.split('.')[-1]}: " + ", ".join(f"{c}={get[(arm, c, 'X1')]['class']}" for c in conds))
    L.append("\n## Per fact (class per arm, baseline / exclude_context / recency_git)\n")
    L.append("| fact | retrieval at baseline | " + " | ".join(a.split('.')[-1][:18] for a in arms) + " |")
    L.append("|---|---|" + "---|" * len(arms))
    for f in FACTS:
        rc = get[(arms[0], "baseline", f)]["retrieval_class"]
        L.append(f"| {f}{' (retrieval-limited)' if f in RETRIEVAL_LIMITED else ''} | {rc} | " + " | ".join(
            " / ".join(get[(arm, c, f)]["class"] for c in ["baseline"] + MITIGATIONS) for arm in arms) + " |")

    # ---- Roy's blind audit (rule section 6)
    rng = np.random.default_rng(0)
    fragile = [r for r in A if r["class"] in ("MIXED", "OLD_FLAGGED", "OTHER")]
    rest = [r for r in A if r["class"] not in ("MIXED", "OLD_FLAGGED", "OTHER")]
    pick = fragile + [rest[i] for i in sorted(rng.choice(len(rest), size=round(0.2 * len(rest)), replace=False))]
    blind = [{"audit_id": i, "fact": r["fact"], "question": None, "answer": r["answer"].split("Sources:")[0].strip()}
             for i, r in enumerate(pick)]
    pats = json.loads((ROOT / "eval/stale_patterns.json").read_text())
    for b in blind:
        b["question"] = pats["facts"][b["fact"]]["question"]
    if not (ROOT / "eval/stale_audit_blind.jsonl").exists():  # fixed sample; the worksheets depend on it
      (ROOT / "eval/stale_audit_blind.jsonl").write_text("\n".join(json.dumps(b, ensure_ascii=False) for b in blind) + "\n")
      (ROOT / "eval/stale_audit_key.json").write_text(json.dumps(
        [{"audit_id": i, "arm": r["arm"], "condition": r["condition"], "rule_class": r["class"]} for i, r in enumerate(pick)], indent=1))
    L.append(f"\n## Hand audit (rule section 6)\n\n{len(blind)} answers for Roy, blind to the rule's class: all "
             f"{len(fragile)} MIXED/OLD_FLAGGED/OTHER + 20% ({len(pick) - len(fragile)}) of the rest, seed 0. "
             "File: eval/stale_audit_blind.jsonl (key held separately). The rule's output stays the headline.")
    (ROOT / "reports/stale_results.md").write_text("\n".join(L) + "\n")
    (ROOT / "reports/stale_results.json").write_text(json.dumps(out, indent=1, default=str))
    print("\n".join(L))


if __name__ == "__main__":
    main()
