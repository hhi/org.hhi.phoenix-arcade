# Voorstel: historische anomalieen opruimen

Datum: 11 juli 2026

Doel: geen gameplay wijzigen, alleen historische ruis in namen, bestanden en
mapping-documentatie verminderen. Elke stap moet byte-/framegedrag behouden en
na afloop met build plus bestaande lockstep/scripted checks worden gevalideerd.

## Aanleiding

`unknown_birds.c` is geen inhoudelijk "unknown" bestand meer. De routines zijn
inmiddels grotendeels benoemd, aan ASM-adressen gekoppeld en volgens `context/STATUS.nl.md`
regel-voor-regel gecontroleerd. De naam stamt uit een eerdere fase waarin dit
blok nog een verdachte/restvertaling was.

Dit patroon komt vaker voor: namen of bestanden dragen nog de geschiedenis van
de port, terwijl de huidige inhoud al veel concreter is.

## Gevonden anomalieen

### 1. `unknown_birds.c`

Status: hoge prioriteit voor hernoemen.

Huidige inhoud:
- per-vogel gedrag via `update_bird_behavior()`;
- vliegfasen, climb/descent/aim/grow-transforms;
- update van vogels 0-3 en 4-7;
- gedeelde vogelvluchtparameters;
- vogel-duikbomselectie;
- formatie-vs-speler botsing.

Voorstel:
- hernoem naar `bird_wave_behavior.c` of `bird_behavior.c`;
- voorkeur: `bird_wave_behavior.c`, omdat `bird_logic.c` al de top-level
  `process_birds()`-dispatch bevat;
- laat de interne `lNNNN_...` namen voorlopig staan waar ze nuttig zijn als
  ASM-anker, maar geef elke extern zichtbare functie een semantische naam.

Impact:
- Makefile gebruikt `$(wildcard *.c)`, dus bestandshernoem is build-technisch
  eenvoudig;
- includes/externs en documentatieverwijzingen moeten wel worden bijgewerkt;
- `context/code-annotated.md`, `context/STATUS.nl.md` en mapping-output bevatten links
  naar de oude bestandsnaam.

### 2. `generated_stubs.c`

Status: hoogste historische ruis.

De bestandsnaam suggereert "alleen generated stubs", maar het bestand bevat
inmiddels echte, live vertalingen:
- `l1df0()` anti-piracy check;
- de volledige sound-effect dispatcherketen `L3A10-L3B5B`;
- daarnaast nog bewuste no-op compatibility stubs zoals `l00b6()` en
  `l14e0()`.

Voorstel:
- splits dit bestand in twee bestanden:
  - `sound_dispatcher.c` voor `L3A10-L3B5B`, inclusief `l23d6`, `l27bd` en
    de `l3a..`/`l3b..` helpers;
  - `rom_compat_stubs.c` of `legacy_rom_helpers.c` voor bewuste no-op stubs
    en kleine ROM-helpervertalingen zoals `l1df0()`.
- verwijder de term "generated" uit live codepaden, tenzij het bestand echt
  opnieuw gegenereerd wordt.

Impact:
- laag qua runtime, maar hoog qua documentatie/mapping;
- `scoring.c` roept `l3a10()` aan en moet niet inhoudelijk veranderen;
- na split opnieuw `tools/generate_mappings.py` draaien.

### 3. Verouderde mapping-output

Status: opruimen na bestandshernoems.

`context/mapping/c_functions_by_address.md` bevat nog verwijzingen naar
verwijderde of dode duplicaat-stubs, bijvoorbeeld oude regels rond `l3452`,
`l37b0`, `l3800`, `l3980` en meerdere "Unknown / None" records voor functies
die in comments wel degelijk een ASM-range hebben.

Voorstel:
- mapping pas regenereren nadat de bronbestanden opgeschoond zijn;
- daarna expliciet controleren op:
  - "Dode duplicaat" regels die niet meer bestaan in de bron;
  - "Unknown / None" voor functies met `[ASM: ...]` comments;
  - verzamelstub-artefacten die ontstaan door losse `[ASM:]` notities zonder
    functiedefinitie.

