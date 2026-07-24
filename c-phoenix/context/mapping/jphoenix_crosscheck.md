# Cross-check v3: definitieve categorisering per functie

> [!IMPORTANT]
> **Eindconclusie van de nauwkeurigheids-audit (11 juli 2026).** Na de
> volledige keten — gcov-coverage, PC-adres-cross-check, per-adres-
> duplicaathercontrole en een verse passieve lockstep-vergelijking
> (byte-exact op 7 transiënte blips na, regio `4000-4BE5`) — resteert
> **geen enkel bevestigd ontbrekend of afwijkend spelgedrag** in de
> C-poort. De enige echte fout die deze audit vond was een
> *achtergebleven niet-ASM-hack* (`clear_stale_copyright_line()`, kopie
> van een in jphoenix teruggedraaide correctie) — verwijderd op 11 juli.
> De categorieën B, C1 en D hieronder zijn tijdens de audit herroepen;
> hun doorgestreepte koppen en correctienotities documenteren waarom.
> Zie ../STATUS.nl.md voor de actuele verificatiestatus.

## Aanleiding

Deze verdieping kwam voort uit een concrete tegenspraak: `add_to_score` en
`game_demo` stonden in de "niet geraakt door c-phoenix"-lijst, maar de score
stijgt zichtbaar tijdens het spel en de attract-mode-demo speelt wel degelijk
af. "Niet geraakt" bleek dus niet te betekenen "dit spelgedrag ontbreekt" —
het betekent alleen "deze specifieke, aan een ROM-adres gekoppelde C-functie
is niet degene die het werk doet". Dat dwong een preciezere blik af op alle
33 afwijkende functies (21 "alleen jphoenix" + 8 "alleen c-phoenix" +
4 "geen van beide"), met drie controles per functie:

1. Is er een naamgenoot-duplicaat op hetzelfde ROM-adres die wél live is
   (zoals `check_demo_mode_player_and_alien` naast het dode `game_demo`)?
2. Heeft de originele asm ergens een `CALL`/`JP`-referentie naar dit adres,
   of — subtieler — een **indirecte jumptable-dispatch**? De asm bevat zes
   `JP (HL)`-sprongen (`context/code-annotated.asm:856,1464,1503,1742,2993,5849`)
   die via een tabel met MSB:LSB-adresparen dispatchen. Een eenvoudige
   tekst-grep op `$XXXX` mist die doelen, omdat het adres alleen als *data*
   in de tabel staat, niet als CALL/JP-operand. Concreet bewijs: tabel
   `T0814` (`context/code-annotated.asm:1746-1758`) bevat `22 30` (MSB:LSB
   voor `$2230`) als dispatch-doel voor game-level 4/6/8 — exact het adres
   van `spiral_fill_animation`. Dat adres leek dus "ongebruikt" bij een
   naïeve caller-grep, maar wordt legitiem aangeroepen via deze tabel.
3. Heeft de C-functie zelf een echte aanroeper in c-phoenix (niet alleen
   haar eigen declaratie/definitie of een asm-adrescommentaar)?

jphoenix's coverage-tool registreert PC bij elke echte opcode-fetch
(`I8080.java:414`, `recordInstruction`, aangeroepen direct na `nxtpcb()` in
de fetch-decode-loop), dus "door jphoenix geraakt" betekent altijd
daadwerkelijke executie op de referentie-hardware — nooit een toevallige
data-read.


## A. Onschuldige duplicaat op hetzelfde ROM-adres (2)

Een levende naamgenoot op exact hetzelfde adres doet het echte werk; deze specifieke functie is dode restcode. Geen actie nodig buiten opruiming.

| Dode functie | Levende naamgenoot (100% geraakt) |
|---|---|
| `game_demo` | `check_demo_mode_player_and_alien` |
| `l37cc` | `l37cc_erase_bonus_explosion` |

## B. ~~Bevestigde state-progressie-divergentie~~ HARNAS-ARTEFACT, geen bug (8)

**Herroepen op 11 juli 2026.** De vergelijking van de RAM-dump-sporen van
beide emulatoren onder hetzelfde script toonde aan dat jphoenix soms
meerdere vblanks per spel-loop-iteratie verbruikt (206 van 4600
dump-frames ontbreken: frames waarin `WaitVBlankCoin` niet gepolld werd),
terwijl c-phoenix per constructie exact één frame per iteratie doet.
Input-events (die op framenummer vuren) landen daardoor op verschillende
*spelmomenten*, en de spelverlopen lopen legitiem uiteen — geen enkele
constante frame-offset lijnt de sporen uit. Dat c-phoenix bij de bot-
geoptimaliseerde scripts verder komt dan jphoenix is dus een artefact
van het meetharnas, geen vertaalfout. De functies hieronder zijn gewoon
live (de mothership-groep is bovendien in echte gameplay bevestigd via
de `my_session.txt`-opname). De passieve
(input-loze) lockstep-vergelijking — die dit probleem niet heeft — is op
11 juli opnieuw gedraaid en is byte-exact op 7 transiënte
één-frame-blips na.

