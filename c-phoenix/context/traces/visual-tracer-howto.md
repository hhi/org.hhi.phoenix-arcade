# How-to: Visual Object Tracer

The visual tracer converts Phoenix RAM dumps into an interactive HTML view of
object positions. It is for movement, object-state, and per-object
jphoenix/C-Phoenix investigation; it is not a pixel screenshot and does not
replace RAM comparison.

Each dump record contains a four-byte frame number and RAM `$4000-$4BFF`.
The viewer uses an object's position fields or its saved screen-RAM address.
It follows the 208x256 physical Phoenix display rather than the rotated memory
layout. For birds, `$4B71/$4B72` is the draw anchor `A`; raw grid data is `G`.
The physical position `V` applies background scroll:
`V.y = (A.y - CounterB9) mod 256`.

Generate a full comparison tracer with:

```sh
make tracerun \
  COMPARE_SCRIPT=context/input-scripts/two_player_last_grown_bird.txt \
  COMPARE_FRAMES=9000 COMPARE_NAME=last-grown-bird \
  COMPARE_STOP_AFTER=999999
```

Generate and serve the same tracer over HTTP with:

```sh
make tracer-view \
  COMPARE_SCRIPT=context/input-scripts/two_player_last_grown_bird.txt \
  COMPARE_FRAMES=9000 COMPARE_NAME=last-grown-bird \
  COMPARE_STOP_AFTER=999999
```

The command prints the `http://127.0.0.1:8766/` URL and stays active until
`Ctrl-C`. To serve an existing `/tmp` tracer without regenerating it, use
`make tracer-view-only` (override the file with
`TRACE_VIEW_OUTPUT=/tmp/other-diff.html`).

For one C-Phoenix dump, first use `make headlessrun` with `REPLAY_RAM_DUMP`,
then generate and serve HTML:

```sh
python3 tools/view_sprite_trace.py /tmp/c-last-grown-bird.bin \
  --player 1 --output=/tmp/phoenix-trace.html
make tracer-view-only TRACE_VIEW_OUTPUT=/tmp/phoenix-trace.html
```

For a direct two-dump comparison:

```sh
python3 tools/view_sprite_trace.py /tmp/j-last-grown-bird.bin \
  --compare /tmp/c-last-grown-bird.bin \
  --reference-label jphoenix --port-label c-phoenix \
  --kind birds --include-kind player_ship --player 1 \
  --output=/tmp/bird-diff.html
```

## Controls

- **Player** selects a player RAM bank.
- **Visible objects** has all-object and per-slot visibility controls. Clicking
  a row selects it without changing visibility.
- Every slot has a fixed colour shared by its row, marker, and trail. Hovering
  a visible marker always shows its ID and available `V`, `A`, and `G` values.
- **Show selected object label** keeps text beside an explicitly selected marker
  and is off by default. **Show coordinates on grid** adds coordinate text.
- **Show raw grid trace** adds a dashed raw-bird path; **Show inactive traces**
  restores paths for inactive slots. An active-to-off bird or alien gets one
  red pulse at its final position.
- Frame controls navigate dumped records. Selecting a slot stops playback.
  Level controls move between contiguous `round + level` segments; trails reset
  at a new segment unless previous-level traces are enabled.
- Slot structures below the grid show current RAM fields. Bird records include
  shape, draw address, shape-table offset, timer, grid X/Y, and phase.

`LevelAndRound` (`$43B8`) stores level in its low nibble and round in its high
nibble. In game state `$03`, levels `1/3` are alien waves and `5/7` are bird
waves. `GameState` is `$43A4`; no birds are expected at level 1, round 0,
state `$03`.

Red markers and diff navigation apply only to records present in both dumps.
Unmatched tail records are reported separately. The viewer draws points and
paths, not sprites or tile layers; use RAM parity and semantic lockstep for
broader conclusions.
