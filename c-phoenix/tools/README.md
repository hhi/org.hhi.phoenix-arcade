# Phoenix C-Port Tools

This directory contains utility scripts to help verify, map, compare, and
document the Z80-to-C translation of the Phoenix arcade game.

Dutch documentation: [README.nl.md](README.nl.md).

## Documentation Generation

The following scripts analyze the C source code and the original Z80 assembly to
generate cross-referenced Markdown documentation. They read the
`[ASM: XXXX-YYYY]` tags found in the C comments to link C functions back to
their original ROM addresses.

All generated documentation is placed in the `context/` directory.

## Graph and Result Index

The static `generate_*callgraph.py` tools write **design-time** source graphs
to [context/graphs/README.md](../context/graphs/README.md). In contrast,
`generate_c_runtime_callgraph.py` consumes a trace recorded by
`make runtimegraph` and writes **runtime** call evidence to
`context/runtimegraphs/<scenario>/`; `generate_c_design_runtime_comparison.py`
compares those observed edges with the design graph. The corresponding graph
and result locations are part of each command's output, so generated artifacts
remain discoverable rather than being implicit scratch files.

### Other build and maintenance tools

| Tool | Purpose | Result/location |
| --- | --- | --- |
| `generate_classic_render_assets.py` | Decodes validated graphics and colour PROMs for the classic SDL renderer. | Tracked `phoenix_render_assets.h`; build-time asset, not gameplay ROM access. |
| `generate_knowledge_graph_visual.py` | Renders the knowledge-graph architecture overview from the current graph metadata. | Tracked `c-annotated/kennisgraaf_meta_architectuur.svg`; run `make knowledge-graph-visual`. |
| `migrate_artifacts.py` | Normalizes links and locations in curated trace artifacts. | Updated files under `context/traces/`. |
| `melody_dump.c` | Small C diagnostic for sound-table inspection. | Console diagnostic output; not part of normal builds. |

The C2 and JPhoenix tool directories have their own indexes:
[../../c2-phoenix/tools/README.md](../../c2-phoenix/tools/README.md) and
[../../jphoenix-emulator-port/tools/README.md](../../jphoenix-emulator-port/tools/README.md).

### `generate_mappings.py`
**Usage:** `python3 tools/generate_mappings.py`

This script parses all `.c` and `.h` files to extract the `[ASM: ...]`
annotations and generates two markdown files in `context/mapping/`:

1. **`c_functions_by_address.md`**: A chronological list of all ported
   functions sorted by their starting ROM address. It automatically identifies
   gaps in the `0x0000-0x3FFF` address space.
2. **`c_functions_per_file.md`**: An alphabetical list of functions grouped by
   their C source file.

Both generated files include clickable relative links to navigate directly to
the specific line in the C source code.

### `generate_annotated_asm.py`
**Usage:** `python3 tools/generate_annotated_asm.py`

This script transforms both `context/Phoenix.asm` and
`context/code-annotated.asm` into their corresponding Markdown files, with
generated cross-reference notes at C function entry points, data/gap
annotations, and Markdown headers for assembly labels.

### `generate_interactive_asm_html.py`
**Usage:** `python3 tools/generate_interactive_asm_html.py`

This script turns `context/Phoenix.md` into `context/Phoenix.html`. The result
has filterable, colour-coded code/data label navigation with checkbox type
filters, address-prefixed
`.EQU` hover descriptions, clickable in-assembly label references, an in-page
C source viewer that opens cross-references at the linked line, visible ASM
start/end boundaries for mapped C function scopes, and
back/forward controls.

## Verification and Replay

### `input_bot.py`
For purpose, mutation modes, multiple targets, and a complete workflow, see
[input-bot-howto.md](input-bot-howto.md).

**Usage:** `python3 tools/input_bot.py evaluate --script context/input-scripts/basic_playthrough.txt --frames 4000 --target player_bullet_fired`

Runs `c-phoenix` headlessly with an input script and `--coverage-dump=`, then
prints a compact summary of reached game states, levels, high-level coverage
hits, and optional built-in targets.

