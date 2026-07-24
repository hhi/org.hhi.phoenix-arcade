# Draaiboek: volledige verificatie en bug-jacht

Dit is de herhaalbare procedure waarmee de C-poort tegen de echte
Z80-executie (jphoenix) wordt gevalideerd, zoals uitgevoerd op
11-12 juli 2026. Volg de stappen in volgorde; elke stap heeft een verwacht
resultaat.

## 0. Voorwaarden

```bash
cd ../jphoenix-emulator-port && make compile && make verify   # 30 tests groen
cd ../c-phoenix && make                                       # schone build
```

- **Na élke wijziging aan jphoenix: herbouwen én de referentie-dumps
  opnieuw genereren.** Vergelijken tegen een verouderde dump geeft
  schijn-regressies.
- De poll-klok (`-Dphoenix.inputclock=poll`) is vereist voor élke
  scripted vergelijking. Zonder die vlag landen input-events op andere
  spelmomenten en is de vergelijking betekenisloos.

## 1. Snelle regressie (na elke spellogica-wijziging, ~2 min)

De passieve attract-cyclus, byte-voor-byte:

```bash
cd ../jphoenix-emulator-port
printf '# leeg\n' > /tmp/passive.txt
java -Dphoenix.ramdump=/tmp/jphx_passive.bin -Dphoenix.ramdump.frames=3600 \
     -cp build/classes PhoenixCoverageRunner /tmp/passive.txt /tmp/cov 3600
cd ../c-phoenix
./c-phoenix --run-frames=3610 --ram-dump=/tmp/port_passive.bin
python3 tools/compare_ram_dumps.py /tmp/jphx_passive.bin /tmp/port_passive.bin \
    --align-c98 --stop-after 999999 --regions 4000-4BE5 | grep -c "^Frame-paar"
```

**Verwacht: ~7** afwijkende frame-paren (losse één-frame scherm-blips,
de gedocumenteerde dump-moment-ruisklasse). Meer, of áánhoudende
divergentie = regressie. Altijd `--stop-after 999999` (de default 5
stopt op boot-ruis en mist alles daarna).

## 2. Volledige batchverificatie (na grotere wijzigingen, ~2 uur)

```bash
python3 tools/lockstep/run_batch.py      # alle scripts, resultaten in results.jsonl
```

De batch herstart automatisch waar hij bleef (reeds aanwezige regels in
results.jsonl worden overgeslagen) — na een codewijziging dus eerst
results.jsonl weggooien/hernoemen, anders vergelijk je tegen runs van
een oude binary (dit beet ons ook).

**Verwacht:** (vrijwel) alle scripts `clean=True`. De clean-definitie:
- **Spelstaat** ($4340-$47FF + $4B40-$4BE5) byte-exact over de hele
  run. Toegestane uitzonderingen: het game-start-init-venster
  (records 40-60, meervblank-init-dumpmoment) en losse **1-record**
  zelfherstellende blips (teller-resets die net voor/na het dumpmoment
  vallen). **≥2 aaneengesloten afwijkende records = echte bug.**
- **Scherm** (fore $4000-$433F + background $4800-$4B3F) mag alleen
  zelfherstellende blips ≤8 records tonen.
- Uitgesloten ruis: $4388-$438D (jphoenix laadt hiscore.sav),
  scherm-mirrors $4161/$4181, en alles boven $4BE5 (Z80-stackresidu).

## 3. Aggregatie naar functie-verificatie

```bash
python3 tools/lockstep/aggregate.py      # -> context/mapping/lockstep_verified.json
python3 tools/generate_mappings.py       # Status-kolom bijwerken
python3 tools/generate_annotated_asm.py
```

Een functie geldt als **grond-waarheid-geverifieerd** wanneer ≥95% van
zijn instructie-adressen (opcode-fetches; operand-bytes tellen niet) is
uitgevoerd door jphoenix binnen minimaal één clean run. "Gedeeltelijk"
is meestal verklaarbaar (ongebruikte dispatch-takken, DSW-varianten, de
anti-piracy-tak die op een originele ROM nooit vuurt) — controleer de
lijst, maar verwacht daar geen bugs.

## 4. Bug-jacht: een dirty script onderzoeken

Dit is de methode die alle 13 vangsten opleverde:

1. **Dump beide sporen** van het dirty script (frames ruim boven het
   eerste divergentie-record uit results.jsonl):
   `tools/lockstep/dump_pair.sh context/input-scripts/<script>.txt <frames> <naam>`
2. **Vind het eerste afwijkende record** en druk de afwijkende bytes af
   (RAM-offset = adres − $4000). Het `first_state_divergence`-veld in
   results.jsonl geeft het startpunt al.
3. **Diff de frame-overgang**: vergelijk wat ref én port elk schreven
   van record N−1 naar N. Meestal is álles identiek op één write na —
   dat verschil benoemt de schuldige routine vrijwel direct
   (RAMUse.md geeft de veldbetekenis, de mapping-tabel de functie).
4. **Leg asm naast C**: zoek de schrijver in context/code-annotated.asm
   (let op de zes `JP (HL)`-jumptabellen; een grep op `CALL $XXXX`
   mist die) en vergelijk instructie voor instructie met de C-vertaling.
   De klassiekers tot nu toe: RLCA/RRCA als shift i.p.v. rotate,
   flank- vs niveau-input ($00BB is een flankdetector!), verwisselde
   bron/bestemming-parameters, ontbrekende staart-JP's, niet-ASM
   guards, en "verzonnen" herschrijvingen — check bij twijfel of een
   functie überhaupt op de asm lijkt.
5. **Fix, herbouw, herdraai hetzelfde script** en bevestig dat het
   eerste divergentie-record opschuift of verdwijnt. Divergentie die
   opschuift = er zit nóg een fout in dezelfde fase; herhaal.
6. **Sluit af met stap 1** (passieve regressie) om te bevestigen dat de
   fix niets anders raakt, en werk zo nodig de publieke status bij.

## 5. Bewijsmateriaal

Na een geslaagde batch horen `results.jsonl` en de `pc-coverage/`-CSV's
gearchiveerd te worden onder `context/verification/<datum>/`, zodat de
claim "geverifieerd" altijd herleidbaar blijft tot de run die hem
onderbouwde. De RAM-dumps zelf zijn wegwerp (reproduceerbaar uit
script + emulator-revisies); leg wél de git-revisies van c-phoenix en
jphoenix-emulator-port vast in de archiefmap.
