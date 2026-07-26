# Werkinstructie: visuele objecttracer

Deze werkinstructie beschrijft hoe je een Phoenix RAM-dump omzet in een
interactieve HTML-weergave van objectposities. Gebruik de tracer om beweging,
objectstatus en object-voor-object afwijkingen tussen jphoenix en C-Phoenix te
onderzoeken. Hij is geen pixelscreenshot en vervangt geen RAM-vergelijking.

## Uitgangspunten

- Werk vanuit de repository-root (`c-phoenix`).
- Een dump bevat per record een 4-byte framenummer gevolgd door RAM
  `$4000-$4BFF`.
- De getoonde positie komt rechtstreeks uit de RAM-velden van het gekozen
  object. Als die ontbreken, gebruikt de tracer het bewaarde
  screen-RAM-adres als anker.
- Voor vogels is het screen-RAM-adres het primaire visuele anker: de
  ASM-routine `DrawBirdObject` leest dit uit `$4B71/$4B72` (per slot). De
  ruwe vogelgridvelden blijven in de details zichtbaar, maar kunnen bij een
  faseovergang veranderen zonder dat de getekende vogel teleporteert.
- De vogelcategorie is een ROM-fase: `plain_bird` voor type `1..A`, `egg` voor
  `B..D` en `grown_bird` voor `E..F`. `plain_bird` zegt dus niet dat de sprite
  visueel klein is; de typecode en het bijbehorende shape-profiel bepalen de
  zichtbare vorm.
  Valt dit draw-adres buiten `$4000-$433F` of `$4800-$4B3F`, dan tekent de
  viewer geen marker: de vogel is logisch nog actief maar al buiten beeld.
- De fysieke Phoenix-monitor is 208x256 pixels. Het schermgeheugen is
  gedraaid: `+1` gaat een rij omlaag en `+32` een kolom naar links. De viewer
  volgt deze fysieke oriëntatie, niet de liggende RAM-volgorde.

## Voorbereiden

Voor een nieuw scenario kun je de opname en vervolgketen combineren:

```bash
make recordtracerun RECORD_NAME=bird-investigation
```

Speel de sessie en sluit het spelvenster. Vervolgens gebruikt Make
`/tmp/bird-investigation.txt` als invoer voor de jphoenix- en C-Phoenix-replay,
de RAM-vergelijking en de visual tracer. De replay loopt standaard 400 frames
door na het laatste opgenomen invoerevent en vergelijkt de gehele run. Gebruik
`RECORD_TRACE_FRAMES`, `RECORD_TRACE_TAIL_FRAMES` en
`RECORD_TRACE_STOP_AFTER` om dat te wijzigen.
Wanneer een emulator-dump faalt, toont de keten de laatste regels van het
betreffende log en bewaart zij het volledige log in
`/tmp/<RECORD_NAME>-jphoenix.log` of `/tmp/<RECORD_NAME>-c-phoenix.log`.

Voor een volledige keten - jphoenix- en C-Phoenix-dump, RAM-vergelijking en
HTML-tracer - is er een Make-doel. Dit gebruikt `comparerun` als onderlaag en
genereert vervolgens de tracer uit precies die twee dumps:

```bash
make tracerun \
  COMPARE_SCRIPT=context/input-scripts/two_player_last_grown_bird.txt \
  COMPARE_FRAMES=9000 \
  COMPARE_NAME=last-grown-bird \
  COMPARE_STOP_AFTER=999999
```

De HTML komt standaard in `/tmp/last-grown-bird-diff.html`. De relevante
instellingen zijn `VISUAL_TRACE_OUTPUT`, `VISUAL_TRACE_PLAYER` (standaard `1`),
`VISUAL_TRACE_KIND` (standaard `auto`) en `VISUAL_TRACE_EXTRA_ARGS`.

Maak eerst een C-Phoenix RAM-dump met een deterministische replay:

```bash
make replayrun \
  REPLAY_SCRIPT=context/input-scripts/two_player_last_grown_bird.txt \
  REPLAY_FRAMES=9000 \
  REPLAY_RAM_DUMP=/tmp/c-last-grown-bird.bin
```

Gebruik voor een vergelijking daarnaast de RAM-dump uit de identieke
jphoenix-replay. De tracer vergelijkt recordvolgorde, niet alleen gelijke
framenummers; zorg daarom dat beide runs dezelfde replay en dumpcadans hebben.

## Eén dump bekijken

Genereer voor een opname met meerdere levels standaard een automatische tracer:

```bash
python3 tools/view_sprite_trace.py /tmp/c-last-grown-bird.bin \
  --player 1 \
  --output=/tmp/phoenix-trace.html
```

