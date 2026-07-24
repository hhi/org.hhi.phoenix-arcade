# Program-ROM-Tabelcatalogus

Engelse versie: [rom-table-catalog.md](rom-table-catalog.md). Machineleesbare
bron: [rom-table-catalog.json](rom-table-catalog.json).

## Reikwijdte

Dit is de werkinventaris voor program-ROM-data die C-Phoenix gebruikt. Hij
claimt niet dat alle `0x4000` bytes van de program-ROM al begrepen zijn. Hij
scheidt begrensde lookuptabellen van dynamische pointerpayloads en generieke
ROM-naar-RAM-kopieen.

De catalogus bevat nu **50 gecatalogiseerde regio's**, waarvan **alle 50
geëxtraheerd** zijn als benoemde C-data in `phoenix_tables.c`. **De bron
bevat nul directe `prg_mem`-reads en nul indirecte ROM-reads via
`mem_read()`, nergens meer in de codebase** (zie de
`draw_bird_shape_350c`-sectie verderop voor de laatste twee). De
geannoteerde ASM bevat 111 data-ankers, waarvan veel geen lookuptabel
zijn.

**Een volledige `T-label`-sweep (21 juli 2026) heeft alle 111 `Txxxx`-labels
in `code-annotated.asm` tegen de catalogus afgezet**, als aanvulling op de
tot dan toe gebruikte `prg_mem`-grep-methodiek (die structureel blind is
voor tabellen die nooit via een letterlijke `prg_mem[...]`-expressie
liepen). Resultaat: 97 labels al geëxtraheerd en correct aangesloten; 5 zijn
Z80-`JP (HL)`-jumptabellen (`T040E`, `T0735`, `T0759`, `T0814`, `T3018`)
terecht als C-`switch`-statements vertaald, geen data -- bewust buiten
scope; 2 (`T0560`, `T0B38`) waren al ROM-vrij maar leefden als lokale
`static const`-arrays rechtstreeks ingebakken in `state_init.c`/
`player_logic.c`, van vóór het `phoenix_tables.c`-patroon -- inmiddels
gecentraliseerd, zie de `T0560`/`T0B38`-sectie hieronder; en 4 (`T1800`,
`T1BA0`, `T1D00`, `T1F00`) waren echt nog niet-geëxtraheerde ROM-tabellen,
inmiddels allemaal opgelost (zie de secties hieronder). De sweep bevestigde ook een
echte dubbele vertaling van `InitGlobalLevelData` (`$0580`): zowel
`state_init.c` als `init_global_level_data.c` implementeren hem
onafhankelijk, beide worden echt aangeroepen, beide bevatten identieke
data -- vandaag geen bug, maar een niet-samengevoegd duplicaat dat later
ongemerkt kan uiteenlopen.

**Een vervolgende, volledige audit van alle 163 `mem_read()`-aanroepen in
de codebase (zelfde datum) vond een tweede, tot dan toe onzichtbaar
ROM-leespad.** `mem_read()` ([z80_core.h](../z80_core.h)) is de centrale
Z80-adresdecoder en valt voor elk adres `< 0x4000` transparant terug op
`prg_mem` -- code die daar ROM via leest duikt nooit op in een
`prg_mem[`-grep. Van de 163 aanroepplekken bleken alle op één functie na
puur op RAM-adressen te werken (struct-offsets, schermposities, allemaal
`>= 0x4000` door constructie); de ene uitzondering is
`utilities.c:print_text_lines()` (en zijn `draw_row()`-hulpfunctie),
aangeroepen vanuit 6 bestanden met vaste letterlijke ROM-adressen
(`0x1800`, `0x1960`, `0x19C0`, `0x1A00`, `0x1BA0`) -- exact `T1800` en
`T1BA0` uit de sweep hierboven, plus drie adressen (`0x1960`/`0x19C0`/
`0x1A00`) die toevallig binnen het al geëxtraheerde
`score-average-scroll-text-page`-bereik vallen zonder dat deze lezer die
array daadwerkelijk gebruikt.

Deze audit **loste ook `stars_scroll_down`'s eerder onopgeloste
RAM-pointer op** (`M43B2:M43B3`, in `RAMUse.md` gedocumenteerd als doel
"T1C00 of T1D00 of T1F00"): die wordt geschreven door
`init_global_level_data()`'s al geëxtraheerde 12-byte-kopie
(`level-data-page`), en het decoderen van de eigen bytes van die pagina op
offset 7:8 voor elk van de 4 bronblokken geeft exact `0x1C00`, `0x1C00`,
`0x1F00` en `0x1D00` -- een volledig statisch, bewijsbaar antwoord, geen
runtime-onzekerheid. `T1C00` is al geëxtraheerd; `T1D00` en `T1F00` zijn
de twee resterende stukken die nodig zijn om die read volledig op te
lossen. Zie `stars-scroll-down-target-tables` en
`attract-mode-text-tables` in de JSON `dynamic_or_payload_readers`/nieuwe
regio-entries voor detail. Geen van beide sweeps heeft code gewijzigd --
dit is puur inventarisatie.

