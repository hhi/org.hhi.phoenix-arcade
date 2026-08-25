# Phoenix Arcade

🇳🇱 Nederlands · 🇬🇧 [English](README.md)

<img src="demo/c2-variant-hires3a-full.png" alt="Phoenix gameplay: een golf duikende vogels boven het speelschip, in de moderne hoge-resolutieweergave" width="360">

*Phoenix* is de arcade-shoot-'em-up uit 1980 waarin je duikende vogels en een
gepantserd moederschip afweert. Met deze repository speel je dat spel
gewoon — in een pixel-perfecte reconstructie, een opnieuw getekende
hoge-resolutieversie of een Redot-vertical-slice — en als je nieuwsgierig
wordt, kun je precies bekijken hoe het origineel onder de motorkap werkte.

## Speel het

Kies een uiterlijk en bouw het. Elk commando bouwt vanuit de broncode, dus de
eerste keer wordt er gecompileerd; zie [Vereisten](#vereisten) voor wat je
nodig hebt.

| Versie | Wat je krijgt | Commando | Volledige details |
| --- | --- | --- | --- |
| **Modern, hoge resolutie** | Opnieuw getekende glyphs, vloeiende kleur en licht, dezelfde spelregels | `make c2-run` | [`c2-phoenix/README.nl.md`](c2-phoenix/README.nl.md) |
| **Klassiek, pixel-perfect** | Het originele 8×8-uiterlijk, herbouwd in C | `cd c-phoenix && make run` | [`c-phoenix/README.nl.md`](c-phoenix/README.nl.md) |
| **Origineel arcade-board** | Draait de echte programmacode uit 1980 op een op Java gebaseerde hardware-emulator | `cd jphoenix-emulator-port && make run` | [`jphoenix-emulator-port/README.nl.md`](jphoenix-emulator-port/README.nl.md) |
| **Redot-vertical-slice** | De C-gamecore in een via de GPU samengestelde Redot-scene, met audio | `make -C redot-port/native extension` | [`redot-port/README.nl.md`](redot-port/README.nl.md) |
| **Browserprototype** | De C-gamecore als WebAssembly, lokaal in je browser | `make web` | [`browser-port/README.nl.md`](browser-port/README.nl.md) |

Elke README onder "volledige details" heeft de besturing, buildopties en
command-line-vlaggen voor die versie (bijvoorbeeld de pijltjestoetsen/WASD om
te bewegen en Space om te schieten, hetzelfde in de drie desktopimplementaties).

De Redot-poort is een in de editor speelbare vertical slice voor macOS op
Apple Silicon. Open na het bouwen van de extensie `redot-port/project.godot`
in Redot 26.2 en start de scene. Hij valt buiten `make build`, omdat hij een
eigen Redot- en native-extensietoolchain heeft.

De browservariant is een experimentele, statische WebAssembly-build. Zij
vereist alleen Emscripten om te bouwen en een lokale HTTP-server om te
openen; de speler installeert geen app. Hij valt eveneens buiten `make build`.

Alleen de JPhoenix-emulatorroute heeft je eigen, legaal verkregen Phoenix
Amstar-ROM-set nodig. De repository levert nooit ROM-bytes mee; zie
[`roms/README.nl.md`](roms/README.nl.md) voor de voorbereidingsinstructies.
C-Phoenix, C2, Redot en het browserprototype gebruiken de versiebeheerde
renderassetheader en voeren geen `romprepare` uit.

Om alle drie de versies in één keer te bouwen zonder er één te starten,
gebruik je `make build` (`make all` is een alias).

## Bekijk het eerst

Nog niet klaar om te bouwen? **[Lees de demo-handleiding](demo/README.nl.md)**
— die begint met speelbare opnamen van een echte sessie, naast de
hoge-resolutieweergave, voordat er iets over de ontwikkeltooling volgt.

## Bekijk hoe het spel werkt

**[Open de interactieve Knowledge Base Explorer](c-phoenix/c-annotated/knowledge-base-explorer/index.html)**
om een spelsysteem — spelersschild, vogelgolven, score, video of geluid — te
volgen naar de leesbare C-functie, het oorspronkelijke Z80-adresbereik en de
bijbehorende uitleg. Het is een statische pagina die direct vanuit de checkout
te openen is; bouwen is niet nodig.

## Hoe het project is opgebouwd

Phoenix Arcade is één monorepo, opgebouwd in lagen: speelbare spellen
bovenaan, en het materiaal dat ze verklaart eronder genest.

```text
phoenix-arcade/
├─ demo/                     Opnamen, screenshots en de begeleide showcase
├─ jphoenix-emulator-port/   Java-emulator — draait de originele ROM uit 1980
├─ c-phoenix/                Moderne, handmatig vertaalde C-poort van het spel
│  ├─ c-annotated/           Knowledge base die de C-code koppelt aan de originele Z80-assembly
│  ├─ animations/            Galerij van vijandelijke vluchtpatronen en bewegingsdata
│  └─ tools/                 Visuele tracer, lockstep-checker en andere analysetools
├─ c2-phoenix/                Hoge-resolutiepresentatie, gebouwd op de c-phoenix-engine
├─ redot-port/                Redot-vertical-slice, gebaseerd op de C-gamecore
├─ browser-port/              Experimentele zelfstandige WebAssembly-browservariant
└─ roms/                     Handleiding om je eigen ROM-set voor te bereiden
```

- [`jphoenix-emulator-port/`](jphoenix-emulator-port/README.nl.md) is de
  nauwkeurigheidsbasis: een Java-desktopemulator (gebouwd met moderne
  Gradle/LibGDX-tooling) die het originele Intel 8080-programma, de
  graphics-ROM en de kleur-PROM precies zo draait als het arcade-board deed.
  De eigen README is de referentie voor build, besturing en command-line-opties.
- [`c-phoenix/`](c-phoenix/README.nl.md) is een vanaf nul, handmatig
  vertaalde C-poort van diezelfde ROM-logica — georganiseerd als leesbare
  modules in plaats van assembly, en frame-voor-frame gecontroleerd tegen de
  Java-emulator op gelijkwaardigheid. De eigen README is het startpunt voor
  alles wat eronder genest zit (build, besturing en de tooling hieronder).
  - [`c-annotated/`](c-phoenix/c-annotated/nl/README.md) — knowledge base die
    de C-code koppelt aan de originele Z80-assembly; de **[interactieve
    explorer](c-phoenix/c-annotated/knowledge-base-explorer/index.html)** is
    de directe, onderwerpgerichte ingang.
  - [`animations/`](c-phoenix/animations/nl/README.md) — galerij van
    vijandelijke vluchtpatronen en bewegingsdata.
  - [`tools/`](c-phoenix/tools/README.nl.md) — visuele tracer,
    lockstep-checker en andere analysetools.
- [`c2-phoenix/`](c2-phoenix/README.nl.md) hergebruikt de spel-engine van de
  C-poort en vervangt alleen de renderer door een hoge-resolutieversie; dit
  is de versie op de afbeelding hierboven. De eigen
  [`tools/`](c2-phoenix/tools/README.md) genereren de bijbehorende
  semantische traces.
- [`redot-port/`](redot-port/README.nl.md) draait dezelfde C-gamecore in een
  Redot-scene, met een native GDExtension voor de 60 Hz-simulatie en de video-
  en audiobrug. Hij richt zich nu op macOS met Apple Silicon en is speelbaar
  vanuit de Redot-editor.
- [`browser-port/`](browser-port/README.nl.md) is de zelfstandige experimentele
  browser-shell. Hij compileert de canonieke C-Phoenix-core met Emscripten en
  vereist noch Redot noch een native applicatie bij de speler.
- [`demo/`](demo/README.nl.md) brengt alle drie samen met gecureerde
  opnamen, screenshots en een rondleiding langs de tooling hieronder.

## Ga dieper: bestudeer hoe Phoenix echt werkt

Alles hierboven is speelbare software. Daaronder ligt een volledige,
brongekoppelde uitleg van het originele spel uit 1980, gemaakt voor iedereen
die nieuwsgierig genoeg is om te vragen: "waarom beweegt die vogel zo?" of
"hoe weten we eigenlijk dat de C-poort zich gedraagt als het origineel?"
Niets hiervan is nodig om te spelen — het is er voor wie onder de motorkap
wil kijken. De [demo-handleiding](demo/README.nl.md) doorloopt de
hoogtepunten hieronder in een begeleide volgorde; de secties hier zijn de
naslagversie.

### Zie hoe de ROM verandert in leesbare code

Het originele spel kwam als Z80-assembly, gebrand in ROM-chips. Drie
bestanden, na elkaar, maken daar iets leesbaars van:

```text
Phoenix.asm  →  Phoenix.md  →  Phoenix.html
 handmatig geannoteerde    dezelfde assembly als    een interactieve pagina:
 originele assembly        gekoppelde, doorblader-  klik op een label, spring
                            bare Markdown            direct naar de C-functie
                                                      die het vervangt
```

- [`Phoenix.asm`](c-phoenix/context/Phoenix.asm) — de originele
  Z80-assembly, met de hand geannoteerd met wat elke routine doet en welk
  RAM het aanraakt. (Credits: [Sorbas2020](https://github.com/Sorbas2020/Phoenix))
- [`Phoenix.md`](c-phoenix/context/Phoenix.md) — hetzelfde materiaal,
  automatisch gegenereerd als brongekoppelde Markdown; GitHub rendert dit
  bestand direct leesbaar.
- [`Phoenix.html`](c-phoenix/context/Phoenix.html) — een interactieve
  versie van dezelfde pagina, met code/data-filters, adrestooltips en
  klikbare links naar de C-broncode. Op GitHub toont deze link alleen de
  ruwe broncode; om hem echt te gebruiken, draai je `make c-asm-view` en
  open je het `http://127.0.0.1:8765/…`-adres dat wordt getoond.

![Interactieve Phoenix ASM-cross-reference in donker thema](demo/phoenix-interactive-asm-dark.jpg)

### Bekijk een speelsessie frame voor frame

De **visuele tracer** speelt een opgenomen sessie af als een fysiek
speelveld: elke alien, vogel en kogel getekend als een bewegende stip met
een eigen spoor, naast het exacte framenummer en de RAM-status erachter.
`make c-tracer-view` genereert er een en opent hem meteen (`make
c2-tracer-view` en `make j-tracer-view` doen hetzelfde voor de andere twee
versies).

De tabel hieronder is één frame — record 945 — uit dezelfde opgenomen
sessie, op drie manieren getoond: zoals de twee speelbare versies het
renderen, en zoals de tracer de onderliggende status ziet.

| C-Phoenix (speelbaar) | C2-Phoenix (speelbaar, hoge resolutie) | Wat de tracer laat zien |
| --- | --- | --- |
| <img src="demo/bird-investigation-gameplay-frame-0945.png" width="200" alt="C-Phoenix vogelgolf bij record 945"> | <img src="demo/c2-phoenix-hires-frame-0945.png" width="200" alt="C2-Phoenix hoge-resolutieweergave van dezelfde vogelgolf bij record 945"> | <img src="demo/bird-investigation-visual-tracer-frame-0945.png" width="320" alt="Visuele tracer bij record 945 met vogelgolf-slots en paden"> |

Er is ook een vriendelijkere, spel-niveau **semantische viewer** — score,
levens, niveauovergangen en vijandgebeurtenissen in plaats van ruwe posities
— via `make c2-demo-view`.

### Wat een "lockstep"-vergelijking echt bewijst

De C-poort is niet alleen gebouwd om op Phoenix te *lijken* — hij wordt
gecontroleerd of hij zich *precies zo gedraagt*, en dat is de sterkste
claim die dit project maakt. Dit is wat er gebeurt:

![Hoe lockstep-verificatie werkt: dezelfde opgenomen invoer stuurt zowel de originele ROM uit 1980 als de C-poort aan, en hun spelgeheugen wordt na elk afzonderlijk frame byte voor byte vergeleken](demo/lockstep-explained.nl.svg)

In woorden: een **lockstep**-run voert dezelfde reeks knopindrukken in op
zowel de Java-emulator (die de echte ROM uit 1980 draait) als de C-poort,
frame voor frame, en vergelijkt daarna wat elk van beide na elk afzonderlijk
frame in het geheugen heeft geschreven: spelerpositie, vijand-slots, score,
levens, timers — alles. Als de twee nooit verschillen, is de poort bewezen
gelijkwaardig voor die opgenomen sessie, niet alleen "lijkt erop". De drie
schermafbeeldingen hierboven zijn zelf één product van die vergelijking:
dezelfde onderliggende opname, op drie manieren weergegeven.

De huidige batch draait 57 opgenomen scenario's op deze manier en meldt
byte-exacte overeenstemming voor allemaal; zie het [verificatieverslag van
12 juli](c-phoenix/context/verification/2026-07-12/README.md) voor de
concrete revisies en resultaten. De herhaalbare methode staat in
[`tools/lockstep/README.nl.md`](c-phoenix/tools/lockstep/README.nl.md), met
de volledige stap-voor-stap-procedure in
[`tools/lockstep/PROCEDURE.md`](c-phoenix/tools/lockstep/PROCEDURE.md).

### Zie hoe vijanden echt bewegen

Elke alienformatie en vogelduik in Phoenix volgt een vast vluchtpad,
opgeslagen in de ROM als een korte lijst bewegingsvectoren. De
animatiegalerij zet elk daarvan om in een geanimeerd diagram, rechtstreeks
getekend uit die data — dit is een live preview van drie ervan tegelijk,
die nu draait:

<img src="c-phoenix/animations/00_overview_flight_patterns.svg" width="380" alt="Geanimeerd overzicht van een alien-zwenking, een vogel-duikbom en de afdaling van het moederschip, gegenereerd uit de originele ROM-bewegingsdata">

De [volledige animatie- en trajectgalerij](c-phoenix/animations/nl/README.md)
telt 78 van dit soort animaties, één per ROM-gedefinieerd patroon, plus de
zes groei-en-explosiefases van de vogel, in het Nederlands of Engels.

### Het referentiemateriaal achter dit alles

- [`c-phoenix/context/`](c-phoenix/context/README.nl.md) is de
  archiefkast: de geannoteerde assembly, RAM/ROM-plattegronden, gegenereerde
  callgraphs en elke opgenomen trace staan hier, op één plek geïndexeerd.
- [`context/input-scripts/`](c-phoenix/context/input-scripts/README.nl.md)
  bevat de opgenomen knopindruk-scripts (`bird-investigation.txt` en
  soortgenoten) achter elke demo, tracer en lockstep-run hierboven — speel
  er één af en je krijgt exact dezelfde sessie terug, byte voor byte.
- [`context/traces/`](c-phoenix/context/traces/README.nl.md) verzamelt
  korte, geschreven case-studies — "dit is de RAM-byte die vogelgroei
  bijhoudt, en dit is het bewijs" — in plaats van ruwe dumps.
- [`c-annotated/`](c-phoenix/c-annotated/nl/README.md) is de
  machineleesbare knowledge base: een graph die C-functies, ROM-adressen,
  RAM-velden en tabellen met elkaar verbindt, met eigen validatiecontroles.
  Beschikbaar in het Nederlands of Engels.

### Toolreferenties, om je eigen onderzoek te draaien

Alles hierboven wordt geproduceerd door kleine, gedocumenteerde scripts,
niet met de hand. Deze indexen zijn geschreven voor wie zelf een trace,
vergelijking of graph wil draaien in plaats van de `make`-snelkoppelingen
te gebruiken — sla ze over tenzij dat precies is wat je zoekt:

- [`c-phoenix/tools/README.nl.md`](c-phoenix/tools/README.nl.md) — de
  trace-, mapping-, vergelijkings- en input-bot-scripts achter de analyse.
  Daaronder de [input-bot](c-phoenix/tools/input-bot-howto.nl.md): jij benoemt
  een moment dat je wilt zien — level negen, een wissel tussen twee spelers — en
  hij zoekt een inputscript dat daar komt. Hij vond 50 van de 59 replay-scripts
  waar het dekkingsbewijs van dit project op rust.
- [`c2-phoenix/tools/README.md`](c2-phoenix/tools/README.md) — hetzelfde
  idee voor de semantische traces van de hoge-resolutiepresentatie.
- [`jphoenix-emulator-port/tools/README.md`](jphoenix-emulator-port/tools/README.md)
  — callgraph- en ROM-coverage-tools voor de Java-emulator.

## Kies je startpunt

| Als je wilt… | Begin dan hier |
| --- | --- |
| Gewoon spelen, hoge-resolutieweergave | `make c2-run` |
| Gewoon spelen, pixel-perfecte klassieker | `cd c-phoenix && make run` |
| Gewoon spelen, op de originele ROM-code | `cd jphoenix-emulator-port && make run` |
| Eerst kijken voordat je iets bouwt | **[Lees de demo-handleiding](demo/README.nl.md)** |
| Zien hoe een vijandgolf echt beweegt | [Open de animatiegalerij](c-phoenix/animations/nl/README.md) |
| Een speelsessie frame voor frame traceren | `make c-tracer-view` |
| Begrijpen wat een lockstep-vergelijking bewijst | [Lees "Wat een lockstep-vergelijking echt bewijst"](#wat-een-lockstep-vergelijking-echt-bewijst) |
| De geannoteerde assembly interactief doorbladeren | `make c-asm-view` |
| De geannoteerde assembly als platte bestanden lezen | [`Phoenix.asm`](c-phoenix/context/Phoenix.asm) → [`Phoenix.md`](c-phoenix/context/Phoenix.md) |
| De brongekoppelde knowledge base bestuderen | [Open de C-annotated-documentatie](c-phoenix/c-annotated/nl/README.md) |
| Je eigen trace- of vergelijkingsscript draaien | [Open de C-Phoenix-toolindex](c-phoenix/tools/README.nl.md) |
| Alle drie versies bouwen zonder er één te starten | `make build` (of `make all`) |
| Lokale build-uitvoer verwijderen voor een schone build | `make clean` |
| De hele repository bouwen en controleren | `make verify` |

## Vereisten

- **Om te spelen:** GCC of Clang, SDL2 en GNU Make voor de C-versies; JDK 11+
  (17+ voor de optionele LibGDX-frontend) voor de Java-versie. Python 3 is
  alleen nodig voor de JPhoenix-route die de ROM-set voorbereidt.
- **Voor de browserprototype-build:** daarnaast Emscripten (`emcc`) en een
  lokale HTTP-server, bijvoorbeeld die van Python 3.
- **Om dieper te gaan:** hetzelfde, plus Graphviz voor de volledige
  vergelijkings- en graphketen.

De projecten zijn vooral ontwikkeld op **macOS** en ondersteunen ook Linux.
Gebruik op Windows WSL2 voor de volledige C-, Java-, tracer- en graphketen.
De Java-kern kan native op Windows worden gebouwd met JDK 11+.

## Licentie

De eigen, oorspronkelijke Phoenix Arcade-bijdragen vallen onder de
[MIT-licentie](LICENSE). Herkomst en uitsluitingen van materiaal van derden
staan in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). De originele
Phoenix-ROM zelf wordt niet meegeleverd of gelicentieerd door dit project —
zie [`roms/README.nl.md`](roms/README.nl.md).

## Voor bijdragers en beheerders

<details>
<summary>Buildvarianten, repositorycontroles en ROM-onderhoudstools</summary>

### C2-rendervarianten

`c2-phoenix` levert vijf renderer-experimenten op dezelfde engine. Bouw met
`make c2-run C2_VARIANT=classic` voor het originele, ongemengde uiterlijk, of
een andere `C2_VARIANT`-waarde (`hires2`, `hires2a`, `hires3`, `hires3a`, de
standaard) om een individuele stap afzonderlijk te vergelijken. Zie
[`demo/c2-hires-variants-comparison.md`](demo/c2-hires-variants-comparison.nl.md)
voor een galerij naast elkaar.

### ROM-voorbereidingscommando's

```sh
make romprepare ROM_DIR=/pad/naar/phoenix-amstar-chips
```

De ROM-handleiding ([`roms/README.nl.md`](roms/README.nl.md)) legt uit welke
losse chipbestanden worden verwacht en wat de build ermee doet; de
doelmappen zelf hebben hun eigen korte notities:
[`roms/local/README.nl.md`](roms/local/README.nl.md) (waar je je eigen
chipdumps neerzet) en
[`roms/assembled/README.nl.md`](roms/assembled/README.nl.md) (waar de build
de samengestelde images wegschrijft).

### Ontwerptijd-broncodegraphs

`c-phoenix/context/graphs/` bevat gegenereerde callgraphs van de C-broncode
zelf — welke functie welke aanroept, niet wat een speelsessie daadwerkelijk
heeft uitgevoerd (dat is de runtime-callgraphgalerij in de
[demo-handleiding](demo/README.nl.md)). Regenereer ze met `make -C
c-phoenix docs`; zie
[`context/graphs/README.nl.md`](c-phoenix/context/graphs/README.nl.md) voor
welke vraag elke graaf beantwoordt, hoe de generatoren werken en wat ze niet
zien.

### Repositorycontroles

```sh
make links        # Controleer lokale Markdown-links.
make large-files  # Meld bestanden >= 1 MiB; blokkeer niet-goedgekeurde >= 20 MiB.
```

Grote gegenereerde dumps en HTML-traces worden genegeerd. Gecureerde
gecomprimeerde fixtures en demomateriaal staan in
[LARGE-FILES.md](LARGE-FILES.md).

### Repositoryonderhoudstools

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

`gen-phoenix-tables` is bewust behoudend: gebruik `ALLOW_MISMATCH=1` alleen
nadat een daadwerkelijke wijziging van de ROM-set is beoordeeld.

</details>