De standaardmodus `auto` decodeert per frame de actieve overlay: zestien
alienrecords tijdens alienfases en acht vogelrecords tijdens vogelfases. Het
spelersschip blijft als referentieobject beschikbaar.

Gebruik een expliciete vogeltracer alleen voor een gerichte vogelanalyse:

```bash
python3 tools/view_sprite_trace.py /tmp/c-last-grown-bird.bin \
  --kind birds \
  --include-kind player_ship \
  --player 1 \
  --output=/tmp/bird-trace.html
```

Gebruik de standaard lokale viewer-target:

```bash
make tracer-view-only TRACE_VIEW_OUTPUT=/tmp/bird-trace.html
```

Open de door Make gemelde URL (standaardpoort `8766`). Stop de server met
`Ctrl-C` in dezelfde terminal.

## Twee dumps vergelijken

Gebruik `--compare` voor jphoenix tegenover C-Phoenix. `--include-kind` mag
worden herhaald wanneer meerdere contextobjecten nodig zijn.

```bash
python3 tools/view_sprite_trace.py /tmp/j-last-grown-bird.bin \
  --compare /tmp/c-last-grown-bird.bin \
  --reference-label jphoenix \
  --port-label c-phoenix \
  --kind birds \
  --include-kind player_ship \
  --player 1 \
  --output=/tmp/bird-diff.html
```

De objectfamilie bij `--kind` bepaalt een gericht onderzoeksonderwerp.
Zonder vlag kiest de viewer `auto` en volgt hij de alien-/vogeloverlay per
frame. `--kind all` voegt ook alle overige positioneerbare families toe.
`--include-kind player_ship` voegt het schip toe zonder de acht vogel-slots te
vervangen. Beschikbare families zijn: `player_ship`, `player_bullet`,
`above_player_bullet`, `enemy_bullet`, `aliens` en `birds`.

## Bediening en lezing

- **Player** kiest de RAM-bank van speler 1 of 2.
- **Visible objects** bevat een schakelaar voor **all objects** en een aparte
  schakelaar per slot. Daardoor kun je bijvoorbeeld vogel 3 en het
  spelersschip laten staan terwijl de overige vogelpaden verborgen zijn.
- Beweeg over een actuele zichtbare marker om altijd het object-ID en de
  beschikbare coördinaten te zien, bijvoorbeeld
  `#bird-3 V(4,130) A(4,116) G(33,8)`.
- **Show selected object label** toont deze tekst ook permanent naast de
  marker van het expliciet geselecteerde slot. Dit staat standaard uit; de
  marker zelf blijft wel oplichten.
  **Show coordinates on grid** schrijft die coördinaten ook permanent bij de
  actuele markers: `V` is de fysieke scroll-gecorrigeerde drawpositie, `A`
  is het ongescrollde screen-RAM anker en `G` zijn de ruwe vogelbytes.
- **Show raw grid trace** staat standaard uit en toont voor vogels op verzoek
  het gestippelde spoor uit de ruwe gridvelden `$4B75/$4B77`. Het solide spoor
  blijft de fysieke drawpositie; vergelijk beide om logische vluchtsturing en
  zichtbare tilepositie naast elkaar te zien.
- **Show inactive traces** staat standaard uit. Een slot waarvan de status in
  de gekozen frame inactief is, toont dan geen oud pad meer. Schakel dit in
  om de laatste bekende historie van uitgeschakelde slots toch te vergelijken.
  Op het exacte overgangsframe van een alien of vogel van actief naar off
  toont het grid een rode concentrische puls op de laatste zichtbare positie,
  ook wanneer inactieve sporen verborgen zijn.
- De objectlijst staat bij voldoende breedte in twee kolommen; de acht
  vogel-slots zijn daardoor tegelijk zichtbaar. Klik een objectregel om de
  details ervan te selecteren, zonder de zichtbaarheid te wijzigen. Elke
  objectregel heeft een vaste kleurswatch die overeenkomt met de marker en
  het spoor op het grid. Selecteer een regel of hover een gridmarker om de
  koppeling extra te benadrukken.
  Een expliciet geselecteerd slot houdt ook zijn objectlabel zichtbaar op het
  grid; de initiële standaardselectie doet dat niet. Een klik op een slotregel
  of slotkaart stopt afspelen, zet de selectie vast en markeert beide
  selectievlakken.
- De frame-overview direct onder de schuif toont level, ronde en gamestate van
  de gekozen frame, inclusief de gedecodeerde betekenis en de globale
  scrollwaarde. De schuif en afspeelknop lopen door de gedumpte records.
  Afspelen volgt de normale gamecadans van 60 records per seconde; bij een
  zware trace slaat de viewer tussengelegen frames over om die cadans te
  behouden.
  De knoppen direct naast afspelen gaan precies één record terug of vooruit
  en stoppen afspelen. Houd een van deze knoppen ingedrukt voor een langzame
  herhaling tot je loslaat.