On machines without an SDL display, add `--sdl-video-driver dummy`. `evaluate`
is intentionally headless because it passes `--run-frames=` to the emulator.
To watch a generated script, run `./build/c-phoenix --input-script=...` directly
without `--run-frames=`.

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/basic_playthrough.txt \
  --frames 8000 \
  --target level_transition
```

For late-stage search, preserve a known-good route and mutate only after a
specific frame:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/generated/mutated_rank_01_score_1362603.txt \
  --frames 14000 \
  --target mothership_tile_hit \
  --target mothership_explosion \
  --mutate-after 5200
```

For mothership/core targeting, `sweep` mode keeps the route before
`--mutate-after` and then repeatedly sweeps left/right while firing:

```bash
python3 tools/input_bot.py evaluate \
  --script context/input-scripts/generated/mutated_rank_01_score_5003729.txt \
  --frames 26000 \
  --target mothership_active_gameplay \
  --target mothership_tile_60_hit \
  --target mothership_core_window \
  --target mothership_core_gate_70 \
  --target mothership_explosion \
  --sdl-video-driver dummy \
  --no-render
```

For a goal-oriented workflow, see
`context/input-scripts/README.md` under "How to instruct the input bot for a
specific goal".

### `compare_ram_dumps.py`
**Usage:** `python3 tools/compare_ram_dumps.py [options]`

Performs a byte-exact lockstep comparison between the RAM state of the original
Z80 execution and the C port. See `lockstep/PROCEDURE.md` for the repeatable
workflow.

### `lockstep/`

Contains batch tooling for running every curated input script through both
jphoenix and c-phoenix, aggregating the clean runs, and producing manual dump
pairs for divergence research. See [lockstep/README.md](lockstep/README.md).

### `trace_sprites.py`
**Usage:** `python3 tools/trace_sprites.py <ram-dump> --kind all [options]`

Extracts changed-only object timelines from the shared c-phoenix/jphoenix
RAM-dump format. It supports `player_ship`, `player_bullet`,
`above_player_bullet`, `enemy_bullet`, `aliens`, `birds`, `bird_explosion`,
`player_explosion`, `mothership`, and `shield_segments`; use `--kind all` for
the full registry or repeat `--kind` for a subset.

```bash
SDL_VIDEODRIVER=dummy ./build/c-phoenix --run-frames=4000 \
    --input-script=context/input-scripts/my_session.txt \
    --ram-dump=/tmp/phoenix-ram.bin --no-render
python3 tools/trace_sprites.py /tmp/phoenix-ram.bin --kind all \
    --only-active --output=/tmp/objects.csv
```

### `view_sprite_trace.py`
**Usage:** `python3 tools/view_sprite_trace.py <ram-dump> --output=<file.html>`

Creates a standalone interactive HTML object viewer for families with explicit
RAM X/Y coordinates or screen-address anchors. The default `auto` mode follows
the shared `$4B70-$4BAF` overlay per frame, switching between 16 alien records
and 8 bird records as the level changes.

```bash
python3 tools/view_sprite_trace.py /tmp/phoenix-ram.bin \
    --player 1 --output=/tmp/phoenix-paths.html
```

For porting work, pass a second dump with `--compare` to generate a C vs
jphoenix diff viewer:

```bash
python3 tools/view_sprite_trace.py /tmp/jphoenix-ram.bin \
    --compare /tmp/c-phoenix-ram.bin \
    --reference-label jphoenix --port-label c-phoenix \
    --kind birds --player 1 --output=/tmp/bird-diff.html
```

Serve the generated viewer through the standard local server rather than
opening it via `file://`:

```bash
make tracer-view-only TRACE_VIEW_OUTPUT=/tmp/phoenix-paths.html
```

This command is run from `c-phoenix/` and prints the localhost URL. Mothership,
shield, and explosion families remain available in `trace_sprites.py` as event
timelines, but do not have a visual view because their RAM structures do not
provide a coherent object coordinate.
