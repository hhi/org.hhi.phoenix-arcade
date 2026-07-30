#!/usr/bin/env python3
"""Report how much of the c-phoenix knowledge graph is backed by a verified claim.

A node only counts as claim-verified when a knowledge-claims.json entry
targets it via an `asserts` relation. Everything else remains at its
extraction status (confirmed / derived / documented) without an explicit,
sourced human claim attached. This is a visibility tool, not a hard gate,
unless --fail-under is given.

Usage:
    python3 c-phoenix/c-annotated/tools/report_claim_coverage.py
    python3 c-phoenix/c-annotated/tools/report_claim_coverage.py --fail-under 5
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

GRAPH = Path("c-phoenix/c-annotated/knowledge-graph.json")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-under",
        type=float,
        default=None,
        help="Exit 1 if overall coverage percentage drops below this value",
    )
    args = parser.parse_args()

    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    nodes = graph["nodes"]
    relations = graph["relations"]

    substantive = [n for n in nodes if n["kind"] != "claim"]
    total_by_kind = Counter(n["kind"] for n in substantive)

    # Claims marked "inventory" only restate facts the generator already
    # extracted. They are counted separately so they cannot inflate the
    # figure that is supposed to mean "a human verified this".
    inventory_claims = {
        n["id"] for n in nodes
        if n["kind"] == "claim" and n.get("claim", {}).get("kind") == "inventory"
    }
    verified_ids = {
        r["to"] for r in relations
        if r["kind"] == "asserts" and r["from"] not in inventory_claims
    }
    inventory_ids = {
        r["to"] for r in relations
        if r["kind"] == "asserts" and r["from"] in inventory_claims
    } - verified_ids

    asserted_ids = verified_ids
    covered_by_kind = Counter(n["kind"] for n in substantive if n["id"] in asserted_ids)
    inventory_by_kind = Counter(n["kind"] for n in substantive if n["id"] in inventory_ids)

    print(f"{'kind':<14} {'verified':>9} {'invent.':>8} {'total':>7} {'ver.pct':>8}")
    print("-" * 48)
    total_covered = 0
    total_inventory = 0
    total_nodes = 0
    for kind in sorted(total_by_kind):
        covered = covered_by_kind.get(kind, 0)
        inventory = inventory_by_kind.get(kind, 0)
        total = total_by_kind[kind]
        total_covered += covered
        total_inventory += inventory
        total_nodes += total
        pct = 100 * covered / total if total else 0.0
        print(f"{kind:<14} {covered:>9} {inventory:>8} {total:>7} {pct:>7.1f}%")

    overall_pct = 100 * total_covered / total_nodes if total_nodes else 0.0
    print("-" * 48)
    print(f"{'overall':<14} {total_covered:>9} {total_inventory:>8} {total_nodes:>7} {overall_pct:>7.1f}%")

    claims = [n for n in nodes if n["kind"] == "claim"]
    verified_claims = len(claims) - len(inventory_claims)
    print()
    print(
        f"{verified_claims} verified claim(s) assert {len(verified_ids)} node(s); "
        f"{len(inventory_claims)} inventory claim(s) restate {len(inventory_ids)} more."
    )
    print("The percentage above counts verified claims only.")

    if args.fail_under is not None and overall_pct < args.fail_under:
        print(f"\nFAILED: coverage {overall_pct:.1f}% is below required {args.fail_under}%")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
