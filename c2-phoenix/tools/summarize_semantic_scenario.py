#!/usr/bin/env python3
"""Summarize semantic-object and event coverage for one C2 replay export."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


CONTRACT = "org.hhi.phoenix.c2.semantic-frame/v1"


def coverage(document: dict) -> dict:
    frames = document.get("frames", [])
    active_kinds = set()
    event_types = Counter()
    players = set()
    level_rounds = set()
    states = set()
    for frame in frames:
        game = frame.get("game", {})
        players.add(game.get("player"))
        level_rounds.add((game.get("level"), game.get("round")))
        states.add(game.get("state"))
        for object_ in frame.get("objects", []):
            if object_.get("active"):
                active_kinds.add(object_["kind"])
        event_types.update(event["type"] for event in frame.get("events", []))
    return {
        "frames": len(frames),
        "players": sorted(player for player in players if player is not None),
        "level_rounds": sorted(level_round for level_round in level_rounds if None not in level_round),
        "states": sorted(state for state in states if state is not None),
        "active_kinds": sorted(active_kinds),
        "event_types": dict(sorted(event_types.items())),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("semantic_trace", type=Path)
    parser.add_argument("--name", default="scenario")
    parser.add_argument("--require-kind", action="append", default=[])
    parser.add_argument("--require-event", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    document = json.loads(args.semantic_trace.read_text(encoding="utf-8"))
    if document.get("schema") != CONTRACT:
        raise ValueError("unsupported semantic frame contract")
    result = coverage(document)
    print(f"C2 semantic scenario: {args.name}")
    print(f"  frames: {result['frames']}")
    print(f"  players: {', '.join(result['players']) or '(none)'}")
    print(
        "  level/rounds: "
        + ", ".join(f"{level}/{round_}" for level, round_ in result["level_rounds"])
    )
    print(f"  states: {', '.join(result['states'])}")
    print(f"  active kinds: {', '.join(result['active_kinds'])}")
    print(
        "  events: "
        + ", ".join(f"{name}={count}" for name, count in result["event_types"].items())
    )
    missing_kinds = sorted(set(args.require_kind) - set(result["active_kinds"]))
    missing_events = sorted(set(args.require_event) - set(result["event_types"]))
    if missing_kinds or missing_events:
        if missing_kinds:
            print(f"  missing required kinds: {', '.join(missing_kinds)}")
        if missing_events:
            print(f"  missing required events: {', '.join(missing_events)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
