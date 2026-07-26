# Phoenix Arcade

Phoenix Arcade is een plek voor verschillende manieren om de arcadegame
*Phoenix* uit 1980 te beleven en te bestuderen. Bereid vóór het bouwen of
draaien van een project eerst een legaal verkregen Phoenix Amstar-ROM-set voor,
zoals beschreven in [`roms/README.nl.md`](roms/README.nl.md).

## Kies je startpunt

| Als je wilt… | Begin dan hier |
| --- | --- |
| De native C2-presentatie in hoge resolutie spelen | `make c2-run` |
| De klassieke C-poort draaien | `cd c-phoenix && make run` |
| De Java-emulator draaien | `cd jphoenix-emulator-port && make run` |
| De interactieve ASM-documentatie genereren en tonen | `make c-asm-view` |
| De C-Phoenix-vergelijkingstracer genereren en tonen | `make c-tracer-view` |
| De JPhoenix-demotracer genereren en tonen | `make j-tracer-view` |
| De hele repository bouwen en controleren | `make verify` |
| Replays, tracer-uitvoer en callgraphs bekijken | [demo/](demo/README.nl.md) |

De projecten in deze repository zijn:

- [`c-phoenix/`](c-phoenix/): een C-poort van het oorspronkelijke spel.
- [`c2-phoenix/`](c2-phoenix/): een interactieve presentatie in hoge resolutie
  met hetzelfde spelgedrag; geen hardware-emulator.
- [`jphoenix-emulator-port/`](jphoenix-emulator-port/): een Java-emulator van
  de oorspronkelijke arcadehardware.
- [`demo/`](demo/): gecureerde video's, replays, runtime-callgraphs en een
  showcase.

De eigen, oorspronkelijke Phoenix Arcade-bijdragen vallen onder de
[MIT-licentie](LICENSE). Herkomst en uitsluitingen van materiaal van derden
staan in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Snel starten

Na het voorbereiden van de ROM-set is dit de kortste route naar iets
interactiefs:

```sh
make c2-run
```

Wil je in plaats daarvan alle beschikbare controles bouwen en draaien:

```sh
make verify
```

De projecten zijn vooral ontwikkeld op **macOS** en ondersteunen ook Linux.
Gebruik op Windows WSL2 voor de volledige C-, Java-, tracer- en graphketen. De
Java-kern kan native op Windows met JDK 11+ worden gebouwd; voor de optionele
LibGDX-frontend is `jphoenix-emulator-port/gradlew.bat` aanwezig.

## ROMs

Alle workflows gebruiken momenteel een legaal verkregen dump van de Phoenix
Amstar-ROM-set. ROM-bytes moeten afkomstig zijn van je eigen bord of een
andere geautoriseerde bron; download of commit geen ongeverifieerde dumps.
Volg [`roms/README.nl.md`](roms/README.nl.md) om de set te plaatsen,
controleren en samen te stellen. De belangrijkste commando's zijn:

```sh
make romprepare ROM_DIR=/pad/naar/phoenix-amstar-chips
```

De ROM-handleiding legt uit welke losse chipbestanden worden verwacht en wat
de build ermee doet.

## Vereisten

- C-projecten: GCC of Clang, SDL2, GNU Make en Python 3.
- Java-emulator: JDK 11+; JDK 17+ voor de optionele LibGDX-frontend.
- Volledige vergelijkings- en graphketen: Python 3 en Graphviz.

## Repositorycontroles

```sh
make links        # Controleer lokale Markdown-links.
make large-files  # Meld bestanden >= 1 MiB; blokkeer niet-goedgekeurde >= 20 MiB.
```

Grote gegenereerde dumps en HTML-traces worden genegeerd. Gecureerde
gecomprimeerde fixtures en demomateriaal staan in
[LARGE-FILES.md](LARGE-FILES.md).