| Functie | Bestand | ROM-range |
|---|---|---|
| `l3462_no_birds_left` | collision_detection.c | 3462-346D |
| `l3ad0` | generated_stubs.c | 3AD0-3AF6 |
| `l3af8` | generated_stubs.c | 3AF8-3B00 |
| `l3b02` | generated_stubs.c | 3B02-3B19 |
| `erase_mothership` | mothership_logic.c | 246A-2475 |
| `mothership_core_hit_check` | mothership_logic.c | 2520-255D |
| `l2552_mothership_explosion_done` | state_endings.c | 2552-255D |
| `state_6_mother_ship_explosion` | state_endings.c | 2400-244B |

## C0. Zichtbaar spelgedrag klopt, maar via een losse herimplementatie elders (1)

Dit was de aanleiding voor deze hele check: `add_to_score` — de score stijgt
wél zichtbaar tijdens het spel, maar niet via deze adres-gemapte functie.

| Functie | Bestand | ROM-range | Waar het écht gebeurt |
|---|---|---|---|
| `add_to_score` | utilities.c | 0220-0232 | add_score() in scoring.c — losstaand herschreven BCD-optellogica. Bevestigd (11 juli): de enige asm-callers van $0220 zijn $2731/$275C, midden in het L2700-gebied waarvan de vertaling (`update_scores_and_sound`) inderdaad `add_score()` gebruikt. |

## C1. ~~Echte ROM-code zonder c-phoenix-aanroeper~~ VOLLEDIG OPGELOST: duplicaten en inlines (14)

**Herroepen op 11 juli 2026.** Per-adres-hercontrole (bestaat er een
*andere* C-functie wiens `[ASM:]`-range hetzelfde adres dekt, en is díe
geraakt?) loste alle 14 op — er is **geen enkel bevestigd ontbrekend
spelgedrag**. Twee subgroepen:

**Dode duplicaten** — levende vertaling bestaat onder een andere naam
(en is gcov-bevestigd geraakt):

| Dode stub | Levende vertaling | ROM-adres |
|---|---|---|
| `l3800` | `collision_detection_for_birds` (collision_detection.c) | 3800 |
| `l3894` | `l3844_small_bird_hit` (collision_detection.c) | 3894 |
| `l38a1` | `l38a1_erase_bird` (collision_detection.c) | 38A1 |
| `l38f8` | `bird_explosion_slot` (collision_detection.c) | 38F8 |
| `l3980` | `check_bird_formation_player_collision` (bird_wave_behavior.c) | 3980 |
| `drawfirst4birdobjects` | `draw_first_4_bird_objects` (bird_logic.c) | 3474 |
| `spiral_fill_animation` | `level_4_6_8_spiral_fill` (state_play.c) | 2230 |
| `l0c00_bonus_explosion_scoring` | `l0c00_kill_score` | 0C00 |
| `l0cf4` | `handle_animations_for_killed_aliens` | 0FC0 |

**Geïnlined bij de aanroepplekken** — de ROM-hulproutine is in C niet als
losse functie aangeroepen maar ter plekke vertaald (memset/memcpy/
directe expressies); de asm-callers en hun C-tegenhangers zijn
gecontroleerd:

| Functie | ASM-callers | C-equivalent |
|---|---|---|
| `add_bc_to_mem` ($0206) | $01AB (slow-print score-tabel) | inline in de vertaling van de caller |
| `clear_b_bytes_at_hl` ($05D8) | $0158, $050B, $0537, $0557 (init-routines) | memset (o.a. state_init.c:65) |
| `copy_b_bytes_hl_to_de` ($05E0) | $054F, $0592, $32E3 | memcpy/loops in de callers |
| `print_score_column` ($06E8) | $04C9 (state_1_flashing_score) | inline in state_1_flashing_score |
| `l14e0` ($14E0) | $01CA (coin-check-continuatie slow-print) | centraal in wait_vblank_coin |

Doorslaggevend bewijs dat deze aanpak klopt: de passieve lockstep-
vergelijking van 11 juli (3491 frames, volledige attract-cyclus inclusief
spiraal- én vogel-demo, regio `4000-4BE5`) is **byte-exact op 7
transiënte één-frame-blips na** — als een van deze routines echt zou
ontbreken, was dat daar als aanhoudende divergentie zichtbaar geweest.

## C1b. Vals alarm: overkoepelende stub-entry overlapt al bestaande live code (2)

