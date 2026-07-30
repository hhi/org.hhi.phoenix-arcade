#!/usr/bin/env python3
"""Validate the generated c-phoenix knowledge graph.

Usage:
    python3 c-phoenix/c-annotated/tools/validate_knowledge_graph.py
"""

from __future__ import annotations

import json
from pathlib import Path


GRAPH = Path("c-phoenix/c-annotated/knowledge-graph.json")
REQUIRED_KINDS = {
    "c-function", "asm-routine", "ram-slot", "rom-pattern",
    "game-state", "claim", "table-asset",
}
RELATION_KINDS = {"implements", "calls", "uses-table", "handles-state", "asserts"}


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    problems: list[str] = []
    if graph.get("schema_version") != 1:
        problems.append("schema_version must be 1")
    if set(graph.get("node_kinds", [])) != REQUIRED_KINDS:
        problems.append("node_kinds must list the four supported kinds")

    nodes = graph.get("nodes")
    relations = graph.get("relations")
    if not isinstance(nodes, list) or not isinstance(relations, list):
        problems.append("nodes and relations must be lists")
        nodes, relations = [], []
    ids = [node.get("id") for node in nodes if isinstance(node, dict)]
    if len(ids) != len(set(ids)):
        problems.append("node IDs must be unique")
    known_ids = set(ids)
    for node in nodes:
        if not isinstance(node, dict):
            problems.append("every node must be an object")
            continue
        if node.get("kind") not in REQUIRED_KINDS:
            problems.append(f"{node.get('id')}: unsupported node kind")
        if not node.get("name"):
            problems.append(f"{node.get('id')}: missing name")
        if node.get("status") not in {"confirmed", "derived", "documented"}:
            problems.append(f"{node.get('id')}: unsupported status")
        source = node.get("source")
        if isinstance(source, dict) and not (Path("c-phoenix") / source.get("path", "")).is_file():
            problems.append(f"{node['id']}: source path does not exist")
        if node.get("kind") == "claim":
            claim = node.get("claim", {})
            if not claim.get("statement") or not claim.get("sources") or not claim.get("relates_to"):
                problems.append(f"{node['id']}: claim needs statement, sources and relates_to")
            for source_ref in claim.get("sources", []):
                source_path = source_ref.split("#", 1)[0]
                if not (Path("c-phoenix") / source_path).is_file():
                    problems.append(f"{node['id']}: claim source does not exist: {source_ref}")
    for relation in relations:
        if relation.get("from") not in known_ids or relation.get("to") not in known_ids:
            problems.append(f"relation has an unknown endpoint: {relation}")
        if relation.get("kind") not in RELATION_KINDS:
            problems.append(f"relation has an unsupported kind: {relation}")

    if problems:
        print("Knowledge graph validation failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print(f"Knowledge graph: OK ({len(nodes)} nodes, {len(relations)} relations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
