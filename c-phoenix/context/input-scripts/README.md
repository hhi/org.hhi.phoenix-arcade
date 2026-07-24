# Input scripts

This directory holds deterministic button-press timelines used to drive
`c-phoenix` through real gameplay without a human at the controls.

Dutch documentation: [README.nl.md](README.nl.md).

## Why

Manually playing the game proves a fix works once, for whatever happened during
that session. Input scripts turn "coin in, start, move around, shoot, die" into
a fixed, replayable sequence. That enables:

- **Regression checks**: run the same script before and after a change, dump RAM
  every frame, and compare the traces.
- **Lockstep verification against jphoenix**: run comparable input through both
  emulators and compare dumps with `tools/compare_ram_dumps.py`.

Both techniques depend on reproducible input.

## Format

One event per line: `<frame> <button> <press|release>`.

- `frame` - the `frame_counter` value at which the event fires.
- `button` - one of `coin`, `start1`, `start2`, `fire`, `left`, `right`,
  `shield`.
- `press` / `release` - button down or up. There is no auto-release.
- Blank lines and lines starting with `#` are ignored.

## Running One

```bash
make
./c-phoenix --run-frames=4000 \
    --input-script=context/input-scripts/extended_playthrough.txt \
    --ram-dump=/tmp/trace.bin
```

`--run-frames=N` runs headless for exactly N frames and exits. `--ram-dump=`
writes one `4-byte frame number + 3072-byte $4000-$4BFF snapshot` record per
frame, in the same format jphoenix produces.

The same path is available through make:

```bash
make headlessrun \
    REPLAY_SCRIPT=context/input-scripts/my_session.txt \
    REPLAY_FRAMES=15000 \
    REPLAY_RAM_DUMP=/tmp/trace.bin
```

Use `make replayrun REPLAY_SCRIPT=context/input-scripts/my_session.txt` to
watch a script play out live.

## Evaluating Coverage

```bash
python3 tools/input_bot.py evaluate \
    --script context/input-scripts/basic_playthrough.txt \
    --frames 4000 \
    --target player_bullet_fired \
    --target enemy_bullets_active \
    --sdl-video-driver dummy \
    --no-render
```

The evaluator does not change gameplay. It runs the emulator with
`--coverage-dump=`, reads the resulting JSON, and reports reached game states,
levels, routine hits, and target hits/misses.

## How to Instruct the Input Bot for a Specific Goal

Use the bot when you need a deterministic replay that reaches a specific
gameplay condition but hand-writing the input timing would be guesswork.

### 1. Pick a built-in target

```bash
python3 tools/input_bot.py list-targets
```

Target families include early smoke checks, progress targets, bird targets,
player-state targets, and mothership targets such as
`mothership_active_gameplay`, `mothership_core_gate_70`, and
`mothership_explosion`.

If no built-in target represents the goal, add C instrumentation first via
`coverage_hit("stable_target_name")`, then add a matching target predicate in
`tools/input_bot.py`.

### 2. Evaluate the seed before mutating

```bash
python3 tools/input_bot.py evaluate \
  --script context/input-scripts/basic_playthrough.txt \
  --frames 4000 \
  --target player_bullet_fired \
  --target level_transition \
  --sdl-video-driver dummy \
  --no-render
```

If the seed misses the broad phase entirely, choose an earlier/easier seed or a
broader target.

### 3. Choose a mutation mode

Use `regenerate` for early exploration:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/basic_playthrough.txt \
  --frames 8000 \
  --iterations 40 \
  --target gameplay_level_5 \
  --mutation-mode regenerate
```

Use `jitter` when a seed already reaches the rough phase and timing variation is
enough:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/generated/mutated_rank_01_score_1327922.txt \
  --frames 20000 \
  --iterations 80 \
  --target gameplay_level_8 \
  --target mothership_active_gameplay \
  --mutate-after 5760 \
  --mutation-mode jitter
```

Use `sweep` when a known route reaches a shooting window and shots need to scan
left/right across a target area:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/generated/mutated_rank_01_score_3092917.txt \
  --frames 26000 \
  --iterations 80 \
  --target mothership_core_gate_70 \
  --target mothership_explosion \
  --mutate-after 10000 \
  --mutation-mode sweep
```

### 4. Tune the run

Useful knobs:

- `--frames`: long enough to include the target and aftermath.
- `--iterations`: higher values improve chances but cost time.
- `--keep`: how many top candidates to save.
- `--random-seed`: deterministic bot randomness.
- `--mutate-after`: preserve a known-good route before this frame.
- `--output-dir`: use `/tmp/...` for exploratory batches.

### 5. Promote a useful candidate

Evaluate the winner explicitly. If it is useful, copy it into
`context/input-scripts/` with a descriptive name and a header comment explaining
what it exercises, where it came from, key frames, and why it is worth keeping.

## Gotcha: use long holds, not short pulses

Several internal routines call `wait_vblank_coin()` more than once per outer
frame, so a one-frame `press`/`release` pulse can land between input samples and
do nothing. Hold buttons for tens of frames.

## Existing Scripts

- `basic_playthrough.txt` - short smoke test for basic gameplay.
- `extended_playthrough.txt` - longer regression-check script.
- `passive_playthrough.txt` - stationary player route for death/game-over.
- `two_player_playthrough.txt` - two-player turn-switch coverage.
- `two_player_last_grown_bird.txt` - 2-player route where player 1 faces one
  remaining grown bird.

## Recording One Instead of Writing It

```bash
make recordrun
```

By default this records to a timestamped `/tmp/c-phoenix-session-*.txt` file.
Override the path when you want a stable name:

```bash
make recordrun RECORD_SCRIPT=/tmp/c-phoenix-session.txt
```

Play normally; the file is flushed after every event. Then replay it headless:

```bash
make headlessrun \
    REPLAY_SCRIPT=/tmp/c-phoenix-session.txt \
    REPLAY_FRAMES=15000 \
    REPLAY_RAM_DUMP=/tmp/trace.bin
```

## How to Report a Bug Spotted During Manual Play

Start with input recording enabled:

```bash
make recordrun RECORD_SCRIPT=/tmp/bug_seen_YYYYMMDD_short_name.txt
```

When the bug appears:

1. Click once inside the game window to pause.
2. Press `F12` if a screenshot would help.
3. Write down player, level/round, what looked wrong, what happened just before
   it, and whether sound/music was involved.
4. Quit normally after the recording has captured the moment.

Give the AI/debugging session the replay path and the symptom. For a first
local comparison, run:

```bash
make comparerun \
    COMPARE_SCRIPT=/tmp/bug_seen_YYYYMMDD_short_name.txt \
    COMPARE_FRAMES=15000 \
    COMPARE_NAME=bug_seen
```

That runs C-Phoenix and jphoenix headlessly, compares RAM dumps, and leaves
`/tmp/ref_bug_seen.bin` plus `/tmp/port_bug_seen.bin` behind for deeper traces
when useful.

Keep generated dumps in `/tmp` while investigating. Move material into
`context/traces/` only when it has a clear, written conclusion.
