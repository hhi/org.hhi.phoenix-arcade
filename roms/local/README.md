# Phoenix ROM Chip Dumps (Local)

Dutch version: [README.nl.md](README.nl.md).

This directory is the intended place to put your own physical Phoenix
Amstar chip dumps (`ic45`, `ic46`, `mmi6301.ic40`, etc. — see the table
in [`../README.md`](../README.md)). It is empty by default and is the
default `ROM_DIR` for `make romcheck` / `make rombuild`; those commands
expect the chip files to already be here (or elsewhere via
`ROM_DIR=<path>`) when you run them. The incoming filenames are not important:
`make romnormalize` and `make romprepare` identify the expected chips by
SHA-256, rename a unique match to its canonical filename, and create
`phoenix_amstar-set1.zip` after a complete match if it does not yet exist.

Everything here except this README is git-ignored (see `.gitignore` in
this directory): the chip bytes are copyrighted ROM content and must
never be committed. Populate it yourself from your own legally obtained
dump; nothing here is provisioned by the repository.
