#!/usr/bin/env python3
"""Generate the initial machine-readable knowledge graph for c-phoenix.

The graph is intentionally conservative: extracted nodes and relations are
derived from the checkout, while semantic claims must be added explicitly to
knowledge-claims.json with sources and a certainty status. Narrative
explanations remain in Markdown; their paths are attached as evidence rather
than being converted into facts.

Usage:
    python3 tools/generate_knowledge_graph.py
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path("c-phoenix")
OUTPUT = ROOT / "c-annotated" / "knowledge-graph.json"
CLAIMS = ROOT / "c-annotated" / "knowledge-claims.json"
FUNCTION_RE = re.compile(
    r"^\s*(?:static\s+)?(?:[A-Za-z_]\w*(?:\s*\*)?\s+)+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{",
    re.M,
)
ASM_RE = re.compile(r"\[ASM:\s*([0-9A-Fa-f]{4})(?:-([0-9A-Fa-f]{4}))?\]")
CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
RAM_RE = re.compile(r"(?:\$|0x)([4][0-9A-Fa-f]{3})\b")
MARKDOWN_C_LINK_RE = re.compile(r"\]\(\.\./([^/)]+\.c)(?:#[^)]+)?\)")
SVG_PATTERN_RE = re.compile(
    r"Cluster ([AB]) Patroon (\d+) \(ROM \$([0-9A-F]+), (\d+) Stappen\)"
)
TABLE_RE = re.compile(r"extern const uint8_t (\w+)(?:\[(0x[0-9A-Fa-f]+)\])?;")
STATE_RE = re.compile(r"\b((?:GAME_STATE|LEVEL_PATTERN)_[A-Z0-9_]+)\s*=\s*(0x[0-9A-Fa-f]+)")
KEYWORDS = {"if", "for", "while", "switch", "return", "sizeof"}


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def function_body(text: str, start: int) -> str:
    """Return the body starting at an opening brace, with nested braces."""
    depth = 0
    for end, char in enumerate(text[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:end + 1]
    raise ValueError("Unterminated C function body")


def function_id(path: Path, name: str) -> str:
    return f"c:{path.stem}:{name}"


def source_functions(root: Path) -> tuple[list[dict], dict[str, list[str]], dict[str, str]]:
    nodes: list[dict] = []
    name_to_ids: dict[str, list[str]] = defaultdict(list)
    bodies: dict[str, str] = {}
    for source in sorted(root.glob("*.c")):
        text = source.read_text(encoding="utf-8")
        relative = source.relative_to(root).as_posix()
        for match in FUNCTION_RE.finditer(text):
            name = match.group(1)
            node_id = function_id(source, name)
            # ASM ranges are taken only from the documentation block directly
            # above the definition, avoiding an accidental association with an
            # earlier routine in the same file.
            prefix = text[max(0, text.rfind("\n\n", 0, match.start()) - 800):match.start()]
            asm_ranges = []
            for start, end in ASM_RE.findall(prefix):
                asm_ranges.append({"start": start.upper(), "end": (end or start).upper()})
            nodes.append(
                {
                    "id": node_id,
                    "kind": "c-function",
                    "name": name,
                    "source": {"path": relative, "line": line_number(text, match.start())},
                    "asm_ranges": asm_ranges,
                    "status": "confirmed",
                }
            )
            name_to_ids[name].append(node_id)
            bodies[node_id] = function_body(text, text.find("{", match.start()))
    return nodes, name_to_ids, bodies


def document_evidence(root: Path) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Map C files and RAM slots to the documentation that mentions them."""
    c_docs: dict[str, list[str]] = defaultdict(list)
    ram_docs: dict[str, list[str]] = defaultdict(list)
    for document in sorted((root / "c-annotated").glob("*.md")) + sorted((root / "animations").glob("*.md")):
        relative = document.relative_to(root).as_posix()
        text = document.read_text(encoding="utf-8")
        for source in MARKDOWN_C_LINK_RE.findall(text):
            c_docs[source].append(relative)
        for address in RAM_RE.findall(text):
            ram_docs[address.upper()].append(relative)
    return c_docs, ram_docs


def rom_pattern_nodes(root: Path) -> list[dict]:
    nodes: list[dict] = []
    for svg in sorted((root / "animations").glob("cluster_*/*.svg")):
        match = SVG_PATTERN_RE.search(svg.read_text(encoding="utf-8"))
        if not match:
            continue
        cluster, number, address, steps = match.groups()
        nodes.append(
            {
                "id": f"rom-pattern:{int(number):02d}",
                "kind": "rom-pattern",
                "name": f"Cluster {cluster} patroon {int(number):02d}",
                "rom": {"address": f"${address}", "steps": int(steps), "cluster": cluster},
                "evidence": {
                    "source": "phoenix_tables.c",
                    "documentation": "animations/animation-trajectory.md",
                    "visualization": svg.relative_to(root).as_posix(),
                },
                "status": "derived",
            }
        )
    return nodes


