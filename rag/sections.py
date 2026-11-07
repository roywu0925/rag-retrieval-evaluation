"""Section registry and THE HIT RULE.

=====================================================================
THE HIT RULE IS DEFINED AND ENFORCED IN THIS FILE ONLY.
=====================================================================
Gold labels are section ids, never chunk ids. Chunk ids change with every
chunking config; section ids are a function of the corpus alone.

  * A section id is (file, section_path). section_path is the heading path
    below H1, e.g. "Results > Tier 1: degradation sweep".
  * Leaf unit = the H3 section. An H2 with no H3 children is a leaf too.
  * Text under an H2 before its first H3 child is its own unit, the "H2
    intro", with section_path = the H2 heading. Text before the first H2 in
    a file is "(preamble)".
  * Every chunk carries exactly one section id (see chunker.py, which
    asserts chunk.section_id in REGISTRY at creation).
  * is_hit() is the only function that decides whether a retrieved chunk
    matches a question. Metrics code must call it, not compare ids itself.
  * load_eval_set() rejects any gold label that is not a registered section
    id, so a typo or a heading edit fails loudly instead of scoring 0.
"""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

CORPUS = Path(__file__).resolve().parent.parent / "corpus"
CORPUS_FILES = ["README.md", "PART1_DETAIL.md", "CONTEXT.md",
                "TIER2A_RESULTS.md", "REPRODUCING.md"]

SectionId = Tuple[str, str]  # (file, section_path)


@dataclass
class Section:
    file: str
    path: str            # heading path below H1, or "(preamble)"
    kind: str            # "h3" | "h2-leaf" | "h2-intro" | "preamble"
    start_line: int      # 1-based, inclusive
    end_line: int        # 1-based, inclusive
    lines: List[str] = field(repr=False, default_factory=list)

    @property
    def id(self) -> SectionId:
        return (self.file, self.path)

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    @property
    def has_body(self) -> bool:
        """False for a heading with no text of its own (e.g. an empty H2 intro).
        Such a section yields no chunks, so it can never be a gold label."""
        body = self.lines if self.kind == "preamble" else self.lines[1:]
        return any(l.strip() for l in body)


def parse_file(fname: str, corpus: Path = CORPUS) -> List[Section]:
    lines = (corpus / fname).read_text().splitlines()
    # Collect heading positions (outside code fences).
    heads = []  # (idx, level, title)
    fence = False
    for i, l in enumerate(lines):
        if l.lstrip().startswith("```"):
            fence = not fence
            continue
        m = None if fence else re.match(r"^(#{1,6})\s+(.*\S)\s*$", l)
        if m:
            lvl = len(m.group(1))
            if lvl >= 4:
                raise ValueError(f"{fname}:{i+1}: H{lvl} found; hit rule assumes <=H3")
            heads.append((i, lvl, m.group(2).strip()))

    # Boundaries: every H2 and H3 starts a new unit; H1 starts the preamble.
    starts = [(i, lvl, t) for i, lvl, t in heads if lvl in (2, 3)]
    sections: List[Section] = []

    first = starts[0][0] if starts else len(lines)
    if any(s.strip() for s in lines[:first]):
        sections.append(Section(fname, "(preamble)", "preamble", 1, first, lines[:first]))

    cur_h2 = None
    for j, (i, lvl, title) in enumerate(starts):
        end = starts[j + 1][0] if j + 1 < len(starts) else len(lines)
        if lvl == 2:
            cur_h2 = title
            has_children = j + 1 < len(starts) and starts[j + 1][1] == 3
            path, kind = title, ("h2-intro" if has_children else "h2-leaf")
        else:
            if cur_h2 is None:
                raise ValueError(f"{fname}:{i+1}: H3 before any H2")
            path, kind = f"{cur_h2} > {title}", "h3"
        sections.append(Section(fname, path, kind, i + 1, end, lines[i:end]))

    # Exhaustive and disjoint: every line belongs to exactly one section.
    covered = sum(s.end_line - s.start_line + 1 for s in sections)
    blank_lead = 0 if sections and sections[0].start_line == 1 else first
    assert covered + blank_lead == len(lines), f"{fname}: sections do not tile the file"
    return sections


