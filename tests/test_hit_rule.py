"""Invariant checks for sections, chunker and hit rule. Free, no API calls.
Run:  .venv/bin/python tests/test_hit_rule.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rag.chunker import chunk_corpus  # noqa: E402
from rag.sections import REGISTRY, is_hit, load_eval_set  # noqa: E402

CONFIGS = [{"chunk_size": cs, "overlap_pct": ov} for cs in (256, 512, 1024) for ov in (0.0, 0.10, 0.25)]


def body_lines(sec):
    ls = sec.lines if sec.kind == "preamble" else sec.lines[1:]
    return [l for l in ls if l.strip()]


def main():
    # 1. section ids are identical across every config (labels can't drift)
    ids_by_cfg = {}
    for cfg in CONFIGS:
        chunks = chunk_corpus(cfg)
        ids_by_cfg[str(cfg)] = {(c["file"], c["section"]) for c in chunks}
        # 2. every non-blank line of a section appears in some chunk of THAT section
        by_sec = {}
        for c in chunks:
            by_sec.setdefault((c["file"], c["section"]), []).append(c["text"])
        for sid, sec in REGISTRY.items():
            joined = "\n".join(by_sec.get(sid, []))
            for l in body_lines(sec):
                for piece in [l] if len(l) < 200 else [l[:100]]:
                    assert piece in joined, (cfg, sid, l[:60])
        # 3. no chunk text contains a heading from a different section
        for c in chunks:
            for l in c["text"].splitlines()[1:]:
                if l.startswith("## ") or l.startswith("### "):
                    assert c["kind"] == "preamble" or False, (cfg, c["chunk_id"], l)
        # 4. sizes respected
        assert max(c["tokens"] for c in chunks) <= cfg["chunk_size"]
        # 5. measured overlap
        frag = [c for c in chunks if c["idx_in_section"] > 0]
        if frag:
            ovl = sum(c["n_overlap_lines"] for c in frag) / len(frag)
            print(f"  {cfg}: {len(chunks)} chunks, mean overlap {ovl:.1f} lines over {len(frag)} continuation chunks")
    first = next(iter(ids_by_cfg.values()))
    assert all(v == first for v in ids_by_cfg.values()), "section id set differs across configs"

    # 6. hit rule
    q = {"gold_file": "README.md", "gold_section": "Limitations",
         "also_acceptable": [{"gold_file": "CONTEXT.md", "gold_section": "Working style notes"}]}
    assert is_hit({"file": "README.md", "section": "Limitations"}, q)
    assert is_hit({"file": "CONTEXT.md", "section": "Working style notes"}, q)
    assert not is_hit({"file": "README.md", "section": "Methodology"}, q)

    # 7. unknown gold label fails loudly
    tmp = Path(__file__).parent / "_bad.jsonl"
    tmp.write_text('{"question":"x","gold_file":"README.md","gold_section":"No such heading","tier":"B"}\n')
    try:
        load_eval_set(tmp)
        raise AssertionError("bad label accepted")
    except ValueError:
        pass
    finally:
        tmp.unlink()
    # 8. every planned config maps to a distinct index name (0.095 once collided with 0.10)
    from rag.index import index_name
    from rag.sweep_plan import RUNS, config_for
    cfgs = {(c["model"], c["chunk_size"], c["overlap_pct"]): c
            for c in (config_for(r)[0] for r, _, _ in RUNS)}
    names = [index_name(c["model"], c) for c in cfgs.values()]
    assert len(set(names)) == len(cfgs), names
    print(f"OK: {len(first)} section ids stable across {len(CONFIGS)} configs; "
          f"{len(names)} planned indexes have distinct names; all invariants hold")


if __name__ == "__main__":
    main()
