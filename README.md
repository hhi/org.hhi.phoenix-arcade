# Phoenix Arcade

Phoenix Arcade is a home for a few different ways to experience and study the
1980 arcade game *Phoenix*. Before building or running a project, prepare a
legally obtained Phoenix Amstar ROM set as described in
[`roms/README.md`](roms/README.md).

## Start with the Demo

**For the best introduction, read the [Phoenix demo guide](demo/README.md).**
It starts with playable recordings and then shows how to replay them visibly
or headlessly, inspect visual tracers and runtime graphs, and navigate the
interactive C-annotated assembly viewer.

The demo guide is the repository's recommended starting point for the
end-to-end Phoenix experience. Return here for project-level setup, ROM
preparation, and maintenance commands.

## Study the C Port

The C port has a source-linked knowledge base and a visual movement archive.
They connect C functions, annotated Z80 routines, RAM slots, ROM patterns,
states, tables, claims, and SVG trajectory views.

- [C-Phoenix knowledge base](c-phoenix/c-annotated/README.md) — choose Dutch
  or English; includes the machine-readable graph and its validators.
- [Animation and trajectory archive](c-phoenix/animations/README.md) — choose
  Dutch or English; covers bird animation phases and ROM-driven movement
  patterns.

## Choose Your Starting Point

| If you want to… | Start here |
| --- | --- |
| Experience the full Phoenix demonstration | **[Read the demo guide](demo/README.md)** |
| Build all three runnable implementations | `make build` (or `make all`) |
| Remove local build output before a fresh build | `make clean` |
| Play the native, high-resolution C2 presentation | `make c2-run` |
| Run the classic C port | `cd c-phoenix && make run` |
| Run the Java emulator | `cd jphoenix-emulator-port && make run` |
| Study the C-port knowledge base | [Open C-annotated documentation](c-phoenix/c-annotated/README.md) |
| Explore ROM movement patterns | [Open animations and trajectories](c-phoenix/animations/README.md) |
| Generate and view the interactive ASM documentation | `make c-asm-view` |
| Generate and view the C-Phoenix comparison tracer | `make c-tracer-view` |
| Generate and view the JPhoenix demo tracer | `make j-tracer-view` |
| Build and check the whole repository | `make verify` |

The projects in this repository are:

- [`c-phoenix/`](c-phoenix/): a C port of the original game.
- [`c2-phoenix/`](c2-phoenix/): an interactive, high-resolution presentation
  built around the same game behaviour; it is not a hardware emulator.
- [`jphoenix-emulator-port/`](jphoenix-emulator-port/): a Java emulator of the
  original arcade hardware.
- [`demo/`](demo/): curated videos, replays, runtime callgraphs, and a
  showcase.

Original Phoenix Arcade contributions are available under the
[MIT License](LICENSE). Third-party provenance and exclusions are described in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Quick Start for Development

After preparing the ROM set, for the shortest route to something interactive,
run:

```sh
make c2-run
```

To compile C-Phoenix, C2-Phoenix, and JPhoenix without starting a program,
use:

```sh
make build
```

`make all` is an alias for `make build`. Neither target runs tests, generates
documentation or tracers, prepares ROMs, or starts a viewer.

For a fresh local build, use `make clean` first. It removes only generated C,
C2-native, and Java compilation output; it preserves ROMs, source files,
recordings, traces, and generated documentation.

To build and run every available check instead, use:

```sh
make verify
```

The projects were developed mainly on **macOS** and also support Linux. On
Windows, use WSL2 for the full C, Java, tracing, and graph toolchain. The Java
core can be built natively on Windows with JDK 11+; the optional LibGDX
frontend includes `jphoenix-emulator-port/gradlew.bat`.

## ROMs

All workflows currently require a legally obtained dump of the Phoenix Amstar
ROM set. ROM bytes must come from your own board or another authorised source;
do not download or commit unverified dumps. Follow
[`roms/README.md`](roms/README.md) to place, validate, and assemble the set.
The key commands are:

```sh
make romprepare ROM_DIR=/path/to/phoenix-amstar-chips
```

The ROM guide explains the expected individual chip files and what the build
does with them.

## Requirements

- C projects: GCC or Clang, SDL2, GNU Make, and Python 3.
- Java emulator: JDK 11+; JDK 17+ for the optional LibGDX frontend.
- Full comparison and graph pipeline: Python 3 and Graphviz.

## Repository Checks

```sh
make links        # Verify local Markdown links.
make large-files  # Report files >= 1 MiB; reject unapproved files >= 20 MiB.
```

Large generated dumps and HTML traces are ignored. Curated compressed fixtures
and demo material are documented in [LARGE-FILES.md](LARGE-FILES.md).

## Repository Maintenance Tools

Run these targets from the repository root. They provide the supported entry
points for the root utility scripts; invoking the scripts directly is normally
unnecessary.

| Make target | Script | Purpose |
| --- | --- | --- |
| `make links` | `tools/check_markdown_links.py` | Checks local Markdown links. |
| `make large-files` | `tools/audit_large_files.py` | Reports large files and rejects unapproved files of 20 MiB or more. |
| `make public-audit` | `tools/audit_public_export.py` | Reports private-only files that must not enter the planned byte-free public export. Add `--strict` only when invoking the script directly in an enforcement workflow. |
| `make romcheck` | `tools/rom_tool.py` | Validates the supplied Phoenix chip set against the ROM manifest. |
| `make romnormalize` | `tools/rom_tool.py` | Normalizes supplied chip filenames and creates the local archive without assembling ROM images. |
| `make rombuild` | `tools/rom_tool.py` | Builds the assembled program, graphics, and PROM images from validated chips. |
| `make romprepare` | `tools/rom_tool.py` + `tools/generate_phoenix_tables.py` | Builds the ROM images and verifies the C tables derived from program ROM. |
| `make gen-phoenix-tables` | `tools/generate_phoenix_tables.py` | Regenerates the byte payloads in `c-phoenix/phoenix_tables.c` from `program.rom`, but aborts on an unexpected mismatch. |

The ROM workflow, manifest, and expected chip files are described in
[roms/README.md](roms/README.md). `gen-phoenix-tables` is deliberately
conservative: use `ALLOW_MISMATCH=1` only after reviewing a genuine ROM-set
change.
