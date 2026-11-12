"""Propagation rate, rule vs hand audit, recomputed from the raw files (no API calls, no hardcoded values).

  .venv/bin/python scripts/audit_propagation_rate.py   -> stdout + reports/audit/propagation_rate.json

This figure was previously a hardcoded string with no script. When it was
reconstructed, the wrong estimator was initially specified (x78, 14.7%)
because nothing recorded which one produced the published 17%. That is
the reason this script exists.

Inputs: logs/stale_answers.jsonl (the 144 answers and the rule's classes), eval/stale_audit_key.json (the fixed
58-answer audit draw), eval/stale_audit_worksheet_key.json (worksheet item -> audit_id) and Roy's filled-in
reports/audit/worksheet_{1,2}.md, parsed with scripts/score_audit.py's own parser.

Population: the 132 fact answers (SF1-SF11; the 12 X1 answers are scored separately and excluded). Two strata, as
drawn by scripts/analyze_stale.py and pre-registered in reports/stale_fact_rule.md section 6:
  - census: every answer the rule classed MIXED / OLD_FLAGGED / OTHER, all hand-labelled;
  - random: every other fact answer; a seed-0 random draw of it was hand-labelled.

Estimates of the share of answers that would leave a reader believing a superseded value is current:
  - rule:   rule-propagated (MIXED + PROPAGATED) / 132
  - point:  (census propagated + random-sample propagated) / 132
            (the random sample has 0 propagated, so the point estimate needs no extrapolation)
  - upper (published, conservative): (census propagated + p_upper x ALL random-stratum answers) / 132
  - upper sensitivity: (census propagated + sample propagated + p_upper x UNSAMPLED random answers) / 132,
            which treats the hand-labelled sample answers as known (0) rather than uncertain
  p_upper = TWO-SIDED 95% Clopper-Pearson upper limit for the random sample's hand-labelled proportion
            (= one-sided 97.5%). The one-sided 95% limit is reported alongside for reference.
"""
import json
import sys
from pathlib import Path

from scipy.stats import beta

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import score_audit  # noqa: E402  (shared worksheet parser and rule-class -> bucket map)

FRAGILE = ("MIXED", "OLD_FLAGGED", "OTHER")
OUT = ROOT / "reports/audit/propagation_rate.json"


def cp_upper(x, n, conf):
    """Clopper-Pearson upper limit at one-sided level `conf`."""
    return 1.0 if x >= n else float(beta.ppf(conf, x + 1, n - x))


