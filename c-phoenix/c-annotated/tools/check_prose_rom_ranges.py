#!/usr/bin/env python3
"""Cross-check ROM addresses quoted in prose against the [ASM: ...] annotations.

The annotated documents introduce a function with a parenthetical ROM range,
for example:

    The function [`player_update`](../../player_logic.c#L45) (Z80 ROM:
    `$0A20-$0A90`) reads player input ports ...

That range is a second, independent assertion about the same routine: the C
source already carries the authoritative `[ASM: ...]` annotation. Nothing
kept the two in step, so prose could quote an entirely different region and
still read as authoritative.

Two severities are reported:

  disjoint  the quoted range shares no address with any annotation on that
            function -- the prose points at unrelated ROM and is wrong;
  coarse    the quoted range overlaps but does not match exactly, e.g. a
            single span where the source annotates several. Reported only
            with --strict, since summarising is a legitimate style.

Usage:
    python3 c-phoenix/c-annotated/tools/check_prose_rom_ranges.py
    python3 c-phoenix/c-annotated/tools/check_prose_rom_ranges.py --strict
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path("c-phoenix")
GRAPH = ROOT / "c-annotated" / "knowledge-graph.json"

# [`fn`](../../file.c#L..) (Z80 ROM: `$XXXX-$YYYY`)  -- en/nl share this shape,
# and the dash may be an ASCII hyphen or an en dash.
PROSE_RE = re.compile(
    r"\[`(\w+)`\]\(\.\./\.\./(\w+\.c)[^)]*\)\s*\((?:Z80\s+)?ROM:\s*"
    r"`\$([0-9A-Fa-f]{4})[–-]\$([0-9A-Fa-f]{4})`\)"
)


def annotated_ranges() -> dict[str, list[tuple[int, int]]]:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    return {
        node["name"]: [
            (int(r["start"], 16), int(r["end"], 16)) for r in node.get("asm_ranges", [])
        ]
        for node in graph["nodes"]
        if node["kind"] == "c-function" and node.get("asm_ranges")
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also report overlapping-but-inexact ranges, not just disjoint ones",
    )
    args = parser.parse_args()

    ranges = annotated_ranges()
    disjoint: list[str] = []
    coarse: list[str] = []

    for document in sorted((ROOT / "c-annotated").rglob("*.md")):
        text = document.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), 1):
            for name, _source, start, end in PROSE_RE.findall(line):
                annotated = ranges.get(name)
                if not annotated:
                    continue
                prose = (int(start, 16), int(end, 16))
                if any(prose == span for span in annotated):
                    continue
                shown = " ".join(f"${a:04X}-${b:04X}" for a, b in annotated)
                where = f"{document.relative_to(ROOT)}:{line_no}"
                if any(not (prose[1] < a or prose[0] > b) for a, b in annotated):
                    coarse.append(
                        f"{where}: {name} prose ${start.upper()}-${end.upper()} "
                        f"overlaps but does not match annotation {shown}"
                    )
                else:
                    disjoint.append(
                        f"{where}: {name} prose ${start.upper()}-${end.upper()} "
                        f"is disjoint from annotation {shown}"
                    )

    problems = disjoint + (coarse if args.strict else [])
    if problems:
        print("Prose ROM range check failed:")
        for problem in problems:
            print(f"- {problem}")
        if coarse and not args.strict:
            print(f"({len(coarse)} overlapping-but-inexact range(s) hidden; use --strict)")
        return 1

    note = "" if args.strict else f", {len(coarse)} overlapping-but-inexact (use --strict)"
    print(f"Prose ROM ranges: OK (no prose range points at unrelated ROM{note})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
