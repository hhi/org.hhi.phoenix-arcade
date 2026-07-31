#!/usr/bin/env python3
"""Re-verify claims that carry a machine-checkable assertion.

A claim records a human judgement. Some of those judgements are countable —
"eight state constants, each dispatched to exactly one handler" is a fact a
script can re-derive. Where that is true, the claim should not rest on
"someone checked it once"; it should be re-checked on every run.

Claims may therefore carry an optional `assertion` object with two operators:

    "assertion": {
      "counts":   [{"file": "...", "pattern": "...", "expect": 8}],
      "distinct": [{"file": "...", "pattern": "...(capture)...", "expect": 6}]
    }

  counts    the regex must match exactly `expect` times in the file
  distinct  the regex's first capture group must yield exactly `expect`
            distinct values

The vocabulary is deliberately tiny and declarative. An assertion is itself
code, and code can be wrong — four separate scripts in this repository were
found to share the same look-back bug. An assertion complex enough to need
its own review has only moved the trust problem, so anything beyond counting
belongs in a purpose-built check instead.

Claims without an `assertion` are listed as resting on human verification
alone; that is a legitimate state, not a defect. Semantic equivalences such
as "an RLCA rotate is equivalent to a multiplication by two" cannot be
expressed here and should not be forced into it.

Usage:
    python3 c-phoenix/c-annotated/tools/check_claim_assertions.py
    python3 c-phoenix/c-annotated/tools/check_claim_assertions.py --verbose
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path("c-phoenix")
CLAIMS = ROOT / "c-annotated" / "knowledge-claims.json"


def evaluate(claim: dict) -> list[str]:
    failures: list[str] = []
    assertion = claim.get("assertion") or {}

    for rule in assertion.get("counts", []):
        path = ROOT / rule["file"]
        if not path.is_file():
            failures.append(f"{claim['id']}: assertion file missing: {rule['file']}")
            continue
        found = len(re.findall(rule["pattern"], path.read_text(encoding="utf-8")))
        if found != rule["expect"]:
            failures.append(
                f"{claim['id']}: {rule['file']} matches /{rule['pattern']}/ "
                f"{found} time(s), claim asserts {rule['expect']}"
            )

    for rule in assertion.get("distinct", []):
        path = ROOT / rule["file"]
        if not path.is_file():
            failures.append(f"{claim['id']}: assertion file missing: {rule['file']}")
            continue
        values = set(re.findall(rule["pattern"], path.read_text(encoding="utf-8")))
        if len(values) != rule["expect"]:
            failures.append(
                f"{claim['id']}: {rule['file']} yields {len(values)} distinct value(s) "
                f"for /{rule['pattern']}/, claim asserts {rule['expect']}"
            )

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true", help="List every claim and its state")
    args = parser.parse_args()

    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))["claims"]
    checked = [c for c in claims if c.get("assertion")]
    human_only = [c for c in claims if not c.get("assertion")]

    failures: list[str] = []
    for claim in checked:
        failures.extend(evaluate(claim))

    if args.verbose:
        for claim in checked:
            print(f"  machine-checked  {claim['id']}")
        for claim in human_only:
            print(f"  human-verified   {claim['id']}")
        print()

    if failures:
        print("Claim assertion check failed:")
        for failure in failures:
            print(f"- {failure}")
        print(
            "\nEither the source changed and the claim is now false, or the claim was "
            "wrong when written. Both need a human."
        )
        return 1

    print(
        f"Claim assertions: OK ({len(checked)} machine-checked, "
        f"{len(human_only)} resting on human verification)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