def main():
    answers = [json.loads(l) for l in open(ROOT / "logs/stale_answers.jsonl")]
    facts = [a for a in answers if a["fact"] != "X1"]
    n = len(facts)
    rule_prop = sum(score_audit.BUCKET[a["class"]] == "propagated" for a in facts)
    n_census_pop = sum(a["class"] in FRAGILE for a in facts)
    n_random_pop = n - n_census_pop

    audit_key = json.load(open(ROOT / "eval/stale_audit_key.json"))
    by_id = {k["audit_id"]: k for k in audit_key}
    wkey = json.load(open(ROOT / "eval/stale_audit_worksheet_key.json"))
    sheets = {w: score_audit.parse(ROOT / f"reports/audit/worksheet_{w}.md") for w in (1, 2)}
    labels = {"census": [], "random": []}
    for k in wkey:
        if k["fact"] == "X1":
            continue
        ak = by_id[k["audit_id"]]
        assert (ak["arm"], ak["condition"], ak["rule_class"]) == (k["arm"], k["condition"], k["rule_class"]), k
        stratum = "census" if ak["rule_class"] in FRAGILE else "random"
        assert stratum == ("census" if k["worksheet"] == 1 else "random"), k
        ticks = sheets[k["worksheet"]][k["item"]]["ticks"]
        if len(ticks) != 1:
            raise SystemExit(f"worksheet {k['worksheet']} item {k['item']}: expected exactly one tick, got {ticks}")
        labels[stratum].append(ticks[0])
    n_census_lab, n_random_lab = len(labels["census"]), len(labels["random"])
    if n_census_lab != n_census_pop:
        raise SystemExit(f"census stratum: {n_census_lab} labelled of {n_census_pop}; a census must be complete")
    x_census = labels["census"].count("propagated")
    x_random = labels["random"].count("propagated")
    n_unsampled = n_random_pop - n_random_lab

    p_up_2s = cp_upper(x_random, n_random_lab, 0.975)
    p_up_1s = cp_upper(x_random, n_random_lab, 0.95)
    point_num = x_census + x_random
    upper_num = x_census + p_up_2s * n_random_pop
    upper_num_1s = x_census + p_up_1s * n_random_pop
    sens_num = x_census + x_random + p_up_2s * n_unsampled

    res = {
        "population": {"fact_answers": n, "excluded_x1_answers": len(answers) - n},
        "strata": {
            "census": {"definition": "rule class MIXED / OLD_FLAGGED / OTHER", "population": n_census_pop,
                       "hand_labelled": n_census_lab, "hand_propagated": x_census},
            "random": {"definition": "all other fact answers; seed-0 random draw labelled", "population": n_random_pop,
                       "hand_labelled": n_random_lab, "hand_propagated": x_random, "not_sampled": n_unsampled},
        },
        "rule_rate": {"numerator": rule_prop, "denominator": n, "rate": rule_prop / n},
        "hand_point_estimate": {"numerator": point_num, "denominator": n, "rate": point_num / n},
        "p_upper_two_sided_95_clopper_pearson": p_up_2s,
        "hand_upper_bound_two_sided_95": {
            "formula": "(census hand_propagated + p_upper_two_sided_95_clopper_pearson x random population) / fact_answers",
            "numerator": upper_num, "denominator": n, "rate": upper_num / n,
            "note": "Published bound. Chosen because it is the more conservative: the labelled random-sample answers "
                    "are treated as uncertain too."},
        "reference_one_sided_95": {
            "p_upper_one_sided_95_clopper_pearson": p_up_1s,
            "hand_upper_bound_rate": upper_num_1s / n},
        "sensitivity_upper_bound_treating_18_labelled_random_as_known_zero": {
            "formula": "(census hand_propagated + random hand_propagated + p_upper_two_sided_95_clopper_pearson x "
                       "random not_sampled) / fact_answers",
            "numerator": sens_num, "denominator": n, "rate": sens_num / n},
    }
    OUT.write_text(json.dumps(res, indent=1) + "\n")

    print(f"Population: {n} fact answers ({len(answers) - n} X1 answers excluded)\n")
    print(f"Census stratum (rule class MIXED / OLD_FLAGGED / OTHER): {n_census_pop} answers, "
          f"{n_census_lab} hand-labelled, {x_census} propagated")
    print(f"Random stratum (all other fact answers):               {n_random_pop} answers, "
          f"{n_random_lab} hand-labelled, {x_random} propagated, {n_unsampled} not sampled\n")
    print(f"Rule rate:            {rule_prop} / {n} = {rule_prop / n:.4f}")
    print(f"Hand point estimate:  ({x_census} + {x_random}) / {n} = {point_num} / {n} = {point_num / n:.4f}")
    print(f"p_upper, two-sided 95% Clopper-Pearson, {x_random}/{n_random_lab}: {p_up_2s:.4f}")
    print(f"Hand upper bound, two-sided 95% (published; conservative):")
    print(f"  ({x_census} + {p_up_2s:.4f} x {n_random_pop}) / {n} = {upper_num:.3f} / {n} = {upper_num / n:.4f}")
    print(f"Reference, one-sided 95%: p_upper = {p_up_1s:.4f}; "
          f"({x_census} + {p_up_1s:.4f} x {n_random_pop}) / {n} = {upper_num_1s / n:.4f}")
    print(f"Sensitivity, treating the {n_random_lab} labelled random answers as known {x_random}:")
    print(f"  ({x_census} + {x_random} + {p_up_2s:.4f} x {n_unsampled}) / {n} = {sens_num:.3f} / {n} = {sens_num / n:.4f}")
    print(f"\n-> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
