#!/usr/bin/env python3
"""Generate a topic-oriented index from the knowledge graph.

The existing README is a *source listing*: documents grouped by which file
they annotate, counted in files. That ordering is free — it follows from the
filesystem — but it answers only "where does this code live?".

A real question crosses those boundaries. *How does a bird decide to dive?*
touches bird_logic.c and bird_wave_behavior.c (README section 2), the
behaviour scripts in phoenix_tables.c (section 6), sixteen SVGs under
animations/bird_scripts/, and a ROM range no section mentions. This tool
produces the second view: subject catalogue beside shelf order.

Topic *names* are the one judgement here — a short curated list below, since
"what is this about?" is not derivable. Everything else is: membership starts
from nodes whose identifier matches the topic's seed terms, then follows
`calls`, `uses-table`, `handles-state` and `implements` outward, collecting
the functions, ASM ranges, ROM tables, RAM slots, game states and documents
that hang together.

A node may appear under several topics. That is the point of a subject
catalogue and not a defect: a book sits on one shelf but under many subjects.

Usage:
    python3 c-phoenix/c-annotated/tools/generate_topic_index.py
    python3 c-phoenix/c-annotated/tools/generate_topic_index.py --check
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path("c-phoenix")
GRAPH = ROOT / "c-annotated" / "knowledge-graph.json"
OUTPUT = ROOT / "c-annotated" / "topic-index.md"

# The curated part: a topic name and the seed terms that start the traversal.
# Keep this list short and stable; membership below is derived, not listed.
TOPICS: list[tuple[str, str, tuple[str, ...]]] = [
    ("Bird waves and dive attacks", "birds",
     ("bird", "egg", "asm:34", "asm:35", "asm:36", "asm:37")),
    ("Alien swarm movement and flight patterns", "aliens",
     ("alien", "movement_cluster", "direction_vector", "asm:0D")),
    ("Mothership", "mothership",
     ("mothership", "asm:23", "asm:2520", "asm:246A")),
    ("Player ship, bullets and shield", "player",
     ("player", "shield", "bullet", "asm:08", "asm:09", "asm:0A")),
    ("Collision detection and scoring", "collision",
     ("collision", "kill_score", "score", "bcd", "asm:0E")),
    ("Game state machine and level flow", "state",
     ("game_state", "state_0", "state_1", "state_2", "state_3", "state_4",
      "state_5", "state_6", "state_7", "level_", "asm:04")),
    ("Attract mode, coins and demo", "attract",
     ("attract", "splash", "demo", "coin", "credit", "prompt")),
    ("Sprite rendering and video", "video",
     ("sprite", "screen_ram", "vram", "video", "scroll", "starfield")),
    ("Sound hardware and synthesis", "sound",
     ("sound", "tms36xx", "poly18", "astable", "rcdisc", "resampler", "asm:3A")),
]

# Helpers reached from almost everywhere. Including them in a topic says
# nothing about the topic, so they are kept out of the expansion step.
UBIQUITOUS = {
    "coverage_hit", "mem_read", "mem_write", "get_random_number",
    "drawNx2", "draw_image_c_by_b", "hw_write_scroll_register",
    "hw_write_video_register", "hw_write_sound_a", "hw_write_sound_b",
    "print_text_lines", "check_input_bits", "runtime_call_trace",
}


def load_graph() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def collect(graph: dict, seeds: tuple[str, ...]) -> tuple[set[str], set[str]]:
    """Return (core, related).

    `core` are nodes whose own identifier or name matches a seed term — the
    routine is about this topic. `related` are one relation away: reached
    through calls, tables, states or ASM annotations. Keeping them apart is
    the honest presentation, because a neighbour is context, not subject
    matter.
    """
    lowered = tuple(s.lower() for s in seeds)
    core = {
        node["id"]
        for node in graph["nodes"]
        if node["kind"] != "claim"
        and node["name"] not in UBIQUITOUS
        and any(term in node["id"].lower() or term in node["name"].lower() for term in lowered)
    }

    by_id = {n["id"]: n for n in graph["nodes"]}
    outgoing: dict[str, set[str]] = defaultdict(set)
    for relation in graph["relations"]:
        if relation["kind"] in {"calls", "uses-table", "handles-state", "implements"}:
            outgoing[relation["from"]].add(relation["to"])

    related: set[str] = set()
    for node_id in core:
        for target in outgoing.get(node_id, set()):
            node = by_id.get(target)
            if node and node["name"] not in UBIQUITOUS and target not in core:
                related.add(target)
    return core, related


def render(graph: dict) -> str:
    by_id = {n["id"]: n for n in graph["nodes"]}
    claims_for: dict[str, list[str]] = defaultdict(list)
    for relation in graph["relations"]:
        if relation["kind"] == "asserts":
            claims_for[relation["to"]].append(relation["from"])

    lines = [
        "# Phoenix Topic Index",
        "",
        "*Generated by `tools/generate_topic_index.py` — do not edit by hand.*",
        "",
        "A subject catalogue beside the file-oriented "
        "[`README.md`](README.md). Topics cross file boundaries, so a routine "
        "may appear more than once. Topic names are curated; membership is "
        "derived from the knowledge graph.",
        "",
    ]

    for title, _key, seeds in TOPICS:
        core, related = collect(graph, seeds)
        grouped: dict[str, list[dict]] = defaultdict(list)
        for node_id in core:
            node = by_id.get(node_id)
            if node:
                grouped[node["kind"]].append(node)

        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"*{len(core)} nodes on topic, {len(related)} one relation away.*")
        lines.append("")

        # Sort on (name, id): two routines can share a name across files
        # (update_hi_score exists in both scoring.c and state_init.c), and a
        # tie would otherwise resolve differently on each run.
        functions = sorted(grouped.get("c-function", []), key=lambda n: (n["name"], n["id"]))
        if functions:
            lines.append("**Functions**")
            lines.append("")
            for node in functions:
                src = node.get("source", {})
                where = f"{src.get('path','?')}#L{src.get('line','?')}"
                asm = " ".join(f"${r['start']}-${r['end']}" for r in node.get("asm_ranges", []))
                verified = " ✓" if claims_for.get(node["id"]) else ""
                lines.append(f"- `{node['name']}` — [{where}](../{src.get('path','')})"
                             + (f" · {asm}" if asm else "") + verified)
            lines.append("")

        for kind, label in (("table-asset", "ROM tables"),
                            ("game-state", "Game states"),
                            ("ram-slot", "RAM slots"),
                            ("rom-pattern", "Flight patterns")):
            items = sorted(grouped.get(kind, []), key=lambda n: (n["name"], n["id"]))
            if not items:
                continue
            names = ", ".join(f"`{n['name']}`" for n in items[:24])
            more = f" *(+{len(items) - 24} more)*" if len(items) > 24 else ""
            lines.append(f"**{label}** — {names}{more}")
            lines.append("")

        asm_nodes = sorted(grouped.get("asm-routine", []), key=lambda n: n["id"])
        if asm_nodes:
            spans = ", ".join(n["name"].replace("ASM ", "") for n in asm_nodes[:20])
            more = f" *(+{len(asm_nodes) - 20} more)*" if len(asm_nodes) > 20 else ""
            lines.append(f"**ROM ranges** — {spans}{more}")
            lines.append("")

        neighbours = sorted(
            (by_id[n]["name"] for n in related if by_id[n]["kind"] == "c-function")
        )
        if neighbours:
            shown = ", ".join(f"`{n}`" for n in neighbours[:18])
            more = f" *(+{len(neighbours) - 18} more)*" if len(neighbours) > 18 else ""
            lines.append(f"**Reached from here** — {shown}{more}")
            lines.append("")

        lines.append("---")
        lines.append("")

    lines.append("A ✓ marks a routine backed by a verified claim in "
                 "`knowledge-claims.json`.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the committed index differs from a fresh render",
    )
    args = parser.parse_args()

    rendered = render(load_graph())

    if args.check:
        if not OUTPUT.is_file():
            print(f"{OUTPUT}: missing; run without --check to generate it")
            return 1
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            print("Topic index is stale. Run `make kg-topics` and commit the result.")
            return 1
        print(f"Topic index: OK ({len(TOPICS)} topics)")
        return 0

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(TOPICS)} topics)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
