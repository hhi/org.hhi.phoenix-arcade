# C/ASM Mapping and Verification Status

🇬🇧 English · 🇳🇱 [Nederlands](README.nl.md)

Four files answering one question from different angles: **which C function
replaces which piece of the original ROM, and how sure are we?**

The C port was translated by hand from Z80 assembly. That leaves two things to
keep track of — the correspondence itself (this ROM address became that C
function), and the evidence that the translation actually behaves the same.
The first two files below are the map; the other two are the evidence.

## What is here

| File | Answers | Origin |
| --- | --- | --- |
| [`c_functions_by_address.md`](c_functions_by_address.md) | Walking the ROM from `$0000` upward, what lives at each address — a C function, an analysed gap, or padding? | Generated |
| [`c_functions_per_file.md`](c_functions_per_file.md) | The same correspondence sorted by C source file: which ASM ranges does this file cover? | Generated |
| [`jphoenix_crosscheck.md`](jphoenix_crosscheck.md) | For the functions where "is this translation live and correct?" was not obvious, what did the audit conclude? | Written by hand |
| [`lockstep_verified.json`](lockstep_verified.json) | Which functions are byte-exact verified against the original ROM, and by which replay scripts? | Generated |

### Start with the address table

[`c_functions_by_address.md`](c_functions_by_address.md) is the one to open
first. It is the whole 16 KB ROM space in one table, and its **Status** column
is where the two halves meet: a row saying *"Geverifieerd: byte-exacte scripted
lockstep + PC-dekking"* has evidence behind it, a row with an empty Status has
not been examined that way.

Read the note at the top of that file carefully. It says the ROM is 100%
covered, and that means every byte has a name or an explicit gap marker — **not**
that every translation is confirmed correct. Those are different claims, and the
Status column is what separates them.

### Where the evidence comes from

`lockstep_verified.json` is produced by
[`tools/lockstep/aggregate.py`](../../tools/lockstep/aggregate.py), which
collects the results of running the same input scripts through both the Java
emulator (real 1980 ROM) and the C port and comparing RAM byte for byte. Its
criterion is recorded inside the file: a clean run means the game state
(`$4340-$4BE5`, excluding documented noise at `438A-438D`) matched exactly for
the whole run.

**Current contents: generated 2026-07-12, 176 functions verified, 38 partial,
over 57 clean scripts.** The repository now holds 59 input scripts, so a fresh
aggregate would cover a little more. That is a snapshot, not a defect — but it
is why the date matters when you cite these numbers.

`jphoenix_crosscheck.md` is the human end of the same work: the 33 functions
where static analysis and coverage disagreed, each resolved individually into
dead duplicate, inlined helper, harness artefact, or genuine gap.

## Seeing the same thing as a picture

The mapping is a table; sometimes the shape is easier to read.
[`rom_bank_callgraph`](../graphs/rom_bank_callgraph.md) buckets the same
functions by the same `[ASM: nnnn-nnnn]` tags, drawn as a graph — so you can see
at a glance which C modules descend from which region of the original ROM, and
where a bank's functions ended up scattered across several files. See
[`../graphs/README.md`](../graphs/README.md) for the rest of the set.

## Regenerating

The two tables come from one script, run from `c-phoenix/`:

```bash
python3 tools/generate_mappings.py     # or: make docs
```

It reads the `[ASM: nnnn-nnnn]` tags in the C sources' doc comments, pairs them
with the ROM disassembly, and folds in the verification status from
`lockstep_verified.json` — which is why the Status column survives a
regeneration rather than being overwritten.

The JSON is refreshed separately, after a lockstep run:

```bash
python3 tools/lockstep/aggregate.py
```

See [`tools/lockstep/README.md`](../../tools/lockstep/README.md) for the full
procedure.

`jphoenix_crosscheck.md` is not generated. It is an audit conclusion and is
edited by hand when the audit is redone.

## Superseded material

`uncovered_functions.md` used to sit here. It was the raw output of a coverage
run that appeared to show 63 unreached functions; the follow-up audit withdrew
nearly all of those findings. It now lives with the other snapshots in
[`../verification/2026-07-10/`](../verification/2026-07-10/uncovered_functions.md),
because it is a record of how the conclusion was reached rather than a statement
of current status. For that, use the Status column here and
`jphoenix_crosscheck.md`.
