# Batchverificatie 12 juli 2026

Bewijsmateriaal van de finale scripted-lockstep-batch (procedure:
`tools/lockstep/PROCEDURE.md`).

- **c-phoenix-revisie**: a893d8b (+ working-tree-fixes 11-14)
- **jphoenix-emulator-port-revisie**: 9e827d9 (+ poll-klok-patch in working tree)
- **results.jsonl**: per-script-uitslag (clean-vlag, divergentie-runs)
- **pc-coverage/**: per script de door jphoenix daadwerkelijk uitgevoerde
  PC-adressen (basis voor `context/mapping/lockstep_verified.json`)

Resultaat: alle 57 scripts clean (waarvan de laatste 2 na vangst 14 en
de scherm-blip-drempelcorrectie 4→8 records).
