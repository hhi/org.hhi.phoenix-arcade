c-phoenix - Phoenix (1980) arcade port in C
=============================================

Een hand-vertaalde C-poort van de originele Phoenix-arcade-ROM (Z80),
geverifieerd tegen [jphoenix-emulator-port](../jphoenix-emulator-port), een
echte Z80-emulator die de originele ROM-bytes uitvoert.

Engelse documentatie: [README.md](README.md).

Deze root-README is het startpunt. Detaildocumentatie staat bewust dichter bij
de bijbehorende bestanden:

- [STATUS.nl.md](context/STATUS.nl.md) - actuele stand, open observaties en
  verificatiebereik.
- [Centrale demo](../demo/README.nl.md) - video's, screenshots, visuele
  tracing en de gezamenlijke projectshowcase.
- [context/game-design.nl.md](context/game-design.nl.md) - leesbaar overzicht
  van spelontwerp, spelcyclus en architectuur.
- [tools/README.nl.md](tools/README.nl.md) - mapping-, trace-, compare- en
  input-bot-tools.
- [tools/lockstep/README.nl.md](tools/lockstep/README.nl.md) - scripted
  jphoenix-vs-c-phoenix batchverificatie.
- [context/README.nl.md](context/README.nl.md) - ASM-, RAM-, tile-, mapping-,
  graph-, replay- en tracereferenties.
- [context/input-scripts/README.nl.md](context/input-scripts/README.nl.md) -
  replay-scripts, `make replayrun`, bot-doelen en de "bug gezien tijdens
  spelen"-workflow.
- [context/traces/README.nl.md](context/traces/README.nl.md) - gecureerde
  tracecases en Git-beleid.

Bouwen
------

Vereist: `gcc` en SDL2 (`brew install sdl2` op macOS).

```bash
make
```

Dit compileert alle `.c`-bestanden in de projectmap en levert het
`c-phoenix`-binary op.

```bash
make clean
```

Draaien
-------

```bash
./build/c-phoenix
```

Opent een venster op 3x schaal (208x256 -> 624x768) en start het spel normaal
op.

### Besturing

| Actie | Toets(en) |
| --- | --- |
| Links | Pijl-links, A, J |
| Rechts | Pijl-rechts, D, L |
| Vuren | Spatie, W, I |
| Schild | Pijl-omlaag, S, K |
| Start 1 speler | 1 |
| Start 2 spelers | 2 |
| Munt inwerpen | C, 3, 5 |
| Screenshot huidig frame | F12 |
| Pauzeren / hervatten | Linker muisklik in het venster |

Screenshots via F12 worden weggeschreven als `screenshot_<framenummer>.ppm`.

Command-Line Opties
-------------------

| Optie | Werking |
| --- | --- |
| `--run-frames=<n>` | Headless modus: draait exact `n` frames zonder venster/pacing en sluit daarna af. |
| `--input-script=<pad>` | Speelt een deterministisch inputscript af: `<frame> <knop> <press\|release>`. |
| `--ram-dump=<pad>` | Schrijft elk frame de volledige 3KB game-RAM (`$4000-$4BFF`) weg. |
| `--coverage-dump=<pad>` | Schrijft coverage/state-informatie als JSON. |
| `--no-render` | Slaat tekenen over tijdens headless runs. |
| `--screenshot=<pad>` | Schrijft een PPM-screenshot van het laatste gerenderde frame. |
| `--dump-vram=<pad>` | Schrijft een binaire VRAM/registerdump. |
| `--record-input=<pad>` | Neemt interactieve input op als replay-script. |
| `--start-delay=<seconden>` | Wacht voordat het spel start; alleen interactief. |
| `--wait-for-space` | Wacht tot Spatie wordt ingedrukt; alleen interactief. |

Voorbeelden
-----------

```bash
./build/c-phoenix --start-delay=3
./build/c-phoenix --run-frames=3600 --ram-dump=/tmp/port.bin
./build/c-phoenix --run-frames=1200 --input-script=context/input-scripts/basic_playthrough.txt

make replayrun
make replayrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt
make headlessrun
make recordrun
make comparerun
make tracerun
make help

make headlessrun \
  REPLAY_SCRIPT=context/input-scripts/two_player_last_grown_bird.txt \
  REPLAY_FRAMES=9000 \
  REPLAY_RAM_DUMP=/tmp/c-last-grown-bird.bin \
  REPLAY_COVERAGE_DUMP=/tmp/c-last-grown-bird.coverage.json

./build/c-phoenix --input-script=context/input-scripts/generated/mutated_rank_01_score_5003729.txt
./build/c-phoenix --record-input=/tmp/session.txt
```

Zie [context/input-scripts/README.nl.md](context/input-scripts/README.nl.md)
voor de workflow "bug gezien tijdens spelen".
De volledige, eenvoudige pijplijn staat in
[context/traces/replay-tracer-pipeline-howto.nl.md](context/traces/replay-tracer-pipeline-howto.nl.md).

