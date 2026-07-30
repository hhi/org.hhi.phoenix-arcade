#!/usr/bin/env python3
"""Verify that every function name linked in the documentation actually exists.

The annotated documents build their call graph out of links whose label is a
bare symbol name:

    - [`state_3_normal_game_play`](state-play.md#state_3_normal_game_play)
      - [`state_play.c#L237`](../../state_play.c#L237)

validate_documentation.py already checks such labels when the link target is
a `.c` file. Most graph links, however, point at a sibling `.md` and name the
source file only in the adjacent text, so their labels were never checked --
which let plausible-looking but non-existent names survive in both language
sets, each with an invented line number.

This validator checks every function-shaped label in a documentation link
against the symbols actually declared or defined in the C sources, wherever
the link points.

Usage:
    python3 c-phoenix/c-annotated/tools/check_symbol_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("c-phoenix")
DOCS = ROOT / "c-annotated"

# A markdown link whose label is a single back-ticked identifier.
LABELLED_LINK_RE = re.compile(r"\[`(\w+)`\]\(([^)\s]+)\)")
# Function definitions and declarations in C sources and headers. The
# parameter body must not contain parentheses or newlines: allowing them lets
# a greedy match run from one declaration across the next, swallowing the
# following symbol and reporting it as undefined.
SYMBOL_RE = re.compile(r"\b(\w+)\s*\([^;{}()\n]*\)\s*[;{]")
# Labels that are data, not functions: tables, RAM slots, constants.
NON_FUNCTION_RE = re.compile(r"^(?:phoenix_|state\.|[A-Z][A-Z0-9_]*$|M[0-9A-F]{4}$)")


def known_symbols() -> set[str]:
    symbols: set[str] = set()
    for source in list(ROOT.glob("*.c")) + list(ROOT.glob("*.h")):
        symbols.update(SYMBOL_RE.findall(source.read_text(encoding="utf-8")))
    return symbols


def main() -> int:
    symbols = known_symbols()
    problems: list[str] = []

    for document in sorted(DOCS.rglob("*.md")):
        text = document.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), 1):
            for label, target in LABELLED_LINK_RE.findall(line):
                # Only judge labels that look like a function reference: a
                # lowercase identifier containing an underscore or a Z80-style
                # l-prefixed address, pointing at documentation or source.
                if NON_FUNCTION_RE.match(label):
                    continue
                if not re.fullmatch(r"[a-z][a-z0-9_]*", label):
                    continue
                if "_" not in label and not re.fullmatch(r"l[0-9a-f]{4}\w*", label):
                    continue
                if not (target.endswith(".c") or ".md" in target or ".c#" in target):
                    continue
                if label not in symbols:
                    problems.append(
                        f"{document.relative_to(ROOT)}:{line_no}: `{label}` is linked as a "
                        f"function but is declared nowhere in the C sources"
                    )

    if problems:
        print("Symbol link check failed:")
        for problem in sorted(set(problems)):
            print(f"- {problem}")
        return 1
    print(f"Symbol links: OK (every linked function name resolves to a real symbol)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
