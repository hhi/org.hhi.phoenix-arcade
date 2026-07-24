# Phoenix Arcade

Phoenix Arcade is a home for a few different ways to experience and study the
1980 arcade game *Phoenix*. Before building or running a project, prepare a
legally obtained Phoenix Amstar ROM set as described in
[`roms/README.md`](roms/README.md).

## Choose Your Starting Point

| If you want to… | Start here |
| --- | --- |
| Play the native, high-resolution C2 presentation | `make c2-run` |
| Run the classic C port | `cd c-phoenix && make run` |
| Run the Java emulator | `cd jphoenix-emulator-port && make run` |
| Build and check the whole repository | `make verify` |
| Watch replays, tracer output, and callgraphs | [demo/](demo/README.md) |

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

## Quick Start

After preparing the ROM set, for the shortest route to something interactive,
run:

```sh
make c2-run
```

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
