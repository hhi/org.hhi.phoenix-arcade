# Phoenix: Two Implementations, One Verifiable Game

This project brings together two complementary ways to play, understand, and
verify Phoenix (1980).

- **JPhoenix** is a Java emulator that executes the original Intel 8080 ROM.
- **C-Phoenix** is a hand-translated C implementation that follows the ROM's
  frame routines, RAM layout, input, video, and sound decisions.

The goal is not merely a similar game. It is a C implementation that is
readable, reproducible, and comparable with the original ROM execution.

## Why Two Projects?

JPhoenix is the executable reference: it runs the original program bytes on an
8080 emulator. C-Phoenix makes the same behaviour inspectable as C modules,
with links back to assembly addresses. Together they answer a stronger question
than “does it look right?”: *does the translated state evolve like the original
ROM during the same recorded play session?*

## Watch the Demo

The two short recordings below use the same `bird-investigation` input session
and cover the requested game interval around frames 850-2100.

### 1. C-Phoenix gameplay

[Watch the replay](bird-investigation-gameplay-0850-2100.mp4): the playable
C implementation renders the recorded session, from frame 850 through 2100.
It is the player-facing view of the evidence.

### 2. Visual tracer

[Watch the tracer](bird-investigation-visual-tracer-0850-2100.mp4): the same
session is shown as a physical game grid with object paths, current slot state,
visible-object selection, and frame metadata. The tracer has records through
frame 2099, the last available record before 2100.

### One record, three views

All three images are deterministic captures of record 945 from the same
`bird-investigation` input script. The replay presents the bird wave as a
player sees it. The tracer presents the same RAM record as physical positions,
paths, and slot state. `bird-wave slot` identifies a physical `$4B70`
wing-slot whose current visual role is a bird, even though the underlying slot
region is also used by other enemy phases.

C2-Phoenix's native mode shares the same C gamecore and the same recorded
state, replacing only the renderer: instead of the original 8x8 graphics-ROM
tiles it draws a dedicated 16x16 hi-res glyph per character, with PROM-derived
colour and a compositor that joins adjacent glyphs into smooth outlines. See
[`c2-phoenix/NATIVE-ART.md`](../c2-phoenix/NATIVE-ART.md) for how the atlas is
built and verified.

The default C2 look (`hires3a`) softens the hard step between adjacent
primary colours and adds a stable, position-hashed grain, both computed after
the hi-res atlas is drawn. Build with `make c2-run C2_VARIANT=classic` for
the original, unblended rendering, or another `C2_VARIANT` value
(`hires2`, `hires2a`, `hires3`) to compare an individual step of that
experiment in isolation; `c2-phoenix/native/c2_renderer.c` documents each one.
See [`c2-hires-variants-comparison.md`](c2-hires-variants-comparison.md) for
a side-by-side gallery of all five renderers on the same record (also
available as a styled, single-file
[HTML page](c2-hires-variants-comparison.html)).

| C-Phoenix framebuffer, record 945 | C2-Phoenix hi-res, record 945 | Visual tracer, record 945 |
| --- | --- | --- |
| <img src="bird-investigation-gameplay-frame-0945.png" alt="C-Phoenix bird wave at record 945" width="300"> | <img src="c2-phoenix-hires-frame-0945.png" alt="C2-Phoenix native hi-res rendering of the same bird wave at record 945" width="300"> | <img src="bird-investigation-visual-tracer-frame-0945.png" alt="Visual tracer at record 945 showing bird-wave slots and paths" width="600"> |

## What Can Be Explored?

Both projects offer attract mode, one- and two-player play, alien and bird
waves, mothership phases, scoring, shields, and sound. C-Phoenix is organised
by state machine, player, enemies, collisions, video, sound, and platform
integration, with assembly anchors and annotated reference material.

Interactive play can be saved as a small input script:

```text
203 start1 press
220 start1 release
841 fire press
850 fire release
```

The script can be played visibly, run headlessly, or supplied to both projects
for comparison. Lockstep records RAM `$4000-$4BFF` after each frame in both
projects and reports named differences, making divergence inspectable at the
level of player position, object slots, counters, levels, and screen state.

The visual tracer turns RAM dumps into standalone HTML: a physical Phoenix
grid, frame controls, slot structures, object trails, level transitions,
tooltips, and object-level JPhoenix/C-Phoenix differences.

## Try It on Your Mac

Run the default recorded demo and generate each project's standalone tracer:

```sh
make -C c-phoenix demorun
make -C c2-phoenix demorun
make -C jphoenix-emulator-port demorun
```

To replay a recording visibly, use the same script in each implementation:

```sh
make -C c-phoenix replayrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt
make -C c2-phoenix replayrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt
make -C jphoenix-emulator-port replayrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt
```

