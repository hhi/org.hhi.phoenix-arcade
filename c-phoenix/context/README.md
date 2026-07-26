# Phoenix Reference Context

Dutch documentation: [README.nl.md](README.nl.md).

This directory contains the reference material used to keep the C port
traceable to the original Phoenix Z80 ROM and to the jphoenix emulator.

## Main Files

- [code-annotated.asm](code-annotated.asm) - annotated Z80 assembly reference.
- [code-annotated.md](code-annotated.md) - Markdown rendering of the annotated
  assembly, with generated C cross-reference notes.
- [RAMUse.md](RAMUse.md) - RAM map and usage notes.
- [rom-table-catalog.md](rom-table-catalog.md) - program-ROM lookup-table
  inventory, extraction status, and machine-readable catalog.
- [c_files_categorization.md](c_files_categorization.md) - overview of C source
  files grouped by responsibility.
- [fgtiles.md](fgtiles.md) and [bgtiles.md](bgtiles.md) - tile reference notes
  with source attribution.
- [Phoenix.jpg](Phoenix.jpg) - visual reference asset.

## Subdirectories

- [mapping/](mapping/) - generated C/ASM mapping reports and lockstep status
  data.
- [graphs/](graphs/) - generated callgraph and coverage graph artifacts.
- [verification/](verification/) - dated lockstep evidence, recorded revisions,
  and JPhoenix PC coverage used to substantiate it.
- [input-scripts/README.md](input-scripts/README.md) - replay scripts, generated
  bot inputs, `make replayrun`, and bug-reproduction workflow.
- [traces/README.md](traces/README.md) - curated trace artifacts and policy for
  what belongs in Git.

## Maintenance

Regenerate derived mapping and annotation documents from the project root:

```bash
python3 tools/generate_mappings.py
python3 tools/generate_annotated_asm.py
```

Keep ROM-address traceability intact when updating C comments or generated
documentation. If a routine is still uncertain, document the uncertainty rather
than filling in guessed behavior.
