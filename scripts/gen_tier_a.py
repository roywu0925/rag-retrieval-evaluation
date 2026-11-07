"""Generate Tier A questions, section by section. Gold = the generating section.

  .venv/bin/python scripts/gen_tier_a.py --plan    # allocation table only, no API calls
  .venv/bin/python scripts/gen_tier_a.py           # MAIN pool: generate + verify -> eval/tier_a.jsonl
  .venv/bin/python scripts/gen_tier_a.py --pool topup   # TOP-UP pool -> eval/tier_a_topup.jsonl (run after main)

Pools (see reports/writeup_notes.md, scoring plan):
  main  : TARGET questions, sqrt-allocated, untouched. The only pool used for analysis (1).
  topup : 1 question per section that Tier B covers (gold, also_acceptable or required_all), with the
          main pool's questions for that section listed as already asked. Used ONLY in analysis (3).

Rules (fixed before generation):
  eligibility : section body >= MIN_BODY_TOKENS; the generator may also return zero questions
  allocation  : n_i proportional to sqrt(section tokens), largest remainder, total TARGET
  filters     : (1) evidence quote must appear verbatim in the section (whitespace-normalised)
                (2) no self-reference ("this section", "above", "the document", ...)
                (3) an independent verifier call that sees ONLY the section must judge the
                    question answerable from it alone, quoting verbatim evidence
  dropped questions are NOT replaced; the set is whatever survives.
Known bias (stated, not corrected): a question generated from a section is answerable from
that section by construction, and may reuse its wording, which inflates recall.
"""
import argparse
import json
import math
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from rag.sections import REGISTRY, load_eval_set  # noqa: E402
from rag.tokens import ntok  # noqa: E402

MODEL_ID = "us.anthropic.claude-sonnet-4-6"   # INFERENCE_PROFILE-only in us-west-2; 5.x not eligible on this account (OF3)
PRICE_IN, PRICE_OUT = 3.30, 16.50             # USD / 1M, us-west-2 regional list price (Sonnet 4.6)
TARGET, MIN_BODY_TOKENS = 35, 50
LOG = ROOT / "logs/tier_a_calls.jsonl"
POOLS = {"main": ("eval/tier_a.jsonl", "eval/tier_a_raw.jsonl", "eval/tier_a_dropped.json"),
         "topup": ("eval/tier_a_topup.jsonl", "eval/tier_a_topup_raw.jsonl", "eval/tier_a_topup_dropped.json")}
TOPUP_PER_SECTION = 1
SELF_REF = re.compile(r"(?i)\b(this|the above|above|following|preceding) (section|passage|text|document|file|table|excerpt)\b"
                      r"|\bthe (passage|excerpt|text above)\b|\bas (described|mentioned|stated) above\b")

GEN_PROMPT = """You are writing evaluation questions for a retrieval system over a project's documentation.

Below is one section of the documentation (file: {file}; section: {path}).

Write {n} question(s) that are each answerable from this section alone.
- Each question targets one specific fact, number, or decision stated in the section.
- Each question must be self-contained: a reader who has not seen the section must understand what is being asked. Do not refer to "this section", "the text", "above", etc.
- Questions must target different facts.
- For each, give the short answer and an evidence_quote copied verbatim from the section (a contiguous span, max ~40 words) that supports the answer.
If the section cannot support {n} such question(s), return fewer (zero is allowed).
{already}
<section>
{text}
</section>"""

VERIFY_PROMPT = """Below is one section of a project's documentation, and a question.

Decide whether the question can be fully answered using ONLY this section, with no other knowledge of the project.
If yes, give the answer and an evidence_quote copied verbatim from the section (contiguous span).
If no, say what is missing.

<section>
{text}
</section>

<question>{question}</question>"""

GEN_TOOL = {"toolSpec": {"name": "submit_questions", "description": "Submit generated questions.",
    "inputSchema": {"json": {"type": "object", "properties": {"questions": {"type": "array", "items": {
        "type": "object", "properties": {"question": {"type": "string"}, "answer": {"type": "string"},
                                         "evidence_quote": {"type": "string"}},
        "required": ["question", "answer", "evidence_quote"]}}}, "required": ["questions"]}}}}
