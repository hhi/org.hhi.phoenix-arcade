#!/usr/bin/env python3
"""Report [ASM: ...] annotations that the knowledge-graph generator cannot see.

The generator only reads the comment block *directly above* a declaration.
An annotation placed anywhere else still looks correct to a human reader but
never reaches the graph, so the omission is silent. Two shapes are reported:

  in-body   the tag sits inside a function body (usually as the first line
            after the opening brace) instead of above the declaration;
  orphaned  the tag sits in a comment block that precedes neither a function
            nor a table declaration.

Prose notes that merely mention where a routine moved to are legitimate and
are not reported: they are recognised by naming another file, or by carrying
an explicit "verwijderd"/"removed"/"lives in" marker.

Usage:
    python3 c-phoenix/c-annotated/tools/check_asm_annotations.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("c-phoenix")
ASM_RE = re.compile(r"\[ASM:\s*[0-9A-Fa-f]{4}(?:-[0-9A-Fa-f]{4})?\]")
FUNCTION_RE = re.compile(
    r"^\s*(?:static\s+)?(?:[A-Za-z_]\w*(?:\s*\*)?\s+)+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{",
    re.M,
)
BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
LINE_COMMENT_RUN_RE = re.compile(r"(?:^[ \t]*//[^\n]*\n)+", re.M)
DECLARATION_RE = re.compile(
    r"\s*(?:extern\s+)?(?:static\s+)?(?:const\s+)?[A-Za-z_]\w*(?:\s*\*)?\s+\**[A-Za-z_]\w*\s*[\[(=;]"
)
# A note that points at code living elsewhere is documentation, not an
# annotation the generator is expected to pick up.
CROSS_REFERENCE_RE = re.compile(
    r"\b(?:lives in|now lives|verwijderd|removed|see\s+\w+\.c|\w+\.c:)", re.I
)


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def function_spans(text: str) -> list[tuple[int, int, str]]:
    """Return (body_start, body_end, name) for every function definition."""
    spans: list[tuple[int, int, str]] = []
    for match in FUNCTION_RE.finditer(text):
        brace = text.find("{", match.start())
        if brace == -1:
            continue
        depth = 0
        for index, char in enumerate(text[brace:], brace):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    spans.append((brace, index, match.group(1)))
                    break
    return spans


def main() -> int:
    problems: list[str] = []

    for source in sorted(ROOT.glob("*.c")):
        text = source.read_text(encoding="utf-8")
        spans = function_spans(text)

        def enclosing_function(offset: int) -> str | None:
            for body_start, body_end, name in spans:
                if body_start < offset < body_end:
                    return name
            return None

        for comment in list(BLOCK_COMMENT_RE.finditer(text)) + list(
            LINE_COMMENT_RUN_RE.finditer(text)
        ):
            body = comment.group(0)
            if not ASM_RE.search(body):
                continue

            inside = enclosing_function(comment.start())
            if inside is not None:
                problems.append(
                    f"{source.name}:{line_of(text, comment.start())}: [ASM: ...] inside the body of "
                    f"{inside}(); move it above the declaration or the generator will ignore it"
                )
                continue

            if DECLARATION_RE.match(text[comment.end():comment.end() + 300]):
                continue  # correctly precedes a function or table declaration
            if CROSS_REFERENCE_RE.search(body):
                continue  # prose note pointing at code elsewhere

            first = body.strip().splitlines()[0][:70]
            problems.append(
                f"{source.name}:{line_of(text, comment.start())}: [ASM: ...] precedes no declaration "
                f"({first!r})"
            )

    if problems:
        print("ASM annotation check failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("ASM annotations: OK (every [ASM: ...] tag is attached to a declaration)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
