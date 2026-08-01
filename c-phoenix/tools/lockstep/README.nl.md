# Scripted-lockstep-batchverificatie

Engelse documentatie: [README.md](README.md).

## Wat deze batch doet, in één plaat

![Hoe lockstep-verificatie werkt: dezelfde opgenomen invoer stuurt zowel de originele ROM uit 1980 als de C-poort aan, en hun spelgeheugen wordt na elk afzonderlijk frame byte voor byte vergeleken](../../../demo/lockstep-explained.nl.svg)

Deze map automatiseert die vergelijking voor álle opgenomen scenario's
tegelijk, in plaats van één voor één.

## Draaien

Draait elk input-script uit `context/input-scripts/` inclusief `generated/`
door zowel jphoenix met de opt-in poll-klok (`-Dphoenix.inputclock=poll`) als
c-phoenix, en vergelijkt de RAM-dumps record-voor-record.

Vereist: `../jphoenix-emulator-port` gebouwd (`make compile`) en een gebouwde
`./build/c-phoenix`.

```bash
# Volledige batch, ongeveer twee uur. RAM-dumps worden per script weggegooid:
python3 tools/lockstep/run_batch.py          # schrijft results.jsonl en
                                             # pc-coverage/ naast het script

# Aggregatie naar het repo-artefact:
python3 tools/lockstep/aggregate.py          # schrijft context/mapping/lockstep_verified.json
python3 tools/generate_mappings.py           # werkt de statuskolom bij

# Eén script handmatig dumpen voor divergentie-onderzoek:
tools/lockstep/dump_pair.sh context/input-scripts/<script>.txt <loopframes> <naam>
# -> /tmp/ref_<naam>.bin en /tmp/port_<naam>.bin
```

Criterium "clean": spelstaat (`$4340-$47FF` plus `$4B40-$4BE5`, exclusief
hi-score-ruis op `$4388-$438D`) is byte-exact over de hele run, met als enige
uitzonderingen het game-start-init-venster (records 40-60) en losse
1-record zelfherstellende reset-grens-blips. Scherm-RAM, foreground en
background, mag hooguit zelfherstellende blips van acht records of minder
hebben. De machineleesbare bron staat in `criteria.py`; de herhaalbare
workflow staat in `PROCEDURE.md`.

## Semantische analyse

Voor onderzoek naar de betekenis van een RAM-veld of routine: maak eerst een
dumppaar, kies vervolgens het relevante record en schrijf alleen de kleine
RAM-overgang weg:

```bash
tools/lockstep/dump_pair.sh context/input-scripts/<script>.txt <frames> <naam>
python3 tools/lockstep/semantic_delta.py /tmp/ref_<naam>.bin /tmp/port_<naam>.bin \
  --record <record> --window 1 --regions 43A0-43C7 \
  --output-json=/tmp/<naam>.json --output-md=/tmp/<naam>.md
```

De uitvoer toont per record de mutaties in referentie en port, plus de
overgebleven parity-diffs. Leg een conclusie vast met
[`context/traces/semantic-case-template.nl.md`](../../context/traces/semantic-case-template.nl.md).
De extractor bewijst welke bytes veranderen; toeschrijving aan een schrijver
blijft een handmatige ASM/C-analyse totdat er gerichte write-level tracing is.
Zie [semantic-lockstep-howto.nl.md](../../context/traces/semantic-lockstep-howto.nl.md)
voor de volledige werkwijze en een uitgewerkte 2-player-vogelcase.

Paden zijn standaard relatief: `CPHX` wijst naar deze repo en `JPHX` naar
`../jphoenix-emulator-port`. Override indien nodig:

```bash
CPHX=/path/to/c-phoenix JPHX=/path/to/jphoenix-emulator-port \
  python3 tools/lockstep/run_batch.py
```
