# Replay and Visual Tracer Pipeline

This guide explains the route from a played session to a visual object tracer.
Run `make help` from the c-phoenix repository root to see defaults and short
examples.

## Prerequisites

`recordrun`, `replayrun`, and `headlessrun` require c-phoenix, `gcc`, and
SDL2. `comparerun`, `tracerun`, and `recordtracerun` also require JDK 11+ and
the built jphoenix sibling project:

```text
PHOENIX_THE_GAME/
  c-phoenix/
  jphoenix-emulator-port/
```

Build jphoenix once:

```sh
cd ../jphoenix-emulator-port && make
cd ../c-phoenix
```

`dump_pair.sh` starts `PhoenixCoverageRunner` from `build/classes`; it does
not build jphoenix itself.

## Quick Routes

| Goal | Command | Result |
| --- | --- | --- |
| Record a session | `make recordrun RECORD_NAME=my-session` | `/tmp/my-session.txt` |
| Watch it again | `make replayrun REPLAY_SCRIPT=/tmp/my-session.txt` | visible game window |
| Record, compare, and trace | `make recordtracerun RECORD_NAME=my-session` | input script, two dumps, comparison, HTML |
| Analyse an existing script | `make tracerun COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt COMPARE_FRAMES=13935 COMPARE_NAME=bird-investigation COMPARE_STOP_AFTER=999999` | two dumps, comparison, HTML |

Close the window after `recordrun` or `replayrun`. Headless commands end after
their configured frame count.

```text
recordrun -> input script (.txt) -> replayrun (visible playback)
                                  -> headlessrun -> C-Phoenix RAM dump (.bin)
input script -> comparerun -> jphoenix + C-Phoenix dumps -> terminal report
                                               -> tracerun -> HTML viewer
recordtracerun = recordrun + tracerun
```

## Targets

### `make recordrun`

Play normally while every button transition is saved.

```sh
make recordrun RECORD_NAME=my-session
```

The resulting `/tmp/my-session.txt` is the reproducible source artefact. Move
it to `context/input-scripts/` only when it is a useful regression case.

### `make replayrun`

Play an input script in the normal visible game window.

```sh
make replayrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt
```

It creates no file; close the window when finished.

### `make headlessrun`

Run without a window, optionally producing one C-Phoenix RAM dump.

```sh
make headlessrun \
  REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt \
  REPLAY_FRAMES=13935 \
  REPLAY_RAM_DUMP=/tmp/bird-investigation.bin
```

### `make comparerun`

Run the same input in jphoenix and c-phoenix, then compare selected RAM
regions.

```sh
make comparerun \
  COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt \
  COMPARE_FRAMES=13935 \
  COMPARE_NAME=bird-investigation \
  COMPARE_STOP_AFTER=999999
```

It writes `/tmp/ref-bird-investigation.bin` and
`/tmp/port-bird-investigation.bin` and reports the comparison in the terminal.

### `make tracerun`

`tracerun` runs `comparerun` first, then writes a standalone viewer:

```sh
make tracerun \
  COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt \
  COMPARE_FRAMES=13935 \
  COMPARE_NAME=bird-investigation \
  COMPARE_STOP_AFTER=999999
```

Then serve the generated viewer through the standard local server:

```sh
make tracer-view-only TRACE_VIEW_OUTPUT=/tmp/bird-investigation-diff.html
```

Open the URL printed by Make (default port `8766`) and stop the server with
`Ctrl-C`.

### `make recordtracerun`

Record interactively, close the window, then automatically run the complete
jphoenix/c-phoenix comparison and HTML-tracer chain.

```sh
make recordtracerun RECORD_NAME=my-session
```

It replays until 400 frames after the last recorded input by default. Use
`RECORD_TRACE_FRAMES` to override that boundary.

## Output Files

An input script is readable text, one transition per line:

```text
203 start1 press
220 start1 release
841 fire press
850 fire release
```

A RAM dump is binary. Every record is a four-byte big-endian frame number plus
3072 bytes for RAM `$4000-$4BFF`. It contains state, object slots, positions,
and screen RAM, not video, audio, or input events.

A successful comparison ends with `No differences found.` A difference names
the paired record, RAM address, known symbol, and both byte values. It is an
investigation signal, not automatically proof of a gameplay bug.

The generated HTML embeds decoded object records and provides the Phoenix grid,
frame controls, slot data, trails, tooltips, level navigation, and object-level
diffs. It may be tens or hundreds of MB: retain the input script and regenerate
dumps and HTML instead of committing those large generated files.
