# Player Logic (`player_logic.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`player_logic.c`](../../player_logic.c). Deze module beheert het spelerschip, joystickinvoer, schild-activatie, kogelspawning en de rendering van het speler-krachtveld.

---

## Inhoudsopgave
1. [Speler Update-lus](#1-speler-update-lus)
2. [Besturing & X-positie](#2-besturing--x-positie)
3. [Kogelmechanica & Spawning](#3-kogelmechanica--spawning)
4. [Schild- & Krachtveldbeheer](#4-schild--krachtveldbeheer)
5. [Scherm RAM-controller](#5-scherm-ram-controller)

---

## 1. Speler Update-lus

### `player_update`
#### **Beschrijving**
De functie [`player_update`](../../player_logic.c#L35-L42) (Z80 ROM: `$0876–$0885`) is de centrale per-frame update-routine voor de speler.

#### **Context & Aanroep**
Aangeroepen in elke frame-update van de actieve game-loop (alien- en vogel-levels):
```c
player_update();
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../../coverage.c#L12)
  - [`player_data_controller`](#player_data_controller) — [`player_logic.c#L37`](../../player_logic.c#L37)
  - [`copy_current_to_old_player_data`](#copy_current_to_old_player_data) — [`player_logic.c#L38`](../../player_logic.c#L38)
  - [`update_player_position_bullet_shield`](#update_player_position_bullet_shield) — [`player_logic.c#L39`](../../player_logic.c#L39)
  - `get_screen_ram_address_for_player_ship` — [`hw_video_audio.c`](../../hw_video_audio.c)
  - [`map_player_ship_position`](#map_player_ship_position) — [`player_logic.c#L41`](../../player_logic.c#L41)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2000_alien_wave_main_loop`](alien-wave.md#l2000_alien_wave_main_loop) — [`alien_wave.c#L222`](../../alien_wave.c#L222)
  - [`process_birds`](bird-logic.md#process_birds) — [`bird_logic.c#L29`](../../bird_logic.c#L29)
  - [`state_play_frame_update`](state-play.md#state_play_frame_update) — [`state_play.c`](../../state_play.c)

---

### `copy_current_to_old_player_data`
#### **Beschrijving**
De functie [`copy_current_to_old_player_data`](../../player_logic.c#L49-L58) (Z80 ROM: `$0886–$0897`) verschuift de huidige positiegegevens van de speler en kogels naar de 'oude' geheugenbuffers ten behoeve van het schonen van het scherm in het volgende frame.

---

## 2. Besturing & X-positie

### `move_player`
#### **Beschrijving**
De functie [`move_player`](../../player_logic.c#L114-L146) (Z80 ROM: `$08C4–$08F3`) verwerkt schild-activatie en joystick-invoer.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`draw_shields`](#draw_shields) — [`player_logic.c#L118`](../../player_logic.c#L118)
  - `check_input_bits` — [`platform_sdl.c`](../../platform_sdl.c)
  - [`update_player_ship_x`](#update_player_ship_x) — [`player_logic.c#L142`](../../player_logic.c#L142)
  - [`get_player_ship_animation_frame_values`](#get_player_ship_animation_frame_values) — [`player_logic.c#L145`](../../player_logic.c#L145)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`update_player_position_bullet_shield`](#update_player_position_bullet_shield) — [`player_logic.c#L95`](../../player_logic.c#L95)

#### **Stap-voor-stap werking**
1. **Schild actief check:** Als beweging geblokkeerd is (`PlayerState & 0x01 == 0`), roept hij [`draw_shields`](#draw_shields) aan en stopt.
2. **Schildknop flankdetectie:** Detecteert of de schildknop (`BTN_SHIELD`) nieuw ingedrukt is via `check_input_bits`. Zo ja: activeert het schild voor 5 seconden (`ShieldCount = SHIELD_DURATION_INITIAL`), blokkeert spelerbeweging en zet `state.M4362 = 0x40`.
3. **Beweging & Frame:** Roept [`update_player_ship_x`](#update_player_ship_x) aan en werkt het sprite-frame bij.

---

### `update_player_ship_x`
#### **Beschrijving**
De functie [`update_player_ship_x`](../../player_logic.c#L66-L87) (Z80 ROM: `$0900–$0921`, `$0926–$092E`) leest de joystick in (`state.IN0Current`) en beweegt X tussen grenzen `0x0D` (links) en `0xC0` (rechts).

---

### `map_player_ship_position`
#### **Beschrijving**
De functie [`map_player_ship_position`](../../player_logic.c#L153-L161) (Z80 ROM: `$097A–$0995`) raadpleegt `phoenix_player_x_position_mapping` om de effectieve botsings-kaders `state.M439E` en `state.M439F` te berekenen.

---

## 3. Kogelmechanica & Spawning

### `get_assigned_player_bullet_tile` & `spawn_player_bullet`
#### **Beschrijving**
Functie [`get_assigned_player_bullet_tile`](../../player_logic.c#L168-L182) (Z80 ROM: `$0930–$093C`) vuurt op flank-detectie van `BTN_FIRE` een kogel af via [`spawn_player_bullet`](../../player_logic.c#L203-L229) (Z80 ROM: `$093D–$0961`).

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`update_player_bullet_y`](#update_player_bullet_y) — [`player_logic.c#L170`](../../player_logic.c#L170)
  - `check_input_bits` — [`platform_sdl.c`](../../platform_sdl.c)
  - [`get_player_ship_animation_frame_values`](#get_player_ship_animation_frame_values) — [`player_logic.c#L226`](../../player_logic.c#L226)

---

### `update_player_bullet_y`
#### **Beschrijving**
De functie [`update_player_bullet_y`](../../player_logic.c#L236-L244) (Z80 ROM: `$0964–$0975`) verplaatst de spelerkogel 8 pixels omhoog (`Y -= 8`). Zodra de top van het scherm bereikt is (`Y < 0x1F`), wordt de kogel verwijderd (`bullet_state &= 0xF7`).

---

## 4. Schild- & Krachtveldbeheer

### `draw_shields` & `shields_expired`
#### **Beschrijving**
De functie [`draw_shields`](../../player_logic.c#L294-L320) (Z80 ROM: `$0AA0–$0AC1`) animeert en rendert de 4x4 tegelmatrix van het speler-krachtveld. Zodra het schild verloopt (`ShieldCount == 0xC0`), wist [`shields_expired`](../../player_logic.c#L276-L287) het krachtveld en herstelt de spelerstatus.

---

## 5. Scherm RAM-controller

### `player_data_controller`
#### **Beschrijving**
De functie [`player_data_controller`](../../player_logic.c#L250-L267) (Z80 ROM: `$0700–$0717`) ververst de VRAM-objecten voor het spelerschip en de spelerkogels tussen adresseringen `0x43C0` en `0x43EC`.
