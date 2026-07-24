# Input Bot: Purpose and Use

`tools/input_bot.py` is a deterministic evaluator and mutator for replay
scripts. It replays a script headlessly with C-Phoenix, reads coverage output,
and can generate new candidate scripts. It is not a live-playing AI and does
not change gameplay code.

## Preparation

Work from the repository root and build the emulator first:

```bash
make
python3 tools/input_bot.py list-targets
```

An input script has lines in this form:

```text
<frame> <button> <press|release>
```

After the preserved seed, the bot mainly generates `left`, `right`, `fire`,
and `shield` events. A seed should therefore first reach the desired game
phase reliably.

## Evaluate an Existing Script

Use `evaluate` to see which states, levels, and targets a script reaches:

```bash
python3 tools/input_bot.py evaluate \
  --script context/input-scripts/basic_playthrough.txt \
  --frames 4000 \
  --target player_bullet_fired \
  --sdl-video-driver dummy \
  --no-render
```

`evaluate` writes temporary coverage JSON and reports the relevant summary.
Use `--coverage-out=/tmp/coverage.json` to retain the JSON.

## Mutation and Evaluation Cycle

The two commands have distinct responsibilities:

1. `evaluate` replays **one existing script** once and reports `HIT` or
   `MISS` for each target. Use it to assess a seed or prove a candidate.
2. `mutate` creates **N variants** from that seed (`--iterations N`). Each
   variant is immediately replayed headlessly and assessed against the same
   coverage data used by `evaluate`.
3. `mutate` scores every variant and writes only the best `--keep` variants.
   A filename such as `mutated_rank_01_score_3092917.txt` means it received
   the highest score in that search, not that every target was proved.
4. Select a saved candidate and run `evaluate` explicitly with **every
   required target**. It is a valid fixture only when every required target
   reports `HIT`.
5. Repeat the search with a different `--random-seed`, more iterations, a
   different mutation mode, or a later `--mutate-after` when verification
   still reports a `MISS`.

In short: `mutate` **searches and ranks**; `evaluate` **checks and proves**.
The seed is never overwritten. Generated candidates and their coverage files
are written to `--output-dir`.

### Complete example: search for a 2P bonus life

The seed already reaches the 2P route but does not yet prove a bonus life.
Keep its first 2500 frames and vary only the later input:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/p2_bonus_life.txt \
  --frames 12000 --iterations 80 --keep 5 \
  --target two_player_game_started \
  --target player_2_bank_initialized \
  --target two_player_turn_switch \
  --target bonus_life_awarded \
  --mutate-after 2500 --mutation-mode jitter --random-seed 1 \
  --output-dir /tmp/input-bot-p2-bonus
```

This runs 80 independent candidate replays and may save, for example:

```text
/tmp/input-bot-p2-bonus/mutated_rank_01_score_123456.txt
/tmp/input-bot-p2-bonus/mutated_rank_01_score_123456.coverage.json
```

Then check the **entire** target set, not only the new target:

```bash
python3 tools/input_bot.py evaluate \
  --script /tmp/input-bot-p2-bonus/mutated_rank_01_score_123456.txt \
  --frames 12000 \
  --target two_player_game_started \
  --target player_2_bank_initialized \
  --target two_player_turn_switch \
  --target bonus_life_awarded \
  --sdl-video-driver dummy --no-render
```

Replace `123456` with the score actually written. When output reports four
`HIT`s, the candidate can be promoted to `context/input-scripts/` after a
repeatable second `evaluate`. A `MISS` means it is not a fixture: adjust the
search parameters and restart at `mutate`.

## Search for New Candidates

Use `mutate` to create and rank candidate scripts:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/basic_playthrough.txt \
  --frames 8000 \
  --iterations 20 \
  --target level_transition \
  --random-seed 1
```

The best scripts and their coverage are written by default to
`context/input-scripts/generated/`. The same `--random-seed` produces the
same mutations while the emulator and seed remain unchanged.

## Multiple Targets

Repeat `--target` for a combined goal. Every reached target receives a ranking
bonus. This is useful when all conditions are needed for a useful trace:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/generated/mutated_rank_01_score_3092917.txt \
  --frames 26000 \
  --iterations 80 \
  --target mothership_active_gameplay \
  --target mothership_tile_60_hit \
  --target mothership_core_window \
  --target mothership_core_gate_70 \
  --target mothership_explosion \
  --mutate-after 10000 \
  --mutation-mode sweep \
  --random-seed 1
