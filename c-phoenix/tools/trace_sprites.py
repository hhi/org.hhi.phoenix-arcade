#!/usr/bin/env python3
"""Extract per-object movement and event traces from a Phoenix RAM dump.

The dump format is shared by c-phoenix and jphoenix:
    4-byte big-endian frame number + 3072 bytes for $4000-$4BFF.

The tracer deliberately distinguishes RAM-backed object slots from visual
effects that have no independent coordinate structure. Mothership and shield
entries therefore expose state/tile-region changes rather than invented X/Y
coordinates.
"""

import argparse
import csv
import json
import struct
import sys
import zlib


RAM_BASE = 0x4000
RAM_SIZE = 0x0C00
RECORD_SIZE = 4 + RAM_SIZE
ALIEN_COUNT = 16
BIRD_COUNT = 8
ENEMY_BULLET_COUNT = 5
ALIEN_LEVELS = {0x00, 0x01, 0x02, 0x03, 0x0A, 0x0B}
BIRD_LEVELS = {0x05, 0x07}
MOTHERSHIP_LEVELS = {0x09, 0x0A, 0x0B}

KINDS = (
    "all",
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

FIELDNAMES = (
    "frame", "player", "kind", "id", "level_and_round", "game_state",
    "active", "phase", "type", "state", "shape", "x", "y",
    "old_screen_addr", "screen_addr", "movement_pattern", "timer", "score",
    "flags", "region_hash", "source",
)


def ram_byte(ram, address):
    return ram[address - RAM_BASE]


def ram_word(ram, address):
    return (ram_byte(ram, address) << 8) | ram_byte(ram, address + 1)


def player_name(mode):
    if mode == 0:
        return "player1"
    if mode == 1:
        return "player2"
    if mode == 2:
        return "intro"
    return "other"


def record_base(frame, ram, kind, object_id, source):
    return {
        "frame": frame,
        "player": player_name(ram_byte(ram, 0x43A3)),
        "kind": kind,
        "id": object_id,
        "level_and_round": ram_byte(ram, 0x43B8),
        "game_state": ram_byte(ram, 0x43A4),
        "source": source,
    }


def slot_snapshot(frame, ram, kind, object_id, grid, screen, source):
    state = ram_byte(ram, grid)
    snapshot = record_base(frame, ram, kind, object_id, source)
    snapshot.update({
        "active": bool(state & 0x08),
        "state": state,
        "shape": ram_byte(ram, grid + 1),
        "x": ram_byte(ram, grid + 2),
        "y": ram_byte(ram, grid + 3),
        "old_screen_addr": ram_word(ram, screen),
        "screen_addr": ram_word(ram, screen + 2),
    })
    return snapshot


def player_ship_snapshots(frame, ram):
    yield slot_snapshot(
        frame, ram, "player_ship", 0, 0x43C0, 0x43E0, "$43C0-$43C3,$43E0-$43E3"
    )


def player_bullet_snapshots(frame, ram):
    yield slot_snapshot(
        frame, ram, "player_bullet", 0, 0x43C4, 0x43E4, "$43C4-$43C7,$43E4-$43E7"
    )


def above_player_bullet_snapshots(frame, ram):
    yield slot_snapshot(
        frame, ram, "above_player_bullet", 0, 0x43C8, 0x43E8,
        "$43C8-$43CB,$43E8-$43EB"
    )


def enemy_bullet_snapshots(frame, ram):
    for slot in range(ENEMY_BULLET_COUNT):
        yield slot_snapshot(
            frame, ram, "enemy_bullet", slot, 0x43CC + slot * 4,
            0x43EC + slot * 4,
            f"${0x43CC + slot * 4:04X}-${0x43CF + slot * 4:04X},"
            f"${0x43EC + slot * 4:04X}-${0x43EF + slot * 4:04X}",
        )


def alien_snapshots(frame, ram):
    level = ram_byte(ram, 0x43B8) & 0x0F
    if level not in ALIEN_LEVELS:
        return
    for slot in range(ALIEN_COUNT):
        movement = 0x4B50 + slot * 2
        grid = 0x4B70 + slot * 4
        screen = 0x4BB0 + slot * 4
        snapshot = slot_snapshot(
            frame, ram, "alien", slot, grid, screen,
            f"${movement:04X}-${movement + 1:04X},${grid:04X}-${grid + 3:04X},"
            f"${screen:04X}-${screen + 3:04X}",
        )
        snapshot["movement_pattern"] = ram_word(ram, movement)
        yield snapshot


def bird_variant(bird_type):
    if bird_type == 0:
        return "inactive"
    if bird_type < 0x0B:
        return "plain_bird"
    if bird_type <= 0x0D:
        return "egg"
    return "grown_bird"


def bird_snapshots(frame, ram):
    if (ram_byte(ram, 0x43B8) & 0x0F) not in BIRD_LEVELS:
        return
    for slot in range(BIRD_COUNT):
        base = 0x4B70 + slot * 8
        bird_type = ram_byte(ram, base)
        phase = ram_byte(ram, base + 6)
        snapshot = record_base(
            frame, ram, "bird", slot, f"${base:04X}-${base + 7:04X}"
        )
        snapshot.update({
            "active": bird_type != 0,
            "phase": "climbing" if phase >= 0x10 else "descending",
            "type": bird_variant(bird_type),
            "state": bird_type,
            "shape": bird_type,
            "vertical_offset": ram_byte(ram, base + 3),
            "x": ram_byte(ram, base + 5),
            "y": ram_byte(ram, base + 7),
            "screen_addr": ram_word(ram, base + 1),
            "movement_pattern": phase,
            "timer": ram_byte(ram, base + 4),
        })
        yield snapshot


def bird_explosion_snapshots(frame, ram):
    for object_id, base, phase in (
        (0, 0x4370, "normal"),
        (1, 0x4374, "normal"),
        (2, 0x4378, "bonus"),
        (3, 0x437C, "bonus"),
    ):
        timer = ram_byte(ram, base)
        snapshot = record_base(
            frame, ram, "bird_explosion", object_id, f"${base:04X}-${base + 3:04X}"
        )
        snapshot.update({
            "active": timer != 0,
            "phase": phase,
            "timer": timer,
            "score": ram_byte(ram, base + 1),
            "screen_addr": ram_word(ram, base + 2),
        })
        yield snapshot


def player_explosion_snapshots(frame, ram):
    game_state = ram_byte(ram, 0x43A4)
    timer = ram_byte(ram, 0x43A5)
    particle_flag = ram_byte(ram, 0x4363)
    snapshot = record_base(frame, ram, "player_explosion", 0, "$43A4-$43A5,$4363,$43E2-$43E3")
    snapshot.update({
        "active": game_state == 0x04,
        "phase": "exploding" if game_state == 0x04 else "inactive",
        "timer": timer,
        "flags": particle_flag,
        "screen_addr": ram_word(ram, 0x43E2),
    })
    yield snapshot


def mothership_snapshots(frame, ram):
    level = ram_byte(ram, 0x43B8) & 0x0F
    game_state = ram_byte(ram, 0x43A4)
    if game_state == 0x06:
        phase = "explosion"
    elif game_state == 0x07:
        phase = "score_display"
    elif level in MOTHERSHIP_LEVELS:
        phase = "active"
    else:
        phase = "inactive"
    flags = (
        ram_byte(ram, 0x4366)
        | (ram_byte(ram, 0x4367) << 8)
        | (ram_byte(ram, 0x436B) << 16)
        | (ram_byte(ram, 0x4363) << 24)
    )
    region = ram[0x4800 - RAM_BASE:0x4B40 - RAM_BASE]
    snapshot = record_base(frame, ram, "mothership", 0, "$4363,$4366-$4367,$436B,$4800-$4B3F")
    snapshot.update({
        "active": phase != "inactive",
        "phase": phase,
        "timer": ram_byte(ram, 0x43A5),
        "flags": flags,
        "region_hash": zlib.crc32(region),
    })
    yield snapshot


def shield_snapshots(frame, ram):
    shield_count = ram_byte(ram, 0x43A6)
    snapshot = record_base(frame, ram, "shield_segments", 0, "$43A6,$4362,$43E2-$43E3")
    snapshot.update({
        "active": shield_count > 0xC0,
        "phase": "active" if shield_count > 0xC0 else "inactive",
        "timer": shield_count,
        "flags": ram_byte(ram, 0x4362),
        "screen_addr": ram_word(ram, 0x43E2),
    })
    yield snapshot


EXTRACTORS = {
    "player_ship": player_ship_snapshots,
    "player_bullet": player_bullet_snapshots,
    "above_player_bullet": above_player_bullet_snapshots,
    "enemy_bullet": enemy_bullet_snapshots,
    "aliens": alien_snapshots,
    "birds": bird_snapshots,
    "bird_explosion": bird_explosion_snapshots,
    "player_explosion": player_explosion_snapshots,
    "mothership": mothership_snapshots,
    "shield_segments": shield_snapshots,
}


def iter_frames(path):
    with open(path, "rb") as dump:
        record_index = 0
        while True:
            record = dump.read(RECORD_SIZE)
            if not record:
                return
            record_index += 1
            if len(record) != RECORD_SIZE:
                raise ValueError(
                    f"truncated record {record_index}: expected {RECORD_SIZE} bytes, "
                    f"got {len(record)}"
                )
            frame = struct.unpack_from(">I", record)[0]
            yield frame, record[4:]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Trace Phoenix object slots and visual effects from a RAM dump."
    )
    parser.add_argument("ram_dump", help="RAM dump written by --ram-dump")
    parser.add_argument(
        "--kind", choices=KINDS, action="append",
        help="object family to trace; repeat, or use all (default: all)"
    )
    parser.add_argument(
        "--format", choices=("csv", "jsonl"), default="csv", help="output format"
    )
    parser.add_argument("--output", default="-", help="output file, or - for stdout")
    parser.add_argument(
        "--all-frames", action="store_true", help="emit every selected object every frame"
    )
    parser.add_argument(
        "--only-active", action="store_true", help="omit snapshots whose active flag is false"
    )
    parser.add_argument(
        "--slot", type=int, action="append", metavar="N",
        help="trace one numeric object id; repeat to select multiple ids"
    )
    parser.add_argument(
        "--player", choices=("all", "1", "2"), default="all",
        help="restrict output to the active player bank"
    )
    return parser.parse_args()