For reproducible non-visual execution, use the implementations that provide a
headless runner:

```sh
make -C c-phoenix headlessrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt REPLAY_FRAMES=13935
make -C c2-phoenix headlessrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt REPLAY_FRAMES=13935
```

From the repository root, generate and serve visual tracers through localhost:

```sh
make c-tracer-view    # C-Phoenix versus JPhoenix comparison tracer (port 8766)
make j-tracer-view    # JPhoenix standalone object tracer (port 8766)
make c2-tracer-view   # C2-Phoenix standalone object tracer (port 8767)
```

Each viewer prints its exact `http://127.0.0.1:…` URL and keeps the server
running until `Ctrl-C`. To serve an existing result without regeneration, add
`-only` to the target, for example `make c-tracer-view-only`.

## Inspect the C-annotated Assembly

C-Phoenix also provides an interactive route from the annotated Z80 source to
the translated C code:

```text
Phoenix.asm → Phoenix.md → Phoenix.html
```

From the repository root, generate and serve the viewer with:

```sh
make c-asm-view       # port 8765
```

The locally served page links ASM labels and symbols to C functions and source
files, distinguishes code and data labels, shows data representations in C,
and marks the ASM span covered by each C function. It includes filter controls,
hover details, back/forward label navigation, and an explicit Light/Dark theme
switch.

![Interactive Phoenix ASM cross-reference in dark theme](phoenix-interactive-asm-dark.jpg)

Use `make c-asm-view-only` to serve the already-generated page. Do not use
`file://`: the built-in C-source viewer needs localhost to load C files.

## The Input Bot: Naming a Moment and Letting the Machine Find It

Proving the C port behaves like the original means getting the game into
awkward places: a two-player handoff, a bonus life, the mothership's core
window, level nine. Playing your way there by hand and writing down every
button press would take an afternoon per scenario, and you would have to do it
again the moment anything changed.

So it was done the other way around. You **name the moment you want** and the
bot goes looking for it.

![How the input bot finds a test case: a seed input script is mutated into twenty variations, each replayed headless, scored against a named target, and the best kept as the seed of the next generation](input-bot-search.svg)

It takes one existing replay as a seed, mutates it into a batch of variations,
replays each one headless at full speed, and scores the result against the
target you named — `gameplay_level_9`, `mothership_core_gate_70`,
`two_player_turn_switch`, and [25 others](../c-phoenix/tools/input-bot-reference.md). The best scripts are kept. With
`--generations` the winner becomes the seed of the next round, so the search
climbs towards deep targets that no single random mutation would ever reach.

Every run is reproducible: the same `--random-seed` produces the same search.

**This is not a side tool — it is most of the evidence.** Of the 59 input
scripts in the repository, 9 were written by hand and **50 were found by the
bot**. Together they reach 79.9% of the C functions, and that coverage figure
is what the equivalence claim below rests on.

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/basic_playthrough.txt \
  --frames 8000 --iterations 20 --generations 5 \
  --target gameplay_level_9 --random-seed 1 \
  --output-dir /tmp/input-bot-level9
