#!/usr/bin/env python3
"""Evaluate replay scripts against c-phoenix coverage output."""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path


# A search run is raw output, not a fixture: a script only belongs in
# context/input-scripts/generated once `evaluate` has confirmed it reaches the
# target. Defaulting there put unvetted scripts among the vetted ones and made
# every example that omitted --output-dir write into the committed corpus.
DEFAULT_OUTPUT_DIR = "/tmp/input-bot"

TARGETS = {
    "alien_kill": lambda c: hit(c, "alien_killed_with_score"),
    "bird_hit": lambda c: hit(c, "small_bird_hit") or hit(c, "large_bird_or_egg_hit"),
    "bonus_life_awarded": lambda c: hit(c, "bonus_life_awarded"),
    "bird_wave_entry": lambda c: summary(c, "bird_wave_frames") > 0,
    "bird_wave_gameplay": lambda c: summary(c, "bird_wave_gameplay_frames") > 0,
    "enemy_bullets_active": lambda c: summary(c, "enemy_bullet_active_frames") > 0,
    "coin_accepted": lambda c: hit(c, "coin_accepted"),
    "game_over": lambda c: summary(c, "game_overs") > 0,
    "gameplay_level_5": lambda c: summary(c, "max_gameplay_level_and_round") >= 0x05,
    "gameplay_level_7": lambda c: summary(c, "max_gameplay_level_and_round") >= 0x07,
    "gameplay_level_8": lambda c: summary(c, "max_gameplay_level_and_round") >= 0x08,
    "gameplay_level_9": lambda c: summary(c, "max_gameplay_level_and_round") >= 0x09,
    "grown_bird_bonus_explosion": lambda c: hit(c, "grown_bird_bonus_explosion"),
    "level_transition": lambda c: summary(c, "level_transitions") > 0,
    "mothership_active": lambda c: summary(c, "mothership_frames") > 0,
    "mothership_active_gameplay": lambda c: summary(c, "mothership_gameplay_frames") > 0,
    "mothership_core_gate_70": lambda c: hit(c, "mothership_core_gate_70_seen"),
    "mothership_core_window": lambda c: hit(c, "mothership_core_window_seen"),
    "mothership_explosion": lambda c: hit(c, "mothership_explosion_trigger")
    or game_state_seen(c, "6"),
    "mothership_tile_4c_hit": lambda c: hit(c, "mothership_tile_4c_hit"),
    "mothership_tile_60_hit": lambda c: hit(c, "mothership_tile_60_hit"),
    "mothership_tile_hit": lambda c: hit(c, "mothership_tile_hit"),
    "player_bullet_fired": lambda c: hit(c, "spawn_player_bullet"),
    "player_death": lambda c: summary(c, "player_deaths") > 0 or hit(c, "player_killed"),
    "shield_used": lambda c: hit(c, "player_shield_pressed"),
    "two_player_game_started": lambda c: hit(c, "two_player_game_started"),
    "two_player_turn_switch": lambda c: hit(c, "two_player_turn_switch"),
    "player_2_bank_initialized": lambda c: hit(c, "player_2_bank_initialized"),
}


def hit(coverage: dict, name: str) -> bool:
    return coverage.get("hits", {}).get(name, {}).get("hits", 0) > 0


def summary(coverage: dict, name: str) -> int:
    return int(coverage.get("summary", {}).get(name, 0))


def game_state_seen(coverage: dict, state: str) -> bool:
    return coverage.get("game_states", {}).get(state, {}).get("hits", 0) > 0