`l3452` en `l37b0` waren de twee entries met de meeste losse adresranges (15 en 6).
Bij het uitsplitsen bleek bijna elke sub-range al te vallen binnen het adresbereik
van een andere, apart benoemde en (vermoedelijk) live functie — deze twee zijn dus
géén reële coverage-gaten, maar overbodige, te-breed-gemapte stubs uit
`generated_stubs.c` die nooit zijn opgeruimd nadat de echte implementaties elders
werden geschreven.

| Functie | Bestand | ROM-range | Overlapt met (voorbeeld) |
|---|---|---|---|
| `l3452` | generated_stubs.c | 1EE0-1EFA, 2030-2037, 21DC-21FC, 2204-222B, 2260-22C5, 22CA-22E8, 22F0-22F4, 22FA-2337, 3000-3012, 3028-306D, 3074-314E, 315A-31AD, 31B4-325E, 3264-32F0, 3452-345B | `l3028`, `l30ba`, `l3124`, `get_random_number`, `l3074_breakout_delay`, `l315a`, `l31b4`, `l322c`, `l3264`, `level_9_mothership_fade_in`, `level_A_mothership_and_aliens_fade_in` — precies de dispatch-doelen van jumptabel `T3018` (`context/code-annotated.asm:5856-5863`, Counter93-index) |
| `l37b0` | generated_stubs.c | 34C0-3519, 3520-35A2, 35B0-35DB, 35E0-373E, 3744-37AA, 37B0-37C6 | `draw_bird_shape_350c`, `drawbirdobject`, `update_bird_behavior`, `l366a_stall`, `l3672_aim`, `l36d2_grow`, `l3628_climb`, `l36c0_animate`, `l35e0_descend`, `l3695_aim_up`, `l3744_restart`, `l3758_bonus_explosion_animation`, `l3796_bonus_explosion_left`, `l37b0_print_bonus_score` |

## C2. Wel aangesloten in c-phoenix, verkeerde/ongebruikte tak (1)

| Functie | Bestand | ROM-range | Toelichting |
|---|---|---|---|
| `init_alien_movement_pointers` | state_init.c | 0506-0514 | Aanroep bestaat (state_init.c:81), maar de guard-conditie ervoor wordt door geen van de 55 scripts geraakt. |

## D. ~~Geen aanwijzing voor gebruik~~ Opgelost: dode duplicaat (1)

| Functie | Bestand | ROM-range | Correctie 11 juli |
|---|---|---|---|
| `l0e9e` | generated_stubs.c | 0280-0285, 0E9E-0EA3 | Levende vertaling `l0e10` dekt $0E9E; deze stub is een dode duplicaat. |

## In geen van beide geraakt, en geen asm-referentie (4)

Vermoedelijk echt dode code (2 dragen zelfs `_unused` in hun naam).

| Functie | Bestand | ROM-range |
|---|---|---|
| `l00b6` | generated_stubs.c | 00B6-00B7 |
| `l0e02_unused` | weapon_collision.c | 0E02-0E0B |
| `l3462` | generated_stubs.c | 3462-346D |
| `unused_bcd_subtracter` | utilities.c | 0236-0252 |

## Consequenties voor `code-annotated.asm`/`.md` en de mapping-tabellen

### 1. `c_functions_by_address.md` wordt mechanisch gegenereerd, niet curated

[`tools/generate_mappings.py`](../../tools/generate_mappings.py) bouwt de
tabel door in elk `.c`-bestand te zoeken naar `[ASM: XXXX-YYYY]`-docblocks en
die één-op-één in een rij te zetten. De generator heeft geen begrip van
"welke van deze twee functies op hetzelfde adres is de levende" — hij ziet
alleen tekst-patronen, geen call-graph. Categorie A hierboven
(`game_demo`/`l37cc`) ontstaat dus niet door een menselijke fout in de
tabel, maar is een **structureel blinde vlek van de generator**: elke
docblock met een `[ASM: ...]`-commentaar wordt gelijkwaardig weergegeven,
of hij nu wordt aangeroepen of niet.

### 2. De "100% covered"-claim bovenaan het bestand dekt een andere lading dan gesuggereerd