VERIFY_TOOL = {"toolSpec": {"name": "submit_verdict", "description": "Submit the verdict.",
    "inputSchema": {"json": {"type": "object", "properties": {
        "answerable_from_section_alone": {"type": "boolean"}, "answer": {"type": "string"},
        "evidence_quote": {"type": "string"}, "missing": {"type": "string"}},
        "required": ["answerable_from_section_alone"]}}}}


def body(sec):
    return "\n".join(sec.lines if sec.kind == "preamble" else sec.lines[1:])


def norm(s):
    """Matcher normalisation, applied identically to quote and section text.
    Fixed 2026-11-06 (instrument bug, two false drops): markdown blockquote markers at line starts are layout,
    not content, a line wrap after '/' must not insert a space ('physics/\\nsweep' == 'physics/sweep'), and table-row
    boundaries ('| |') are layout."""
    s = s.replace("**", "").replace("`", "").replace("*", "")
    s = re.sub(r"(?m)^[ \t]*(?:>[ \t]?)+", "", s)   # blockquote markers (incl. nested '> >') at line start
    s = re.sub(r"/\s+", "/", s)                     # whitespace after a slash
    s = re.sub(r"\s+", " ", s)
    # Fixed 2026-11-06 (instrument bug, paired pool): a markdown table-row boundary is '| |' ('|' end of row,
    # newline, '|' start of next). A contiguous quote across rows written with one '|' is the same content.
    # Applied to both sides, so a quote that does keep '| |' still matches.
    s = re.sub(r"\|(?: ?\|)+", "|", s)
    return s.strip().lower()


def allocate():
    elig = [s for s in REGISTRY.values() if s.has_body and ntok(body(s)) >= MIN_BODY_TOKENS]
    skipped = [s for s in REGISTRY.values() if s.has_body and s not in elig]
    w = [math.sqrt(ntok(body(s))) for s in elig]
    raw = [TARGET * x / sum(w) for x in w]
    n = [int(r) for r in raw]
    for i in sorted(range(len(elig)), key=lambda i: raw[i] - n[i], reverse=True)[:TARGET - sum(n)]:
        n[i] += 1
    return list(zip(elig, n)), skipped


def topup_alloc():
    """1 per Tier B-covered section; plus the main pool's questions per section (to avoid repeats)."""
    from rag.sections import _groups, gold_ids
    main_out = ROOT / POOLS["main"][0]
    if not main_out.exists():
        raise SystemExit("top-up needs the main pool first (eval/tier_a.jsonl missing)")
    cov = set()
    for q in load_eval_set(ROOT / "eval/tier_b.jsonl"):
        cov |= gold_ids(q)
        for g in _groups(q):
            cov |= g
    asked = {}
    for q in load_eval_set(main_out):
        asked.setdefault((q["gold_file"], q["gold_section"]), []).append(q["question"])
    return [(REGISTRY[sid], TOPUP_PER_SECTION) for sid in REGISTRY if sid in cov], asked


def already_text(qs):
    if not qs:
        return ""
    return ("\nThese questions about this section already exist; target DIFFERENT facts:\n"
            + "\n".join(f"- {q}" for q in qs) + "\n")