De make-workflow voor die lus is:

```bash
make recordrun
make replayrun REPLAY_SCRIPT=/tmp/c-phoenix-session.txt
make headlessrun REPLAY_SCRIPT=/tmp/c-phoenix-session.txt REPLAY_FRAMES=9000
make comparerun COMPARE_SCRIPT=/tmp/c-phoenix-session.txt COMPARE_FRAMES=9000 COMPARE_NAME=session
make tracerun COMPARE_SCRIPT=/tmp/c-phoenix-session.txt COMPARE_FRAMES=9000 COMPARE_NAME=session
```

Voor een nieuwe interactieve sessie is de volledige keten één commando:

```bash
make recordtracerun RECORD_NAME=bird-investigation
```

Speel het scenario en sluit daarna het spelvenster. De opname staat dan in
`/tmp/bird-investigation.txt`; Make start vervolgens automatisch beide
replays, de RAM-vergelijking en de HTML-tracer. Standaard replayt deze keten
automatisch tot 400 frames na het laatste opgenomen invoerevent en vergelijkt
zij de gehele run. Pas dat aan met `RECORD_TRACE_FRAMES`,
`RECORD_TRACE_TAIL_FRAMES` en `RECORD_TRACE_STOP_AFTER`.

`make tracerun` voert eerst `comparerun` uit en maakt daarna de zelfstandige
HTML-visual-tracer. Standaard komt die in `/tmp/<COMPARE_NAME>-diff.html`.
Voor de volledige vogeltrace:

```bash
make tracerun \
  COMPARE_SCRIPT=context/input-scripts/two_player_last_grown_bird.txt \
  COMPARE_FRAMES=9000 \
  COMPARE_NAME=last-grown-bird \
  COMPARE_STOP_AFTER=999999
```

Gebruik de lokale viewer-target om in een stap te genereren en te tonen:

```bash
make tracer-view \
  COMPARE_SCRIPT=context/input-scripts/two_player_last_grown_bird.txt \
  COMPARE_FRAMES=9000 \
  COMPARE_NAME=last-grown-bird \
  COMPARE_STOP_AFTER=999999
```

Deze meldt de localhost-URL (standaardpoort `8766`) en houdt de server actief
tot `Ctrl-C`. Gebruik voor een reeds gegenereerde tracer
`make tracer-view-only TRACE_VIEW_OUTPUT=/tmp/last-grown-bird-diff.html`.
Pas de traceruitvoer aan met `VISUAL_TRACE_OUTPUT`, `VISUAL_TRACE_PLAYER`,
`VISUAL_TRACE_KIND` en `VISUAL_TRACE_EXTRA_ARGS`.

Lockstep-Verificatie
--------------------

Het volledige recept staat in [tools/lockstep/PROCEDURE.md](tools/lockstep/PROCEDURE.md). De toolopties
staan in [tools/README.nl.md](tools/README.nl.md). Kort:

```bash
cd ../jphoenix-emulator-port
java -Dphoenix.ramdump=/tmp/jphx.bin -Dphoenix.ramdump.frames=3600 \
     -cp build/classes PhoenixDesktop
cd ../c-phoenix
make
./build/c-phoenix --run-frames=3610 --ram-dump=/tmp/port.bin
python3 tools/compare_ram_dumps.py /tmp/jphx.bin /tmp/port.bin \
    --align-c98 --stop-after 999999
```

Trace-, Replay- en Bottools
---------------------------

Zie [tools/README.nl.md](tools/README.nl.md) voor de toolreferentie en
[context/input-scripts/README.nl.md](context/input-scripts/README.nl.md) voor
praktische replay/bot-workflows.

```bash
python3 tools/trace_sprites.py /tmp/port.bin --kind all \
    --only-active --output=/tmp/objects.csv

python3 tools/view_sprite_trace.py /tmp/port.bin \
    --kind aliens --player 1 --output=/tmp/alien-paths.html

python3 tools/view_sprite_trace.py /tmp/jphx.bin \
    --compare /tmp/port.bin \
    --reference-label jphoenix --port-label c-phoenix \
    --kind birds --player 1 --output=/tmp/bird-diff.html

python3 tools/generate_mappings.py
```

Commentaarconventie
-------------------

Niet-triviale C-functies die ROM-gedrag vertalen horen een kort blok boven de
functie te hebben. Houd ASM-traceerbaarheid en functionele uitleg gescheiden.

```c
/*
 * [ASM: XXXX-YYYY]
 * Functionele rol: wat deze routine in spel- of hardwaretermen doet.
 * Leest/schrijft RAM: belangrijkste statevelden of RAM-regio's.
 * Belangrijke branch/invariant: alleen als dit helpt.
 * Verificatie/trace-notitie: alleen wanneer er concreet bewijs is.
 */
```

Als de routine nog onduidelijk is, documenteer de onzekerheid expliciet in
plaats van gedrag te verzinnen.
