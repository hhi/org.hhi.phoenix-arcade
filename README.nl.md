# Phoenix Arcade

Phoenix Arcade is een plek voor verschillende manieren om de arcadegame
*Phoenix* uit 1980 te beleven en te bestuderen. Bereid vóór het bouwen of
draaien van een project eerst een legaal verkregen Phoenix Amstar-ROM-set voor,
zoals beschreven in [`roms/README.nl.md`](roms/README.nl.md).

## Begin met de demo

**Lees voor de beste introductie de [Phoenix-demo-handleiding](demo/README.nl.md).**
Die begint met speelbare opnamen en laat vervolgens zien hoe je deze zichtbaar
of headless herhaalt, visuele tracers en runtimegrafieken onderzoekt en door de
interactieve C-geannoteerde assemblyviewer navigeert.

De demo-handleiding is het aanbevolen startpunt voor de volledige
Phoenix-ervaring. Kom hier terug voor projectopzet, ROM-voorbereiding en
onderhoudscommando's.

## Kies je startpunt

| Als je wilt… | Begin dan hier |
| --- | --- |
| De volledige Phoenix-demo ervaren | **[Lees de demo-handleiding](demo/README.nl.md)** |
| Alle drie uitvoerbare implementaties bouwen | `make build` (of `make all`) |
| Lokale build-uitvoer verwijderen voor een schone build | `make clean` |
| De native C2-presentatie in hoge resolutie spelen | `make c2-run` |
| De klassieke C-poort draaien | `cd c-phoenix && make run` |
| De Java-emulator draaien | `cd jphoenix-emulator-port && make run` |
| De interactieve ASM-documentatie genereren en tonen | `make c-asm-view` |
| De C-Phoenix-vergelijkingstracer genereren en tonen | `make c-tracer-view` |
| De JPhoenix-demotracer genereren en tonen | `make j-tracer-view` |
| De hele repository bouwen en controleren | `make verify` |

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

## Snel starten met ontwikkelen

Na het voorbereiden van de ROM-set is dit de kortste route naar iets
interactiefs:

```sh
make c2-run
```

Gebruik voor het compileren van C-Phoenix, C2-Phoenix en JPhoenix zonder een
programma te starten:

```sh
make build
```

`make all` is een alias voor `make build`. Geen van beide targets voert tests
uit, genereert documentatie of tracers, bereidt ROMs voor of start een viewer.

Gebruik voor een frisse lokale build eerst `make clean`. Dit verwijdert alleen
gegenereerde C-, C2-native- en Java-compile-uitvoer; ROMs, bronbestanden,
opnamen, traces en gegenereerde documentatie blijven behouden.

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

## Repositoryonderhoudstools

Voer deze targets uit vanuit de repository-root. Zij zijn de ondersteunde
ingang voor de root-hulpscripts; de scripts direct aanroepen is normaal niet
nodig.

| Make-target | Script | Doel |
| --- | --- | --- |
| `make links` | `tools/check_markdown_links.py` | Controleert lokale Markdown-links. |
| `make large-files` | `tools/audit_large_files.py` | Meldt grote bestanden en blokkeert niet-goedgekeurde bestanden van 20 MiB of meer. |
| `make public-audit` | `tools/audit_public_export.py` | Meldt private bestanden die niet in de beoogde bytevrije publieke export mogen komen. Voeg `--strict` alleen toe wanneer het script direct in een handhavingsworkflow wordt gebruikt. |
| `make romcheck` | `tools/rom_tool.py` | Valideert de aangeleverde Phoenix-chipset tegen het ROM-manifest. |
| `make romnormalize` | `tools/rom_tool.py` | Normaliseert aangeleverde chipbestandsnamen en maakt het lokale archief zonder ROM-images samen te stellen. |
| `make rombuild` | `tools/rom_tool.py` | Bouwt de samengestelde programma-, graphics- en PROM-images uit gevalideerde chips. |
| `make romprepare` | `tools/rom_tool.py` + `tools/generate_phoenix_tables.py` | Bouwt de ROM-images en controleert de uit de program-ROM afgeleide C-tabellen. |
| `make gen-phoenix-tables` | `tools/generate_phoenix_tables.py` | Genereert de bytepayloads in `c-phoenix/phoenix_tables.c` opnieuw uit `program.rom`, maar stopt bij een onverwachte afwijking. |

De ROM-workflow, het manifest en de verwachte chipbestanden staan in
[roms/README.nl.md](roms/README.nl.md). `gen-phoenix-tables` is bewust
behoudend: gebruik `ALLOW_MISMATCH=1` alleen nadat een daadwerkelijke wijziging
van de ROM-set is beoordeeld.