```

Choose only targets that can meaningfully occur together. A broad target set
increases the search space and can rank a script with many easy side goals
above one that reaches the important primary goal.

Targets are **score bonuses**, not hard filters. `mutate` can therefore keep a
high-scoring script that does not reach every requested target. Always check a
candidate again with `evaluate` before promoting it to a fixture.

## Target Catalogue

| Group | Targets | Meaning and use |
| --- | --- | --- |
| Start and two players | `coin_accepted`, `two_player_game_started`, `player_2_bank_initialized`, `two_player_turn_switch` | Validate coin/start, both RAM banks, and a real player handoff. Combine the final three for a 2P fixture. |
| Player and projectiles | `player_bullet_fired`, `shield_used`, `player_death`, `game_over`, `enemy_bullets_active` | Short smoke, collision, and ending routes. |
| Progress | `level_transition`, `gameplay_level_5`, `gameplay_level_7`, `gameplay_level_8`, `gameplay_level_9` | Find a route that reaches a specified round in real gameplay. |
| Aliens and birds | `alien_kill`, `bird_hit`, `bird_wave_entry`, `bird_wave_gameplay`, `grown_bird_bonus_explosion` | `bird_hit` is broad; use `grown_bird_bonus_explosion` for the grown-bird route. |
| Mothership | `mothership_active`, `mothership_active_gameplay`, `mothership_tile_hit`, `mothership_tile_4c_hit`, `mothership_tile_60_hit`, `mothership_core_window`, `mothership_core_gate_70`, `mothership_explosion` | Build a phased case: active in gameplay, tile hit, core window, `$70` gate, explosion. |
| Score | `bonus_life_awarded` | Confirms that score actually crosses the bonus-life threshold. Combine with 2P targets for the planned 2P bonus-life fixture. |

The current list is authoritative and can always be queried with:

```bash
python3 tools/input_bot.py list-targets
```

## Recommended Cases

| Case | Seed | Targets | Purpose |
| --- | --- | --- | --- |
| Short smoke | `basic_playthrough.txt` | `level_transition` | Fast input-route and round-reset check. |
| Broad 1P regression | `bird-investigation.txt` | relevant gameplay, bird, and mothership targets | Reference session; extensive, not compact. |
| 2P bank and turn | `p2_bonus_life.txt` | `two_player_game_started`, `player_2_bank_initialized`, `two_player_turn_switch`, `grown_bird_bonus_explosion` | Current 2P regression route. |
| 2P bonus life | `p2_bonus_life.txt` | previous set plus `bonus_life_awarded` | New sought fixture; the current seed has not yet proved it. |
| Compact mothership | a late-gameplay seed | `mothership_active_gameplay`, `mothership_tile_60_hit`, `mothership_core_window`, `mothership_core_gate_70`, `mothership_explosion` | Shorter mothership substitute for the broad session. |

## Complete Examples

Evaluate the existing 2P route:

```bash
python3 tools/input_bot.py evaluate \
  --script context/input-scripts/p2_bonus_life.txt \
  --frames 9000 \
  --target two_player_game_started \
  --target player_2_bank_initialized \
  --target two_player_turn_switch \
  --target grown_bird_bonus_explosion \
  --sdl-video-driver dummy --no-render
```

Search for the 2P bonus-life case while preserving the proven opening route:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/p2_bonus_life.txt \
  --frames 12000 --iterations 80 --keep 5 \
  --target two_player_game_started \
  --target player_2_bank_initialized \
  --target two_player_turn_switch \
  --target bonus_life_awarded \
  --mutate-after 2500 --mutation-mode jitter --random-seed 1 \
  --output-dir /tmp/input-bot-p2-bonus

python3 tools/input_bot.py evaluate \
  --script /tmp/input-bot-p2-bonus/mutated_rank_01_score_<score>.txt \
  --frames 12000 --target bonus_life_awarded \
  --sdl-video-driver dummy --no-render
```

For a mothership search, use `sweep` and first retain a seed that demonstrably
reaches mothership gameplay. Promote a candidate only after a clean replay
and, where applicable, a lockstep comparison.

## Mutation Modes

- `regenerate` (default): preserves the seed until `--mutate-after`, then
  generates a new pattern.
- `jitter`: mainly varies existing event timing; use when the seed already
  reaches the right phase.
- `sweep`: preserves the route, then repeatedly moves left/right while firing;
  useful for mothership or area targets.

Use `--mutate-after` to preserve a known-good opening route. The default is
frame `220`.

## View and Keep Results

Replay a candidate visibly without `--run-frames`:

```bash
make replayrun \
  REPLAY_SCRIPT=context/input-scripts/generated/mutated_rank_01_score_....txt
```

Promote a winner to `context/input-scripts/` only when it records a repeatable
scenario or regression. Add a header comment with its goal, seed, and relevant
targets.
