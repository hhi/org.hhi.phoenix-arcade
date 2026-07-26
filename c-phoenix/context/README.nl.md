# Phoenix Referentiecontext

Engelse documentatie: [README.md](README.md).

Deze map bevat het referentiemateriaal waarmee de C-poort traceerbaar blijft
naar de originele Phoenix Z80-ROM en naar de jphoenix-emulator.

## Hoofdbestanden

- [Phoenix.asm](Phoenix.asm) - geannoteerde Z80-assemblyreferentie.
- [Phoenix.md](Phoenix.md) - gegenereerde Markdown-weergave van `Phoenix.asm`,
  met C-kruisverwijzingen.
- [Phoenix.html](Phoenix.html) - interactieve HTML-weergave met labelnavigatie,
  selectievakjes voor code/data/overig, `.EQU`-tooltips met geheugenadres
  en zichtbare ASM-begin-/eindgrenzen voor gemapte C-functiebereiken, plus een
  ingebouwde C-bronviewer die kruisverwijzingen op de gekoppelde regel opent.
- [ComputerArcheology.md](ComputerArcheology.md) - bronverwijzing naar Computer
  Archeology voor Phoenix.
- [code-annotated.asm](code-annotated.asm) en [code-annotated.md](code-annotated.md)
  - verouderde geannoteerde assemblyreferentie en -weergave.
- [rom-table-catalog.nl.md](rom-table-catalog.nl.md) - inventaris van
  program-ROM-lookuptabellen, extractiestatus en machineleesbare catalogus.
- [game-design.nl.md](game-design.nl.md) - spelontwerp, spelcyclus en
  architectuuroverzicht van de C-port.
- [c_files_categorization.md](c_files_categorization.md) - overzicht van
  C-bronbestanden gegroepeerd per verantwoordelijkheid.
- [Phoenix.jpg](Phoenix.jpg) - visueel referentiebeeld.

## Submappen

- [mapping/](mapping/) - gegenereerde C/ASM-mappingrapporten en
  lockstep-statusdata.
- [graphs/](graphs/) - gegenereerde callgraph- en coverage-artefacten.
- [input-scripts/README.nl.md](input-scripts/README.nl.md) - replay-scripts,
  gegenereerde bot-inputs, `make replayrun` en bugreproductieworkflow.
- [traces/README.nl.md](traces/README.nl.md) - gecureerde trace-artefacten en
  beleid voor wat in Git thuishoort.

## Interactieve ASM genereren en bekijken

Genereer vanuit de repository-root (aanbevolen) de Markdown en HTML met:

```bash
make c-asm-docs
```

Start een lokale viewer met ondersteuning voor C-bronlinks:

```bash
make c-asm-view
```

Gebruik het volgende commando om de al gegenereerde HTML te tonen zonder
opnieuw te genereren:

```bash
make c-asm-view-only
```

Open `http://127.0.0.1:8765/context/Phoenix.html`; voeg `?theme=light` toe
voor de expliciete lichte variant. Gebruik `ASM_VIEW_PORT=8766` (of een andere
vrije poort) om de standaardpoort te wijzigen. Stop de viewer met `Ctrl-C`.

De equivalente commando's wanneer je ze vanuit de map `c-phoenix/` uitvoert:

```bash
make interactive-asm
make interactive-asm-view
make interactive-asm-view-only
```

Gebruik de lokale viewer en open `Phoenix.html` niet via `file://`: de
ingebouwde C-bronviewer moet C-bestanden via HTTP kunnen ophalen.

## Onderhoud

Genereer alle afgeleide mapping-, annotatie- en grafiekdocumenten met:

```bash
make -C c-phoenix docs
```

Houd ROM-adrestraceerbaarheid intact bij wijzigingen aan C-comments of
gegenereerde documentatie. Als een routine nog onzeker is, documenteer die
onzekerheid in plaats van gedrag in te vullen op basis van aannames.
