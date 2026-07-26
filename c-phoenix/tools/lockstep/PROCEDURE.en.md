# Procedure: Full Verification and Divergence Investigation

This is the repeatable procedure for validating the C port against real Z80
execution in JPhoenix. The Dutch original is [PROCEDURE.md](PROCEDURE.md).

## 1. Build both sides

```sh
cd ../jphoenix-emulator-port && make compile && make verify
cd ../c-phoenix && make
```

Rebuild JPhoenix and regenerate its reference dumps after every JPhoenix
change. Every scripted comparison needs `-Dphoenix.inputclock=poll`; without
it, input events land on different game-loop moments.

## 2. Run the right scope

| Scope | Command | Result |
| --- | --- | --- |
| Quick passive regression | Follow the command in [PROCEDURE.md](PROCEDURE.md#1-snelle-regressie-na-elke-spellogica-wijziging-2-min) | A short state/screen parity check. |
| Full batch | `python3 tools/lockstep/run_batch.py` | `results.jsonl` and `pc-coverage/` beside this procedure. |
| Aggregate clean evidence | `python3 tools/lockstep/aggregate.py` then `python3 tools/generate_mappings.py` | `context/mapping/lockstep_verified.json` and refreshed mapping status. |
| One divergence | `tools/lockstep/dump_pair.sh context/input-scripts/<script>.txt <frames> <name>` | `/tmp/ref_<name>.bin` and `/tmp/port_<name>.bin`. |
| Inspect one transition | `python3 tools/lockstep/semantic_delta.py /tmp/ref_<name>.bin /tmp/port_<name>.bin --record <n> --regions 43A0-43C7` | Named byte changes and remaining parity differences. |

The batch resumes from existing `results.jsonl` entries. Move or remove that
file before rerunning after a binary change, otherwise it would mix stale and
new evidence.

## 3. Interpret results

The machine-readable thresholds are in `criteria.py`. Game state is expected
to be byte exact except for the documented start window and isolated
self-healing one-record reset blips. Screen RAM may have self-healing blips of
at most eight records. A sustained difference is a regression, not tolerated
noise.

Archive `results.jsonl`, `pc-coverage/`, and the two Git revisions under
`context/verification/<date>/`. RAM dumps are reproducible scratch artifacts;
do not archive them unless a specific investigation requires it.