Impact:
- alleen documentatie/tooling;
- goed moment om de generator robuuster te maken tegen losse ASM-notities.

### 4. Address-only functienamen die semantiek al hebben

Status: gefaseerd aanpakken, niet massaal.

Er zijn nog veel `lNNNN` functies. Dat is niet automatisch fout: bij een
ASM-port is het soms juist handig om het adres zichtbaar te houden. Maar bij
extern zichtbare of domeinlogica-functies met duidelijke betekenis is alleen
een adresnaam onnodige historische ballast.

Kandidaten:
- `alien_wave.c`: `l2130`, `l2146`, `l2150` t/m `l21a5`, `l21ba`, `l2204`,
  `l24c4`, `l3000`;
- `generated_stubs.c`: sound helpers `l3a10`, `l3b43`, `l3ad0`, etc.;
- `birds_vertical_movement.c`: `l2668`, `l26aa`, `l26d0`;
- `utilities.c`: `l25b7`, `l34de`;
- `misc_logic.c`: `l24a0`, `l24f2`, `l32b0`;
- `player_explosion.c`: `l211c`, `l20e8`, `l2070`;
- `state_endings.c`: `l0b15`, `l0ba0`, `l0bba`.

Voorstel:
- niet overal blind hernoemen;
- prioriteit geven aan extern aangeroepen functies en functies die in
  callgraphs/documentatie als publieke knooppunten verschijnen;
- stijl: `semantic_name()` met ASM-adres in comment, of bij twijfel
  `lNNNN_semantic_name()` zoals nu al deels gebeurt.

### 5. Dubbele of overlappende historische helpers

Status: eerst onderzoeken, dan pas wijzigen.

Er zijn op het eerste gezicht dubbele namen/rollen rond mothership/spiral-code:
- `state_play.c` heeft statische `l2260_spiral_draw()` en
  `l2292_spiral_routine()`;
- `mothership_impl.c` heeft eveneens `l2260_spiral_draw()` en
  `l2292_spiral_routine()` als globale functies.

Dit kan bewust zijn door verschillende callsites of zichtbaarheid, maar het is
een klassieke plek waar historische duplicatie kan blijven liggen.

Voorstel:
- eerst callsites en ASM-ranges vergelijken;
- alleen samenvoegen als de twee implementaties aantoonbaar hetzelfde bereik
  en dezelfde state-mutaties hebben;
- anders expliciet documenteren waarom beide bestaan.

## Aanpak

1. Maak eerst alleen een rename/split branch zonder gedragswijzigingen.
2. Begin met `unknown_birds.c` -> `bird_wave_behavior.c`.
3. Splits daarna `generated_stubs.c`.
4. Update alle documentatielinks en comments die naar oude bestandsnamen
   verwijzen.
5. Regenereer mapping/callgraph-output pas aan het einde.
6. Valideer met:
   - `make clean && make`;
   - bestaande unittest-set;
   - korte scripted playthrough;
   - lockstep tegen bekende referentie waar beschikbaar.

## Niet doen in deze cleanup

- Geen Z80-gedrag "mooier" maken.
- Geen tabellen interpreteren of herstructureren zonder tracebewijs.
- Geen massale hernoemactie van alle `lNNNN` functies in een keer.
- Geen dode code verwijderen zonder eerst callgraph plus ASM-range te
  controleren.

## Uitvoering (11 juli 2026)

- Hernoemd naar `bird_wave_behavior.c`.
- `generated_stubs.c` gesplitst in `sound_dispatcher.c` en
  `rom_compat_stubs.c`.
- Mapping-generator aangepast voor ingesprongen functiedefinities en
  ontbrekende ASM-ankers toegevoegd aan de verplaatste interne helpers.
- Spiral-dubbels bleken al eerder verwijderd; geen codewijziging nodig.

## Conclusie

Ja, er zijn meerdere historische anomalieen. De belangrijkste zijn
`unknown_birds.c` en `generated_stubs.c`: beide bestandsnamen vertellen vooral
iets over een oude portingfase, niet meer over de huidige inhoud. Daarna komt
de mapping-output, die door oude stub-artefacten en losse ASM-notities nog
vervuilde conclusies kan tonen.
