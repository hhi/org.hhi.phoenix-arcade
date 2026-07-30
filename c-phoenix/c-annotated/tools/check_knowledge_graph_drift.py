#!/usr/bin/env python3
"""Detect drift between the committed knowledge graph and a fresh regeneration.

This performs the same extraction as generate_knowledge_graph.py but never
writes to disk: it recomputes the graph in memory from the current checkout
and compares it against the committed c-annotated/knowledge-graph.json. Any
difference means the graph was not regenerated after a source change (or was
hand-edited) and should be treated as a build failure before the drift gets
any older.

Usage:
    python3 c-phoenix/c-annotated/tools/check_knowledge_graph_drift.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_knowledge_graph import OUTPUT, ROOT, build_graph  # noqa: E402


def main() -> int:
    fresh = build_graph(ROOT)
    fresh_text = json.dumps(fresh, indent=2, ensure_ascii=False) + "\n"
    committed_text = OUTPUT.read_text(encoding="utf-8")

    if fresh_text == committed_text:
        print(
            f"Knowledge graph drift check: OK "
            f"({len(fresh['nodes'])} nodes, {len(fresh['relations'])} relations match committed file)"
        )
        return 0

    committed = json.loads(committed_text)

    committed_by_id = {n["id"]: n for n in committed.get("nodes", [])}
    fresh_by_id = {n["id"]: n for n in fresh["nodes"]}
    added = sorted(fresh_by_id.keys() - committed_by_id.keys())
    removed = sorted(committed_by_id.keys() - fresh_by_id.keys())
    changed = sorted(
        node_id
        for node_id in fresh_by_id.keys() & committed_by_id.keys()
        if fresh_by_id[node_id] != committed_by_id[node_id]
    )

    committed_rel = {(r["kind"], r["from"], r["to"]) for r in committed.get("relations", [])}
    fresh_rel = {(r["kind"], r["from"], r["to"]) for r in fresh["relations"]}
    added_rel = sorted(fresh_rel - committed_rel)
    removed_rel = sorted(committed_rel - fresh_rel)

    def _print_sample(label: str, items: list) -> None:
        print(f"  {label} ({len(items)}):")
        for item in items[:20]:
            print(f"    {item}")
        if len(items) > 20:
            print(f"    ... and {len(items) - 20} more")

    print("Knowledge graph drift check: FAILED")
    print(f"  committed: {len(committed_by_id)} nodes, {len(committed_rel)} relations")
    print(f"  fresh:     {len(fresh_by_id)} nodes, {len(fresh_rel)} relations")
    if added:
        _print_sample("nodes only in fresh regeneration", [f"+ {n}" for n in added])
    if removed:
        _print_sample("nodes only in committed file", [f"- {n}" for n in removed])
    if changed:
        _print_sample("nodes with changed content", [f"~ {n}" for n in changed])
    if added_rel:
        print(f"  relations only in fresh regeneration: {len(added_rel)}")
    if removed_rel:
        print(f"  relations only in committed file: {len(removed_rel)}")
    print()
    print("Run `python3 c-phoenix/c-annotated/tools/generate_knowledge_graph.py` and commit the result.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
