# Scripted Lockstep Batch Verification

Dutch documentation: [README.nl.md](README.nl.md).

Runs every input script from `context/input-scripts/`, including `generated/`,
through both jphoenix with the opt-in poll clock
(`-Dphoenix.inputclock=poll`) and c-phoenix, then compares the RAM dumps record
by record.

Requirements: a built `../jphoenix-emulator-port` (`make compile`) and a built
`./build/c-phoenix`.

```bash
# Full batch, roughly two hours. RAM dumps are discarded per script:
python3 tools/lockstep/run_batch.py          # writes results.jsonl and
                                             # pc-coverage/ next to the script

# Aggregate into the repository artifact:
python3 tools/lockstep/aggregate.py          # writes context/mapping/lockstep_verified.json
python3 tools/generate_mappings.py           # updates the status column

# Dump one script manually for divergence investigation:
tools/lockstep/dump_pair.sh context/input-scripts/<script>.txt <loopframes> <name>
# -> /tmp/ref_<name>.bin and /tmp/port_<name>.bin
```

The "clean" criterion: game state (`$4340-$47FF` plus `$4B40-$4BE5`, excluding
hi-score noise at `$4388-$438D`) is byte-exact for the full run, except for the
game-start initialization window (records 40-60) and isolated one-record
self-healing reset-boundary blips. Screen RAM, both foreground and background,
may only show self-healing blips of eight records or less. The machine-readable
criterion lives in `criteria.py`; the repeatable workflow is documented in
[PROCEDURE.en.md](PROCEDURE.en.md) and [PROCEDURE.md](PROCEDURE.md) (Dutch).

## Semantic analysis

For a RAM-field or routine meaning investigation, first create a dump pair,
then extract only the relevant RAM transition:

```bash
tools/lockstep/dump_pair.sh context/input-scripts/<script>.txt <frames> <name>
python3 tools/lockstep/semantic_delta.py /tmp/ref_<name>.bin /tmp/port_<name>.bin \
  --record <record> --window 1 --regions 43A0-43C7 \
  --output-json=/tmp/<name>.json --output-md=/tmp/<name>.md
```

The extractor shows mutations in both implementations and remaining parity
diffs for each record. Record a conclusion using the
[semantic case template](../../context/traces/semantic-case-template.md).
It proves which bytes changed; identifying the writer still requires ASM/C
analysis until targeted write-level tracing exists.

Paths are relative by default: `CPHX` points to this repository and `JPHX` to
`../jphoenix-emulator-port`. Override them when needed:

```bash
CPHX=/path/to/c-phoenix JPHX=/path/to/jphoenix-emulator-port \
  python3 tools/lockstep/run_batch.py
```
