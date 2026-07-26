# Batch Verification — 12 July 2026

Evidence from the final scripted lockstep batch. The repeatable method is in
[`tools/lockstep/PROCEDURE.en.md`](../../../tools/lockstep/PROCEDURE.en.md);
the Dutch evidence note remains [README.md](README.md).

- **c-phoenix revision:** `a893d8b` (+ working-tree fixes 11–14)
- **jphoenix-emulator-port revision:** `9e827d9` (+ poll-clock patch in the
  working tree)
- **results.jsonl:** one result per input script, including its `clean` flag
  and divergence runs
- **pc-coverage/:** program-counter addresses actually executed by JPhoenix per
  script; input to `context/mapping/lockstep_verified.json`

Result: all 57 scripts were clean. The final two completed after finding issue
14 and correcting the transient screen-blip threshold from four to eight
records.
