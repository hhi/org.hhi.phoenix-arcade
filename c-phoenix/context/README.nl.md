# Phoenix Referentiecontext

Engelse documentatie: [README.md](README.md).

Deze map bevat het referentiemateriaal waarmee de C-poort traceerbaar blijft
naar de originele Phoenix Z80-ROM en naar de jphoenix-emulator.

## Hoofdbestanden

- [code-annotated.asm](code-annotated.asm) - geannoteerde Z80-assemblyreferentie.
- [code-annotated.md](code-annotated.md) - Markdown-weergave van de
  geannoteerde assembly, met gegenereerde C-kruisverwijzingen.
- [RAMUse.md](RAMUse.md) - RAM-map en gebruiksnotities.
- [rom-table-catalog.nl.md](rom-table-catalog.nl.md) - inventaris van
  program-ROM-lookuptabellen, extractiestatus en machineleesbare catalogus.
- [game-design.nl.md](game-design.nl.md) - spelontwerp, spelcyclus en
  architectuuroverzicht van de C-port.
- [c_files_categorization.md](c_files_categorization.md) - overzicht van
  C-bronbestanden gegroepeerd per verantwoordelijkheid.
- [fgtiles.md](fgtiles.md) en [bgtiles.md](bgtiles.md) - tile-referenties met
  bronvermelding.
- [Phoenix.jpg](Phoenix.jpg) - visueel referentiebeeld.

## Submappen

- [mapping/](mapping/) - gegenereerde C/ASM-mappingrapporten en
  lockstep-statusdata.
- [graphs/](graphs/) - gegenereerde callgraph- en coverage-artefacten.
- [input-scripts/README.nl.md](input-scripts/README.nl.md) - replay-scripts,
  gegenereerde bot-inputs, `make replayrun` en bugreproductieworkflow.
- [traces/README.nl.md](traces/README.nl.md) - gecureerde trace-artefacten en
  beleid voor wat in Git thuishoort.

## Onderhoud

Genereer afgeleide mapping- en annotatiedocumenten vanuit de projectroot:

```bash
python3 tools/generate_mappings.py
python3 tools/generate_annotated_asm.py
```

Houd ROM-adrestraceerbaarheid intact bij wijzigingen aan C-comments of
gegenereerde documentatie. Als een routine nog onzeker is, documenteer die
onzekerheid in plaats van gedrag in te vullen op basis van aannames.
