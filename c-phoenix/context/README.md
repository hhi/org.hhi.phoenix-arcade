# Phoenix Reference Context

Dutch documentation: [README.nl.md](README.nl.md).

This directory contains the reference material used to keep the C port
traceable to the original Phoenix Z80 ROM and to the jphoenix emulator.

## Main Files

- [Phoenix.asm](Phoenix.asm) - annotated Z80 assembly reference.
- [Phoenix.md](Phoenix.md) - generated Markdown rendering of `Phoenix.asm`,
  with C cross-reference notes.
- [Phoenix.html](Phoenix.html) - interactive HTML rendering with label
  navigation with code/data/other checkbox filters, address-prefixed
  `.EQU` tooltips, visible ASM start/end boundaries for mapped C function
  scopes, and an in-page C source viewer that opens cross-references at the
  linked line.
- [ComputerArcheology.md](ComputerArcheology.md) - Computer Archeology Phoenix
  source reference.
- [code-annotated.asm](code-annotated.asm) and [code-annotated.md](code-annotated.md)
  - legacy annotated assembly reference and rendering.
- [rom-table-catalog.md](rom-table-catalog.md) - program-ROM lookup-table
  inventory, extraction status, and machine-readable catalog.
- [c_files_categorization.md](c_files_categorization.md) - overview of C source
  files grouped by responsibility.
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
python3 tools/generate_interactive_asm_html.py
```

Keep ROM-address traceability intact when updating C comments or generated
documentation. If a routine is still uncertain, document the uncertainty rather
than filling in guessed behavior.
