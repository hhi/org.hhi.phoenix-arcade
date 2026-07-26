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

Put the individual files from your Phoenix Amstar set in `roms/local/`. The
filenames do not have to match the canonical names shown here: `make
romprepare` identifies every expected chip by its SHA-256 hash and renames a
unique full match to the canonical name. The names below are therefore the
resulting normalized layout:

```text
roms/local/
  ic45              ic46              ic47              ic48
  h5-ic49.5a        h6-ic50.6a        h7-ic51.7a        h8-ic52.8a
  b1-ic39.3b        b2-ic40.4b        ic23.3d           ic24.4d
  mmi6301.ic40      mmi6301.ic41
```

`roms/local/` is the default location used by the scripts. A complete match
also creates `roms/local/phoenix_amstar-set1.zip` when it is absent, containing
the canonical chip names. Unrecognized files and files from another revision
are left unchanged and cause validation to fail.

## 3. Prepare the ROM set

From the repository root (the top-level directory), run:

```sh
make romprepare
```

To normalize filenames and create the local ZIP without building the assembled
images, run `make romnormalize`.

`make romprepare` verifies every supplied chip, combines them into three files in
`roms/assembled/`, and updates the C sources derived from those files:

| File | Used for |
| --- | --- |
| `program.rom` | The game program |
| `graphics.rom` | The game graphics |
| `proms.rom` | The colour palette |

It also prepares two C source files:

- The assembled ROM files are retained as reproducible build and byte-level
  test inputs. The classic C-Phoenix renderer uses generated decoded tile
  pixels and RGB colours, so it does not link raw ROM arrays.
- `c-phoenix/phoenix_tables.c` contains named game-data tables for the shared
  game core. This lets C-Phoenix and C2-Phoenix use the game rules and timing
  without searching the program ROM directly while playing.
- C2-Phoenix generates its hi-res sprite atlas directly from `graphics.rom`
  and `proms.rom`; that build-time step does not read `program.rom`.

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