Vier van die 28 regio's zijn toegevoegd na het decoderen van
`alien-closed-loop-pointers`' eigen payload (zie de noot bij die entry):
de dynamische-lezercategorie "alien-bewegingspatroon-dispatch" bleek een
echt begrensd tabelpaar te zijn (`alien-movement-pattern-cluster-a`/`-b`)
en is geëxtraheerd, niet alleen opnieuw gecatalogiseerd. Dat legde ook
een aparte, tot dan toe verkeerd meegetelde dynamische lezing in
`alien_logic.c:init_alien_positions` bloot (3 reads, ten onrechte bij de
patroon-dispatch-telling opgeteld), die ook bleek te extraheren
(`alien-position-layout-page`/`alien-position-pointer-table`) -- het
worst-case-bereik is via tijdelijke instrumentatie over vijf scripts
bevestigd exact op de paginagrens (`0x15FF`) uit te komen, zonder ooit
door te lopen in de naastgelegen `phoenix_alien_shape_offset_page`.
`alien_logic.c` heeft nu geen enkele directe `prg_mem`-read meer.

De categorie "wapen-botsing-patroon-lookup" bleek soortgelijk deels een
duplicaat: van de 4 reads hoort er maar 3 bij een echt nieuwe tabel
(`formation-hit-window`, `$1740-$175F`); de vierde
(`weapon_collision.c:l0c00_kill_score`) leest dezelfde
alien-bewegingspatroon-pointer die al gedekt wordt door
`alien-movement-pattern-cluster-a`/`-b`, bevestigd door zijn
indexrekenkunde te herleiden tot exact hetzelfde `$4B50-$4B6F`-
adresseringsschema dat elders al gebruikt wordt, en roept nu
`phoenix_alien_movement_byte()` aan in plaats van een tabel te
dupliceren. `weapon_collision.c` heeft nu geen enkele directe
`prg_mem`-read meer.

De bird-sound-cadence-entry is opgelost van `partial` naar `extracted`:
de index (`B4BD6`) wordt bij zijn enige schrijver gemaskeerd met `& 0x1F`
-- hetzelfde veld dat al gebruikt wordt om de geëxtraheerde
`phoenix_bird_descent_caps`-tabel te indexeren -- dus overschrijdt hij
nooit `0x1F`.

De entry mothership-and-player-explosion-pointers stond aanvankelijk
gecatalogiseerd als `$1B00-$1B5F`, wat zowel te breed was (`$1B00-$1B3F`
is ongerelateerde data die geen van beide lezers raakt) als te smal (de
index van de player-explosion-lezer reikt tot `$1B9F`). Het is nu
`$1B40-$1B9F`, opgelost van `partial` naar `extracted`.

De entries player-explosion-tiles en player-explosion-control stonden
aanvankelijk als twee losse, speler-only bereiken gecatalogiseerd. Hun
lezer, `l2085_particles`, blijkt gedeeld te worden met de
mothership-explosie (aangeroepen vanuit `state_endings.c` met basis
`$2A00`/`$2B00`, voorheen ongecatalogiseerd), en de loopindex over de
control-tabel is niet strak bewezen begrensd. De twee entries zijn
samengevoegd tot één pagina van 1024 bytes die beide varianten dekt;
zie het `note`-veld in de JSON voor detail.

De entries sprite-shape-offsets en alien-animation-descriptors stonden
aanvankelijk als twee losse, smalle bereiken gecatalogiseerd
(`$1600-$161F` en `$16A0-$16CF`). Beide waren veel te klein: de ASM toont
een dichte, ongelabelde "T1600"-megatabel die doorloopt tot `$169F`, en de
"T16A0"-tabel blijkt 32 entries van 3 bytes te zijn die doorloopt tot
`$16FF` -- bevestigd door de alien-closed-loop-patroontabellen
(`$1020-$13FF`) direct te inspecteren, waarvan de waarden (de index in
beide tabellen) nooit `0x1F` overschrijden. De twee entries zijn
samengevoegd tot één pagina van 256 bytes; zie het `note`-veld in de
JSON voor detail.

De bird-shape-pointers-entry stond aanvankelijk gecatalogiseerd als
`$3E08-$3E7F`. De index is voor realistische type/frame-waarden aantoonbaar
`>= 0x08`, maar `frame` is een onbegrensde RAM-byte, dus is de volledige
`$3E00-$3E7F`-pagina behouden (die overlapt met de al geëxtraheerde
`T3E00`-bullet-pixel-mask-bytes) in plaats van aan te nemen dat het smallere
bereik altijd standhoudt -- dezelfde redenering als bij de
bird-hit-mask-page-entry hierboven.

