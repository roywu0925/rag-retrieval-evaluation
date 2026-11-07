"""Constructed answers (written by hand, NOT model outputs) that pin what each pattern must do.
These test the instrument before freeze; they are not tuned on stale-fact answers (none exist)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rag.stale_classify import BUCKET, classify, load  # noqa: E402

P, _ = load()

CASES = [
    # SF1 NGS accuracy
    ("SF1", "NGS positions are accurate to 0.15-0.30 yd.", "PROPAGATED"),
    ("SF1", "The 0.15–0.30 yd range was unsourced; no numeric spec is published and the data are quantised to 0.01 yd.", "CURRENT_FLAGGED"),
    ("SF1", "No published specification exists; positions are quantized to 0.01 yards.", "CURRENT"),
    ("SF1", "The Kalman filter assumes 0.25 yd position noise.", "PROPAGATED"),
    # SF2 p99
    ("SF2", "The p99 latency is 68.9 ms, comfortably inside budget.", "PROPAGATED"),
    ("SF2", "p99 is 76–102 ms.", "CURRENT"),
    ("SF2", "The p99 latency was measured at 88.4 ms.", "CURRENT"),
    ("SF2", "An earlier single run reported 68.9 ms; corrected, p99 is 76.2-101.7 ms.", "CURRENT_FLAGGED"),
    ("SF2", "p99 is 68.9 ms, though other runs gave 76-102 ms.", "MIXED"),
    # SF3 destination info
    ("SF3", "Destination info is worth about 0.887 yd.", "PROPAGATED"),
    ("SF3", "It improves error by 0.31 yd at 1.9 s and 1.51 yd at 3 s.", "CURRENT"),
    ("SF3", "Knowing the landing spot is worth ~0.9 yd.", "PROPAGATED"),
    # SF4 scoped table
    ("SF4", "Defensive Coverage 2.707 yd, Targeted Receiver 1.174 yd.", "PROPAGATED"),
    ("SF4", "On week 1 data: 2.707 yd for Defensive Coverage and 1.174 yd for Targeted Receiver.", "CURRENT_FLAGGED"),
    ("SF4", "2.707 and 1.174 yd; on the full 18 weeks values move by less than 0.3 yd.", "MIXED"),
    # SF5 role-split exceptions
    ("SF5", "Every baseline except constant_acceleration and damped_velocity has lower Targeted Receiver error.", "PROPAGATED"),
    ("SF5", "The exceptions are constant_acceleration, damped_velocity and constant_position.", "CURRENT"),
    # SF6 crossing sigma
    ("SF6", "The Kalman filter overtakes constant velocity at sigma = 0.029.", "PROPAGATED"),
    ("SF6", "At the 1.9 s horizon the crossing is 0.103 yd (0.147 under quadrature).", "CURRENT"),
    ("SF6", "On week 1 data the crossing was 0.029.", "PROPAGATED"),          # 'week 1' is NOT a marker (rev 2)
    ("SF6", "The crossing was originally 0.029 but is now 0.103 yd.", "CURRENT_FLAGGED"),
    # SF7 coverage
    ("SF7", "Only 4.6% of tracks (24 of 526) reach 3 s.", "PROPAGATED"),
    ("SF7", "3.5% of tracks (394 of 11,254) survive to 3 s.", "CURRENT"),
    # SF8 IMM margin
    ("SF8", "IMM beats kalman_ca by 51%.", "PROPAGATED"),
    ("SF8", "IMM (25.68 yd) beats kalman_ca (40.62 yd) by 58%.", "CURRENT"),
    ("SF8", "The original week-1 estimate was 51%.", "OLD_FLAGGED"),           # rev 3: 'original' is a marker
    # SF9 Tier 2A
    ("SF9", "None of the four signals is deployment-ready.", "PROPAGATED"),
    ("SF9", "Yes: Signal 1 (input PSI) works as a monitor for K5, leading the failure by 0.830 yd.", "CURRENT"),
    ("SF9", "The first-pass report said none of the four signals was ready; corrected, input PSI works for K5.", "CURRENT_FLAGGED"),
    # SF10 Tier 2 status
    ("SF10", "Tier 2 has not started.", "PROPAGATED"),
    ("SF10", "Yes. Tier 2 serving latency was measured on a SageMaker endpoint in us-west-2 and us-east-1.", "CURRENT"),
    ("SF10", "Tier 2 has not started; the plan is a SageMaker endpoint for serving.", "MIXED"),
    ("SF10", "The documents do not say.", "ABSTAIN"),
    ("SF10", "Tier 2 latency has not been measured.", "MIXED"),       # negated completion = old status
    ("SF10", "Tier 2 hasn't been done.", "MIXED"),
    # SF11 Task K
    ("SF11", "Task K, the learned-model part, has not started.", "PROPAGATED"),
    ("SF11", "Yes, K1-K5 were trained and evaluated.", "CURRENT"),
    ("SF11", "Part 1 is complete but the learned-model part (Task K) is not started.", "MIXED"),
    ("SF11", "It's about the weather.", "OTHER"),
    ("SF11", "K5 has not been trained yet.", "MIXED"),
    # X1 probe
    ("X1", "It was corrected to 0.77 yd.", "HALLUCINATED"),
    ("X1", "The lag figure was corrected to 0.31.", "HALLUCINATED"),
    ("X1", "The documentation does not give the corrected value.", "CORRECT"),
    ("X1", "It was a lag figure.", "OTHER"),
]


def test_cases():
    bad = [(f, a, e, classify(a, f, P)) for f, a, e in CASES if classify(a, f, P) != e]
    for b in bad:
        print("FAIL", b)
    assert not bad, f"{len(bad)} of {len(CASES)} cases failed"


def test_every_fact_has_question_and_cases():
    assert set(P["facts"]) == {f"SF{i}" for i in range(1, 12)} | {"X1"}
    assert {c[0] for c in CASES} == set(P["facts"])
    assert all(P["facts"][f]["question"].endswith("?") for f in P["facts"])


def test_rev2_markers_removed():
    joined = " ".join(P["supersession_markers"])
    assert "week" not in joined and r"\bold\b" not in joined


def test_s2_without_original():
    drop = P["sensitivity_drop_markers"]["S2_without_original"]
    assert classify("The original week-1 estimate was 51%.", "SF8", P, drop) == "PROPAGATED"
    assert classify("The original 51% was replaced by 58%.", "SF8", P, drop) == "CURRENT_FLAGGED"


def test_buckets():
    assert BUCKET["MIXED"] == "propagated" and BUCKET["OLD_FLAGGED"] == "neither"


if __name__ == "__main__":
    test_cases(); test_every_fact_has_question_and_cases(); test_rev2_markers_removed(); test_s2_without_original(); test_buckets()
    print(f"ok: {len(CASES)} constructed cases, all facts covered")
