"""Heading-first chunker.

config = {"chunk_size": 512, "overlap_pct": 0.10}

1. The corpus is split into sections by rag/sections.py (H3 leaves).
2. A section that fits in chunk_size becomes one whole chunk.
3. A larger section is packed line by line into chunks of at most chunk_size
   tokens. Consecutive chunks of the same section share their trailing lines,
   up to overlap_pct * chunk_size tokens. Overlap never crosses a section
   boundary. A single line longer than the budget is split by token windows.
4. Each chunk's text starts with a heading-path prefix "[FILE > path]", which
   counts toward chunk_size.

Each chunk's source section id is set here and asserted against
sections.REGISTRY. The hit rule depends on this metadata (see sections.py).
"""
import hashlib
from typing import Dict, List

from rag.sections import REGISTRY, Section
from rag.tokens import decode, encode, ntok

BASELINE = {"chunk_size": 512, "overlap_pct": 0.10}


def _prefix(sec: Section) -> str:
    return f"[{sec.file} > {sec.path}]\n"


def _body_lines(sec: Section) -> List[str]:
    # Drop the section's own heading line (the prefix carries the full path),
    # except in the preamble, where the H1 title is real content.
    return sec.lines if sec.kind == "preamble" else sec.lines[1:]


def _split_long(line: str, budget: int) -> List[str]:
    t = encode(line)
    return [decode(t[i:i + budget]) for i in range(0, len(t), budget)]


def chunk_section(sec: Section, chunk_size: int, overlap_pct: float) -> List[Dict]:
    prefix = _prefix(sec)
    budget = chunk_size - ntok(prefix)
    if budget < 32:
        raise ValueError(f"chunk_size {chunk_size} leaves <32 tokens after prefix for {sec.id}")
    ov_budget = int(round(overlap_pct * chunk_size))

    lines: List[str] = []
    for l in _body_lines(sec):
        lines.extend(_split_long(l, budget) if ntok(l) > budget else [l])
    if not "".join(lines).strip():
        return []
    lt = [ntok(l + "\n") for l in lines]

    bodies: List[List[int]] = []  # each = list of line indices
    i = 0
    while i < len(lines):
        cur, used = [], 0
        # overlap: trailing lines of the previous chunk, same section only
        if bodies and ov_budget > 0:
            prev = bodies[-1]
            for j in reversed(prev):
                if used + lt[j] > ov_budget or len(cur) + 1 >= len(prev):
                    break
                cur.insert(0, j)
                used += lt[j]
        start_new = len(cur)
        while i < len(lines) and used + lt[i] <= budget:
            cur.append(i)
            used += lt[i]
            i += 1
        if len(cur) == start_new:   # overlap left no room; drop it
            cur, used = [i], lt[i]
            i += 1
        bodies.append(cur)

    chunks = []
    for k, idxs in enumerate(bodies):
        body = "\n".join(lines[j] for j in idxs).strip("\n")
        if not body.strip():
            continue
        text = prefix + body
        shared = [] if k == 0 else sorted(set(idxs) & set(bodies[k - 1]))
        chunks.append({"file": sec.file, "section": sec.path, "kind": sec.kind,
                       "text": text, "tokens": ntok(text),
                       "n_overlap_lines": len(shared),
                       "overlap_tokens": sum(lt[j] for j in shared)})
    for k, c in enumerate(chunks):
        c["idx_in_section"] = k
        c["n_in_section"] = len(chunks)
        c["is_whole_section"] = len(chunks) == 1
    return chunks


def measured_overlap(chunks: List[Dict], chunk_size: int) -> Dict:
    """The experimental overlap variable. Overlap is whole lines, so the measured
    value falls below overlap_pct by a size-dependent amount; analysis uses
    `pct`, and the nominal value is only a footnote.

    pct      : mean overlap tokens per continuation chunk / chunk_size * 100
               (continuation = not the first chunk of its section)
    pct_all  : total overlap tokens / total chunk tokens * 100 (all chunks,
               i.e. fraction of embedded tokens that are duplicates)
    """
    cont = [c for c in chunks if c["idx_in_section"] > 0]
    ov = sum(c["overlap_tokens"] for c in cont)
    return {"pct": 100.0 * ov / len(cont) / chunk_size if cont else 0.0,
            "pct_all": 100.0 * ov / sum(c["tokens"] for c in chunks),
            "n_continuation": len(cont), "n_chunks": len(chunks)}


def chunk_corpus(config: Dict) -> List[Dict]:
    cs, ov = int(config["chunk_size"]), float(config["overlap_pct"])
    out = []
    for sec in REGISTRY.values():
        for c in chunk_section(sec, cs, ov):
            # ---- hit-rule enforcement: every chunk maps to a registered section
            assert (c["file"], c["section"]) in REGISTRY, (c["file"], c["section"])
            assert c["tokens"] <= cs, (c["file"], c["section"], c["tokens"])
            c["chunk_id"] = f"{c['file']}::{c['section']}::{c['idx_in_section']}"
            c["text_sha256"] = hashlib.sha256(c["text"].encode()).hexdigest()
            out.append(c)
    return out
