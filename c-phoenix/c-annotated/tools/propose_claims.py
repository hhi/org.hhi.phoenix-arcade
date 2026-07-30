#!/usr/bin/env python3
"""Propose knowledge-claims work, in two deliberately different modes.

This tool never writes to knowledge-claims.json.

Not every claim is worth the same. A claim earns its place when it records
a judgement that no script can make -- typically that two independent
sources assert the same thing in different words, where disagreement was
possible. `claim:vector-offset-formula` is the model: the documentation
says `vector_offset = step_byte x 2`, the C port says
`(idx << 1) | (idx >> 7)`, and a human confirmed those are equivalent.

By contrast, restating what the generator already extracted ("table X is
N bytes, declared in the header and defined in the .c") adds no judgement.
It raises the coverage percentage without verifying anything. Both are
supported here, but they are kept apart so the metric cannot be inflated
by the cheap kind:

    --mode inventory   Ready-to-paste claims restating extracted facts.
                       Fast, mechanical, marked `"kind": "inventory"` so
                       report_claim_coverage.py can separate them out.

    --mode candidates  No statements at all: a ranked worklist of nodes
                       where two sources exist and could be compared, so a
                       human can write a real claim. This is the mode that
                       grows verified knowledge.

Usage:
    python3 c-phoenix/c-annotated/tools/propose_claims.py --mode candidates
    python3 c-phoenix/c-annotated/tools/propose_claims.py --mode inventory --kind table-asset
    python3 c-phoenix/c-annotated/tools/propose_claims.py --mode inventory --kind all --limit 5
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
        "kind": "inventory",
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
        "kind": "inventory",
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
        "kind": "inventory",
        "sources": [f"game_constants.h#L{line}"],
        "relates_to": [node["id"]] + sorted(owning)[:3],
    }


def candidate_worklist(graph: dict, already: set[str]) -> list[dict]:
    """Rank c-functions where two comparable sources exist but no claim does.

    A function documented in prose *and* annotated with an ASM range is a
    place where the documentation could silently drift from the
    implementation: exactly the disagreement a claim is meant to rule out.
    No statement is generated -- deciding what the two sources jointly
    assert is the human's job, and the reason the claim is worth anything.

    Ranked by how connected the function is, since a wrong belief about a
    heavily-called routine propagates furthest.
    """
    degree: dict[str, int] = {}
    for relation in graph["relations"]:
        if relation["kind"] in {"calls", "uses-table", "handles-state"}:
            degree[relation["from"]] = degree.get(relation["from"], 0) + 1
            degree[relation["to"]] = degree.get(relation["to"], 0) + 1

    candidates = []
    for node in graph["nodes"]:
        if node["kind"] != "c-function" or node["id"] in already:
            continue
        docs = node.get("evidence", {}).get("documentation", [])
        ranges = node.get("asm_ranges", [])
        if not docs or not ranges:
            continue
        candidates.append(
            {
                "id": node["id"],
                "name": node["name"],
                "source": f"{node['source']['path']}#L{node['source']['line']}",
                "asm": [f"${r['start']}-${r['end']}" for r in ranges],
                "docs": docs,
                "degree": degree.get(node["id"], 0),
            }
        )
    return sorted(candidates, key=lambda c: (-c["degree"], c["id"]))


def print_candidates(candidates: list[dict], limit: int | None) -> None:
    shown = candidates[:limit] if limit else candidates
    print(f"{len(candidates)} function(s) documented in prose AND annotated with an ASM range,")
    print("but not yet pinned down by a claim. Highest-traffic first.\n")
    print("For each: read the prose against the implementation, and only if they")
    print("agree in substance (not merely in wording) write a claim recording that.\n")
    for entry in shown:
        # evidence.documentation lists every document linking to the source
        # *file*; the one named after that file is the one actually describing
        # this function, so lead with it and only count the rest.
        stem = Path(entry["source"].split("#")[0]).stem.replace("_", "-")
        primary = [d for d in entry["docs"] if Path(d).stem == stem]
        others = len(entry["docs"]) - len(primary)

        print(f"  {entry['name']}  [{entry['degree']} relations]")
        print(f"    node : {entry['id']}")
        print(f"    code : {entry['source']}  {' '.join(entry['asm'])}")
        for doc in primary or entry["docs"][:1]:
            print(f"    prose: {doc}")
        if others:
            print(f"           (+{others} other document(s) linking to this file)")
        print()
    if limit and len(candidates) > len(shown):
        print(f"... and {len(candidates) - len(shown)} more.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=["inventory", "candidates"],
        default="candidates",
        help="candidates: worklist for real claims (default); inventory: mechanical restatements",
    )
    parser.add_argument(
        "--kind",
        choices=["rom-pattern", "table-asset", "game-state", "all"],
        default="all",
        help="Only used by --mode inventory",
    )
    parser.add_argument("--limit", type=int, default=None, help="Only emit the first N proposals")
    args = parser.parse_args()

    graph, already = load()

    if args.mode == "candidates":
        print_candidates(candidate_worklist(graph, already), args.limit)
        return 0

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
    print("// These restate already-extracted facts and are marked \"kind\": \"inventory\";")
    print("// they raise coverage without verifying anything new. Review, then paste the")
    print("// accepted ones into knowledge-claims.json and run: make kg-generate && make kg-check")
    print()
    print(",\n".join(json.dumps(p, indent=6, ensure_ascii=False) for p in shown))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