def converse(client, prompt, tool, max_tokens):
    t0 = time.time()
    r = client.converse(modelId=MODEL_ID, messages=[{"role": "user", "content": [{"text": prompt}]}],
                        inferenceConfig={"maxTokens": max_tokens},
                        toolConfig={"tools": [tool], "toolChoice": {"tool": {"name": tool["toolSpec"]["name"]}}})
    u = r["usage"]
    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps({"tool": tool["toolSpec"]["name"], "in": u["inputTokens"], "out": u["outputTokens"],
                            "latency_ms": round(1000 * (time.time() - t0)), "routing": "cross-region-profile"}) + "\n")
    for block in r["output"]["message"]["content"]:
        if "toolUse" in block:
            return block["toolUse"]["input"], u
    raise RuntimeError(f"no tool call in response: {r['output']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--pool", choices=sorted(POOLS), default="main")
    a = ap.parse_args()
    OUT, RAW, DROPPED = (ROOT / x for x in POOLS[a.pool])
    asked = {}
    if a.pool == "topup":
        alloc, asked = topup_alloc()
        print(f"TOP-UP pool: {len(alloc)} sections x {TOPUP_PER_SECTION}")
        for s_, n in alloc:
            print(f"  {n}  {s_.file:18s} {s_.path[:60]}   (main pool already has {len(asked.get(s_.id, []))})")
        if a.plan:
            return
    alloc_main, skipped = allocate()
    if a.pool == "main":
        alloc = alloc_main
    big = {"Results", "Current state"}
    if a.pool == "topup":
        skipped = []
    print(f"eligible {len(alloc)}  skipped(<{MIN_BODY_TOKENS} tok) {len(skipped)}: "
          + ", ".join(f"{s.file}::{s.path}" for s in skipped))
    for s, n in sorted(alloc, key=lambda x: -ntok(body(x[0]))):
        print(f"  {n}  {ntok(body(s)):5d} tok  {s.file:18s} {s.path[:70]}")
    share = sum(n for s, n in alloc if s.path.split(" > ")[0] in big and s.file in ("PART1_DETAIL.md", "CONTEXT.md"))
    print(f"allocated {sum(n for _, n in alloc)}; to PART1 'Results' + CONTEXT 'Current state' (53% of tokens): {share}")
    if a.plan:
        return

    import boto3
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    for p in (OUT, RAW):
        if p.exists():
            raise SystemExit(f"{p} exists; refusing to overwrite a generated eval set")
    kept, dropped, tin, tout = [], [], 0, 0
    for sec, n in alloc:
        if n == 0:
            continue
        text = f"[{sec.file} > {sec.path}]\n{body(sec)}"
        try:
            g, u = converse(client, GEN_PROMPT.format(file=sec.file, path=sec.path, n=n, text=text,
                                                          already=already_text(asked.get(sec.id))), GEN_TOOL, 2000)
        except Exception as e:  # authorization etc.: stop, never retry
            raise SystemExit(f"STOPPED on generation call for {sec.id}: {type(e).__name__}: {e}")
        tin, tout = tin + u["inputTokens"], tout + u["outputTokens"]
        qs = g.get("questions", [])
        with open(RAW, "a") as f:
            f.write(json.dumps({"file": sec.file, "section": sec.path, "requested": n, "response": g}) + "\n")
        if len(qs) < n:
            dropped.append({"section": sec.id, "reason": f"generator returned {len(qs)} of {n}"})
        for q in qs[:n]:
            reason = None
            if norm(q["evidence_quote"]) not in norm(text):
                reason = "generator evidence quote not verbatim in section"
            elif SELF_REF.search(q["question"]):
                reason = "self-referential wording"
            else:
                try:
                    v, u = converse(client, VERIFY_PROMPT.format(text=text, question=q["question"]), VERIFY_TOOL, 600)
                except Exception as e:
                    raise SystemExit(f"STOPPED on verify call for {sec.id}: {type(e).__name__}: {e}")
                tin, tout = tin + u["inputTokens"], tout + u["outputTokens"]
                q["verifier"] = v
                if not v.get("answerable_from_section_alone"):
                    reason = f"verifier: not answerable alone ({v.get('missing', '')[:120]})"
                elif norm(v.get("evidence_quote", "")) not in norm(text):
                    reason = "verifier evidence quote not verbatim in section"
            rec = {"question": q["question"], "gold_file": sec.file, "gold_section": sec.path, "tier": "A",
                   "also_acceptable": [], "expected_answer": q["answer"], "evidence_quote": q["evidence_quote"],
                   "generator": MODEL_ID, "pool": a.pool}
            if reason:
                dropped.append({"section": sec.id, "question": q["question"], "reason": reason})
            else:
                kept.append(rec)
    with open(OUT, "w") as f:
        for r in kept:
            f.write(json.dumps(r) + "\n")
    DROPPED.write_text(json.dumps(dropped, indent=1))
    load_eval_set(OUT)  # gold labels must be registered sections
    cost = tin * PRICE_IN / 1e6 + tout * PRICE_OUT / 1e6
    print(f"kept {len(kept)}  dropped {len(dropped)}  tokens in {tin} out {tout}  cost ${cost:.4f}")


if __name__ == "__main__":
    main()
