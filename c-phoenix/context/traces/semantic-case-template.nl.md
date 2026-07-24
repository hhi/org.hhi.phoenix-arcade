# Semantische tracecase: template

Gebruik deze template wanneer een lockstep-onderzoek de betekenis van een
RAM-veld, bit, routine of overgang onderbouwt. Een case documenteert bewijs;
hij is geen vervanging voor de geannoteerde ASM als bron van waarheid.

````md
# CASE-<KORTE-NAAM>

## Vraag

Welke betekenis of invariant wordt onderzocht?

## Hypothese

Formuleer een toetsbare hypothese. Noem alternatieve verklaringen wanneer die
nog bestaan.

## Scenario

- Inputscript: `context/input-scripts/<naam>.txt`
- Target-window: record `N..M`
- Relevante RAM: `$....`, `$....`
- Verwachte states/level/player-bank: ...

## Reproductie

```bash
tools/lockstep/dump_pair.sh context/input-scripts/<naam>.txt <frames> <naam>
python3 tools/lockstep/semantic_delta.py \
  /tmp/ref_<naam>.bin /tmp/port_<naam>.bin \
  --record <N> --window 1 --regions <bereiken> \
  --output-json=/tmp/<naam>.json --output-md=/tmp/<naam>.md
```

## Statisch bewijs

- ASM: `$....-$....`; relevante instructies en branches.
- RAMUse: velden/adressen.
- C: functie(s) en bestaande `[ASM: ...]`-ankers.

## Dynamisch bewijs

Beschrijf alleen de waargenomen mutaties uit het deltavenster: welke waarde
verandert op welk record, welke parity-diffs zijn er, en welke run is clean.

## Conclusie

De bevestigde betekenis, inclusief de grenzen ervan.

## Betrouwbaarheid

`hoog`, `middel` of `laag`, met een korte reden. Een clean lockstep-run
bevestigt gedrag, maar geeft niet zelfstandig een betekenis aan een naamloos
veld.
````

Bewaar alleen de ingevulde Markdown-case en eventueel kleine JSON-uittreksels
in Git. Laat RAM-dumps en HTML-viewers in `/tmp` staan, behalve wanneer een
tracecase ze expliciet als compacte en noodzakelijke regressiefixture
rechtvaardigt.