def run_emulator(args: argparse.Namespace, coverage_path: Path) -> subprocess.CompletedProcess:
    cmd = [
        args.emulator,
        f"--run-frames={args.frames}",
        f"--input-script={args.script}",
        f"--coverage-dump={coverage_path}",
    ]
    if args.ram_dump:
        cmd.append(f"--ram-dump={args.ram_dump}")
    if getattr(args, "no_render", False):
        cmd.append("--no-render")

    env = os.environ.copy()
    if args.sdl_video_driver:
        env["SDL_VIDEODRIVER"] = args.sdl_video_driver

    return subprocess.run(
        cmd,
        cwd=args.cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def load_coverage(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def sorted_hit_names(coverage: dict) -> list[str]:
    hits = coverage.get("hits", {})
    return sorted(name for name, data in hits.items() if data.get("hits", 0) > 0)


def print_summary(coverage: dict, targets: list[str]) -> None:
    frames = coverage.get("frames", {})
    summ = coverage.get("summary", {})

    print("Replay summary")
    print(f"  frames: {frames.get('total', 0)}")
    print(f"  max_level_and_round: 0x{int(summ.get('max_level_and_round', 0)):02X}")
    print(f"  max_gameplay_level_and_round: 0x{int(summ.get('max_gameplay_level_and_round', 0)):02X}")
    print(f"  level_transitions: {summ.get('level_transitions', 0)}")
    print(f"  player_deaths: {summ.get('player_deaths', 0)}")
    print(f"  game_overs: {summ.get('game_overs', 0)}")
    print(f"  attract_frames: {summ.get('attract_frames', 0)}")
    print(f"  gameplay_frames: {summ.get('gameplay_frames', 0)}")
    print(f"  enemy_bullet_active_frames: {summ.get('enemy_bullet_active_frames', 0)}")
    print(f"  player_bullet_active_frames: {summ.get('player_bullet_active_frames', 0)}")
    print(f"  bird_wave_frames: {summ.get('bird_wave_frames', 0)}")
    print(f"  bird_wave_gameplay_frames: {summ.get('bird_wave_gameplay_frames', 0)}")
    print(f"  mothership_frames: {summ.get('mothership_frames', 0)}")
    print(f"  mothership_gameplay_frames: {summ.get('mothership_gameplay_frames', 0)}")

    seen_levels = [
        level for level, data in coverage.get("levels", {}).items()
        if data.get("hits", 0) > 0
    ]
    seen_states = [
        state for state, data in coverage.get("game_states", {}).items()
        if data.get("hits", 0) > 0
    ]
    print(f"  game_states_seen: {', '.join(seen_states) or '-'}")
    print(f"  levels_seen: {', '.join(seen_levels) or '-'}")

    if targets:
        print("Targets")
        for target in targets:
            ok = TARGETS[target](coverage)
            print(f"  {target}: {'hit' if ok else 'miss'}")

    names = sorted_hit_names(coverage)
    print(f"Coverage hits ({len(names)})")
    for name in names:
        data = coverage["hits"][name]
        print(f"  {name}: {data.get('hits', 0)} first={data.get('first_frame', 0)}")


def evaluate(args: argparse.Namespace) -> int:
    if not Path(args.cwd, args.emulator).exists() and "/" in args.emulator:
        print(f"Emulator not found: {Path(args.cwd, args.emulator)}", file=sys.stderr)
        print("Build it first with: make", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="c-phoenix-coverage-") as tmp:
        coverage_path = Path(args.coverage_out) if args.coverage_out else Path(tmp, "coverage.json")
        result = run_emulator(args, coverage_path)
        if result.returncode != 0:
            print(result.stdout, end="")
            print(result.stderr, end="", file=sys.stderr)
            return result.returncode

        coverage = load_coverage(coverage_path)
        if args.json:
            print(json.dumps(coverage, indent=2, sort_keys=True))
        else:
            print_summary(coverage, args.target)

    return 0


def read_script(path: Path) -> list[tuple[int, str, str]]:
    events: list[tuple[int, str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if len(parts) != 3:
                continue
            frame, button, action = parts
            try:
                events.append((int(frame), button, action))
            except ValueError:
                continue
    return sorted(events)


def write_script(path: Path, events: list[tuple[int, str, str]], source: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("# Generated by tools/input_bot.py mutate\n")
        f.write(f"# Seed: {source}\n")
        for frame, button, action in sorted(events):
            f.write(f"{frame} {button} {action}\n")


def add_pulse(events: list[tuple[int, str, str]], frame: int, button: str, duration: int, limit: int) -> None:
    if frame < 1 or frame >= limit:
        return
    events.append((frame, button, "press"))
    events.append((min(frame + duration, limit), button, "release"))


def generated_candidate(
    seed_events: list[tuple[int, str, str]],
    frames: int,
    rng: random.Random,
    mutate_after: int,
    mutation_mode: str,
) -> list[tuple[int, str, str]]:
    start_frame = max(230, mutate_after)

    if mutation_mode == "jitter":
        events = []
        for frame, button, action in seed_events:
            if frame < mutate_after:
                events.append((frame, button, action))
                continue
            if frame >= frames:
                continue
            if rng.random() < 0.15:
                continue
            jittered = max(mutate_after, min(frames - 1, frame + rng.randint(-18, 18)))
            events.append((jittered, button, action))
        for _ in range(rng.randint(6, 18)):
            button = rng.choice(["fire", "left", "right", "shield"])
            add_pulse(
                events,
                rng.randint(start_frame, max(start_frame + 1, frames - 80)),
                button,
                rng.randint(3, 55),
                frames,
            )
        return sorted(events)

    if mutation_mode == "sweep":
        events = [event for event in seed_events if event[0] < mutate_after]
        for button in ("fire", "left", "right", "shield"):
            events.append((start_frame, button, "release"))

        fire_gap = rng.randint(10, 24)
        fire_duration = rng.randint(3, 8)
        frame = start_frame + rng.randint(0, 40)
        while frame < frames - 20:
            add_pulse(events, frame, "fire", fire_duration, frames)
            frame += fire_gap + rng.randint(-3, 5)

        frame = start_frame + rng.randint(0, 80)
        direction = rng.choice(["left", "right"])
        while frame < frames - 60:
            hold = rng.randint(18, 130)
            events.append((frame, direction, "press"))
            events.append((min(frame + hold, frames - 1), direction, "release"))
            frame += hold + rng.randint(2, 24)
            direction = "left" if direction == "right" else "right"

        for _ in range(rng.randint(0, 3)):
            add_pulse(
                events,
                rng.randint(start_frame + 100, max(start_frame + 101, frames - 100)),
                "shield",
                rng.randint(18, 55),
                frames,
            )

        return sorted(events)

    events = [event for event in seed_events if event[0] < mutate_after]
    if mutate_after > 220:
        for button in ("fire", "left", "right", "shield"):
            events.append((start_frame, button, "release"))

    fire_start = start_frame + rng.randint(0, 140)
    fire_gap = rng.randint(18, 42)
    fire_duration = rng.randint(2, 6)
    frame = fire_start
    while frame < frames - 20:
        add_pulse(events, frame, "fire", fire_duration, frames)
        frame += fire_gap + rng.randint(-6, 10)

    frame = start_frame + rng.randint(0, 180)
    current_direction: str | None = None
    while frame < frames - 40:
        direction = rng.choice(["left", "right", "none", "left", "right"])
        hold = rng.randint(18, 85)
        if current_direction is not None:
            events.append((frame, current_direction, "release"))
            current_direction = None
        if direction != "none":
            events.append((frame, direction, "press"))
            events.append((min(frame + hold, frames - 1), direction, "release"))
            current_direction = direction
        frame += hold + rng.randint(2, 32)

    for _ in range(rng.randint(0, 4)):
        add_pulse(events, rng.randint(start_frame + 100, max(start_frame + 101, frames - 100)), "shield", rng.randint(20, 60), frames)

    return sorted(events)


def wants_gameplay_progress(targets: list[str]) -> bool:
    return any(target.endswith("_gameplay") for target in targets)


def coverage_score(coverage: dict, targets: list[str]) -> int:
    summ = coverage.get("summary", {})
    hits = coverage.get("hits", {})
    max_level = int(summ.get("max_level_and_round", 0))
    max_gameplay_level = int(summ.get("max_gameplay_level_and_round", 0))
    gameplay_focus = wants_gameplay_progress(targets)
    score = max_gameplay_level * 150000 if gameplay_focus else max_level * 100000
    if not gameplay_focus:
        score += max_gameplay_level * 25000
    score += int(summ.get("level_transitions", 0)) * 3000
    score += int(summ.get("player_bullet_active_frames", 0)) * 2
    score += int(summ.get("enemy_bullet_active_frames", 0)) * 5
    if not gameplay_focus:
        score += int(summ.get("bird_wave_frames", 0)) * 20
        score += int(summ.get("mothership_frames", 0)) * 20
    score += int(summ.get("bird_wave_gameplay_frames", 0)) * 50
    score += int(summ.get("mothership_gameplay_frames", 0)) * 100
    score += int(summ.get("gameplay_frames", 0)) // 4
    score -= int(summ.get("attract_frames", 0)) // (1 if gameplay_focus else 4)
    score -= int(summ.get("player_deaths", 0)) * 500

    score += int(hits.get("alien_killed_with_score", {}).get("hits", 0)) * 200
    score += int(hits.get("spawn_player_bullet", {}).get("hits", 0)) * 50
    score += int(hits.get("small_bird_hit", {}).get("hits", 0)) * 1000
    score += int(hits.get("large_bird_or_egg_hit", {}).get("hits", 0)) * 1000
    if not gameplay_focus or int(summ.get("mothership_gameplay_frames", 0)) > 0:
        score += int(hits.get("mothership_tile_hit", {}).get("hits", 0)) * 1500
        score += int(hits.get("mothership_tile_60_hit", {}).get("hits", 0)) * 6000
    score += int(hits.get("mothership_core_window_seen", {}).get("hits", 0)) * 5000
    score += int(hits.get("mothership_core_gate_70_seen", {}).get("hits", 0)) * 50000
    score += int(hits.get("mothership_explosion_trigger", {}).get("hits", 0)) * 50000

    for target in targets:
        if TARGETS[target](coverage):
            score += 50000
    return score


def mutate(args: argparse.Namespace) -> int:
    seed_path = Path(args.seed)
    seed_events = read_script(seed_path)
    if not seed_events:
        print(f"No seed events loaded from {seed_path}", file=sys.stderr)
        return 2

    rng = random.Random(args.random_seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    best: list[tuple[int, Path, dict]] = []

    # With --generations 1 (the default) this is a flat random search: every
    # candidate is a mutation of the original seed and the winner is never
    # reused. Above 1 the round's winner becomes the next round's seed, so the
    # search climbs instead of resampling the same neighbourhood. The seed is
    # only replaced on a strict improvement, which keeps it from wandering
    # back downhill on an unlucky round.
    generations = max(1, getattr(args, "generations", 1))
    current_seed = seed_events
    best_score: int | None = None
    trajectory: list[int] = []

    # regenerate and sweep both throw away every seed event at or after
    # --mutate-after and build a fresh pattern there. Re-seeding with a winner
    # then keeps only its opening, so generations cannot compound: measured on a
    # seed with five marker events past frame 220, jitter carries four of them
    # forward and the other two modes carry none. Say so rather than let a run
    # look like it is climbing when it is not.
    if generations > 1 and args.mutation_mode in ("regenerate", "sweep"):
        print(f"warning: --mutation-mode {args.mutation_mode} rebuilds everything from frame "
              f"{args.mutate_after} onward, so a re-seeded winner keeps only its opening and "
              f"generations cannot build on each other.\n"
              f"         Use --mutation-mode jitter to carry a winner forward, or raise "
              f"--mutate-after past the part you want kept.", file=sys.stderr)

    with tempfile.TemporaryDirectory(prefix="c-phoenix-mutate-") as tmp:
        tmpdir = Path(tmp)
        for gen in range(1, generations + 1):
            if generations > 1:
                print(f"-- generation {gen}/{generations} · seed score "
                      f"{best_score if best_score is not None else 'original'}")
            gen_best: tuple[int, list] | None = None
            for index in range(1, args.iterations + 1):
                candidate = generated_candidate(current_seed, args.frames, rng, args.mutate_after, args.mutation_mode)
                tag = f"g{gen:02d}_{index:04d}" if generations > 1 else f"{index:04d}"
                script_path = tmpdir / f"candidate_{tag}.txt"
                coverage_path = tmpdir / f"coverage_{tag}.json"
                write_script(script_path, candidate, seed_path)

                run_args = argparse.Namespace(
                    emulator=args.emulator,
                    frames=args.frames,
                    script=str(script_path),
                    ram_dump=None,
                    cwd=args.cwd,
                    sdl_video_driver=args.sdl_video_driver,
                    no_render=True,
                )
                result = run_emulator(run_args, coverage_path)
                if result.returncode != 0:
                    print(f"{tag}: emulator failed with exit {result.returncode}", file=sys.stderr)
                    if args.verbose:
                        print(result.stdout, end="")
                        print(result.stderr, end="", file=sys.stderr)
                    continue

                coverage = load_coverage(coverage_path)
                score = coverage_score(coverage, args.target)
                best.append((score, script_path, coverage))
                best.sort(key=lambda item: item[0], reverse=True)
                best = best[:args.keep]
                if gen_best is None or score > gen_best[0]:
                    gen_best = (score, candidate)

                summ = coverage.get("summary", {})
                target_status = ",".join(
                    f"{target}={'hit' if TARGETS[target](coverage) else 'miss'}"
                    for target in args.target
                )
                print(
                    f"{tag}: score={score} "
                    f"max_level=0x{int(summ.get('max_level_and_round', 0)):02X} "
                    f"max_game=0x{int(summ.get('max_gameplay_level_and_round', 0)):02X} "
                    f"deaths={summ.get('player_deaths', 0)} "
                    f"kills={coverage.get('hits', {}).get('alien_killed_with_score', {}).get('hits', 0)} "
                    f"mship_tiles={coverage.get('hits', {}).get('mothership_tile_hit', {}).get('hits', 0)} "
                    f"mship60={coverage.get('hits', {}).get('mothership_tile_60_hit', {}).get('hits', 0)} "
                    f"core={coverage.get('hits', {}).get('mothership_core_window_seen', {}).get('hits', 0)} "
                    f"gate70={coverage.get('hits', {}).get('mothership_core_gate_70_seen', {}).get('hits', 0)} "
                    f"mship_game={summ.get('mothership_gameplay_frames', 0)} "
                    f"{target_status}"
                )
            if gen_best is None:
                print("no candidate survived this generation; stopping", file=sys.stderr)
                break
            # Say out loud whether the seed moved. Only the negative case used
            # to get a line of its own, so a re-seed could be spotted only by
            # comparing two headers twenty lines apart.
            nxt = f"generation {gen + 1}" if gen < generations else "the saved winner"
            if best_score is None:
                best_score, current_seed = gen_best
                if generations > 1:
                    print(f"   best of this round: {best_score}  ->  seeds {nxt}")
            elif gen_best[0] > best_score:
                if generations > 1:
                    print(f"   re-seeded: {best_score} -> {gen_best[0]} "
                          f"(+{gen_best[0] - best_score})  ->  seeds {nxt}")
                best_score, current_seed = gen_best
            elif generations > 1:
                print(f"   no improvement ({gen_best[0]} <= {best_score}); keeping the current seed")
            trajectory.append(best_score)

        # The default --output-dir is the committed corpus in
        # context/input-scripts/generated. A run that happens to produce the
        # same rank and score as a script already in there would otherwise
        # overwrite a vetted fixture without saying so. Collisions are checked
        # up front, so a refusal leaves the directory exactly as it was.
        planned: list[tuple[Path, str]] = []
        for rank, (score, script_path, coverage) in enumerate(best, start=1):
            stem = f"mutated_rank_{rank:02d}_score_{score}"
            planned.append((output_dir / f"{stem}.txt",
                            script_path.read_text(encoding="utf-8")))
            planned.append((output_dir / f"{stem}.coverage.json",
                            json.dumps(coverage, indent=2, sort_keys=True)))

        if not getattr(args, "force", False):
            # an identical rewrite is harmless; only a differing one is a loss
            clashes = [p for p, body in planned
                       if p.exists() and p.read_text(encoding="utf-8") != body]
            if clashes:
                print("refusing to overwrite existing files:", file=sys.stderr)
                for p in clashes:
                    print(f"  {p}", file=sys.stderr)
                print("Write somewhere else with --output-dir, or pass --force to replace them.",
                      file=sys.stderr)
                return 3

        for path, body in planned:
            path.write_text(body, encoding="utf-8")

    if generations > 1 and trajectory:
        moves = sum(1 for x, y in zip(trajectory, trajectory[1:]) if y > x)
        print("seed score per generation: " + " -> ".join(str(s) for s in trajectory)
              + f"   ({moves} re-seed{'' if moves == 1 else 's'} after the first round)")
    print(f"Saved top {len(best)} scripts to {output_dir}")
    return 0


def list_targets(args: argparse.Namespace) -> int:
    """Print the available targets, with the condition each one checks.

    Bare names were not enough to choose between, say, mothership_active and
    mothership_active_gameplay, so the condition is shown alongside. --plain
    restores the old one-name-per-line output for anything that parses this.
    """
    if getattr(args, "plain", False):
        for target in sorted(TARGETS):
            print(target)
        return 0

    conditions = _target_conditions()
    width = max(len(t) for t in TARGETS)
    for target in sorted(TARGETS):
        print(f"{target:<{width}}  {conditions.get(target, '')}")
    print(f"\n{len(TARGETS)} targets. What each one is for, and when to pick it over a "
          f"neighbouring one:\n  tools/input-bot-reference.md")
    return 0


def _target_conditions() -> dict[str, str]:
    """Source text of each TARGETS lambda, read from this file.

    Kept in step with the table by construction: it reads the very definitions
    it describes, so a new target can never show up here without its condition.
    """
    import ast
    try:
        src = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(src)
    except (OSError, SyntaxError):
        return {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "TARGETS":
            out = {}
            for key, value in zip(node.value.keys, node.value.values):
                body = value.body if isinstance(value, ast.Lambda) else value
                out[key.value] = " ".join((ast.get_source_segment(src, body) or "").split())
            return out
    return {}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    evaluate_parser = sub.add_parser("evaluate", help="run a script and summarize coverage")
    evaluate_parser.add_argument("--script", required=True, help="input script to replay")
    evaluate_parser.add_argument("--frames", type=int, default=8000, help="frames to run")
    evaluate_parser.add_argument("--emulator", default="./build/c-phoenix", help="emulator binary")
    evaluate_parser.add_argument("--cwd", default=".", help="working directory for emulator")
    evaluate_parser.add_argument("--coverage-out", help="write/read coverage JSON at this path")
    evaluate_parser.add_argument("--ram-dump", help="optional RAM dump output path")
    evaluate_parser.add_argument("--sdl-video-driver", help="optional SDL_VIDEODRIVER override")
    evaluate_parser.add_argument("--no-render", action="store_true", help="skip rendering during headless runs")
    evaluate_parser.add_argument("--json", action="store_true", help="print raw coverage JSON")
    evaluate_parser.add_argument(
        "--target",
        action="append",
        choices=sorted(TARGETS),
        default=[],
        help="target to evaluate; can be repeated",
    )
    evaluate_parser.set_defaults(func=evaluate)

    targets_parser = sub.add_parser("list-targets",
                                    help="show the built-in targets and what each one checks")
    targets_parser.add_argument("--plain", action="store_true",
                                help="print bare target names only, one per line, for scripting")
    targets_parser.set_defaults(func=list_targets)

    mutate_parser = sub.add_parser("mutate", help="generate and score mutated input scripts")
    mutate_parser.add_argument("--seed", required=True, help="seed input script")
    mutate_parser.add_argument("--frames", type=int, default=8000, help="frames to run each candidate")
    mutate_parser.add_argument("--iterations", type=int, default=20, help="number of candidates per generation")
    mutate_parser.add_argument("--generations", type=int, default=1,
                               help="rounds of search; each round re-seeds with the previous round's "
                                    "best script, so the search climbs instead of resampling the same "
                                    "seed (default 1 = a single flat round)")
    mutate_parser.add_argument("--keep", type=int, default=5, help="number of top scripts to save")
    mutate_parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                               help="where to save the top scripts (default: a scratch "
                                    "directory; promoting a script into "
                                    "context/input-scripts/generated is a deliberate step, "
                                    "taken only after evaluate has confirmed it)")
    mutate_parser.add_argument("--force", action="store_true",
                               help="allow replacing existing files in --output-dir")
    mutate_parser.add_argument("--emulator", default="./build/c-phoenix", help="emulator binary")
    mutate_parser.add_argument("--cwd", default=".", help="working directory for emulator")
    mutate_parser.add_argument("--sdl-video-driver", default="dummy", help="SDL_VIDEODRIVER for emulator")
    mutate_parser.add_argument("--random-seed", type=int, default=1, help="deterministic RNG seed")
    mutate_parser.add_argument("--mutate-after", type=int, default=220, help="preserve seed events before this frame")
    mutate_parser.add_argument("--mutation-mode", choices=["regenerate", "jitter", "sweep"], default="regenerate", help="how to mutate events after --mutate-after")
    mutate_parser.add_argument("--verbose", action="store_true", help="print emulator output on failures")
    mutate_parser.add_argument(
        "--target",
        action="append",
        choices=sorted(TARGETS),
        default=[],
        help="target to reward; can be repeated",
    )
    mutate_parser.set_defaults(func=mutate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
