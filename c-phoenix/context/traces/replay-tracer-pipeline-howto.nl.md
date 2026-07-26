# Replay- en Visual-Tracerpijplijn

Deze werkinstructie beschrijft de volledige route van een gespeelde sessie tot
een visuele objecttracer. Begin met de korte opdrachten; de technische
bestandsuitleg is alleen nodig wanneer je een resultaat wilt onderzoeken.

Gebruik vanuit de projectroot altijd eerst:

```sh
make help
```

Dat toont de beschikbare targets en hun standaardwaarden.

## Voorbereiding

Voor `recordrun`, `replayrun` en `headlessrun` volstaan c-phoenix, `gcc` en
SDL2. Voor `comparerun`, `tracerun` en dus ook `recordtracerun` is daarnaast
jphoenix vereist: de referentie-emulator waarmee c-phoenix wordt vergeleken.

De standaardlocatie is een siblingproject naast c-phoenix:

```text
PHOENIX_THE_GAME/
  c-phoenix/
  jphoenix-emulator-port/
```

Installeer een JDK 11 of nieuwer en bouw jphoenix eenmaal vanuit die map:

```sh
cd ../jphoenix-emulator-port
make
cd ../c-phoenix
```

Dit maakt `../jphoenix-emulator-port/build/classes`. `dump_pair.sh`, dat door
`comparerun` wordt gebruikt, start daar rechtstreeks
`PhoenixCoverageRunner`; het bouwt jphoenix niet automatisch. Ontbreekt de
siblingmap, Java of deze builduitvoer, dan kan `recordtracerun` geen
vergelijking of HTML-difftracer maken.

## Kortste Routes

| Ik wil... | Eenvoudigste opdracht | Resultaat |
| --- | --- | --- |
| een sessie opnemen | `make recordrun RECORD_NAME=mijn-sessie` | speelbaar `.txt`-inputscript in `/tmp` |
| die sessie terugzien | `make replayrun REPLAY_SCRIPT=/tmp/mijn-sessie.txt` | zichtbaar spelvenster met dezelfde invoer |
| de sessie vergelijken en tracen | `make recordtracerun RECORD_NAME=mijn-sessie` | opname, vergelijking en HTML-tracer |
| een bestaand script volledig analyseren | `make tracerun COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt COMPARE_FRAMES=13935 COMPARE_NAME=bird-investigation COMPARE_STOP_AFTER=999999` | twee dumps, vergelijking en HTML-tracer |

Sluit het venster na een zichtbare `recordrun` of `replayrun` zelf. De
headless targets stoppen automatisch na het opgegeven aantal frames.

## Pijplijn

```text
recordrun ──> inputscript (.txt) ──> replayrun (zichtbaar terugkijken)
                                      │
                                      ├──> headlessrun ──> C-Phoenix RAM-dump (.bin)
                                      │
inputscript (.txt) ──> comparerun ──> jphoenix + C-Phoenix RAM-dumps (.bin)
                                      └──> vergelijking in terminal
                                                   │
                                                   v
                                             tracerun ──> HTML-visual-tracer

recordtracerun = recordrun + tracerun
```

`comparerun`, `tracerun` en `recordtracerun` hebben de gebouwde siblingmap
`../jphoenix-emulator-port` nodig. `recordrun`, `replayrun` en `headlessrun`
hebben alleen c-phoenix nodig.

## Targets

### `make recordrun`

Doel: speel zelf en neem iedere knopovergang op.

```sh
make recordrun RECORD_NAME=mijn-sessie
```

Product: `/tmp/mijn-sessie.txt`. Dit kleine tekstbestand is de bron voor alle
volgende stappen en mag, wanneer het een bruikbare regressiecase is, naar
`context/input-scripts/` worden gekopieerd.

### `make replayrun`

Doel: een inputscript zichtbaar en met de normale interactieve presentatie
terugkijken.

```sh
make replayrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt
```

Product: geen bestand. Het spelvenster speelt de opgenomen knoppen op de
bijbehorende frames af. Sluit het venster wanneer je klaar bent.

### `make headlessrun`

Doel: snel en zonder venster een script afspelen, bijvoorbeeld voor een
controle of een enkele C-Phoenix-dump.

```sh
make headlessrun \
  REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt \
  REPLAY_FRAMES=13935 \
  REPLAY_RAM_DUMP=/tmp/bird-investigation.bin
```

Product: optioneel één C-Phoenix `.bin`. Zonder `REPLAY_RAM_DUMP` is het een
stille afloopcontrole zonder uitvoerbestand.

### `make comparerun`

Doel: exact hetzelfde inputscript in jphoenix en c-phoenix draaien en de
gekozen RAM-regio's vergelijken.

