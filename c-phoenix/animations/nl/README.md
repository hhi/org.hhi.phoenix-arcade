# Phoenix Animaties & Trajecten Gids (`c-phoenix/animations`)

Welkom in het centrale visuele archief van de *Phoenix* Arcade Game (`c-phoenix`). Deze directory bevat functionele, geheugen- en visuele analyses van zowel de **vogel-animaties** als de **vectoriële vliegtrajecten** van aliens, vogels en het moederschip.

## Bronstatus

De bron van waarheid is, in deze volgorde: **Z80 ASM/ROM → C-port → geannoteerde analyse → deze visualisaties**. De SVG's maken ROM- en C-data inzichtelijk, maar vervangen die bron niet. Een conclusie zonder koppeling naar ASM, ROM of C-code is een interpretatie die nog gecontroleerd moet worden.

---

## 🗂️ Inhoudsopgave

1. 🚀 [`animation-trajectory.md`](animation-trajectory.md) — **Diepgaande analyse van alle voorgeschreven vliegpatronen, RAM-datastructuren (`$4000-$4BFF`), Z80 ROM-clusterindeling, overkoepelende hoofd-animatie en 128 SVG-animaties.**
2. 📐 [`animation-trajectory-detailed.md`](animation-trajectory-detailed.md) — **Gedetailleerde stap-voor-stap coördinatentabellen op het scherm-grid per individueel patroon (stap #, vector index, dX, dY, cumulatief X/Y).**
3. 🦅 [`bird-animations.md`](bird-animations.md) — **Visuele gids van alle 6 vogel-animatiefases (van ei tot volgroeide vogel en explosie).**

---

## 🏛️ Waarom Verschillende ROM Clusters & Hoofdstukindeling?

- **Cluster A (ROM `$1000–$13FF` / EPROM Chip 1):** Bevat **Patronen 01 t/m 18** voor de geordende formatiegolven in **Alien Wave 1 & 3**.
- **Cluster B (ROM `$2C00–$2FFF` / EPROM Chip 3):** Bevat **Patronen 19 t/m 36** voor **Breakout-aliens** en **Moederschip-escorts** (Levels 9, 10, 11).
- **Hoofdstukindeling:** Volgt exact de 4 fysieke game-entiteit subsystemen uit de Arcade Z80 engine (Wave 1/3 Aliens, Breakout/Escort Aliens, Wave 5/7 Vogel AI & Duik-spawns, Moederschip & Attract Mode).

---

## 🎬 Overkoepelende Hoofd-Animatie

Drie bewegingssoorten uit het spel tegelijk — een alien-zwenking, een vogel-duikbom en de daling van het moederschip — allemaal getekend uit de vectoren die in de ROM staan:

![Hoofd-animatie: een alien-zwenking, een vogel-duikbom met bom, en de gestage daling van het moederschip, gegenereerd uit de originele ROM-bewegingsvectoren](../00_overview_flight_patterns.svg)

Bronbestand: [`00_overview_flight_patterns.svg`](../00_overview_flight_patterns.svg).

---

## 🦅 De vogel, fase voor fase

Een Phoenix-vogel is niet één sprite. Hij komt uit het ei, groeit, valt aan en explodeert — zes onderscheiden animatiefases, elk gereconstrueerd uit de graphics-ROM:

| Ei komt uit | Kleine vogel wiekt | Volgroeide spanwijdte |
| --- | --- | --- |
| <img src="../01_egg_hatching.svg" width="230" alt="Een ei dat uitkomt tot een vogel"> | <img src="../02_small_bird_flapping.svg" width="230" alt="Een kleine vogel die met de vleugels wiekt, frame A en B"> | <img src="../03_grown_bird_matrix.svg" width="230" alt="De 4x4-matrix van vleugelstanden van een volgroeide vogel"> |
| **Duikaanval** | **Explosie en bonus** | **Daling moederschip** |
| <img src="../04_dive_bombing_attack.svg" width="230" alt="Een vogel die op de speler duikt en een bom laat vallen"> | <img src="../05_bird_explosion_bonus.svg" width="230" alt="Een vogel die uiteenspat in deeltjes met 500 punten bonus"> | <img src="../09_mothership_descent_trajectory.svg" width="230" alt="Het moederschip dat langs zijn vaste traject daalt"> |

---

## 🔡 Waar alles werkelijk uit bestaat

De diagrammen hierboven zijn interpretaties. De vellen hieronder niet: die zijn rechtstreeks gerenderd uit de gedecodeerde graphics-ROM en kleur-PROM, met exact dezelfde paletrekensom als het draaiende spel.

Phoenix heeft geen sprite-engine. Elk object op het scherm is een handvol **8×8-karakters** die naar het schermgeheugen worden geschreven, en het karakternummer bepaalt zélf de kleur — bit 5-7 kiezen een van de acht kleurgroepen in de PROM-tabel. Daarom lijkt elk blok van 32 karakters op één familie:

![De volledige voorgrondset van 256 karakters, in acht kleurgroepen, waarmee zichtbaar wordt dat het karakternummer de kleurfamilie kiest](../sprites/character-set-foreground.nl.svg)

Sterren, planeten, het moederschip en de aliens komen uit een tweede, onafhankelijke set:

![De volledige achtergrondset van 256 karakters, in acht kleurgroepen](../sprites/character-set-background.nl.svg)

### De sequenties, met hun karaktersamenstelling

Phoenix heeft een kleine familie **drawNxN-routines**, en welke routine een object tekent bepaalt zijn afmeting én de volgorde waarin de karakters worden weggeschreven. Ze werken allemaal hetzelfde: twee karakters vullen een kolom van boven naar beneden, daarna stapt de routine zijwaarts naar de volgende kolom. Bij elk vel hieronder staat welke routine is gebruikt.

Onder elk frame staan de **karaktercodes** waaruit het is opgebouwd — zoek die op in de sets hierboven en je ziet precies welke pixels de hardware ophaalde.

**Het spelerschip** — acht poses, elk vier karakters, getekend als 2×2-blok uit `phoenix_sprite_character_block_shapes`:

![De acht poses van het spelerschip, elk opgebouwd uit vier 8x8-karakters in een 2x2-blok, met de karaktercodes eronder](../sprites/sequence-player-ship.nl.svg)

<img src="../sprites/animation-player-ship.nl.svg" width="300" alt="De acht poses van het spelerschip als draaiende animatie">

**De formatie-alien** — en dat is niet één sprite. Terwijl hij schuift, klimt en duikt wisselt het spel van *blokgrootte*: `sprite_rendering.c` kiest tijdens runtime `1x1`, `2x1`, `1x2` of `2x2` uit het control-byte van het object. Geen tabel bevat die maat, dus deze poses zijn afgelezen uit het voorgrond-schermgeheugen van de gecommitte opname `c-last-grown-bird.bin.gz`.

In horizontale vlucht, twee karakters naast elkaar:

![Zes poses van de formatie-alien in horizontale vlucht, elk twee karakters breed](../sprites/sequence-alien-level.nl.svg)

<img src="../sprites/animation-alien-level.nl.svg" width="240" alt="De alien in horizontale vlucht">

Klimmend, één karakter breed en twee hoog — hetzelfde beest recht van voren:

![Zes klimmende poses van de formatie-alien, elk een karakter breed en twee hoog](../sprites/sequence-alien-climb.nl.svg)

<img src="../sprites/animation-alien-climb.nl.svg" width="200" alt="De klimmende alien">

Duikend en zwenkend, zijn breedste vorm:

![Acht duikende en zwenkende poses van de formatie-alien, elk een 2x2-blok](../sprites/sequence-alien-dive.nl.svg)

<img src="../sprites/animation-alien-dive.nl.svg" width="240" alt="De duikende alien">

Dezelfde scan over dezelfde opname leverde ook de 3×2-explosieblokken hieronder op, wat een onafhankelijke controle is dat deze manier van aflezen deugt.

Poses groeperen op maat zegt welke vormen bestaan, maar niet in welke volgorde het spel ze toont. Eén object frame voor frame volgen wel — hier verlaat één alien de formatie en zakt veertien rijen op de speler af, terwijl zijn blokgrootte meewisselt:

![Eén alien gevolgd door een duik, met wisselende pose en blokgrootte op volgorde](../sprites/sequence-alien-dive-order.nl.svg)

<img src="../sprites/animation-alien-dive-order.nl.svg" width="240" alt="De duik van één alien in de volgorde waarin hij plaatsvond">

**De piloot van het moederschip** — het hoogste blok dat een van deze routines tekent, vier rijen bij twee kolommen:

![De acht animatieframes van de piloot en antenne van het moederschip, elk acht achtergrondkarakters](../sprites/sequence-mothership-pilot.nl.svg)

<img src="../sprites/animation-mothership-pilot.nl.svg" width="260" alt="De acht frames van de piloot van het moederschip als animatie">

**Een explosie** — acht frames uit `phoenix_alien_explosion_frames`, en hier zit een omweg in. Die bytes zijn *geen* karaktercodes: `alien_logic.c` maakt er met `0x1700 | byte` een adres van en roept dan `drawNx2` met n=3 aan, die daar zes karakters ophaalt uit `phoenix_shield_and_drawnx2_shapes`. Eén frame is dus een 3×2-blok, geen enkel karakter:

![De acht explosieframes, elk een 3x2-blok van zes karakters via een adrestabel, met de karaktercodes eronder](../sprites/sequence-explosion.nl.svg)

<img src="../sprites/animation-explosion.nl.svg" width="330" alt="De acht frames van de explosie als draaiende animatie">

**De bonusexplosie** — dezelfde 3×2-routine, maar twee keer aangeroepen met vaste adressen, één per helft van een bredere explosie:

![De twee helften van de bonusexplosie, elk een 3x2-blok van zes karakters, met de karaktercodes eronder](../sprites/sequence-bonus-explosion.nl.svg)

<img src="../sprites/animation-bonus-explosion.nl.svg" width="330" alt="De twee helften van de bonusexplosie afwisselend als animatie">

### De vogels

Vogels volgen een derde route. `drawbirdobject` zoekt eerst een **breedte** voor het vormtype op in `phoenix_bird_draw_entries`, dan een **pointer** naar de karakterdata in `phoenix_bird_shape_pointers`, waarna `draw_bird_shape_350c` die data per twee karakters afloopt. Een vogel is dus drie tot zeven kolommen breed, puur afhankelijk van zijn type — het ei en de volgroeide vogel zijn dezelfde routine met een ander aantal kolommen:

![Acht vogelvormtypes naast elkaar, van een klein rond ei via een uitkomende vogel tot een volgroeide vogel met volle spanwijdte](../sprites/sequence-bird-growth.nl.svg)

<img src="../sprites/animation-bird-growth.nl.svg" width="420" alt="De vogelvormtypes op volgorde van breedte, van ei tot volle spanwijdte">

Elk type heeft vier eigen frames. **De kleine vogel**, zes karakters breed:

![De vier animatieframes van de kleine vogel, met de karaktercodes eronder](../sprites/sequence-bird-small.nl.svg)

<img src="../sprites/animation-bird-small.nl.svg" width="380" alt="De vier frames van de kleine vogel als animatie">

**De volgroeide vogel**, zeven karakters breed — de breedste sprite die de routine tekent:

![De vier animatieframes van de volgroeide vogel, met de karaktercodes eronder](../sprites/sequence-bird-grown.nl.svg)

<img src="../sprites/animation-bird-grown.nl.svg" width="420" alt="De vier frames van de volgroeide vogel als animatie">

### Deze vellen opnieuw genereren

Ze komen allemaal uit één script, te draaien vanuit de repository-root:

```sh
python3 c-phoenix/tools/generate_sprite_sheets.py
```

Het leest `phoenix_render_assets.h` en `phoenix_tables.c` voor alles wat wél in een tabel staat, en de gecommitte opname `c-last-grown-bird.bin.gz` voor de objecten waarvan de maat pas tijdens runtime wordt bepaald. Elke run meldt welke opname is gebruikt.

Die standaardopname bevat geen moederschip en geen schild van meerdere karakters. Wil je die erbij, maak dan eerst de rijkere bird-investigation-sessie en wijs het script daarnaar — opnieuw vanuit de repository-root:

```sh
make -C c-phoenix tracerun \
  COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt \
  COMPARE_FRAMES=13935 \
  COMPARE_NAME=bird-investigation \
  COMPARE_STOP_AFTER=999999

python3 c-phoenix/tools/generate_sprite_sheets.py \
  --dump /tmp/port_bird-investigation.bin
```

`tracerun` draait eerst `comparerun`, dus het zusterproject JPhoenix moet gebouwd zijn (JDK 11+). Het schrijft `/tmp/port_bird-investigation.bin` — let op het underscore na `port` — plus `/tmp/ref_bird-investigation.bin` voor de emulatorkant. Dumps blijven bewust in `/tmp`; zie [`context/traces/README.nl.md`](../../context/traces/README.nl.md) voor waarom ze niet worden gecommit.

**Het spelerschild** — zestien karakters in een 4×4-blok, de grootste enkele sprite in het spel. Net als bij de alien is die maat een runtime-beslissing, dus ook dit is uit een opname afgelezen:

![Het spelerschild zoals getekend in een opgenomen sessie, een 4x4-blok van zestien karakters, met de karaktercodes erbij](../sprites/sequence-shield.nl.svg)

> **Nog open: het moederschip.** Achtergrond-RAM scannen op kleurgroep kan een moederschipromp niet onderscheiden van een volgroeide vogel — beide zitten in dezelfde hoge groepen, en die scan leverde twee keer vogels op met het label romp. Het object identificeren vraagt om zijn RAM-slot in plaats van zijn kleuren, en dat is werk voor de visual tracer.

Zowel de stilstaande vellen als de bewegende versies worden gegenereerd door [`tools/generate_sprite_sheets.py`](../../tools/generate_sprite_sheets.py) uit `phoenix_render_assets.h` en `phoenix_tables.c`. Niets erin is met de hand getekend; verandert de ROM-data, dan veranderen de vellen mee.

> **Nog toe te voegen:** de moederschipexplosie. Die tekent net als de explosies uit `phoenix_shield_and_drawnx2_shapes`, maar zijn aanroepplek is nog niet uitgezocht, dus hij blijft eruit in plaats van dat er wordt gegokt.

---

## 🎨 Vliegpatronen & Trajecten

Deze map telt 128 SVG-bestanden: de 78 vluchtpatronen hieronder plus de spritevellen uit de vorige sectie. Ze staan als lijst omdat het er zo veel zijn; open een bestand om het te bekijken.

### 👾 Alien Cluster A: Wave 1 & 3 Patronen (ROM `$1000–$13FF`)
- [`07_alien_closed_loop_cluster_a.svg`](../07_alien_closed_loop_cluster_a.svg) — Cluster A overzichts-animatie
- [`cluster_a/pattern_01.svg`](../cluster_a/pattern_01.svg) t/m [`cluster_a/pattern_18.svg`](../cluster_a/pattern_18.svg) — 18 gesloten-lus vectoriële vliegpatronen.

### 🛸 Alien Cluster B: Breakout & Escort Patronen (ROM `$2C00–$2FFF`)
- [`08_alien_breakout_cluster_b.svg`](../08_alien_breakout_cluster_b.svg) — Cluster B overzichts-animatie
- [`cluster_b/pattern_19.svg`](../cluster_b/pattern_19.svg) t/m [`cluster_b/pattern_36.svg`](../cluster_b/pattern_36.svg) — 18 breakout- en escort-aanvalspatronen.

### 🪶 Vogel AI Behavior Scripts (ROM `$3F00–$3F7F`)
- [`bird_scripts/bird_script_00.svg`](../bird_scripts/bird_script_00.svg) t/m [`bird_scripts/bird_script_15.svg`](../bird_scripts/bird_script_15.svg) — 16 AI-gedragscripts.

### 🎯 Vogel Duik- & Spawn-posities (ROM `$3DC0–$3DDF`)
- [`bird_dive_spawns/dive_spawn_00.svg`](../bird_dive_spawns/dive_spawn_00.svg) t/m [`bird_dive_spawns/dive_spawn_15.svg`](../bird_dive_spawns/dive_spawn_15.svg) — 16 start- en duik-coördinaten.

### 🦅 Vogel- & Moederschip Animaties
- 🥚 [`01_egg_hatching.svg`](../01_egg_hatching.svg) — Ei naar vogel transformatie
- 🪶 [`02_small_bird_flapping.svg`](../02_small_bird_flapping.svg) — Wieken van vleugels (Frame A & B)
- 🦅 [`03_grown_bird_matrix.svg`](../03_grown_bird_matrix.svg) — Volgroeide vogel 4x4 spanwijdte
- 💣 [`04_dive_bombing_attack.svg`](../04_dive_bombing_attack.svg) — Duikvlucht & bommenwerpen
- 💥 [`05_bird_explosion_bonus.svg`](../05_bird_explosion_bonus.svg) — Deeltjes-explosie & 500pt bonusscore
- 🎬 [`06_intro_splash_bird.svg`](../06_intro_splash_bird.svg) — Intro splash vogel (Attract Mode)
- 🚀 [`09_mothership_descent_trajectory.svg`](../09_mothership_descent_trajectory.svg) — Moederschip gestaag daal-traject

---

## 🔗 Knowledge Graph Koppelingen

Alle documenten en animaties in deze directory zijn 1-op-1 gekoppeld aan de C-bronbestanden en de Knowledge Graph onder `../../c-annotated/nl/`:
* [`phoenix_tables.c`](../../phoenix_tables.c) → [`phoenix-tables.md`](../../c-annotated/nl/phoenix-tables.md)
* [`alien_logic.c`](../../alien_logic.c) → [`alien-logic.md`](../../c-annotated/nl/alien-logic.md)
* [`bird_logic.c`](../../bird_logic.c) → [`bird-logic.md`](../../c-annotated/nl/bird-logic.md)
* [`bird_wave_behavior.c`](../../bird_wave_behavior.c) → [`bird-wave-behavior.md`](../../c-annotated/nl/bird-wave-behavior.md)
* [`attract_mode.c`](../../attract_mode.c) → [`attract-mode.md`](../../c-annotated/nl/attract-mode.md)