```

A separate `evaluate` step then proves which goals the chosen candidate really
reaches, so a script is only promoted to a fixture once it has been confirmed
twice. Full walkthrough, target catalogue and mutation modes:
[Input bot: purpose and use](../c-phoenix/tools/input-bot-howto.md).

## Evidence for Equivalence

The C port is not judged only by appearance. It is checked, frame by frame,
against the original ROM:

![How lockstep verification works: the same recorded input drives both the original 1980 ROM and the C port, and their game memory is compared byte by byte after every single frame](lockstep-explained.svg)

The current scripted lockstep suite plays 57 scenarios in both
implementations and compares game state record by record. The completed
suite reports byte-exact game-state equality with JPhoenix for those
scenarios; associated PC coverage connects 176 C routines to executed ROM
instruction addresses.

This is strong, reproducible evidence for the covered scenarios and RAM
regions. It is not a claim that every hypothetical, unexecuted input path is
automatically proven. New or changed gameplay remains subject to the same
replay, lockstep, and trace checks.

## Make Execution Visible

Design diagrams describe routes that source code and the ROM *can* contain.
Runtime callgraphs show which routes a recorded session actually executed.

- **JPhoenix** records executed `CALL` transitions in the original Intel 8080
  ROM. Address labels from the annotated assembly make the graph readable as
  routines rather than only hexadecimal addresses.
- **C-Phoenix** records executed C function calls during the equivalent replay.
- The **functional C-Phoenix graph** folds those functions into nine gameplay
  and engine responsibilities. It is the readable starting point; the
  function-level graph remains the drill-down.
- Both graphs use a frequency heatmap: cool colours indicate rarely visited
  routes and warm colours frequently executed routes. Each graph includes a
  legend with that session's concrete value ranges.
- A second graph compares design and execution. Solid green edges are present
  in the design and were observed; dashed grey edges were not observed during
  this recording. That identifies test gaps, not an automatic functional
  difference.

The two levels deliberately remain separate: ROM control flow in JPhoenix and
C control flow in C-Phoenix. ASM address anchors and documentation provide the
semantic connection; lockstep remains the independent check for equivalent
game state.

## Runtime Graph Gallery

The following images are the `bird-investigation` session used by this demo.
They are included locally so the showcase can be viewed without first running
the instrumentation pipeline.

### C-Phoenix: functional decomposition

[![Functional runtime decomposition of the bird-investigation recording: frame loop, game flow, player, birds, mothership, collisions, video, audio and utilities](runtimegraphs/bird-investigation/c_phoenix_functional_runtime_callgraph.png)](runtimegraphs/bird-investigation/c_phoenix_functional_runtime_callgraph.md)

The accompanying [function membership CSV](runtimegraphs/bird-investigation/c_phoenix_functional_runtime_functions.csv) maps each executed function back to
its responsibility, source file and measured in/outgoing call totals.

### C-Phoenix: interactive runtime explorer

[Open the interactive runtime explorer](../c-phoenix/context/runtimegraphs/bird-investigation/c_phoenix_runtime_explorer.html).
It brings the functional decomposition and detailed runtime calls together in
one split view. Expand the tree from domain to subsystem, source module, and
function; the graph aggregates to the selected level while retaining its
runtime context. The breadcrumb keeps the active scope visible. At function
level, **Open source** links to the defining C file and line.

![Runtime explorer overview: functional subsystem tree on the left and the aggregated runtime callgraph on the right](runtime-analysis-explorer-overview.png)

### C-Phoenix: executed C calls

![C-Phoenix runtime callgraph](runtimegraphs/bird-investigation/c_phoenix_runtime_callgraph.png)

### JPhoenix: executed 8080 ROM calls

![JPhoenix runtime callgraph](runtimegraphs/bird-investigation/jphoenix_semantic_runtime_callgraph.png)

### C-Phoenix: design routes compared with this execution

![C-Phoenix design/runtime comparison](runtimegraphs/bird-investigation/c_phoenix_design_runtime_comparison.png)

The solid and dashed edges, frequency colours, and their legends are part of
each image. They distinguish observed control flow from design-time-only
routes for this concrete replay.

## Demonstration Path

For visible playback in each implementation:

```sh
make -C c-phoenix replayrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt
make -C c2-phoenix replayrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt
make -C jphoenix-emulator-port replayrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt
```

For a full comparison and visual tracer, after building the sibling JPhoenix
project with JDK 11+:

```sh
make tracerun \
  COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt \
  COMPARE_FRAMES=13935 \
  COMPARE_NAME=bird-investigation \
  COMPARE_STOP_AFTER=999999
```

The tracer is written to `/tmp/bird-investigation-diff.html`.

For a compact view of what this session executes in the C implementation:

```sh
make runtimegraph RUNTIME_SCENARIO=bird-investigation RUNTIME_FRAMES=13935
```

This writes SVG and PNG summaries plus `c_phoenix_runtime_explorer.html` to
`context/runtimegraphs/bird-investigation/`. The equivalent JPhoenix command
lives in the sibling project; both use the same scenario name and replay.

## Engineering Approach

- The original ROM remains a living reference.
- The C port is hand translated, not behaviourally approximated.
- Deterministic input scripts turn gameplay reports into reproducible evidence.
- RAM dumps, semantic deltas, and annotated assembly connect observation to
  implementation detail.
- Runtime callgraphs distinguish reachable routes from routes actually run by
  a concrete session.
- The input bot turns an observed gameplay moment into a repeatable test case.
- Visual tools make low-level state understandable without debugger or emulator
  expertise.

## Further Reading

- [Replay and visual-tracer pipeline](../c-phoenix/context/traces/replay-tracer-pipeline-howto.md)
- [Visual object tracer](../c-phoenix/context/traces/visual-tracer-howto.md)
- [Semantic lockstep analysis](../c-phoenix/context/traces/semantic-lockstep-howto.md)
- [Input bot: purpose and use](../c-phoenix/tools/input-bot-howto.md)
- [Animations and trajectories](../c-phoenix/animations/en/README.md) — the flight paths every enemy follows, and
  [the sprite sequences](../c-phoenix/animations/en/animation-sequences.md) showing which 8x8 characters each
  object is built from and which C routine draws it

Phoenix is both playable software and a transparent record of how an arcade ROM
can be understood, translated, tested, and explored.
