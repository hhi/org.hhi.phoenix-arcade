# Bird Logic (`bird_logic.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`bird_logic.c`](../../bird_logic.c). Deze module regelt het hoofd-updateproces van de vogelgolven: de spelfasen 4–8, met de actieve vogel-fade-in-fasen 5 en 7. De module omvat eieren uitbroeden, vluchtpaden en het tekenen van de vogel-objecten.

---

## Inhoudsopgave
1. [Hoofdlus van de Vogel-golf](#1-hoofdlus-van-de-vogel-golf)
2. [Vluchtpad & Botsingsafhandeling](#2-vluchtpad--botsingsafhandeling)
3. [Vogel Rendering Routines](#3-vogel-rendering-routines)

---

## 1. Hoofdlus van de Vogel-golf

### `process_birds`
#### **Beschrijving**
De functie [`process_birds`](../../bird_logic.c#L27-L66) (Z80 ROM: `$3400–$344D`) is de hoofd-updatelus voor de vogelgolven (spelfasen 4–8; actieve vogel-fade-in-fasen 5 en 7).

#### **Context & Aanroep**
Wordt vanuit de hoofdgame-state machine aangeroepen tijdens vogel-levels:
```c
process_birds();
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../../coverage.c#L12)
  - [`player_update`](player-logic.md#player_update) — [`player_logic.c#L10`](../../player_logic.c#L10)
  - [`collision_detection_for_birds`](collision-detection.md#collision_detection_for_birds) — [`collision_detection.c`](../../collision_detection.c)
  - [`birds_vertical_movement_update`](birds-vertical-movement.md#birds_vertical_movement_update) — [`birds_vertical_movement.c`](../../birds_vertical_movement.c)
  - [`check_bird_formation_player_collision`](collision-detection.md#check_bird_formation_player_collision) — [`collision_detection.c`](../../collision_detection.c)
  - [`l3462_no_birds_left`](bird-wave-behavior.md#l3462_no_birds_left) — [`bird_wave_behavior.c`](../../bird_wave_behavior.c)
  - [`update_second_bird_bank`](bird-wave-behavior.md#update_second_bird_bank) — [`bird_wave_behavior.c`](../../bird_wave_behavior.c)
  - [`draw_first_4_bird_objects`](#draw_first_4_bird_objects) — [`bird_logic.c#L81`](../../bird_logic.c#L81)
  - [`draw_second_4_bird_objects`](#draw_second_4_bird_objects) — [`bird_logic.c#L93`](../../bird_logic.c#L93)
  - [`refresh_bird_flight_parameters`](bird-wave-behavior.md#refresh_bird_flight_parameters) — [`bird_wave_behavior.c`](../../bird_wave_behavior.c)
  - [`update_first_four_birds`](bird-wave-behavior.md#update_first_four_birds) — [`bird_wave_behavior.c`](../../bird_wave_behavior.c)
  - [`update_second_four_birds`](bird-wave-behavior.md#update_second_four_birds) — [`bird_wave_behavior.c`](../../bird_wave_behavior.c)
  - `try_spawn_bird_dive_bomb` — [`bird_wave_behavior.c`](../../bird_wave_behavior.c)
  - `process_enemy_bombs` — [`weapon_collision.c#L17`](../../weapon_collision.c#L17)
  - [`handle_animations_for_killed_aliens`](alien-logic.md#handle_animations_for_killed_aliens) — [`alien_logic.c#L195`](../../alien_logic.c#L195)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`level_1_3_B_player_alive_aliens`](state-play.md#level_1_3_b_player_alive_aliens) — [`state_play.c#L16`](../../state_play.c#L16)

#### **Geheugen- & Structuur-context**
- `state.BirdsLeft`: Aantal resterende levende vogels.
- `state.Counter9B`: Frame-teller gebruikt om de updates van de eerste bank (vogels 0-3) en tweede bank (vogels 4-7) af te wisselen.

#### **Stap-voor-stap werking**
1. **Speler & Verticale beweging:** Update de speler (`player_update`), verwerkt vogelbotsingen en voert de verticale bewegingsupdate van de vogels uit.
2. **Geen vogels meer (`BirdsLeft == 0`):** Schakelt over naar de ronde-afronding via [`l3462_no_birds_left`](bird-wave-behavior.md#l3462_no_birds_left).
3. **Formatie van 4 of meer vogels (`BirdsLeft >= 4`):** Wisselt op basis van `state.Counter9B & 0x01` af tussen het updaten van de tweede vogelbank (`update_second_bird_bank`) of de eerste vogelbank (`draw_first_4_bird_objects`, `refresh_bird_flight_parameters`, etc.).
4. **Formatie van minder dan 4 vogels:** Tekent en update beide banken direct in hetzelfde frame.

---

## 2. Vluchtpad & Botsingsafhandeling

### `bird_flight_path`
#### **Beschrijving**
De functie [`bird_flight_path`](../../bird_logic.c#L69-L73) verwerkt de geometrische duikvluchtpaden en voert de botsingsdetectie voor vogels uit.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../../coverage.c#L12)
  - [`collision_detection_for_birds`](collision-detection.md#collision_detection_for_birds) — [`collision_detection.c`](../../collision_detection.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`level_1_3_B_player_alive_aliens`](state-play.md#level_1_3_b_player_alive_aliens) — [`state_play.c#L16`](../../state_play.c#L16)

---

## 3. Vogel Rendering Routines

### `draw_first_4_bird_objects`
#### **Beschrijving**
De functie [`draw_first_4_bird_objects`](../../bird_logic.c#L81-L87) (Z80 ROM: `$3474–$3485`) tekent de sprite-objecten voor vogels 0 tot en met 3.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `drawbirdobject` — [`sprite_rendering.c`](../../sprite_rendering.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`process_birds`](#process_birds) — [`bird_logic.c#L44`](../../bird_logic.c#L44), [`L53`](../../bird_logic.c#L53)
  - [`update_second_bird_bank`](bird-wave-behavior.md#update_second_bird_bank) — [`bird_wave_behavior.c`](../../bird_wave_behavior.c)

#### **Stap-voor-stap werking**
Doorloopt de RAM-structuren van adres `0x4B70` tot `0x4B90` in stappen van 8 bytes (`addr += 0x08`) en roept `drawbirdobject(addr)` aan voor elk van de eerste 4 vogel-records.

---

### `draw_second_4_bird_objects`
#### **Beschrijving**
De functie [`draw_second_4_bird_objects`](../../bird_logic.c#L93-L99) (Z80 ROM: `$3486–$3497`) tekent de sprite-objecten voor vogels 4 tot en met 7.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `drawbirdobject` — [`sprite_rendering.c`](../../sprite_rendering.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`process_birds`](#process_birds) — [`bird_logic.c#L54`](../../bird_logic.c#L54)
  - [`update_second_bird_bank`](bird-wave-behavior.md#update_second_bird_bank) — [`bird_wave_behavior.c`](../../bird_wave_behavior.c)

#### **Stap-voor-stap werking**
Doorloopt de RAM-structuren van adres `0x4B90` tot `0x4BB0` in stappen van 8 bytes (`addr += 0x08`) en roept `drawbirdobject(addr)` aan voor elk van de laatste 4 vogel-records.