De bird-hitmask-regio stond aanvankelijk als twee losse 32-byte-bereiken
gecatalogiseerd. De index van `l3844_small_bird_hit` (`b + 0x60`) komt
nooit onder `0x3B60`: `b` zit in `[0, 0x4F]`, dus de index blijft binnen
`[0x3B60, 0x3BAF]`, altijd binnen de `T3B60`-datatabel -- daar is geen
wrap mogelijk. De index van `l38bc_large_hit` (`b + 0xB0`) wrapt wél onder
`0x60` voor `b` in `[0x50, 0x6F]` (grown-bird-tiles `0xE0-0xFF`), en
belandt dan in de codebytes vlak vóór `T3B60` (`0x3B00-0x3B5F`). Dit is
geen theoretisch randgeval: geïnstrumenteerd en gedraaid tegen
`bird-investigation.txt` (13.935 frames), vuurde de wrap **27 keer over 12
verschillende tile-waarden** (bijv. `tile=0xE3 -> index 0x03`,
`tile=0xE8 -> index 0x08`, `tile=0xF9 -> index 0x19`), middenin
`l3b02`'s functiebody (`$3B02-$3B19`) onder andere. De twee bereiken zijn
daarom samengevoegd tot één 256-byte pagina-entry om die bevestigde wrap
exact te bewaren; zie het `note`-veld in de JSON voor detail. Die
codebytes (`0x3B00-0x3B5F`) zijn niet ongeclassificeerd: het zijn de
opcodes voor `l3b02`/`l3b1b`/`l3b28`/`l3b33`/`l3b43`, die al als gewone
functies vertaald en aangeroepen worden in `sound_dispatcher.c`.
`phoenix_bird_hitmask_page` is een bewuste byte-voor-byte duplicaat van
diezelfde fysieke ROM-bytes voor hun losstaande, ongerelateerde gebruik
als inerte lookup-data op het wrap-pad hierboven -- de gecompileerde
objectbytes van een C-functie hebben geen enkele relatie met de
originele Z80-opcodes, dus alleen deze letterlijke kopie is geldig voor
het data-gebruik.

De eigen noot bij de entry alien-closed-loop-pointers (indexbegrenzing op
`0x30-0xF8` plus een randomoffset) klopte, maar was onvolledig: die
beschreef hoe de tabel wordt *geïndexeerd*, niet waar zijn *payload* naar
wijst. Het decoderen van de 104 MSB:LSB-paren in de tabel levert 34
unieke doeladressen op, waarvan er maar 18 in het `0x1020-0x13FF`-cluster
liggen dat de `owner`/`readers`-velden van deze entry suggereerden. De
overige 16 liggen in een tweede, fysiek gescheiden cluster van 1024
patroonlijst-bytes op `0x2C00-0x2FFF` -- dezelfde `0x00`-terminator/
`0xFF`-padding-structuur, dezelfde bewezen `<=0x1F`-waardebegrenzing,
bevestigd door directe byte-inspectie van elke non-`0xFF`-byte in dat
bereik. Twee verdere adressen in dat cluster (`0x2E00`, `0x2E40`) worden
alleen via een apart mechanisme bereikt (`alien_logic.c:l3028`, de
breakout-scheduler), niet via deze tabel. De patroonbytes van beide
clusters zijn inmiddels ook geëxtraheerd (zie
`alien-movement-pattern-cluster-a`/`-b` hieronder) -- `alien_logic.c`'s
`alien_movement_update` en `alien_animation_update` lezen ze via
`phoenix_alien_movement_byte()` in plaats van `prg_mem`.

Verificatienoot: tijdelijke hit-tel-instrumentatie (na gebruik weer
verwijderd) toonde dat de passieve run en `extended_playthrough.txt`
cluster B helemaal nooit raken (0 hits elk), ondanks dat beide
byte-identiek uitkwamen -- een byte-identieke dump bewijst op zichzelf
niet dat een codepad daadwerkelijk doorlopen is. `my_session.txt` (2286
hits) en `bird-investigation.txt` (3266 hits) zijn de scripts die cluster
B daadwerkelijk dekken; beide zijn daarom opgenomen in de evidence bij de
cluster-a/-b-entries hieronder.

