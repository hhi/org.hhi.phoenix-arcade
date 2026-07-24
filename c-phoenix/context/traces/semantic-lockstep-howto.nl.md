# How-to: semantische lockstep-analyse

Deze how-to gebruikt lockstep om onderbouwd vast te leggen wat een RAM-veld,
bit, routine of overgang betekent. Hij vult de geannoteerde Z80-assembly aan;
bij conflict blijven [code-annotated.asm](../code-annotated.asm) en
[RAMUse.md](../RAMUse.md) de bron van waarheid.

## Doel

Gebruik deze workflow wanneer een naam, bitbetekenis of spelmechaniek nog niet
hard genoeg is om veilig in C te benoemen. Begin met een concrete, toetsbare
vraag. Kies vervolgens een klein RAM-venster rond een reproduceerbaar
spelmoment, in plaats van meteen een volledige batch te analyseren.

## Werkwijze

1. Formuleer een hypothese en mogelijke alternatieven.
2. Kies of maak een inputscript dat het relevante spelmoment bereikt.
3. Maak een jphoenix/C-Phoenix-dumppaar met de poll-klok.
4. Zoek het relevante record via `results.jsonl`, een bestaande trace of een
   objectviewer.
5. Extraheer alleen het kleine RAM-venster rond dat record.
6. Leg ASM, C-code en RAM-mutaties naast elkaar.
7. Schrijf de conclusie als gecureerde semantic case met het
   [template](semantic-case-template.nl.md).
8. Pas pas daarna een naam, commentaar of constant toe.

## Dumppaar maken

Bouw beide projecten. De jphoenix-poll-klok is essentieel: zonder die vlag
kunnen invoerevents op andere spelmomenten landen.

```bash
tools/lockstep/dump_pair.sh context/input-scripts/<script>.txt <frames> <naam>
```

Dit schrijft tijdelijke dumps naar `/tmp/ref_<naam>.bin` en
`/tmp/port_<naam>.bin`. Gebruik `/tmp` voor verkennend materiaal. Bewaar
RAM-dumps alleen in Git als zij een noodzakelijke regressiefixture vormen.

## Een deltavenster extraheren

Geef het doelrecord, meestal een venster van een record ervoor en erna, en
alleen de relevante RAM-adressen op:

```bash
python3 tools/lockstep/semantic_delta.py \
  /tmp/ref_<naam>.bin /tmp/port_<naam>.bin \
  --record <record> --window 1 --regions 43A0-43C7 \
  --output-json=/tmp/<naam>-delta.json \
  --output-md=/tmp/<naam>-delta.md
```

De uitvoer bevat per record:

- **Referentie-mutaties**: bytes die jphoenix sinds het vorige record wijzigde.
- **Port-mutaties**: dezelfde overgang in de C-poort.
- **Parity-diffs**: resterende verschillen tussen beide implementaties.

Een lege parity-diff-tabel bevestigt gelijk gedrag in de gekozen regio. Zij
geeft niet automatisch betekenis aan een anoniem veld. Onderbouw die met ASM,
RAMUse en de C-aanroepcontext.

## Bewijs combineren

| Bewijsvorm | Vraag |
| --- | --- |
| ASM | Welke instructies lezen, testen of schrijven de byte? |
| RAMUse | Welk adres of welke structuurruimte is betrokken? |
| C | Welke vertaalde functie correspondeert met de ASM-range? |
| Deltavenster | Welke verandering gebeurt op het relevante record? |
| Lockstep | Is die verandering in referentie en port identiek? |

Een clean deltavenster bewijst niet zelfstandig welke routine de byte schreef.
Directe toewijzingen aan `state` omzeilen vaak `mem_write`; een algemene
write-hook zou daarom onvolledig zijn. Koppel de mutatie voorlopig handmatig
aan de ASM/C-aanroepketen.

## Uitgewerkte case: 2-player laatste volgroeide vogel

