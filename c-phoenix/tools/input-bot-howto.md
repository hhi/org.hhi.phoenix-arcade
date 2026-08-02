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

The best scripts and their coverage go to `/tmp/input-bot/` unless you say
otherwise, and every run prints where it wrote them.

They deliberately do **not** land in `context/input-scripts/generated/`. That
directory is the committed corpus — the 50 scripts the coverage evidence rests
on — and a raw search result is not a fixture yet: it has only been *scored*,
not confirmed. Promote a script by running `evaluate` on it first and then
copying it in, or by passing `--output-dir` explicitly.

Wherever it writes, a run refuses to replace an existing file whose contents
differ, and names the files, rather than quietly overwriting one. `--force`
overrides that. The same `--random-seed` produces the
same mutations while the emulator and seed remain unchanged.

## Generations: Letting the Search Climb

The command above is a **single flat round**. All twenty candidates are mutations
of the same seed, they are scored, the best are kept — and the winner is never
reused. For a shallow target such as `level_transition` that is enough. For a
deep one such as `gameplay_level_9` or `mothership_core_gate_70` it is not: the
run has to survive several minutes of play, and no single random mutation of a
short seed gets there.

`--generations` closes that gap. The best script of round *N* becomes the seed of
round *N+1*, so each round starts from the best position found so far instead of
resampling the same neighbourhood:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/basic_playthrough.txt \
  --frames 8000 \
  --iterations 20 \
  --generations 5 \
  --target gameplay_level_9 \
  --random-seed 1 \
  --output-dir /tmp/input-bot-level9
```

This runs 5 x 20 = 100 replays, and prints a header per round:

```
-- generation 1/5 · seed score original
g01_0001: score=148300 max_game=0x05 ...
...
   best of this round: 148300  ->  seeds generation 2
-- generation 2/5 · seed score 148300
...
   re-seeded: 148300 -> 152900 (+4600)  ->  seeds generation 3
-- generation 3/5 · seed score 152900
...
   no improvement (151740 <= 152900); keeping the current seed
...
seed score per generation: 148300 -> 152900 -> 152900 -> 161100 -> 161100   (2 re-seeds after the first round)
```

Every round ends with one line saying whether the seed moved, and the run ends
with the whole trajectory, so you never have to compare two headers pages apart
to see whether the search is climbing or stuck.

**One caveat, and it decides whether this works at all.** `--generations` only
compounds if the mutator keeps what made the previous winner good, and two of
the three modes do not. `regenerate` (the default) and `sweep` discard every
seed event at or after `--mutate-after` and build a fresh pattern there, so a
re-seeded winner contributes only its opening. Measured on a seed with five
marker events past frame 220: **jitter carries four of them forward, regenerate
and sweep carry none.**

So for generations to mean anything, either

```bash
  --mutation-mode jitter          # keeps the whole winner, nudges its timing
```

or raise `--mutate-after` past the part you want carried forward. A run that
asks for generations with a discarding mode prints a warning saying exactly
this. The behaviour of each mode is pinned by
[`tests/test_input_bot_generations.py`](../tests/test_input_bot_generations.py).

The seed only moves on a **strict improvement**. A round that finds nothing
better prints `no improvement (…); keeping the current seed` and the next round
retries from the same place, so an unlucky round cannot push the search
backwards. `--keep` still ranks across all generations, not per round.

`--generations 1` is the default and behaves exactly as it always did.

The search control flow is covered by
[`tests/test_input_bot_generations.py`](../tests/test_input_bot_generations.py),
which drives `mutate` with a stub emulator — so it runs without SDL2 or a built
binary.

## A Worked Run, and the Trap in It

A real search, six generations of eight candidates against `level_transition`:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/extended_playthrough.txt \
  --frames 6000 --iterations 8 --generations 6 \
  --mutation-mode jitter \
  --target level_transition --random-seed 1
```

```
-- generation 1/6 · seed score original
g01_0007: score=1256823 max_level=0x0B max_game=0x01 deaths=5 kills=11 mship_tiles=10 ... level_transition=hit
   best of this round: 1256823  ->  seeds generation 2
-- generation 2/6 · seed score 1256823
   re-seeded: 1256823 -> 1256919 (+96)  ->  seeds generation 3
-- generation 3/6 · seed score 1256919
   re-seeded: 1256919 -> 1265641 (+8722)  ->  seeds generation 4
-- generation 4/6 · seed score 1265641
   no improvement (1264995 <= 1265641); keeping the current seed
...
seed score per generation: 1256823 -> 1256919 -> 1265641 -> 1265641 -> 1265641 -> 1265641   (2 re-seeds after the first round)
```

The search behaves exactly as intended: two improvements, then a plateau it
refuses to fall off. But the numbers say something else as well, and it is worth
knowing before you trust a run like this.

**Look at `max_level=0x0B` next to `max_game=0x01`.** The first counts any level
*seen*, the attract-mode demo included; the second counts only levels reached in
real play. Round 11 was reached by the demo playing itself. The player never got
past round 1.

That matters because of how the score is built. `level_transition` does not end
in `_gameplay`, so `wants_gameplay_progress()` is false and the score uses
`max_level * 100000` — attract progress and all — while the attract-frame
penalty is divided by four instead of applied in full. The arithmetic:

| | |
| --- | --- |
| `max_level` 0x0B x 100000 | 1,100,000 |
| `max_gameplay_level` 0x01 x 25000 | 25,000 |
| `level_transition` reached | 50,000 |
| 5 deaths x -500 | -2,500 |
| **fixed floor** | **1,172,500** |

**87% of that score is the attract demo.** The part the search can actually move
went from 84,323 to 93,141 — a real 10.5% gain, but on a tenth of the number you
see in the log. And what it was mostly optimising was `mship_tiles`, which at
`mship_game=0` were also all scored during the demo.

**The fix is to name a gameplay target.** Any target ending in `_gameplay` flips
the scoring: `max_gameplay_level * 150000`, no attract bonus, and the full
attract-frame penalty.

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/extended_playthrough.txt \
  --frames 6000 --iterations 8 --generations 6 \
  --mutation-mode jitter \
  --target bird_wave_gameplay --random-seed 1
```

Two habits follow from this. Compare `max_level` against `max_game` in the log
before believing a score, and prefer a `_gameplay` target whenever you want the
player, not the demo, to be doing the work.

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
  --random-seed 1 \
  --output-dir /tmp/input-bot-mothership
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

The table above groups the targets; **every target is discussed individually**,
with the exact condition it checks and when to pick it over a neighbouring one,
in [input-bot-reference.md](input-bot-reference.md). That page also lists every
command-line option with its default. Both are generated from `input_bot.py`, so
they cannot fall behind the code.

The live list is always available from the tool itself:

```bash
python3 tools/input_bot.py list-targets          # names plus the condition each checks
python3 tools/input_bot.py list-targets --plain  # bare names, for scripting
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