def selected_kinds(args):
    requested = args.kind or ["all"]
    if "all" in requested:
        return tuple(EXTRACTORS)
    return tuple(dict.fromkeys(requested))


def snapshot_key(snapshot):
    return tuple((key, value) for key, value in snapshot.items() if key != "frame")


def should_emit(snapshot, previous, args):
    if args.player != "all" and snapshot["player"] != f"player{args.player}":
        return False
    if args.slot is not None and snapshot["id"] not in args.slot:
        return False
    if args.only_active and not snapshot["active"]:
        return False
    return args.all_frames or previous != snapshot_key(snapshot)


def normalized(snapshot):
    return {field: snapshot.get(field) for field in FIELDNAMES}


def write_trace(records, output, output_format):
    close_output = output != "-"
    stream = open(output, "w", newline="", encoding="utf-8") if close_output else sys.stdout
    try:
        if output_format == "csv":
            writer = csv.DictWriter(stream, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(normalized(record) for record in records)
        else:
            for record in records:
                stream.write(json.dumps(record, sort_keys=True) + "\n")
    finally:
        if close_output:
            stream.close()


def main():
    args = parse_args()
    try:
        kinds = selected_kinds(args)
        previous = {}

        def records():
            for frame, ram in iter_frames(args.ram_dump):
                for kind in kinds:
                    for snapshot in EXTRACTORS[kind](frame, ram):
                        key = (kind, snapshot["id"])
                        old_state = previous.get(key)
                        if should_emit(snapshot, old_state, args):
                            yield snapshot
                        previous[key] = snapshot_key(snapshot)

        write_trace(records(), args.output, args.format)
    except (OSError, ValueError) as error:
        print(f"trace_sprites.py: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