def table_asset_nodes(root: Path) -> list[dict]:
    """Extract table/asset nodes from the canonical table header."""
    header = root / "phoenix_tables.h"
    text = header.read_text(encoding="utf-8")
    nodes: list[dict] = []
    for match in TABLE_RE.finditer(text):
        name, size = match.groups()
        preceding = text[max(0, text.rfind("\n\n", 0, match.start()) - 2400):match.start()]
        ranges = [{"start": start.upper(), "end": (end or start).upper()} for start, end in ASM_RE.findall(preceding)]
        node = {
            "id": f"table:{name}",
            "kind": "table-asset",
            "name": name,
            "asset": {"type": "rom-table", "size": int(size, 16) if size else 1},
            "source": {"path": "phoenix_tables.h", "line": line_number(text, match.start())},
            "status": "confirmed",
        }
        if ranges:
            node["asm_ranges"] = ranges
        nodes.append(node)
    return nodes


def game_state_nodes(root: Path) -> list[dict]:
    """Extract named game and level-pattern states from game_constants.h."""
    header = root / "game_constants.h"
    text = header.read_text(encoding="utf-8")
    nodes: list[dict] = []
    for match in STATE_RE.finditer(text):
        name, value = match.groups()
        if name == "LEVEL_PATTERN_MASK":
            continue
        nodes.append(
            {
                "id": f"game-state:{name.lower()}",
                "kind": "game-state",
                "name": name,
                "state": {
                    "category": "game-state" if name.startswith("GAME_STATE_") else "level-pattern",
                    "value": value.upper(),
                },
                "source": {"path": "game_constants.h", "line": line_number(text, match.start())},
                "status": "confirmed",
            }
        )
    return nodes


def claim_nodes(root: Path) -> list[dict]:
    """Load curated semantic claims and keep them distinct from extracted facts."""
    raw_claims = json.loads(CLAIMS.read_text(encoding="utf-8"))["claims"]
    nodes: list[dict] = []
    for claim in raw_claims:
        nodes.append(
            {
                "id": claim["id"],
                "kind": "claim",
                "name": claim["statement"],
                "claim": {
                    "statement": claim["statement"],
                    "sources": claim["sources"],
                    "relates_to": claim["relates_to"],
                },
                "status": claim["status"],
            }
        )
    return nodes


def build_graph(root: Path) -> dict:
    c_nodes, name_to_ids, bodies = source_functions(root)
    c_docs, ram_docs = document_evidence(root)
    nodes: list[dict] = []
    relations: list[dict] = []

    for node in c_nodes:
        source_docs = sorted(set(c_docs.get(node["source"]["path"], [])))
        if source_docs:
            node["evidence"] = {"documentation": source_docs}
        nodes.append(node)
        for asm_range in node["asm_ranges"]:
            asm_id = f"asm:{asm_range['start']}-{asm_range['end']}"
            relations.append({"kind": "implements", "from": node["id"], "to": asm_id})

    asm_ids = sorted({relation["to"] for relation in relations if relation["to"].startswith("asm:")})
    for asm_id in asm_ids:
        start, end = asm_id.removeprefix("asm:").split("-")
        nodes.append(
            {
                "id": asm_id,
                "kind": "asm-routine",
                "name": f"ASM ${start}–${end}",
                "asm": {"start": f"${start}", "end": f"${end}"},
                "evidence": {"source": "C [ASM: ...] annotations"},
                "status": "confirmed",
            }
        )

    for address, documents in sorted(ram_docs.items()):
        nodes.append(
            {
                "id": f"ram:${address}",
                "kind": "ram-slot",
                "name": f"RAM ${address}",
                "ram": {"address": f"${address}"},
                "evidence": {"documentation": sorted(set(documents))},
                "status": "documented",
            }
        )

    table_nodes = table_asset_nodes(root)
    state_nodes = game_state_nodes(root)
    claim_nodes_list = claim_nodes(root)
    nodes.extend(rom_pattern_nodes(root))
    nodes.extend(table_nodes)
    nodes.extend(state_nodes)
    nodes.extend(claim_nodes_list)

    for source_id, body in bodies.items():
        for called_name in sorted(set(CALL_RE.findall(body)) - KEYWORDS):
            candidates = name_to_ids.get(called_name, [])
            if len(candidates) == 1 and candidates[0] != source_id:
                relations.append({"kind": "calls", "from": source_id, "to": candidates[0]})
        for table in table_nodes:
            if table["name"] in body:
                relations.append({"kind": "uses-table", "from": source_id, "to": table["id"]})
        for state in state_nodes:
            if state["name"] in body:
                relations.append({"kind": "handles-state", "from": source_id, "to": state["id"]})
    for claim in claim_nodes_list:
        for target in claim["claim"]["relates_to"]:
            relations.append({"kind": "asserts", "from": claim["id"], "to": target})

    return {
        "schema_version": 1,
        "generated_by": "tools/generate_knowledge_graph.py",
        "source_priority": ["Z80 ASM/ROM", "C-port", "annotated documentation", "visualizations"],
        "node_kinds": [
            "c-function", "asm-routine", "ram-slot", "rom-pattern",
            "game-state", "claim", "table-asset",
        ],
        "nodes": sorted(nodes, key=lambda node: node["id"]),
        "relations": sorted(relations, key=lambda relation: (relation["kind"], relation["from"], relation["to"])),
    }


def main() -> int:
    graph = build_graph(ROOT)
    OUTPUT.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(graph['nodes'])} nodes, {len(graph['relations'])} relations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
