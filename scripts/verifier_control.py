"""(1) Verify the two questions that were falsely dropped by the old norm() (instrument bug, fixed 2026-11-06).
(2) Positive control for the verifier: questions that SHOULD be judged not answerable from the section shown.

Controls are sent through the verifier UNCHANGED (same VERIFY_PROMPT, tool, model, maxTokens as gen_tier_a.py).
Two kinds:
  swap  : a kept Tier A question (gold = section X) shown with an unrelated section Y. Before any call, the answer
          key string is checked to be ABSENT from Y (label check, allowed: no answering from the corpus).
  absent: a question whose answer the corpus does not contain, shown with the most tempting section.
          'near-miss' = the section holds related numbers, but not the asked quantity.
The full filter (verifier says answerable AND its quote is verbatim) is reported next to the raw verdict.

  .venv/bin/python scripts/verifier_control.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.argv = sys.argv[:1]
from scripts.gen_tier_a import MODEL_ID, VERIFY_PROMPT, VERIFY_TOOL, body, converse, norm  # noqa: E402
from rag.sections import REGISTRY  # noqa: E402

OUT = ROOT / "eval/verifier_control.jsonl"


def sec(file, path):
    return REGISTRY[(file, path)]


def text_of(s):
    return f"[{s.file} > {s.path}]\n{body(s)}"


KEPT = [json.loads(l) for l in open(ROOT / "eval/tier_a.jsonl")]
RAW = [json.loads(l) for l in open(ROOT / "eval/tier_a_raw.jsonl")]


def kept_q(prefix):
    (q,) = [q for q in KEPT if q["question"].startswith(prefix)]
    return q


SWAPS = [  # (question prefix, answer key that must be absent from host, host section)
    ("How many trainable parameters", "18,050", ("CONTEXT.md", "Working style notes")),
    ("What is the peak memory usage", "565", ("README.md", "Limitations")),
    ("In the project's repository layout, what is the file size", "148", ("PART1_DETAIL.md", "Baselines")),
    ("When batching 22 players", "17.0", ("CONTEXT.md", "Decisions already taken")),
]
ABSENT = [  # (question, host section, kind)
    ("Which NFL team's plays had the highest mean displacement error for the K5 model in the 2023 season?",
     ("README.md", "Part 2 — the learned models"), "absent"),
    ("What was the total AWS bill for running the SageMaker endpoint over the full 2024 NFL season?",
     ("README.md", "Part 3 — serving latency and cost"), "absent, near-miss"),
]


def main():
    if OUT.exists():
        raise SystemExit(f"{OUT} exists; refusing to overwrite")
    jobs = []
    for r in RAW:  # (1) the two re-admitted questions, verified against their OWN section
        s = sec(r["file"], r["section"])
        for q in r["response"]["questions"][:r["requested"]]:
            if q["question"] not in {k["question"] for k in KEPT} and norm(q["evidence_quote"]) in norm(text_of(s)):
                jobs.append({"kind": "readmit", "question": q["question"], "host": s.id, "gen": q,
                             "expected": "answerable"})
    assert len(jobs) == 2, jobs
    for prefix, key, host in SWAPS:  # (2) controls
        q, h = kept_q(prefix), sec(*host)
        assert key not in body(h), f"control invalid: {key!r} occurs in host {host}"
        jobs.append({"kind": "swap", "question": q["question"], "host": h.id,
                     "true_gold": [q["gold_file"], q["gold_section"]], "expected": "NOT answerable"})
    for question, host, kind in ABSENT:
        jobs.append({"kind": kind, "question": question, "host": sec(*host).id, "expected": "NOT answerable"})

    import boto3
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    tin = tout = 0
    for j in jobs:
        t = text_of(sec(*j["host"]))
        try:
            v, u = converse(client, VERIFY_PROMPT.format(text=t, question=j["question"]), VERIFY_TOOL, 600)
        except Exception as e:
            raise SystemExit(f"STOPPED on {j['kind']}: {type(e).__name__}: {e}")
        tin, tout = tin + u["inputTokens"], tout + u["outputTokens"]
        j["verifier"] = v
        j["says_answerable"] = bool(v.get("answerable_from_section_alone"))
        j["quote_verbatim"] = norm(v.get("evidence_quote", "")) in norm(t) if v.get("evidence_quote") else False
        j["passes_full_filter"] = j["says_answerable"] and j["quote_verbatim"]
        j["model"] = MODEL_ID
        with open(OUT, "a") as f:
            f.write(json.dumps(j, ensure_ascii=False) + "\n")
        print(f"{j['kind']:18s} answerable={j['says_answerable']!s:5s} quote_ok={j['quote_verbatim']!s:5s} "
              f"filter={'PASS' if j['passes_full_filter'] else 'REJECT'}  host={j['host'][1][:40]}  "
              f"q={j['question'][:70]}")
    print(f"tokens in {tin} out {tout}  cost ${tin * 3.30e-6 + tout * 16.50e-6:.4f}")


if __name__ == "__main__":
    main()
