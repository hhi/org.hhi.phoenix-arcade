#!/usr/bin/env python3
"""Propose draft knowledge-claims for graph nodes that have none yet.

This tool never writes to knowledge-claims.json. It emits ready-to-paste
draft claims, built strictly from data already present in the checkout
(the generated graph, the ROM table definitions, and the pattern SVGs), so
that adding coverage becomes a review step instead of an authoring step.

Every proposal must still be read and accepted by a human: the whole point
of knowledge-claims.json is that a claim carries a human's judgement, not a
script's output. Statements are phrased to describe only what the sources
literally show.

Usage:
    python3 c-phoenix/c-annotated/tools/propose_claims.py --kind rom-pattern
    python3 c-phoenix/c-annotated/tools/propose_claims.py --kind table-asset
    python3 c-phoenix/c-annotated/tools/propose_claims.py --kind game-state
    python3 c-phoenix/c-annotated/tools/propose_claims.py --kind all --limit 5
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path("c-phoenix")
GRAPH = ROOT / "c-annotated" / "knowledge-graph.json"
CLAIMS = ROOT / "c-annotated" / "knowledge-claims.json"
TABLES_C = ROOT / "phoenix_tables.c"

TABLE_DEF_RE = re.compile(r"^const uint8_t (\w+)(?:\[[^\]]*\])?\s*=", re.M)


def load() -> tuple[dict, set[str]]:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))["claims"]
    already = {target for claim in claims for target in claim["relates_to"]}
    return graph, already


def table_definition_lines() -> dict[str, int]:
    """Map ROM table name -> line number of its definition in phoenix_tables.c."""
    text = TABLES_C.read_text(encoding="utf-8")
    return {
        match.group(1): text.count("\n", 0, match.start()) + 1
        for match in TABLE_DEF_RE.finditer(text)
    }


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def propose_rom_pattern(node: dict) -> dict | None:
    rom = node.get("rom", {})
    evidence = node.get("evidence", {})
    svg = evidence.get("visualization")
    if not svg or not rom:
        return None
    number = node["id"].split(":", 1)[1]
    return {
        "id": f"claim:pattern-{number}-metadata",
        "statement": (
            f"Cluster {rom['cluster']} pattern {number} starts at ROM {rom['address']} "
            f"and has {rom['steps']} visualized steps."
        ),
        "status": "derived",
        "sources": [svg, evidence.get("documentation", "")],
        "relates_to": [node["id"]],
    }


def propose_table_asset(node: dict, def_lines: dict[str, int]) -> dict | None:
    name = node["name"]
    source = node.get("source", {})
    header_line = source.get("line")
    def_line = def_lines.get(name)
    if not header_line or not def_line:
        return None

    size = node.get("asset", {}).get("size")
    ranges = node.get("asm_ranges", [])
    if ranges:
        span = ", ".join(f"${r['start']}-${r['end']}" for r in ranges)
        statement = (
            f"{name} is the ROM table of {size} bytes annotated at {span}, "
            f"declared in phoenix_tables.h and defined in phoenix_tables.c."
        )
    else:
        statement = (
            f"{name} is a ROM table of {size} bytes, declared in phoenix_tables.h "
            f"and defined in phoenix_tables.c."
        )
    return {
        "id": f"claim:table-{slug(name)}",
        "statement": statement,
        "status": "confirmed",
        "sources": [
            f"phoenix_tables.h#L{header_line}",
            f"phoenix_tables.c#L{def_line}",
        ],
        "relates_to": [node["id"]],
    }


def propose_game_state(node: dict, handlers: dict[str, list[str]]) -> dict | None:
    source = node.get("source", {})
    line = source.get("line")
    if not line:
        return None
    state = node.get("state", {})
    owning = handlers.get(node["id"], [])
    if not owning:
        return None
    handler_names = ", ".join(h.split(":")[-1] for h in sorted(owning)[:3])
    return {
        "id": f"claim:state-{slug(node['name'])}",
        "statement": (
            f"{node['name']} is the {state.get('category', 'state')} with value "
            f"{state.get('value')}, dispatched by {handler_names}."
        ),
        "status": "confirmed",
        "sources": [f"game_constants.h#L{line}"],
        "relates_to": [node["id"]] + sorted(owning)[:3],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--kind",
        choices=["rom-pattern", "table-asset", "game-state", "all"],
        default="all",
    )
    parser.add_argument("--limit", type=int, default=None, help="Only emit the first N proposals")
    args = parser.parse_args()

    graph, already = load()
    def_lines = table_definition_lines()

    handlers: dict[str, list[str]] = {}
    for relation in graph["relations"]:
        if relation["kind"] == "handles-state":
            handlers.setdefault(relation["to"], []).append(relation["from"])

    wanted = {args.kind} if args.kind != "all" else {"rom-pattern", "table-asset", "game-state"}
    proposals: list[dict] = []
    skipped = 0

    for node in graph["nodes"]:
        if node["kind"] not in wanted or node["id"] in already:
            continue
        if node["kind"] == "rom-pattern":
            proposal = propose_rom_pattern(node)
        elif node["kind"] == "table-asset":
            proposal = propose_table_asset(node, def_lines)
        else:
            proposal = propose_game_state(node, handlers)
        if proposal is None:
            skipped += 1
            continue
        proposals.append(proposal)

    shown = proposals[: args.limit] if args.limit else proposals

    print(f"// {len(proposals)} uncovered node(s) with a usable proposal", end="")
    if skipped:
        print(f"; {skipped} skipped for lack of source metadata", end="")
    if args.limit and len(proposals) > len(shown):
        print(f"; showing first {len(shown)}", end="")
    print()
    print("// Review each entry, then paste the accepted ones into knowledge-claims.json")
    print("// and run: make kg-generate && make kg-check")
    print()
    print(",\n".join(json.dumps(p, indent=6, ensure_ascii=False) for p in shown))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
