#!/usr/bin/env python3
"""Validate every file and exact Z80 anchor linked by the knowledge explorer."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GRAPH = ROOT / "c-phoenix/c-annotated/knowledge-graph.json"
EXPLORER = ROOT / "c-phoenix/c-annotated/knowledge-base-explorer/index.html"
ASM_VIEW = ROOT / "c-phoenix/context/code-annotated.html"
ASM_HREF_TEMPLATE = "../../context/code-annotated.html#asm-${esc(String(range.start).toLowerCase())}"


def documentation_paths(node: dict) -> list[str]:
    documentation = node.get("evidence", {}).get("documentation")
    if documentation is None:
        return []
    if isinstance(documentation, str):
        return [documentation]
    if isinstance(documentation, list) and all(isinstance(item, str) for item in documentation):
        return documentation
    raise ValueError("documentation must be a string or a list of strings")


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    explorer = EXPLORER.read_text(encoding="utf-8")
    asm_view = ASM_VIEW.read_text(encoding="utf-8")
    problems: list[str] = []

    if ASM_HREF_TEMPLATE not in explorer:
        problems.append("explorer does not generate address-specific annotated-ASM URLs")

    for node in graph["nodes"]:
        node_id = node["id"]
        if source := node.get("source"):
            path = ROOT / "c-phoenix" / source["path"]
            if not path.is_file():
                problems.append(f"{node_id}: missing C source: {source['path']}")
        try:
            paths = documentation_paths(node)
        except ValueError as error:
            problems.append(f"{node_id}: {error}")
            paths = []
        for path_text in paths:
            relative = path_text.removeprefix("c-annotated/")
            base = ROOT / "c-phoenix/c-annotated" if path_text.startswith("c-annotated/") else ROOT / "c-phoenix"
            if not (base / relative).is_file():
                problems.append(f"{node_id}: missing documentation: {path_text}")
        for asm_range in node.get("asm_ranges", []):
            start = asm_range["start"].lower()
            if not re.search(rf'id="asm-{re.escape(start)}"', asm_view):
                problems.append(f"{node_id}: missing annotated ASM anchor: asm-{start}")

    if problems:
        print("Knowledge-base explorer link validation failed:")
        print("\n".join(f"- {problem}" for problem in problems))
        return 1
    print("Knowledge-base explorer links: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
