#!/usr/bin/env python3
"""Export validated Phoenix trace samples to the C2 semantic frame contract."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType


CONTRACT = "org.hhi.phoenix.c2.semantic-frame/v1"
SEMANTIC_KINDS = (
    "player_ship",
    "player_bullet",
    "above_player_bullet",
    "enemy_bullet",
    "aliens",
    "birds",
    "bird_explosion",
    "player_explosion",
    "mothership",
    "shield_segments",
)
PROJECTILE_KINDS = {
    "player_bullet",
    "above_player_bullet",
    "enemy_bullet",
}
STATE_NAMES = {
    0x00: "new_game_or_player_switch",
    0x01: "score_flash",
    0x02: "round_initialization",
    0x03: "normal_gameplay",
    0x04: "player_explosion",
    0x05: "game_over",
    0x06: "mothership_explosion",
    0x07: "mothership_score_display",
}


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def adapter_modules(repository_root: Path) -> tuple[ModuleType, ModuleType]:
    tools_dir = repository_root / "c-phoenix" / "tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))
    trace = load_module("trace_sprites", tools_dir / "trace_sprites.py")
    viewer = load_module("view_sprite_trace", tools_dir / "view_sprite_trace.py")
    return trace, viewer


def packed_bcd(ram: bytes, trace: ModuleType, address: int) -> int | None:
    values = [trace.ram_byte(ram, address + offset) for offset in range(3)]
    if any(nibble > 9 for value in values for nibble in (value >> 4, value & 0x0F)):
        return None
    return int("".join(f"{value:02X}" for value in values))


def game_context(snapshot: dict, ram: bytes, trace: ModuleType) -> dict:
    level_and_round = snapshot["level_and_round"]
    return {
        "player": snapshot["player"],
        "level": level_and_round & 0x0F,
        "round": level_and_round >> 4,
        "state": STATE_NAMES.get(snapshot["game_state"], "other"),
        "scores": {
            "player1": packed_bcd(ram, trace, 0x4381),
            "player2": packed_bcd(ram, trace, 0x4385),
        },
        "lives": {
            "player1": trace.ram_byte(ram, 0x4390),
            "player2": trace.ram_byte(ram, 0x4391),
        },
    }


def appearance(snapshot: dict) -> dict:
    kind = snapshot["kind"]
    if kind == "bird":
        variant = snapshot.get("type") or "unknown"
        motion = snapshot.get("phase") or "active"
    else:
        variant = "standard"
        motion = snapshot.get("phase") or (
            "active" if snapshot["active"] else "inactive"
        )
    return {"family": kind, "variant": variant, "motion": motion}


def presentation_visible(snapshot: dict, game: dict) -> bool:
    if not snapshot["active"]:
        return False
    if snapshot["kind"] in PROJECTILE_KINDS:
        return game["state"] == "normal_gameplay"
    return True


def semantic_object(snapshot: dict, visual_sample: dict, game: dict | None = None) -> dict:
    game = game or {"state": "normal_gameplay"}
    result = {
        "key": f"{snapshot['player']}:{snapshot['kind']}:{snapshot['id']}",
        "kind": snapshot["kind"],
        "slot": snapshot["id"],
        "active": bool(snapshot["active"]),
        "visible": presentation_visible(snapshot, game),
        "appearance": appearance(snapshot),
    }
    x = visual_sample["visual_x"]
    y = visual_sample["visual_y"]
    if x is not None and y is not None:
        result["position"] = {"x": x, "y": y}
    return result


def semantic_events(previous: dict | None, current: dict) -> list[dict]:
    if previous is None:
        return []
    events = []
    old_game, new_game = previous["game"], current["game"]
    if old_game["player"] != new_game["player"]:
        events.append({"type": "active_player_changed", "player": new_game["player"]})
    if (old_game["level"], old_game["round"]) != (
        new_game["level"], new_game["round"],
    ):
        events.append({
            "type": "level_round_changed",
            "level": new_game["level"],
            "round": new_game["round"],
        })
    if old_game["state"] != new_game["state"]:
        events.append({"type": "game_state_changed", "state": new_game["state"]})
    for player in ("player1", "player2"):
        old_score = old_game["scores"][player]
        new_score = new_game["scores"][player]
        if old_score is not None and new_score is not None and old_score != new_score:
            events.append({
                "type": "score_changed", "player": player,
                "from": old_score, "to": new_score,
            })
        if old_game["lives"][player] != new_game["lives"][player]:
            events.append({
                "type": "lives_changed", "player": player,
                "from": old_game["lives"][player],
                "to": new_game["lives"][player],
            })
    old_objects = {object_["key"]: object_ for object_ in previous["objects"]}
    for object_ in current["objects"]:
        old_object = old_objects.get(object_["key"])
        if old_object is None or old_object["active"] == object_["active"]:
            continue
        events.append({
            "type": "object_activated" if object_["active"] else "object_deactivated",
            "object": object_["key"],
        })
    events.extend(observed_impacts(previous, current))
    return events


def observed_impacts(previous: dict, current: dict) -> list[dict]:
    """Infer only close same-frame projectile/target deactivations as impacts."""
    old_objects = {object_["key"]: object_ for object_ in previous["objects"]}
    current_objects = {object_["key"]: object_ for object_ in current["objects"]}
    ended_projectiles = [
        old for key, old in old_objects.items()
        if old["kind"] in PROJECTILE_KINDS
        and old["active"]
        and key in current_objects
        and not current_objects[key]["active"]
        and old.get("position")
    ]
    ended_targets = [
        old for key, old in old_objects.items()
        if old["kind"] in {"alien", "bird"}
        and old["active"]
        and key in current_objects
        and not current_objects[key]["active"]
        and old.get("position")
    ]
    impacts = []
    for projectile in ended_projectiles:
        px, py = projectile["position"]["x"], projectile["position"]["y"]
        nearest = min(
            ended_targets,
            key=lambda target: (
                (target["position"]["x"] - px) ** 2
                + (target["position"]["y"] - py) ** 2
            ),
            default=None,
        )
        if nearest is None:
            continue
        tx, ty = nearest["position"]["x"], nearest["position"]["y"]
        if (tx - px) ** 2 + (ty - py) ** 2 > 16 ** 2:
            continue
        impacts.append({
            "type": "impact_observed",
            "projectile": projectile["key"],
            "target": nearest["key"],
            "position": {"x": tx, "y": ty},
        })
    return impacts


def hide_terminal_projectile_frames(frames: list[dict]) -> None:
    """End projectile presentation before its retained slot can look stalled."""
    for index, current in enumerate(frames[:-1]):
        following_objects = {
            object_["key"]: object_ for object_ in frames[index + 1]["objects"]
        }
        for object_ in current["objects"]:
            if object_["kind"] not in PROJECTILE_KINDS or not object_["visible"]:
                continue
            successor = following_objects.get(object_["key"])
            if successor is None or not successor["visible"]:
                object_["visible"] = False
                if index > 0:
                    predecessor = next(
                        (
                            candidate
                            for candidate in frames[index - 1]["objects"]
                            if candidate["key"] == object_["key"]
                        ),
                        None,
                    )
                    if predecessor is not None:
                        predecessor["visible"] = False


def export_frames(trace: ModuleType, viewer: ModuleType, dump_path: Path) -> dict:
    frames = []
    for sequence, (frame, ram) in enumerate(trace.iter_frames(dump_path)):
        scroll = trace.ram_byte(ram, 0x43B9)
        objects = []
        context = None
        for kind in SEMANTIC_KINDS:
            for snapshot in trace.EXTRACTORS[kind](frame, ram):
                context = context or game_context(snapshot, ram, trace)
                visual = viewer.viewer_sample(snapshot, scroll=scroll)
                objects.append(semantic_object(snapshot, visual, context))
        if context is None:
            continue
        semantic_frame = {
            "frame": frame,
            "sequence": sequence,
            "timeline": {
                "tick": (
                    trace.ram_byte(ram, 0x4398) << 8
                    | trace.ram_byte(ram, 0x4399)
                ),
            },
            "game": context,
            "objects": objects,
        }
        semantic_frame["events"] = semantic_events(
            frames[-1] if frames else None, semantic_frame
        )
        frames.append(semantic_frame)
    hide_terminal_projectile_frames(frames)
    return {
        "schema": CONTRACT,
        "source": {"adapter": "c2-phoenix", "frame_count": len(frames)},
        "frames": frames,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ram_dump", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Phoenix Arcade monorepo root",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.ram_dump.is_file():
        raise SystemExit(
            "RAM dump not found: "
            f"{args.ram_dump}\n"
            "Create a C-Phoenix comparison dump first, for example:\n"
            "  make -C ../c-phoenix tracerun "
            "COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt "
            "COMPARE_FRAMES=13935 COMPARE_NAME=bird-investigation "
            "COMPARE_STOP_AFTER=999999\n"
            "The default C-Phoenix output is "
            "/tmp/port_bird-investigation.bin (underscore after 'port')."
        )
    trace, viewer = adapter_modules(args.repository_root)
    document = export_frames(trace, viewer, args.ram_dump)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