def build_registry(corpus: Path = CORPUS) -> Dict[SectionId, Section]:
    reg: Dict[SectionId, Section] = {}
    for f in CORPUS_FILES:
        for s in parse_file(f, corpus):
            if s.id in reg:
                raise ValueError(f"duplicate section id {s.id}; disambiguate headings")
            reg[s.id] = s
    return reg


REGISTRY = build_registry()


# ---------------------------------------------------------------- hit rule
# category:
#   standard               one gold section (+ also_acceptable)
#   underspecified_premise as standard for retrieval; the generated answer is scored best/pass/fail
#   multi_section          required_all = list of groups, each a list of acceptable sections.
#                          strict  = every group has a retrieved section
#                          lenient = the gold_file/gold_section alone is retrieved
#   unanswerable/unsettled gold_file = gold_section = "NONE"; no retrieval score; correct = abstain
CATEGORIES = {"standard", "unanswerable", "unsettled", "underspecified_premise", "multi_section"}
NO_GOLD = {"unanswerable", "unsettled"}


def category(q: dict) -> str:
    return q.get("category", "standard")


def gold_ids(q: dict) -> set:
    """All section ids that count as correct for question q (empty for NO_GOLD)."""
    if category(q) in NO_GOLD:
        return set()
    ids = {(q["gold_file"], q["gold_section"])}
    for alt in q.get("also_acceptable") or []:
        ids.add((alt["gold_file"], alt["gold_section"]))
    return ids


def _groups(q: dict) -> List[set]:
    return [{(s["gold_file"], s["gold_section"]) for s in grp} for grp in q.get("required_all") or []]


def is_hit(chunk_meta: dict, q: dict) -> bool:
    """THE hit rule: chunk's source section is gold or also_acceptable."""
    return (chunk_meta["file"], chunk_meta["section"]) in gold_ids(q)


def retrieval_satisfied(retrieved_meta: List[dict], q: dict, rule: str = "strict"):
    """Did the top-k contain what q needs? None for NO_GOLD questions (scored on abstention).
    multi_section: strict = every required_all group hit; lenient = gold section hit."""
    if category(q) in NO_GOLD:
        return None
    got = {(c["file"], c["section"]) for c in retrieved_meta}
    if category(q) == "multi_section" and rule == "strict":
        return all(got & g for g in _groups(q))
    return bool(got & gold_ids(q))


def load_eval_set(path) -> List[dict]:
    qs = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    bad = []
    for n, q in enumerate(qs, 1):
        cat = category(q)
        if cat not in CATEGORIES:
            bad.append((n, ("category", cat)))
        if cat in NO_GOLD:
            if (q.get("gold_file"), q.get("gold_section")) != ("NONE", "NONE") or q.get("also_acceptable"):
                bad.append((n, ("NO_GOLD category must have gold NONE and no also_acceptable",)))
        if cat == "multi_section" and not q.get("required_all"):
            bad.append((n, ("multi_section needs required_all",)))
        ids = set(gold_ids(q)).union(*_groups(q)) if q.get("required_all") else gold_ids(q)
        for sid in ids:
            if sid not in REGISTRY:
                bad.append((n, sid))
            elif not REGISTRY[sid].has_body:
                bad.append((n, sid + ("<heading only, no chunks: label its H3 child>",)))
    if bad:
        raise ValueError("gold labels not in section registry:\n" +
                         "\n".join(f"  line {n}: {sid}" for n, sid in bad))
    return qs


def write_sections_tsv(path) -> None:
    from rag.tokens import ntok
    rows = ["# Valid gold labels: gold_file<TAB>gold_section. Generated by rag/sections.py; do not hand-edit.",
            "# kind: h3 | h2-leaf | h2-intro (H2 text before its first H3) | preamble (before first H2)",
            "gold_file\tgold_section\tkind\tlines\ttokens"]
    for s in REGISTRY.values():
        if not s.has_body:
            continue
        rows.append(f"{s.file}\t{s.path}\t{s.kind}\t{s.start_line}-{s.end_line}\t{ntok(s.text)}")
    Path(path).write_text("\n".join(rows) + "\n")
