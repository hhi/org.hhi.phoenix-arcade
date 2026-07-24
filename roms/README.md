# Preparing Phoenix ROMs

Dutch version: [README.nl.md](README.nl.md).

Before you can start a game, you need a Phoenix Amstar ROM set. Find a legally
usable set yourself; the repository does not include ROM files.

![ROM preparation and assembly](diagrams/rom-provisioning-pipeline.svg)

## 1. Find the ROM set

Find a legally usable Phoenix Amstar ROM set online. Use the Phoenix (Amstar)
set only; other Phoenix revisions use different chips and will not pass
validation.

## 2. Place the chip files

Put the individual files from your Phoenix Amstar set in `roms/local/`. Their
names must be exactly as shown here:

```text
roms/local/
  ic45              ic46              ic47              ic48
  h5-ic49.5a        h6-ic50.6a        h7-ic51.7a        h8-ic52.8a
  b1-ic39.3b        b2-ic40.4b        ic23.3d           ic24.4d
  mmi6301.ic40      mmi6301.ic41
```

`roms/local/` is the default location used by the scripts.

## 3. Prepare the ROM set

From the repository root (the top-level directory), run:

```sh
make romprepare
```

`make romprepare` verifies every supplied chip, combines them into three files in
`roms/assembled/`, and updates the C sources derived from those files:

| File | Used for |
| --- | --- |
| `program.rom` | The game program |
| `graphics.rom` | The game graphics |
| `proms.rom` | The colour palette |

It also prepares two C source files:

- `c-phoenix/rom_data.c` is a generated C version of the three assembled ROM
  files: their bytes are stored as C arrays. The classic C-Phoenix renderer
  uses those arrays for the original graphics and colours.
- `c-phoenix/phoenix_tables.c` contains named game-data tables for the shared
  game core. This lets C-Phoenix and C2-Phoenix use the game rules and timing
  without searching the program ROM directly while playing.

The assembled files are then used by the projects:

![Projects that use the assembled ROMs](diagrams/rom-assembled-consumers.svg)

If your ROM files are in another folder, use it explicitly:

```sh
make romprepare ROM_DIR=/path/to/phoenix-amstar-chips
```

The command stops if a file is missing, has the wrong size, or does not match
the expected set. This protects the projects from being run with a different
Phoenix revision by accident.

`make rombuild` is available when you only want to create the three assembled
ROM files and do not need to refresh the derived C sources.

## 3. Run a project

With the assembled files in place, return to the repository root and choose a
project from the [main README](../README.md#choose-your-starting-point).
The Java emulator reads the assembled files directly. The C projects use the
same validated ROM set while building their game assets.

## More detail

[`phoenix-amstar/rom-set.json`](phoenix-amstar/rom-set.json) is the manifest
used by the validation commands. It records the expected chips, file sizes,
and checksums. You normally do not need to edit it.

For the exact physical-chip mapping, see the table below.

| Assembled file | Chip files |
| --- | --- |
| `program.rom` | `ic45`, `ic46`, `ic47`, `ic48`, `h5-ic49.5a`, `h6-ic50.6a`, `h7-ic51.7a`, `h8-ic52.8a` |
| `graphics.rom` | `b1-ic39.3b`, `b2-ic40.4b`, `ic23.3d`, `ic24.4d` |
| `proms.rom` | `mmi6301.ic40`, `mmi6301.ic41` |
