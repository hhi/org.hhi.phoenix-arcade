# Assembled Phoenix ROM Images (Local)

Dutch version: [README.nl.md](README.nl.md).

This directory holds the assembled `program.rom`, `graphics.rom`, and
`proms.rom` produced by `make rombuild ROM_DIR=/path/to/chips` (see
[`../README.md`](../README.md)). It is the default `ROM_OUTPUT_DIR` for
`rombuild` and the default `ROM_DIR` that `make -C jphoenix-emulator-port
run` loads from.

Everything here except this README is git-ignored (see `.gitignore` in
this directory): the assembled images are copyrighted ROM content and
must never be committed. Run `make rombuild` to (re)generate them from
your own chip dump in [`../local/`](../local/).