De `> [!NOTE]`-conclusie bovenaan `c_functions_by_address.md` ("Zero blocks
of unreferenced executable Z80 code were found... The codebase is 100%
covered regarding executable logic") is **op zichzelf correct** — elke
ROM-byte heeft een naam of een expliciete gap-markering. Maar die claim
gaat over *byte-dekking van het ROM-adresbereik*, niet over *of de
C-vertaling ook daadwerkelijk wordt uitgevoerd door de poort*. Een lezer
kan dat gemakkelijk verwarren met "elke vertaling is bevestigd correct en
actief" — deze cross-check laat zien dat zeker 17% van de geadresseerde
functies (33 van 191) dat niet zijn, in een van de vijf hierboven
beschreven vormen.

### 3. Concrete, aanwijsbare tekortkomingen in de huidige tabel

- **Geen markering voor duplicaten**: `game_demo`/`check_demo_mode_player_and_alien`,
  `l3462`/`l3462_no_birds_left` en `l37cc`/`l37cc_erase_bonus_explosion` staan
  als drie gelijkwaardige rij-paren in de tabel, zonder aanduiding welke van
  elk paar dood is. Iemand die de tabel gebruikt om functie-voor-functie
  asm-vs-C te verifiëren, kan zomaar de dode stub beoordelen in plaats van de
  levende implementatie.
- **Geen markering voor jumptable-only bereikbaarheid**: adressen als
  `$2230` (`spiral_fill_animation`) zijn alleen bereikbaar via de
  `T0814`-jumptabel, niet via een directe `CALL`/`JP`. Wie `code-annotated.asm`
  doorzoekt op `$2230` als caller-bewijs (zoals ik aanvankelijk deed) trekt
  dan de verkeerde conclusie ("nergens aangeroepen = dode code"). De asm zelf
  annoteert de `JP (HL)`-instructie wel met een commentaar ("jump to
  corresponding function according to LevelAndRound"), maar koppelt de
  tabelwaarden niet aan symbolische functienamen zoals bij directe
  `CALL $XXXX ; {code.Naam}`-annotaties.
- **Geen kolom voor "losse herimplementatie elders"**: `add_to_score` staat
  in de tabel alsof hij "de" score-optel-implementatie is; nergens wordt
  vermeld dat `add_score()` in `scoring.c` de werkelijk actieve, anders
  gestructureerde vervanger is. Zonder de call-graph-analyse van deze sessie
  is dat niet uit de tabel af te leiden.

### 4. Doorgevoerde verbeteringen

- **Status-kolom toegevoegd** aan `c_functions_by_address.md`, via een
  `KNOWN_STATUS`-lookup in [`tools/generate_mappings.py`](../../tools/generate_mappings.py)
  die de 33 bevindingen uit deze cross-check vastlegt (Live/Dode duplicaat/
  Herimplementatie-elders/Coverage-gat/Vals-alarm-overlap/Vermoedelijk dood).
  Rijen zonder vermelding zijn nog niet zo onderzocht ("Unconfirmed") — dat
  is nog steeds de meerderheid van de ~313 functies.
- **Automatische duplicaat-detectie** toegevoegd aan de generator: twee
  functie-rijen met identieke `Range`-kolom krijgen nu automatisch een
  "Zelfde adres als: ..."-vermelding, ook voor toekomstige duplicaten die
  niet in de handmatige `KNOWN_STATUS`-lijst staan.
- **De "100% covered"-alinea** in `c_functions_by_address.md` heeft nu een
  expliciete waarschuwing die het onderscheid maakt tussen "elke ROM-byte
  heeft een naam" en "elke naam is bevestigd actief in de C-poort", met
  verwijzing naar dit bestand.
- **Twee jumptabellen geannoteerd** in `code-annotated.asm` (en doorgezet
  naar `code-annotated.md`) met symbolische `{code.Naam}`-verwijzingen naar
  de daadwerkelijke C-functienamen: `T0814` (GameLevel-dispatch, verklaart
  o.a. `spiral_fill_animation` en `process_birds`) en `T3018`
  (Counter93-dispatch, verklaart waarom `l3452` een vals-alarm-overlap is).
  De overige vier `JP (HL)`-sites (`T040E`/GameState — al goed
  gedocumenteerd —, en de twee bit3/bit4-schermobject-tabellen bij
  `0734`/`0758`, niet relevant voor de 33 gevonden functies) zijn ongemoeid
  gelaten.
- **Ontbrekend `[ASM: ...]`-tag hersteld**: `state_7_mother_ship_score_display`
  in `state_endings.c` had het docblock "Translates L244C" maar miste de
  machineleesbare `[ASM: 244C-2469]`-tag, waardoor de generator dat adres
  als "UNREFERENCED DATA" bestempelde in plaats van als deze functie. De
  tag is toegevoegd en het gat-aantal daalde van 134 naar 133.
- **Nieuwe categorie C1b ontdekt** tijdens het aanbrengen van de
  jumptable-annotaties: `l3452` en `l37b0` bleken bij het uitsplitsen van
  hun vele losse adresranges bijna volledig te overlappen met al bestaande,
  apart benoemde functies — dus geen echte coverage-gaten maar
  overkoepelende, nooit opgeruimde stub-entries (zie categorie C1b
  hierboven).

Niet doorgevoerd: uitbreiding van de Status-kolom naar alle ~313 functies
(vereist per functie dezelfde handmatige call-graph-analyse als in deze
sessie) en annotatie van de resterende jumptabellen (niet relevant voor de
huidige bevindingen).
