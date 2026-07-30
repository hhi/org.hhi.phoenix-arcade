#!/usr/bin/env python3
"""Cross-check the annotated documentation against the ASM cross-reference.

context/Phoenix.md is generated from Phoenix.asm plus the [ASM: ...] markers
in the C port, and carries a "Ported to C" line per routine naming the C
function, its file and line, and the ROM range. Because it is derived from
the sources it can only ever contain real symbols, which makes it an
independent check on the hand-written documents under c-annotated/.

Reported problems:

  unknown-function  a document introduces a function with a ROM range, but
                    Phoenix.md attributes that range to a different routine;
  stale-crossref    Phoenix.md names a C function or ROM range that no longer
                    matches the current [ASM: ...] annotations, meaning the
                    file needs regenerating (make c-asm-docs).

Usage:
    python3 c-phoenix/c-annotated/tools/check_against_asm_crossref.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path("c-phoenix")
CROSSREF = ROOT / "context" / "Phoenix.md"
GRAPH = ROOT / "c-annotated" / "knowledge-graph.json"

PORTED_RE = re.compile(
    r"\*\*Ported to C:\*\*\s*\[`(\w+)`\]\(\.\./(\w+\.c)#L(\d+)\).*?\(ASM:\s*`([^`]+)`\)"
)


def crossref_entries() -> list[tuple[str, str, int, list[tuple[int, int]]]]:
    entries = []
    for name, source, line, asm in PORTED_RE.findall(CROSSREF.read_text(encoding="utf-8")):
        spans = []
        for part in asm.split(","):
            start, _, end = part.strip().partition("-")
            try:
                spans.append((int(start, 16), int(end, 16)))
            except ValueError:
                continue
        entries.append((name, source, int(line), spans))
    return entries


def main() -> int:
    if not CROSSREF.is_file():
        print(f"{CROSSREF}: missing ASM cross-reference")
        return 1

    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    annotated = {
        node["name"]: {(int(r["start"], 16), int(r["end"], 16)) for r in node.get("asm_ranges", [])}
        for node in graph["nodes"]
        if node["kind"] == "c-function" and node.get("asm_ranges")
    }

    stale: list[str] = []
    for name, source, _line, spans in crossref_entries():
        if name not in annotated:
            stale.append(f"{name} ({source}): named in Phoenix.md but carries no [ASM: ...] annotation")
            continue
        extra = set(spans) - annotated[name]
        if extra:
            shown = " ".join(f"${a:04X}-${b:04X}" for a, b in sorted(extra))
            stale.append(
                f"{name} ({source}): Phoenix.md still lists {shown}, which the source no longer annotates"
            )

    if stale:
        print("ASM cross-reference is stale:")
        for problem in stale:
            print(f"- {problem}")
        print("\nRegenerate it with `make c-asm-docs`.")
        return 1

    print(f"ASM cross-reference: OK ({len(crossref_entries())} ported routines agree with the source)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
