# Phoenix Animaties & Trajecten Gids (`c-phoenix/animations`)

Welkom in het centrale visuele archief van de *Phoenix* Arcade Game (`c-phoenix`). Deze directory bevat functionele, geheugen- en visuele analyses van zowel de **vogel-animaties** als de **vectoriële vliegtrajecten** van aliens, vogels en het moederschip.

## Bronstatus

De bron van waarheid is, in deze volgorde: **Z80 ASM/ROM → C-port → geannoteerde analyse → deze visualisaties**. De SVG's maken ROM- en C-data inzichtelijk, maar vervangen die bron niet. Een conclusie zonder koppeling naar ASM, ROM of C-code is een interpretatie die nog gecontroleerd moet worden.

---

## 🗂️ Inhoudsopgave

1. 🚀 [`animation-trajectory.md`](animation-trajectory.md) — **Diepgaande analyse van alle voorgeschreven vliegpatronen, RAM-datastructuren (`$4000-$4BFF`), Z80 ROM-clusterindeling, overkoepelende hoofd-animatie en 78 SVG-animaties.**
2. 📐 [`animation-trajectory-detailed.md`](animation-trajectory-detailed.md) — **Gedetailleerde stap-voor-stap coördinatentabellen op het scherm-grid per individueel patroon (stap #, vector index, dX, dY, cumulatief X/Y).**
3. 🦅 [`bird-animations.md`](bird-animations.md) — **Visuele gids van alle 6 vogel-animatiefases (van ei tot volgroeide vogel en explosie).**

---

## 🏛️ Waarom Verschillende ROM Clusters & Hoofdstukindeling?

- **Cluster A (ROM `$1000–$13FF` / EPROM Chip 1):** Bevat **Patronen 01 t/m 18** voor de geordende formatiegolven in **Alien Wave 1 & 3**.
- **Cluster B (ROM `$2C00–$2FFF` / EPROM Chip 3):** Bevat **Patronen 19 t/m 36** voor **Breakout-aliens** en **Moederschip-escorts** (Levels 9, 10, 11).
- **Hoofdstukindeling:** Volgt exact de 4 fysieke game-entiteit subsystemen uit de Arcade Z80 engine (Wave 1/3 Aliens, Breakout/Escort Aliens, Wave 5/7 Vogel AI & Duik-spawns, Moederschip & Attract Mode).

---

## 🎬 Overkoepelende Hoofd-Animatie

- 🚀 [`00_overview_flight_patterns.svg`](../00_overview_flight_patterns.svg) — **Bovenliggende hoofd-animatie die de simultane werking van alle vectoriële vliegpatronen (alien-duik, vogel-sinus en moederschip-daling) demonstreert.**

---

## 🎨 Vliegpatronen & Trajecten (78 SVG-bestanden)

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
