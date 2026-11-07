"""Paired Tier A set: for each of Roy's 13 answerable Tier B questions (R), two machine questions on the SAME gold
section and the SAME fact. MC is Traditional Chinese and ME is English. Comparisons are within-pair:
  R vs MC   style, with language held constant
  MC vs ME  language, with style held constant
  R vs ME   the combined gap
Pre-registered power (scripts/power_paired.py) did NOT clear the 20-point bar, so the analysis is DESCRIPTIVE.

Fixed before generation:
  - The generator sees the fact (Tier B expected_answer, confirmed by Roy) and the gold section. It NEVER sees Roy's
    wording, so MC cannot be a paraphrase of R; R vs MC measures style, not copying.
  - The same filters as Tier A (scripts/gen_tier_a.py): (1) the evidence quote is verbatim in the section (fixed
    norm()); (2) no self-reference, using the English regex PLUS Chinese self-reference terms (ZH_SELF_REF);
    (3) the independent verifier sees only the section and must judge the question answerable, with a verbatim quote.
  - B14 (multi_section) is generated from its gold_section only, like the rest. Its pair can fail filter (3),
    which is reported and never worked around.
  - Machine questions inherit R's gold labels (gold, also_acceptable, required_all, category), so each pair is
    scored by the same rule.
  - Dropped questions are not replaced.

  .venv/bin/python scripts/gen_paired.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.argv = sys.argv[:1]
from scripts.gen_tier_a import (MODEL_ID, PRICE_IN, PRICE_OUT, SELF_REF, VERIFY_PROMPT, VERIFY_TOOL,  # noqa: E402
                                body, converse, norm)
from rag.sections import REGISTRY, load_eval_set  # noqa: E402

OUT, RAW, DROPPED = (ROOT / p for p in ("eval/tier_a_paired.jsonl", "eval/tier_a_paired_raw.jsonl",
                                        "eval/tier_a_paired_dropped.json"))
ZH_SELF_REF = re.compile(r"本節|這一節|這節|本段|這段|上文|上述|以上|下文|本文|此段|該段|這份文件|文件中")

PAIRED_PROMPT = """You are writing evaluation questions for a retrieval system over a project's documentation.

Below is one section of the documentation (file: {file}; section: {path}) and one fact that the section states.

Write two questions that each ask for this fact:
- "zh": written in Traditional Chinese
- "en": written in English
Each question must be answerable from this section alone and self-contained: a reader who has not seen the section must understand what is being asked. Do not refer to "this section", "the text", "above", etc.
For each, give the short answer and an evidence_quote copied verbatim from the section (a contiguous span, max ~40 words) that supports the answer.

<fact>{fact}</fact>

<section>
{text}
</section>"""

PAIRED_TOOL = {"toolSpec": {"name": "submit_pair", "description": "Submit the two questions.",
    "inputSchema": {"json": {"type": "object", "properties": {lang: {"type": "object", "properties": {
        "question": {"type": "string"}, "answer": {"type": "string"}, "evidence_quote": {"type": "string"}},
        "required": ["question", "answer", "evidence_quote"]} for lang in ("zh", "en")},
        "required": ["zh", "en"]}}}}


def main():
    for p in (OUT, RAW):
        if p.exists():
            raise SystemExit(f"{p} exists; refusing to overwrite")
    rs = [q for q in load_eval_set(ROOT / "eval/tier_b.jsonl") if q["category"] not in ("unanswerable", "unsettled")]
    assert len(rs) == 13, len(rs)
    import boto3
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    kept, dropped, tin, tout = [], [], 0, 0
    for r in rs:
        sec = REGISTRY[(r["gold_file"], r["gold_section"])]
        text = f"[{sec.file} > {sec.path}]\n{body(sec)}"
        try:
            g, u = converse(client, PAIRED_PROMPT.format(file=sec.file, path=sec.path, fact=r["expected_answer"],
                                                         text=text), PAIRED_TOOL, 1200)
        except Exception as e:
            raise SystemExit(f"STOPPED on generation for {r['id']}: {type(e).__name__}: {e}")
        tin, tout = tin + u["inputTokens"], tout + u["outputTokens"]
        with open(RAW, "a") as f:
            f.write(json.dumps({"pair_of": r["id"], "response": g}, ensure_ascii=False) + "\n")
        for lang, tag in (("zh", "MC"), ("en", "ME")):
            q = g.get(lang)
            if not q:
                dropped.append({"pair_of": r["id"], "variant": tag, "reason": "generator returned no question"})
                continue
            reason = None
            if norm(q["evidence_quote"]) not in norm(text):
                reason = "generator evidence quote not verbatim in section"
            elif SELF_REF.search(q["question"]) or ZH_SELF_REF.search(q["question"]):
                reason = "self-referential wording"
            else:
                try:
                    v, u = converse(client, VERIFY_PROMPT.format(text=text, question=q["question"]), VERIFY_TOOL, 600)
                except Exception as e:
                    raise SystemExit(f"STOPPED on verify for {r['id']} {tag}: {type(e).__name__}: {e}")
                tin, tout = tin + u["inputTokens"], tout + u["outputTokens"]
                q["verifier"] = v
                if not v.get("answerable_from_section_alone"):
                    reason = f"verifier: not answerable alone ({v.get('missing', '')[:120]})"
                elif norm(v.get("evidence_quote", "")) not in norm(text):
                    reason = "verifier evidence quote not verbatim in section"
            rec = {"id": f"{r['id']}-{tag}", "question": q["question"], "variant": tag, "lang": lang,
                   "pair_of": r["id"], "gold_file": r["gold_file"], "gold_section": r["gold_section"],
                   "also_acceptable": r.get("also_acceptable", []), "required_all": r.get("required_all"),
                   "category": r["category"], "expected_answer": q["answer"], "evidence_quote": q["evidence_quote"],
                   "tier": "A", "pool": "paired", "generator": MODEL_ID, "verifier": q.get("verifier")}
            if reason:
                dropped.append({"pair_of": r["id"], "variant": tag, "question": q["question"], "reason": reason})
            else:
                kept.append(rec)
    with open(OUT, "w") as f:
        for k in kept:
            f.write(json.dumps(k, ensure_ascii=False) + "\n")
    DROPPED.write_text(json.dumps(dropped, indent=1, ensure_ascii=False))
    load_eval_set(OUT)
    print(f"kept {len(kept)} of 26  dropped {len(dropped)}  tokens in {tin} out {tout}  "
          f"cost ${tin * PRICE_IN / 1e6 + tout * PRICE_OUT / 1e6:.4f}")


if __name__ == "__main__":
    main()