Deze case gebruikt de bestaande fixture
[`context/input-scripts/two_player_last_grown_bird.txt`](../input-scripts/two_player_last_grown_bird.txt).
De bredere scenario- en objectinformatie staat in
[`context/traces/two_player_last_grown_bird_compare/README.nl.md`](two_player_last_grown_bird_compare/README.nl.md).

### Vraag

Werkt de delta-extractor op een echt, uitgelijnd 2-player-spelmoment en laat
hij begrijpelijke, gelijke RAM-overgangen zien?

### Scenario

- Targetrecord: `7000`.
- Referentieframe: `7521`; C-Phoenix-frame: `7001`.
- Analysevenster: records `6999..7001`.
- RAM-regio: `$43A0-$43C7`.
- Spelmoment: echte gameplay, player 1, `LevelAndRound = 0x05`,
  `BirdsLeft = 1`, een laatste volgroeide vogel.

De frameheaders verschillen, maar de record-index is in deze fixture het
bruikbare synchronisatiepunt.

### Commando

```bash
gzip -dc context/traces/two_player_last_grown_bird_compare/j-last-grown-bird.bin.gz > /tmp/j-last-grown-bird.bin
gzip -dc context/traces/two_player_last_grown_bird_compare/c-last-grown-bird.bin.gz > /tmp/c-last-grown-bird.bin
python3 tools/lockstep/semantic_delta.py \
  /tmp/j-last-grown-bird.bin \
  /tmp/c-last-grown-bird.bin \
  --record 7000 --window 1 --regions 43A0-43C7 \
  --output-json=/tmp/last-grown-bird-delta.json \
  --output-md=/tmp/last-grown-bird-delta.md
```

### Observatie

| Record | Gelijke mutaties |
| --- | --- |
| `6999` | `CounterB9: 0x7C -> 0x7D`, `PlayerShape: 0x00 -> 0x04`, `PlayerShipX: 0x4C -> 0x4D` |
| `7000` | `PlayerShape: 0x04 -> 0x08`, `PlayerShipX: 0x4D -> 0x4E` |
| `7001` | `CounterB9: 0x7D -> 0x7E`, `PlayerShape: 0x08 -> 0x0C`, `PlayerShipX: 0x4E -> 0x4F` |

Er zijn in `$43A0-$43C7` geen parity-diffs. De case bewijst dat de extractor
de relevante per-record mutaties leesbaar en gelijk voor beide implementaties
rapporteert. Hij doet geen uitspraak over de betekenis van `CounterB9` buiten
de bestaande ASM/RAM-documentatie.

## Verificatie van de semantische laag

Voor deze analyse- en documentatiewijziging zijn uitgevoerd:

```bash
python3 -m unittest discover tests
python3 -m py_compile \
  tools/lockstep/criteria.py \
  tools/lockstep/semantic_delta.py \
  tools/lockstep/run_batch.py \
  tools/lockstep/aggregate.py
git diff --check
```

De unittest-suite slaagt met zes tests. Python-compilatie en
`git diff --check` zijn schoon.

De volledige scripted lockstep-batch is niet opnieuw uitgevoerd: die duurt
ongeveer twee uur en deze wijziging raakt uitsluitend de analyse- en
documentatielaag, niet de gameplay, dumpindeling of vergelijkingsuitkomst.
Draai de batch wel opnieuw nadat spelgedrag, lockstep-criteria of
dumpvergelijkingslogica inhoudelijk verandert.

## Resultaat vastleggen

Maak na een echte semantische bevinding een nieuwe Markdown-case op basis van
[semantic-case-template.nl.md](semantic-case-template.nl.md). Bewaar vraag,
hypothese, target-window, exacte commando's, statisch bewijs, dynamische
observatie, conclusie en betrouwbaarheid. Voeg alleen kleine, leesbare
afgeleiden toe; de reproduceerbare bron blijft inputscript plus commando.
