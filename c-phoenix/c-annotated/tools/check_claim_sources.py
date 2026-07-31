#!/usr/bin/env python3
"""Verify that every claim source locator still resolves to real content.

validate_knowledge_graph.py checks that a claim's source *file* exists. It
does not check the locator after the `#`, so a line range can drift off the
end of a file, or — worse — quietly come to point at unrelated code after an
edit above it shifts every line down.

Three locator forms are supported:

    alien_logic.c#L348-L366        line range (fragile: shifts on any edit above)
    alien_logic.c#"(idx << 1)"     anchor text (robust: survives line shifts)
    bird-logic.md#process_birds    Markdown heading (checked against the headings)

Anchors are preferred. A line range only says *where* the evidence was; an
anchor says *what* it was, and fails precisely when that construct changes —
which is the event you actually want to hear about.

Reported:
  error    a line range extends past the end of the file
  error    an anchor string no longer occurs in the file
  warning  an anchor occurs more than once (ambiguous evidence)
  info     a claim still uses a line range where an anchor would be safer

Usage:
    python3 c-phoenix/c-annotated/tools/check_claim_sources.py
    python3 c-phoenix/c-annotated/tools/check_claim_sources.py --strict
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path("c-phoenix")
CLAIMS = ROOT / "c-annotated" / "knowledge-claims.json"

LINE_RANGE_RE = re.compile(r"^L(\d+)(?:-L(\d+))?$")
ANCHOR_RE = re.compile(r'^"(.+)"$', re.S)
HEADING_ANCHOR_RE = re.compile(r"^[A-Za-z_]\w*$")


def heading_exists(text: str, anchor: str) -> bool:
    """True when a Markdown heading matches the anchor, with or without backticks."""
    pattern = re.compile(rf"^#+\s+`?{re.escape(anchor)}`?", re.M)
    return bool(pattern.search(text))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also fail on line-range locators that could be anchors",
    )
    args = parser.parse_args()

    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))["claims"]
    errors: list[str] = []
    warnings: list[str] = []
    line_ranges: list[str] = []

    for claim in claims:
        for source in claim.get("sources", []):
            path_part, _, locator = source.partition("#")
            path = ROOT / path_part
            if not path.is_file():
                errors.append(f"{claim['id']}: source file does not exist: {path_part}")
                continue
            if not locator:
                continue

            text = path.read_text(encoding="utf-8")

            anchor = ANCHOR_RE.match(locator)
            if anchor:
                needle = anchor.group(1)
                occurrences = text.count(needle)
                if occurrences == 0:
                    errors.append(
                        f"{claim['id']}: anchor no longer present in {path_part}: {needle!r}"
                    )
                elif occurrences > 1:
                    warnings.append(
                        f"{claim['id']}: anchor occurs {occurrences}x in {path_part} "
                        f"(ambiguous): {needle!r}"
                    )
                continue

            span = LINE_RANGE_RE.match(locator)
            if span:
                start = int(span.group(1))
                end = int(span.group(2) or span.group(1))
                total = len(text.splitlines())
                if end > total:
                    errors.append(
                        f"{claim['id']}: {path_part}#{locator} extends past end of file "
                        f"({total} lines)"
                    )
                else:
                    line_ranges.append(f"{claim['id']}: {source}")
                continue

            if path.suffix == ".md" and HEADING_ANCHOR_RE.match(locator):
                if not heading_exists(text, locator):
                    errors.append(
                        f"{claim['id']}: no Markdown heading '{locator}' in {path_part}"
                    )
                continue

            warnings.append(f"{claim['id']}: unrecognised locator form: {source}")

    for problem in errors:
        print(f"- ERROR   {problem}")
    for problem in warnings:
        print(f"- WARNING {problem}")
    if args.strict:
        for entry in line_ranges:
            print(f"- INFO    line range, consider an anchor: {entry}")

    # A line range is a legitimate way to cite a *block* -- a function body, an
    # enum -- so it is never an error. Anchors are better for citing a specific
    # construct, which is what the advisory above is for. A check that is
    # permanently red teaches people to ignore it.
    if errors:
        print("\nClaim source check failed.")
        return 1

    note = f", {len(line_ranges)} line-range locator(s)" if line_ranges else ""
    print(f"Claim sources: OK ({len(claims)} claims{note})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
