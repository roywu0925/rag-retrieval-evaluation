"""Corpus token count and H2-section size distribution.

Token counts use tiktoken cl100k_base as a proxy tokenizer. Titan v2 and
Cohere use their own tokenizers; expect counts within roughly +/-15%.
Headings inside fenced code blocks are ignored.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import tiktoken

CORPUS = Path(__file__).resolve().parent.parent / "corpus"
enc = tiktoken.get_encoding("cl100k_base")


def split_sections(text, level):
    """Return [(heading, body)] split at headings of exactly `level` (or higher)."""
    out, cur_head, cur = [], "(preamble)", []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else re.match(r"^(#{1,6})\s+(.*)", line)
        if m and len(m.group(1)) <= level:
            if cur and "".join(cur).strip():
                out.append((cur_head, "\n".join(cur)))
            cur_head, cur = m.group(2).strip(), [line]
        else:
            cur.append(line)
    if cur and "".join(cur).strip():
        out.append((cur_head, "\n".join(cur)))
    return out


def dist(xs):
    a = np.array(xs)
    return dict(n=len(a), min=int(a.min()), median=int(np.median(a)),
                p90=int(np.percentile(a, 90)), max=int(a.max()), sum=int(a.sum()))


def main():
    total_tok, total_words = 0, 0
    per_file = {}
    rows = {2: [], 3: []}
    for f in sorted(CORPUS.glob("*.md")):
        t = f.read_text()
        tok = len(enc.encode(t))
        total_tok += tok
        total_words += len(t.split())
        per_file[f.name] = tok
        for lvl in (2, 3):
            for head, body in split_sections(t, lvl):
                rows[lvl].append((f.name, head, len(body.split()), len(enc.encode(body))))
    print(f"TOTAL tokens (cl100k): {total_tok}   words: {total_words}")
    for k, v in per_file.items():
        print(f"  {k:20s} {v:6d} tok")
    for lvl in (2, 3):
        r = rows[lvl]
        print(f"\nSections split at H{lvl} and above (n={len(r)})")
        print("  words :", dist([x[2] for x in r]))
        print("  tokens:", dist([x[3] for x in r]))
        for thr in (256, 512, 1024):
            print(f"  sections > {thr} tok: {sum(x[3] > thr for x in r)}")
    if "-v" in sys.argv:
        print("\nH2 sections (file, tokens, heading):")
        for fn, h, w, tk in sorted(rows[2], key=lambda x: -x[3]):
            print(f"  {fn:18s} {tk:5d}  {h[:70]}")


if __name__ == "__main__":
    main()