- **Previous level** en **Next level** springen naar het begin van het vorige
  of volgende aaneengesloten `round + level`-segment. Sporen beginnen
  standaard opnieuw bij het begin van het huidige segment. Schakel
  **show previous level traces** in om de volledige historie over eerdere
  levels te tonen.
- Het detailpaneel toont ook **level** (lage nibble) en **round** (hoge
  nibble) van `LevelAndRound` (`$43B8`), plus de ruwe **game state** uit
  `$43A4` voor de gekozen frame.
- Onder het grid staat per objectslot de RAM-structuur van de gekozen frame.
  Voor vogels bevat die de shape-index, het draw screen-RAM-adres,
  shape-table-offset, timer, grid X/Y en bewegingsfase. Deze waarden zijn
  ruwe trace-informatie; de draw screen anchor is de visuele positie.
- Het volledige historische pad blijft als zichtbaar basis-spoor staan. De
  laatste 90 records krijgen daarboven een aflopende trail: de kop is helder,
  oudere recente segmenten vervagen zonder volledig te verdwijnen.
- Gekleurde lijnen tonen het voorafgaande pad van actieve objecten; de grotere
  marker is de geselecteerde frame.
- Rode markeringen en de **Next diff**/**Previous diff**-knoppen horen bij
  velddifferences tussen objectrecords die in beide dumps bestaan. Zonder
  diff-frames zijn deze knoppen bewust uitgeschakeld. De aparte teller
  **unmatched records** meldt alleen dat een dump langer is dan de andere;
  zulke staartrecords worden niet rood gemarkeerd en tellen niet mee als diff.
- Het detailpaneel toont de ruwe RAM-waarden, de gebruikte fysieke positie en
  de bronadressen. Gebruik die adressen samen met `context/RAMUse.md` en de
  ASM-annotaties om een semantische conclusie te onderbouwen.

## Level, round en gamestate

`LevelAndRound` op `$43B8` bestaat uit twee onafhankelijke nibbles:

| Lage nibble: level | Betekenis tijdens gamestate `$03` |
| --- | --- |
| `0`, `2` | alien fade-in |
| `1`, `3` | actieve aliengolf |
| `4`, `6`, `8` | overgang met spiral fill |
| `5`, `7` | actieve vogelgolf |
| `9` | mothership fade-in |
| `A` | mothership en aliens fade-in |
| `B` | mothership-escorte met aliens |

De hoge nibble is **round**. Die is `0` in de eerste volledige spelcyclus.
Na de vernietiging en scoreweergave van het mothership zet de ROM de lage
nibble terug op `0` en verhoogt hij de hoge nibble met `1`. Round is dus geen
vogelronde en ook geen individuele golf.

`GameState` op `$43A4` bepaalt welke hoofdroutine iedere frame uitvoert:
`$00` nieuw spel, `$01` score knippert, `$02` levelinitialisatie, `$03` normale
gameplay, `$04` spelerexplosie, `$05` GAME OVER, `$06` mothershipexplosie en
`$07` mothershipscore.

Bij `level 1`, `round 0`, `game state $03` draait de actieve **aliengolf**.
Daar zijn geen vogelobjecten te verwachten; vogels worden pas bij level `5`
en `7` verwerkt.

Voor vogels is `A` het screen-RAM anker uit `$4B71/$4B72` dat
`DrawBirdObject` gebruikt om tiles te schrijven. De fysieke `V`-positie telt
daarop de achtergrondscroll toe volgens de renderer: `V.y = (A.y -
CounterB9) mod 256`, met `CounterB9` op `$43B9` dat de ROM naar `$5800`
schrijft. Daardoor verandert `V`-Y nu wel als de vogel-laag verticaal
beweegt. `V` blijft een drawpositie, geen centrum van de mogelijk meertegels
grote vogelvorm.

## Grenzen

- De tracer tekent punten en paden, geen Phoenix-sprites of tilelagen.
- Alleen objectfamilies met expliciete X/Y-velden of een screen-RAM-adres zijn
  geschikt voor deze viewer. Mothership- en schildstatus vragen een andere
  analysevorm.
- Een gelijk pad bewijst alleen dat de geëxtraheerde objectvelden gelijk zijn.
  Controleer RAM-parity en de semantische lockstep-laag voor een bredere
  conclusie.

## Controle na wijziging

```bash
python3 -m unittest discover tests
git diff --check
```

Bij wijzigingen aan de extractor of viewer: genereer de bedoelde HTML opnieuw
en controleer minimaal één actief object op het canvas, de objectlijst en de
diffnavigatie.
