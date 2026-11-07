"""Deterministic stale-fact answer classifier. Implements reports/stale_fact_rule.md (revision 2) over
eval/stale_patterns.json. No LLM judge. Pure function of (answer text, fact id, pattern file).

Classes (rule section 2): CURRENT, CURRENT_FLAGGED, MIXED, PROPAGATED, OLD_FLAGGED, ABSTAIN, OTHER.
Buckets: propagated = PROPAGATED + MIXED; current = CURRENT + CURRENT_FLAGGED; neither = the rest.
SF4 (mode "scoped"): a sentence holding an old table value counts as marked if it holds a scope marker or a
supersession marker. If every such sentence is scoped and no `current` matcher fires, the class is CURRENT_FLAGGED
("current means a scoped value", rule section 2), not OLD_FLAGGED.
X1 (mode "hallucination_probe"): HALLUCINATED / CORRECT / OTHER. `num_not` looks at DECIMAL numbers only.
"""
import hashlib
import json
import re
from pathlib import Path

PATTERNS = Path(__file__).resolve().parent.parent / "eval/stale_patterns.json"
BUCKET = {"CURRENT": "current", "CURRENT_FLAGGED": "current", "MIXED": "propagated", "PROPAGATED": "propagated",
          "OLD_FLAGGED": "neither", "ABSTAIN": "neither", "OTHER": "neither"}
NUM = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\d.]*\d)")
DEC = re.compile(r"(?<![\w.])\d+\.\d+")


def load(path=PATTERNS):
    raw = Path(path).read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def normalise(s):
    s = s.lower().replace("**", "").replace("`", "")
    s = s.replace("–", "-").replace("—", "-")
    return re.sub(r"(?<=\d),(?=\d{3})", "", s)


def sentences(s, split):
    return [x.strip() for x in re.split(split, s) if x.strip()]


def _hit(m, sent, answer):
    if "context" in m and not re.search(m["context"], sent):
        return False
    if "answer_absent" in m and re.search(m["answer_absent"], answer):
        return False
    if "re" in m:
        return bool(re.search(m["re"], sent))
    if "all_re" in m:
        return all(re.search(r, sent) for r in m["all_re"])
    if "num_range" in m:
        lo, hi = m["num_range"]
        return any(lo <= float(x) <= hi for x in NUM.findall(sent))
    if "num_not" in m:
        return any(float(x) not in m["num_not"] for x in DEC.findall(sent))
    raise ValueError(f"unknown matcher {m}")


def classify(answer, fact_id, pats, drop_markers=()):
    """drop_markers: marker regexes to remove, for sensitivity lines (e.g. pats['sensitivity_drop_markers']['S2_without_original'])."""
    f = pats["facts"][fact_id]
    a = normalise(answer)
    sents = sentences(a, pats["sentence_split"])
    any_re = lambda rs, s: any(re.search(r, s) for r in rs)
    abstains = any_re(pats["abstention_phrases"], a)

    if f.get("mode") == "hallucination_probe":
        if any(_hit(m, s, a) for m in f["hallucinated"] for s in sents):
            return "HALLUCINATED"
        if abstains or any(_hit(m, s, a) for m in f["correct"] for s in sents):
            return "CORRECT"
        return "OTHER"

    old_sents = [s for s in sents if any(_hit(m, s, a) for m in f["old"])]
    cur = any(_hit(m, s, a) for m in f["current"] for s in sents)
    markers = [m for m in pats["supersession_markers"] if m not in drop_markers] + f.get("scope_markers", [])
    all_marked = all(any_re(markers, s) for s in old_sents)

    if old_sents and cur:
        return "CURRENT_FLAGGED" if all_marked else "MIXED"
    if old_sents:
        if not all_marked:
            return "PROPAGATED"
        return "CURRENT_FLAGGED" if f.get("mode") == "scoped" else "OLD_FLAGGED"
    if cur:
        return "CURRENT"
    return "ABSTAIN" if abstains else "OTHER"