```sh
make comparerun \
  COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt \
  COMPARE_FRAMES=13935 \
  COMPARE_NAME=bird-investigation \
  COMPARE_STOP_AFTER=999999
```

Producten: `/tmp/ref-bird-investigation.bin` (jphoenix),
`/tmp/port-bird-investigation.bin` (c-phoenix) en een leesbaar
vergelijkingsrapport in de terminal.

### `make tracerun`

Doel: eerst `comparerun` uitvoeren en daarna de objectposities en verschillen
in één zelfstandige HTML-pagina tonen.

```sh
make tracerun \
  COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt \
  COMPARE_FRAMES=13935 \
  COMPARE_NAME=bird-investigation \
  COMPARE_STOP_AFTER=999999
```

Product: naast de twee dumps `/tmp/bird-investigation-diff.html`. Toon die
via de uniforme lokale viewer:

```sh
make tracer-view-only TRACE_VIEW_OUTPUT=/tmp/bird-investigation-diff.html
```

De target toont de URL op `http://127.0.0.1:8766/` en stopt met `Ctrl-C`.

### `make recordtracerun`

Doel: de hele route met één opdracht. Je speelt eerst zelf; na het sluiten van
het venster maakt Make de vergelijking en de tracer.

Voorwaarde: voer eerst de stappen uit onder **Voorbereiding** uit; deze target
start jphoenix via `tracerun`.

```sh
make recordtracerun RECORD_NAME=mijn-sessie
```

Standaard leest de target het laatste eventframe uit de opname en draait nog
400 frames door. Voor een vaste eindgrens gebruik je bijvoorbeeld
`RECORD_TRACE_FRAMES=15000`.

## Producten en Inhoud

### Inputscript (`.txt`)

Een opname is gewone tekst: één knopovergang per regel.

```text
# Recorded session, Wed Jul 15 22:32:36 2026
203 start1 press
220 start1 release
841 fire press
850 fire release
```

De eerste waarde is het frame. Daarna volgen knop (`coin`, `start1`, `left`,
`fire`, enzovoort) en actie (`press` of `release`). Dit bestand bevat geen
beeld, geluid of RAM; het beschrijft uitsluitend wat de speler deed.

### RAM-dump (`.bin`)

Een dump is binair en bestaat uit opeenvolgende records:

```text
4 bytes  framenummer, big-endian
3072 bytes RAM-snapshot: $4000-$4BFF
```

De eerste record begint conceptueel als:

```text
00 00 00 01 | <3072 RAM-bytes van frame 1>
```

De RAM bevat onder andere game state, level/round, speler-, alien- en
vogelslots en scherm-RAM. Het is geen video, geen audiobestand en geen
inputscript. De tracer leest deze snapshots om dots, paden en slotgegevens te
tekenen.

### Vergelijking in de terminal

`comparerun` vergelijkt standaard de gameplay/objectregio's
`$4340-$47FF,$4B40-$4BE5` en lijnt dumps uit op `Counter98`. Bij gelijkheid
eindigt het rapport bijvoorbeeld met:

```text
Uitgelijnd op Counter98: 339 gemeenschappelijke tellerwaarden
Vergelijk 339 frames (ref: 339, port: 339), regio's: 4340-47FF,4B40-4BE5
Geen verschillen gevonden.
```

Bij een verschil wordt het framepaar, RAM-adres, bekende veldnaam en de twee
bytewaarden getoond:

```text
Frame-paar 7000 (ref #7000 / port #7000): 1 verschil(len)
  0x43C1 PlayerShape              ref=0x04 port=0x08
```

Een verschil is een onderzoekssignaal, geen automatisch bewezen gameplaybug:
drawvolgorde en dumptiming kunnen bijvoorbeeld scherm-RAM doen afwijken.

### Visual tracer (`.html`)

De tracer is een zelfstandige HTML-pagina met de gedecodeerde objectrecords
ingesloten. Zij bevat het Phoenix-grid, framebediening, slots, paden,
tooltips, levelovergangen en bij een vergelijking de jphoenix/C-Phoenix-diff.

De HTML is bedoeld om in een browser te openen, niet om in Git te bewaren:
zij kan tientallen tot honderden MB groot worden. Bewaar het inputscript en
de korte readme; genereer dumps en HTML opnieuw wanneer nodig.

## Welke Route Kies Ik?

- Alleen opnieuw beleven: `replayrun`.
- Snel controleren na een C-wijziging: `headlessrun`.
- Uitzoeken waarom de C-poort van de ROM-referentie afwijkt: `comparerun`.
- Objectbewegingen of verschillen op het grid bekijken: `tracerun`.
- Een nieuw probleem tijdens spelen vastleggen en meteen analyseren:
  `recordtracerun`.
