# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Wat dit project is

Een hand-vertaalde C-poort van de originele Phoenix-arcade-ROM (1980,
Z80/8085). Elke C-functie vertaalt een concreet ROM-adresbereik; de
poort wordt byte-voor-byte geverifieerd tegen de referentie-emulator
`../jphoenix-emulator-port` (een echte Z80-emulator die de originele
ROM-bytes uitvoert). **Correctheid = identiek RAM-gedrag aan de echte
ROM**, inclusief originele ROM-bugs — "verbeteringen" bovenop de
emulatie zijn ongewenst (een eerdere copyright-wis-hack veroorzaakte
precies zo'n divergentie en is verwijderd).

Statusdocumentatie: `context/STATUS.nl.md` (huidige stand, open observaties en
verificatiebereik). De lockstep-procedure staat in `tools/lockstep/PROCEDURE.md`.

## Commando's

```bash
make                 # bouwt ./c-phoenix (vereist gcc + SDL2)
make clean
./c-phoenix          # interactief venster (3x schaal)

# Headless/deterministisch (basis van alle verificatie):
./c-phoenix --run-frames=3610 --ram-dump=/tmp/port.bin
./c-phoenix --run-frames=4600 --input-script=context/input-scripts/extended_playthrough.txt

# Python-tooling-tests:
python3 -m unittest discover tests            # alles
python3 -m unittest tests.test_trace_sprites  # één module

# Mapping-documentatie regenereren na wijzigen van [ASM:]-docblocks:
python3 tools/generate_mappings.py
python3 tools/generate_annotated_asm.py
```

### Lockstep-verificatie (draai dit na elke spellogica-wijziging)

```bash
# Referentie-dump (eenmalig, of na jphoenix-wijzigingen — herbouw dan eerst
# met `make compile` in ../jphoenix-emulator-port):
cd ../jphoenix-emulator-port
printf '# leeg\n' > /tmp/passive.txt
java -Dphoenix.ramdump=/tmp/jphx.bin -Dphoenix.ramdump.frames=3600 \
     -cp build/classes PhoenixCoverageRunner /tmp/passive.txt /tmp/cov 3600
cd -

./c-phoenix --run-frames=3610 --ram-dump=/tmp/port.bin
python3 tools/compare_ram_dumps.py /tmp/jphx.bin /tmp/port.bin \
    --align-c98 --stop-after 999999 --regions 4000-4BE5
```

Verwacht resultaat: alleen losse één-frame-blips (dump-moment-ruis).
Elke *aanhoudende* divergentie is een echte bug. Cruciaal:
- Altijd `--stop-after 999999` (de default 5 stopt op boot-ruis en mist
  alles daarna).
- Regio `4000-4BE5`: de bytes daarboven zijn Z80-stackresidu dat de
  poort per ontwerp niet heeft.
- **Alleen passieve (input-loze) runs zijn vergelijkbaar.** Scripted
  runs zijn tussen de emulatoren structureel onvergelijkbaar: jphoenix
  verbruikt soms >1 vblank per spel-loop-iteratie, c-phoenix precies
  één, dus input-events landen op verschillende spelmomenten.

## Architectuur

- **`PhoenixState` (`phoenix_state.h`)** is een byte-exacte afbeelding
  van de 3KB game-RAM `$4000-$4BFF`; veldnamen volgen `context/RAMUse.md`.
  Alle geheugen- en I/O-toegang loopt via `mem_read`/`mem_write` in
  `z80_core.h` (ROM `<$4000`, RAM, hardware-poorten `$5000/$5800/$6000/
  $6800/$7000/$7800`) — nooit rechtstreekse pointer-rekenkunde op state.
- **Hoofdlus**: `phoenix_main_loop()` (`hw_video_audio.c`) spiegelt de
  ROM-resetvector: `wait_vblank_coin()` per frame, dan attract-tak
  (`splash_and_demo`) of speeltak (`game_state_machine` →
  `state_0..7`-functies verspreid over `game_state_machine.c`,
  `state_init.c`, `state_play.c`, `state_endings.c`).
- **Platform-scheiding**: `platform_sdl.c` bevat al het niet-ROM-werk
  (SDL-venster/audio, frame-pacing, bank-swap van de volledige state
  voor 2-speler, `--record-input`/`--ram-dump`/screenshot-hooks).
  Headless-modus (`--run-frames`) slaat audio/rendering/pauze bewust
  over voor determinisme.
- **Vertaal-administratie**: elke vertaalde functie draagt een docblock
  met `[ASM: XXXX-YYYY]`. `tools/generate_mappings.py` genereert daaruit
  `context/mapping/c_functions_by_address.md` (adres→functie-tabel met
  Status-kolom en gap-analyse; handmatige bevindingen staan in de
  `KNOWN_STATUS`-dict in het script). Let op: een kale `[ASM:]`-tag
  zonder direct volgende functiedefinitie wordt aan de eerstvolgende
  functie geplakt — verweesde tags dus altijd omzetten naar proza.
- **Referentiemateriaal**: `context/code-annotated.asm` is de
  geannoteerde originele disassembly (de bron van waarheid bij twijfel);
  `context/RAMUse.md` beschrijft elk RAM-adres. De asm bevat zes
  `JP (HL)`-jumptable-dispatches — een tekst-grep op `CALL $XXXX` mist
  die doelen (tabellen `T040E`, `T0814`, `T3018` e.a. zijn inmiddels
  symbolisch geannoteerd).

## Werkafspraken en valkuilen

- **Vertaal exact, verzin niets.** Bij twijfel: asm ernaast leggen.
  De volledige valkuilen-checklist (RRCA/carry, PUSH/RET-trampolines,
  anti-piracy-checks die je nooit mag "wegoptimaliseren", enz.) staat in
  `tools/lockstep/PROCEDURE.md`.
- **Dode duplicaten zijn een bekend patroon**: dezelfde ROM-routine kan
  historisch twee C-vertalingen hebben (één levend, één stub). Check
  vóór je een functie reviewt/aansluit of de mapping-tabel een levende
  naamgenoot op hetzelfde adres toont; 23 van zulke duplicaten zijn al
  verwijderd.
- **Input-scripts** (`context/input-scripts/`, formaat: `<frame> <knop>
  <press|release>`) zijn de basis voor reproduceerbare regressies; neem
  echte speelsessies op met `--record-input=`. Knop-holds moeten
  tientallen frames duren, geen losse pulsen.
- Commit nooit ongevraagd; de gebruiker reviewt eerst de working tree.
- Werk `context/STATUS.nl.md` bij wanneer de publieke status of open observaties
  veranderen; bewaar verificatiestappen in `tools/lockstep/PROCEDURE.md`.
