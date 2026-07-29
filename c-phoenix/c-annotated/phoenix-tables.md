# Phoenix Static ROM Tables (`phoenix_tables.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van de statische gegevensbestanden in [`phoenix_tables.c`](../phoenix_tables.c). Deze module bevat alle uit de Arcade ROM geëxtraheerde opzoektabellen, bewegingspatronen, botsings-kaders en sprite-shape pointers.

---

## Inhoudsopgave
1. [Overzicht Statische Tabellen](#1-overzicht-statische-tabellen)
2. [Speler- & Niveau-instellingen](#2-speler--niveau-instellingen)
3. [Alien- & Vogelgedragtabellen](#3-alien--vogelgedragtabellen)

---

## 1. Overzicht Statische Tabellen

### Statische Gegevensbronnen
`phoenix_tables.c` is het centrale archief van alle ROM-opzoektabellen uit de originele Z80 machinecode, waardoor de C-port 100% getrouw draait zonder afhankelijkheid van externe ROM-bestanden.

#### **Knowledge Graph Koppelingen**
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`init_player_data_structure`](state-init.md#init_player_data_structure) — [`state_init.c`](../state_init.c)
  - [`init_global_level_data`](init-global-level-data.md#init_global_level_data) — [`init_global_level_data.c`](../init_global_level_data.c)
  - [`map_player_ship_position`](player-logic.md#map_player_ship_position) — [`player_logic.c`](../player_logic.c)
  - [`l20e8`](player-explosion.md#l20e8) — [`player_explosion.c`](../player_explosion.c)
  - [`l3844_small_bird_hit`](collision-detection.md#l3844_small_bird_hit) — [`collision_detection.c`](../collision_detection.c)

---

## 2. Speler- & Niveau-instellingen

### `phoenix_player_init_data` & `phoenix_player_x_position_mapping`
- `phoenix_player_init_data[0x20]`: Z80 ROM `$0560–$057F`. Standaard startwaarden voor de speler- en kogel-datastructuren in RAM.
- `phoenix_player_x_position_mapping[0x10]`: Z80 ROM `$0B38–$0B47`. Zet de X-coördinaat om naar exacte botsings-grenzen `M439E` en `M439F`.

---

## 3. Alien- & Vogelgedragtabellen

### `phoenix_alien_movement_cluster_a` & `phoenix_bird_behaviour_scripts`
- `phoenix_alien_movement_cluster_a`: Z80 ROM `$1000–$13FF`. Bevat de vectoriële vliegpatronen van de zwerm-aliens in levels 1 en 3.
- `phoenix_bird_behaviour_scripts`: Z80 ROM `$3F00–$3FFF`. Bevat het AI-gedrag (klimmen, dalen, eierleggen en duikvluchten) van de vogels in levels 5 en 7.