Zes van de tien dynamische "attract-mode tekst/shapes"-reads zijn opgelost
in vier nieuwe tabellen. De drie `draw_n_by_2()`-aanroepen van
`draw_score_average_table_tiles()` hebben alle drie een vast
(niet-runtime-berekend) bronadres -- de signatuur van de hulpfunctie is
gewijzigd van `(hl, de, rows)` naar `(hl, const uint8_t *src, rows)` zodat
de letterlijke bytes als array meegegeven konden worden:
`score-average-table-tiles-a` (`$0A40-$0A4B`, gedeeld door aanroep 1 en 3)
en `score-average-table-tiles-b` (`$3C00-$3C0B`, aanroep 2). De index van
`draw_intro_bird_animation_frame` is een vrij lopende RAM-byte, die
legitiem alle 32 waarden in `[0x3A,0x59]` bestrijkt, niet alleen T233A's
eigen 23-byte bereik -- dezelfde "tabel-grenst-aan-code"-situatie als
bird-hit-mask-page, want bytes `$2351-$2359` zijn de opcodes voor
`mothership_impl.c:l2351_mothership_animation`; geëxtraheerd als
`intro-bird-animation-frames` (`$233A-$2359`, volledig bereik). De twee
reads van `slow_print_score_average_table` zijn geïndexeerd via
`Counter98`, een vrij lopende 16-bit-teller zonder wiskundige grens;
geëxtraheerd als `score-average-scroll-text-page` (`$1860-$1B5F`) nadat
tijdelijke hit-tel-instrumentatie op passieve runs van 3610, 30000 en
60000 frames liet zien dat het bereikte adres nooit boven `$1B3F` uitkomt,
bij elke lengte. De resterende vier reads (`drawNx2`'s eigen twee,
`draw_bird_shape_350c`'s twee) zijn gedeelde generieke hulpfuncties die
vanuit meerdere bestanden met zowel vaste als onbegrensde,
runtime-berekende adressen worden aangeroepen, en zijn niet op te lossen
via tabelextractie alleen -- zie Dynamische Data hieronder.

De inschatting hierboven dat `drawNx2` "genuinely unresolved" was, bleek
**onjuist** en is gecorrigeerd. Bij het opnieuw natrekken van zijn drie
enige echte aanroepplekken (alle in `alien_logic.c`) bleken ze stuk voor
stuk begrensd: twee geven een vast letterlijk adres mee (`$17D0`,
`$17D6`), en de derde leidt zijn adres af van de al geëxtraheerde
`phoenix_alien_explosion_frames` (5 mogelijke bytewaarden, OR'd met
`$1700`) -- geen onbegrensde runtime-waarde, gewoon een al geëxtraheerde
tabel die de vorige analyse niet ver genoeg had teruggevolgd.
Geëxtraheerd als `shield-and-drawnx2-shapes` (`$17B8-$17FF`), die ook
`player_logic.c:shields_expired`'s vaste aanroep dekt en één van
`player_explosion.c`'s waarden die van de mothership-pointer-tabel zijn
afgeleid.

Vrijwel de hele categorie "generieke ROM-naar-RAM/scherm-kopieerhulpen"
(22 van de 23 reads) bleek eveneens begrensd, zodra elke aanroepplek van
elke generieke hulpfunctie apart werd nagetrokken in plaats van de
categorie-brede omschrijving "adres is een parameter van de aanroeper"
te vertrouwen. Opvallende bevindingen: `utilities.c:draw_image_c_by_b`'s
5 aanroepplekken herleiden tot `shield-table`, `shield-and-drawnx2-
shapes`, drie waarden die al binnen `mothership-and-player-explosion-
pointers` liggen, `alien-wave-animation-shapes` en `starfield-page`;
`sprite_rendering.c`'s 4 reads delen één pagina (`sprite-character-
block-shapes`) waarvan het indexbereik empirisch is geverifieerd
(`$00-$DC` waargenomen, niet de 2-waardenset die de init-tabel alleen
zou suggereren); `init_global_level_data.c`'s tweetraps-pointerlookup
herleidt tot een uitputtende, statisch bekende set van 4 adressen,
rechtstreeks gedecodeerd uit de eigen ROM-bytes van de pointertabel; en
`misc_logic.c:l32b0`'s bereikbare bereik is bewijsbaar constant
ongeacht `BirdsLeft` (de `-8n`/`+8n`-termen in zijn adresrekenkunde
vallen exact tegen elkaar weg). Zie de nieuwe regio-entries hieronder
voor detail per geval.

Eén extractie in deze ronde introduceerde eerst een echte regressie, die
niet bij review maar door de standaard RAM-dump-lockstepcontrole werd
gevangen: een eerste versie van `add_planets_to_background`'s herbedrading
nam aan dat de bytes van de `T1E60`-subtabel rechtstreeks gebruikt
werden, terwijl ze in werkelijkheid een *index* zijn naar een nóg verder,
voorheen niet-geëxtraheerd bereik van 32 bytes (`$1E00-$1E1F`) via
`hl = 0x1E00 | T1E60_byte`. Het passieve script liep uiteen bij frame 580
(`BackgroundScreen`-bytes op `$4852`/`$4853`/`$4872`/`$4873`); het
extraheren van dat bereik als `planet-shape-page` en het herstellen van
de dispatch loste het op, bevestigd byte-identiek over alle 4
standaardscripts. Een goede herinnering dat "de eigen index van de lezer
is begrensd" en "de byte die de lezer teruggeeft IS het eindantwoord"
twee losse claims zijn -- de tweede faalde hier stilletjes tot de
lockstepcontrole het ving.

`hw_video_audio.c:stars_scroll_down`'s eerder resterende read is nu
opgelost: zie de `T1D00`/`T1F00`-sectie hieronder. De 5 indirecte
`mem_read()`-gebaseerde ROM-reads die de audit vond, zijn ook opgelost:
zie de `T1800`/`T1BA0`-sectie verderop. De laatste 2 reads,
`attract_mode.c:draw_bird_shape_350c`'s eigen reads, zijn ook opgelost:
zie de `draw_bird_shape_350c`-sectie tegen het einde van dit document.

### `T1D00`/`T1F00` geëxtraheerd, `stars_scroll_down` volledig opgelost (21 juli 2026)

Als vervolg op de audit hierboven zijn `T1D00` ("Mother ship object 26x9
tiles") en `T1F00` ("starfield background without planets") als volle
pagina's geëxtraheerd (`mothership-tile-page`, `starfield-no-planets-
page`), met dezelfde low-byte-free-wheel-redenering als `starfield-page`.
Een nieuwe dispatch-hulpfunctie, `phoenix_starfield_or_mothership_byte()`,
routeert op basis van het hoge adresbyte (`0x1C`/`0x1D`/`0x1F`) naar de
juiste van de drie pagina's; `stars_scroll_down` gebruikt die nu in plaats
van `prg_mem`. Geverifieerd met byte-identieke RAM-dumps over alle 4
standaardscripts, plus tijdelijke hit-tel-instrumentatie (na gebruik
verwijderd) die bevestigde dat alle drie pagina's daadwerkelijk geraakt
worden en er nooit een ander hoog byte voorkomt: `0x1C` 2682-8696 keer,
`0x1D` 234 keer (drie van de vier scripts; nul in
`extended_playthrough.txt`), `0x1F` 0-4426 keer, `other` 0 over alle 4
scripts. `hw_video_audio.c` heeft nu geen enkele directe `prg_mem`-read
meer.

### `T1800`/`T1BA0` geëxtraheerd, `print_text_lines()` volledig opgelost (21 juli 2026)

Als vervolg op de `mem_read()`-audit hierboven zijn `T1800` en `T1BA0`
geëxtraheerd als `phoenix_attract_text_page` en
`phoenix_players_button_text`. Hun exacte bereiken zijn niet geraden: de
adresrekenkunde van `print_text_lines()`/`draw_row()` is precies
gesimuleerd voor elke echte `(addr,count)`-aanroepplek (de
rij-teken-loop is een echte ongemaskeerde 16-bit `INC HL`, anders dan bij
de meeste andere geëxtraheerde tabellen met hun low-byte-only
free-wheeling), wat bevestigt dat de breedste echte aanroep (`0x1800`,
count=3) precies `0x1800-0x185F` raakt -- direct grenzend aan, maar niet
overlappend met, `phoenix_score_average_text_page`. Een nieuwe
dispatch-hulpfunctie, `phoenix_text_byte()`, routeert over alle drie de
bereiken (`phoenix_attract_text_page`, `phoenix_score_average_text_page`,
`phoenix_players_button_text`); `print_text_lines()`/`draw_row()`
gebruiken die nu in plaats van `mem_read()`. Geverifieerd met
byte-identieke RAM-dumps over alle 4 standaardscripts, plus tijdelijke
hit-tel-instrumentatie (na gebruik verwijderd) die bevestigde dat alle
drie bereiken daadwerkelijk geraakt worden en er nooit een adres buiten
valt: `attract` 4424-15008 keer, `score_avg` 16184-53508 keer,
`players_btn` 0-2408 keer (alleen in `my_session.txt`, dat een
coin-insert-/start-sequentie bevat), `other` 0 over alle 4 scripts. Er
zijn nergens meer ROM-reads via `mem_read()` in de codebase.

### `T0560`/`T0B38` gecentraliseerd (21 juli 2026)

De twee lokaal-ingebakken-maar-ongecatalogiseerde tabellen uit de sweep
zijn verplaatst naar `phoenix_tables.c` als `phoenix_player_init_data` en
`phoenix_player_x_position_mapping`, met `[ASM:]`-doc-comments en
byte-voor-byte-tests. Dit was een pure relocatie -- de vertalingen waren
al ROM-vrij en correct, dus `state_init.c:init_player_data_structure()`
en `player_logic.c:map_player_ship_position()` verwijzen nu simpelweg
naar de gecentraliseerde arrays in plaats van hun eigen lokale
`static const`-kopieën. Geverifieerd met byte-identieke RAM-dumps over
alle 4 standaardscripts (er is geen dispatch-logica geïntroduceerd, dus
geen hit-tel-instrumentatie nodig hier).

### `InitGlobalLevelData`-duplicaat opgelost (21 juli 2026)

Het laatste openstaande punt uit de T-label-sweep: `state_init.c`'s
onafhankelijke `static init_global_level_data()` (met zijn eigen lokale
`T0598`/`T05A8`/`T05B4`/`T05C0`/`T05CC`-arrays) is verwijderd, en
`state_init.c` roept nu de gedeelde externe `init_global_level_data()`
uit `init_global_level_data.c` aan (die al `level-data-pointer-table`/
`level-data-page` gebruikte) -- dezelfde functie die `attract_mode.c`'s
demo-dispatch al aanriep. Beide vertalingen bevatten identieke
ROM-bytes, dus dit was een pure deduplicatie, geen gedragswijziging.
Geverifieerd met byte-identieke RAM-dumps over alle 4 standaardscripts.
Zie de `known_issues`-entry in de JSON-catalogus, nu gemarkeerd als
`resolved`.

### `draw_bird_shape_350c`-shapedata geëxtraheerd -- de laatste twee reads (21 juli 2026)

De laatste overgebleven reads uit de allereerste extractieronde:
`attract_mode.c:draw_bird_shape_350c()`'s `shape`-pointer komt uit twee
bronnen. `l38a1_erase_bird`'s wis-pad geeft een *vaste* letterlijke
waarde mee (`0x1700 | (phoenix_bird_erase_shape_selector + 0xDE)` =
`0x17F0`, clip-aanpasbaar tot `+6`) die volledig binnen de al
geëxtraheerde `shield-and-drawnx2-shapes` (`$17B8-$17FF`) blijkt te
vallen -- geen nieuwe tabel nodig, alleen een dispatch die ernaartoe
routeert. `drawbirdobject`'s normale teken-pad leidt `shape` af van de
al geëxtraheerde `bird-shape-pointers`-tabel, waarvan de inhoud na het
bullet-mask-voorvoegsel altijd `0x3Cxx`/`0x3Dxx` is, en landt in het
veel grotere, voorheen niet-gecatalogiseerde `$3C00-$3DB7`-shape-data-
gebied. Dat bereik is niet wiskundig bewijsbaar (rijenaantal en
clip-diepte hangen allebei af van vrije RAM-toestand), dus empirisch
vastgesteld: tijdelijke hit-tel-instrumentatie over alle 4
standaardscripts (1009-8084 tekenaanroepen per run) toonde het
bereikbare gebied stabiel op *exact* `$3C00-$3DB7` in elke run -- wat
toevallig ook precies is waar de al geëxtraheerde
`egg-transformation-types` begint (`$3DB8`), een natuurlijke, niet
gegokte grens. Geëxtraheerd als `phoenix_bird_shape_data_page`, met een
nieuwe dispatch-hulpfunctie `phoenix_bird_shape_data_byte()` die tussen
die tabel en `shield-and-drawnx2-shapes` routeert.

Geverifieerd met byte-identieke RAM-dumps over alle 4 standaardscripts,
plus de hit-tel-instrumentatie hierboven (na gebruik verwijderd) die de
bereiken van beide paden precies bevestigde, niet alleen het
gecombineerde dump-resultaat.

**De codebase heeft nu nul directe `prg_mem`-reads en nul indirecte
ROM-reads via `mem_read()`, nergens meer** -- de volledige
program-ROM-data-afhankelijkheid waar deze catalogus voor is opgezet,
is nu volledig gecentraliseerd in `phoenix_tables.c`.

## Status

| Status | Betekenis |
| --- | --- |
| `extracted` | Benoemde C-data, een byte-voor-byte brontest en lockstep-replaybewijs. |
| `mapped` | Adresbereik, lezer en doel zijn begrepen; de gamecore gebruikt nog `prg_mem`. |
| `partial` | Een stabiel bereik of lezer is bekend, maar de volledige structuur vraagt meer analyse. |

## Gecatalogiseerde Regio's

| ROM-regio | Familie | Eigenaar | Lezende module | Status |
| --- | --- | --- | --- | --- |
| `$1500-$151F` | Alien-control-state-pointers | Alien-initialisatie | `alien_logic.c` | extracted |
| `$1520-$153F` | Alien-initiele-layoutpointers | Alien-initialisatie | `alien_logic.c` | extracted |
| `$1600-$16FF` | Shape-offsets, animatiedescriptors (volledige pagina, zie noot hieronder) | Alien/spelerbeweging | `alien_logic.c`, `player_logic.c` | extracted |
| `$1700-$173F` | Alien-richtingsvectoren | Alienbeweging | `alien_logic.c` | extracted |
| `$1760-$1767`, `$17B0-$17B7` | Round-populatie, alien-explosievolgorde | Wave/explosie | `alien_wave.c`, `alien_logic.c` | extracted |
| `$1B40-$1B9F`, `$198C` | Mothership/spelerexplosiepointers (gecorrigeerd van `$1B00-$1B5F`; zie noot hierboven), bird-erase-selector | Rendering/botsing | `mothership_impl.c`, `player_explosion.c`, `collision_detection.c` | extracted |
| `$2800-$2BFF` | Speler- en mothership-explosietiles/control-bytes (volledige pagina, zie noot hieronder) | Speler-/mothership-explosie | `player_explosion.c`, `state_endings.c` | extracted |
| `$3300-$33FF` | Alien closed-loop-bewegingskeuze | Alienbeweging | `alien_logic.c` | extracted |
| `$3B00-$3BFF` | Small/large-bird-hitmasks (volledige pagina, zie noot hieronder) | Bird-botsing | `collision_detection.c` | extracted |
| `$3DB8-$3DBF`, `$3DC0-$3DDF`, `$3DE0-$3DFF` | Egg-transformaties, dive-spawns, bird-sound-cadence | Bird wave/botsing/geluid | `collision_detection.c`, `bird_wave_behavior.c`, `sound_dispatcher.c` | extracted |
| `$3E00-$3E07` | Player-bullet-bitmasks | Bird-botsing | `collision_detection.c` | extracted |
| `$3E00-$3ECF` | Bird-shapepointers (volledige pagina, zie noot hieronder), formatieparameters, draw-entries | Bird-rendering/wave | `attract_mode.c`, `bird_wave_behavior.c` | extracted |
| `$3ED0-$3EDF` | Bird verticale scrollstappen | Birdbeweging | `birds_vertical_movement.c` | extracted |
| `$3EE0-$3EFF` | Bird-daalsnelheidscaps | Birdbeweging | `birds_vertical_movement.c` | extracted |
| `$3F00-$3F7F` | Bird-gedragsscripts (gecorrigeerd van oorspronkelijk gecatalogiseerd `$3F00-$3FFF`; zie JSON-noot) | Bird wave | `bird_wave_behavior.c` | extracted |
| `$1000-$13FF` | Alien-bewegingspatroon-cluster A: T1000-idle/resetlijst plus 18 closed-loop-patronen (voorheen ongecatalogiseerd, zie noot hierboven) | Alienbeweging | `alien_logic.c` | extracted |
| `$2C00-$2FFF` | Alien-bewegingspatroon-cluster B: 18 meer closed-loop-patronen, fysiek gescheiden van cluster A (voorheen ongecatalogiseerd, zie noot hierboven) | Alienbeweging | `alien_logic.c` | extracted |
| `$1500-$15FF` | Alien-positielayout-pagina voor `init_alien_positions`'s dynamische lookup (volledige pagina, overlapt bewust twee al geëxtraheerde tabellen, zie noot hierboven) | Alien-initialisatie | `alien_logic.c` | extracted |
| `$063A-$0649` | Pointertabel voor de alien-positielayout-lookup, 16 entries geïndexeerd 0-15 | Alien-initialisatie | `alien_logic.c` | extracted |
| `$1740-$175F` | Formatie-kogeltreffervenster, 4 bytes/tile geïndexeerd door `chr & 0x07` (zie noot hierboven) | Speler-kogel-botsing | `weapon_collision.c` | extracted |
| `$0A40-$0A4B` | Score-average-table-tilepaar voor `draw_n_by_2()`-aanroep 1 en 3 (vast bronadres) | Attract-mode tekstrendering | `attract_mode.c` | extracted |
| `$3C00-$3C0B` | Score-average-table-tilepaar voor `draw_n_by_2()`-aanroep 2 (vast bronadres) | Attract-mode tekstrendering | `attract_mode.c` | extracted |
| `$3C00-$3DB7` | Bird-shape-bitmapdata voor `draw_bird_shape_350c()` (empirisch begrensd, eindigt exact bij `egg-transformation-types` -- zie noot hierboven) | Attract-mode-/bird-rendering | `attract_mode.c` | extracted |
| `$233A-$2359` | Intro-bird-animatieframe-index (volledig bereik, tabel grenst aan code, zie noot hierboven) | Attract-mode bird-animatie | `attract_mode.c` | extracted |
| `$1860-$1B5F` | Score-average-scrolltekst/pointerdata (empirisch begrensd, zie noot hierboven) | Attract-mode tekstrendering | `attract_mode.c` | extracted |
| `$0598-$05A7` | Level-data-pointertabel, 16 entries geïndexeerd door `LevelAndRound & 0x0F` | Level-initialisatie | `init_global_level_data.c` | extracted |
| `$05A8-$05D7` | Level-data-pagina: 4 statisch gedecodeerde blokken van 12 bytes (zie noot hierboven) | Level-initialisatie | `init_global_level_data.c` | extracted |
| `$0A00-$0A3F` | Grid-naar-scherm-ram-adrestabel, bitmask-begrensd | Schermcoördinaatmapping | `utilities.c` | extracted |
| `$1400-$1500` | Sprite-/alien-karakterblokshapes (volledige pagina + 1 byte, zie noot hierboven) | Sprite-/alien-rendering | `sprite_rendering.c`, `hw_video_audio.c` | extracted |
| `$1770-$17AF` | Schild-schadetoestand-shapes, bitmask-begrensd | Speler-schildrendering | `player_logic.c` | extracted |
| `$17B8-$17FF` | Shield-expired- en `drawNx2`-shapes (gecorrigeerd van "genuinely unresolved", zie noot hierboven) | Speler-schild-/alien-explosierendering | `attract_mode.c`, `player_logic.c`, `player_explosion.c` | extracted |
| `$1BC0-$1BFF` | Mothership-piloot-/antenne-animatieframes, bitmask-begrensd | Mothership-animatie | `alien_wave.c` | extracted |
| `$1C00-$1CFF` | Sterrenveld-/achtergronddata (volledige pagina) | Achtergrond-sterrenveld | `mothership_logic.c`, `state_play.c` | extracted |
| `$1E00-$1E1F` | Planeet-shape-bronbeeld (gevonden via een echte lockstepregressie, zie noot hierboven) | Attract-/achtergrond-planeetdecoratie | `hw_video_audio.c` | extracted |
| `$1E20-$1EDF` | Planeet- en galaxy-decoratietabellen, bitmask-begrensd | Attract-/achtergronddecoratie | `hw_video_audio.c` | extracted |
| `$3F80-$3FFF` | "Level 3/8 initial bird data" (bewijsbaar constant bereik, zie noot hierboven) | Bird-wave-initialisatie | `misc_logic.c` | extracted |
| `$0560-$057F` | Speler-/kogel-struct-initdata, gecentraliseerd vanuit een lokale `T0560`-array in `state_init.c` (zie noot hierboven) | Speler-/kogel-initialisatie | `state_init.c` | extracted |
| `$0B38-$0B47` | Speler-schip-X-positiemapping, gecentraliseerd vanuit een lokale `T0B38`-array in `player_logic.c` (zie noot hierboven) | Spelerrendering | `player_logic.c` | extracted |
| `$1800-$185F` | Attract-mode-/HUD-tekst (score-/hi-score-headers) voor `print_text_lines()` (zie noot hierboven) | Attract-mode-/HUD-tekst | `utilities.c` | extracted |
| `$1BA0-$1BBF` | "1 OR 2 PLAYERS BUTTON"-statische tekst voor `print_text_lines()` (zie noot hierboven) | Attract-mode-/HUD-tekst | `utilities.c` | extracted |
| `$1D00-$1DFF` | Mothership-objecttiles (`stars_scroll_down`'s 2e doelpagina, zie noot hierboven) | Achtergrond-sterrenveld / mothership-fade-in | `hw_video_audio.c` | extracted |
| `$1F00-$1FFF` | Sterrenveld zonder planeten (`stars_scroll_down`'s 3e doelpagina, zie noot hierboven) | Achtergrond-sterrenveld / mothership-fade-in | `hw_video_audio.c` | extracted |

## Dynamische Data

Geen. Elke read die ooit buiten de begrensde-tabeltelling viel, is
opgelost tot een benoemde, geteste array (of een dispatch over twee of
meer van zulke arrays) -- zie de secties hierboven, met name
`draw_bird_shape_350c` voor de laatste twee. De JSON-array
`dynamic_or_payload_readers` is nu leeg; behouden in het schema voor
toekomstige regressies, niet als bewering dat dynamische reads nooit
meer kunnen terugkeren.

## Bekende Aandachtspunten

Momenteel geen openstaande punten. De ene entry die tijdens de
T-label-sweep werd gevonden -- dubbele `InitGlobalLevelData`-vertalingen
in `state_init.c` en `init_global_level_data.c` -- is opgelost op 21 juli
2026 (zie de sectie hierboven); de JSON-array `known_issues` bewaart er
een `resolved`-record van voor de geschiedenis.

## Extractieregel

Verplaats een regio tegelijk naar een benoemde `const`-array in
`phoenix_tables.c`, declareer hem in `phoenix_tables.h`, behoud het ASM-bereik,
voeg een byte-voor-byte test tegen `rom_data.c` toe en draai vervolgens een
deterministische lockstep-replay. Werk de JSON-catalogus in dezelfde wijziging
bij.

Zowel `phoenix_tables.c` als `phoenix_tables.h` worden op ASM-startadres
gesorteerd gehouden -- voeg nieuwe extracties op de juiste plek in, niet
achteraan plakken. Bij twee entries met hetzelfde startadres (een bewuste
overlap, bijv. een smalle tabel en een volledige-pagina-duplicaat die
hem dekt) komt de smallere eerst. Hulpfuncties die van meerdere tabellen
afhangen (bijv. `phoenix_alien_movement_byte()`) staan direct na de
laatste tabel waar ze van afhangen, want ze hebben zelf geen ASM-adres.
