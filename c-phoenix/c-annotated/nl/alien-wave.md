# Alien Wave (`alien_wave.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een diepgaande geannoteerde analyse van alle functies in [`alien_wave.c`](../../alien_wave.c). Deze module bevat de hoofd-lussen en dispatch-routines voor de alien-golven (levels 1, 3 en B).

---

## Inhoudsopgave
1. [Hoofdlus van de Alien Wave](#1-hoofdlus-van-de-alien-wave)
2. [Frame Dispatches & Interleaving](#2-frame-dispatches--interleaving)
3. [Ronde-overgangen & Wave Completion](#3-ronde-overgangen--wave-completion)
4. [Achtergrond & Sterren-scrolling](#4-achtergrond--sterren-scrolling)
5. [Breakout & Retarget Dispatcher](#5-breakout--retarget-dispatcher)

---

## 1. Hoofdlus van de Alien Wave

### `l2000_alien_wave_main_loop`
#### **Beschrijving**
De functie [`l2000_alien_wave_main_loop`](../../alien_wave.c#L220-L248) (Z80 ROM: `$2000–$202A`) is de centrale update-lus voor de alien-golven (levels 1, 3 en B) zolang de speler in leven is.

#### **Context & Aanroep**
Wordt vanuit de hoofdgame-state machine aangeroepen tijdens het spelen van een alien-level:
```c
l2000_alien_wave_main_loop();
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../../coverage.c#L12)
  - [`player_update`](player-logic.md#player_update) — [`player_logic.c#L10`](../../player_logic.c#L10)
  - [`check_enemy_bullet_to_player_collision`](weapon-collision.md#check_enemy_bullet_to_player_collision) — [`weapon_collision.c#L12`](../../weapon_collision.c#L12)
  - `l24a0` — [`sound_dispatcher.c#L15`](../../sound_dispatcher.c#L15)
  - [`l21ba`](#l21ba) — [`alien_wave.c:L230`](../../alien_wave.c#L230)
  - [`l2130`](#l2130) — [`alien_wave.c:L235`](../../alien_wave.c#L235)
  - [`l2146`](#l2146) — [`alien_wave.c:L246`](../../alien_wave.c#L246)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`state_play_frame_update`](state-play.md#state_play_frame_update) — [`state_play.c#L105`](../../state_play.c#L105)

#### **Geheugen- & Structuur-context**
- `state.M435F`: Frame-teller die 0..3 interleaved sub-frames aanstuurt (`state.M435F & 0x03`).
- `state.AliensLeft`: Aantal resterende levende aliens.
- `state.M435E`: Vlag voor versnelde beweging bij minder dan 5 aliens over (`0xFF` activeert de snelle interleaved modus).

#### **Stap-voor-stap werking**
1. **Speler & Botsingen:** Verwerkt de speler-invoer via [`player_update`](player-logic.md#player_update), controleert vijandelijke kogel-inslagen op het spelerschip en roept `l24a0` aan voor geluid.
2. **Sub-frame teller:** Leest `masked_counter = state.M435F & 0x03` en verhoogt `state.M435F`.
3. **Geen aliens meer (`AliensLeft == 0`):** Schakelt over naar de ronde-overgangafhandeling via [`l21ba(masked_counter)`](#l21ba).
4. **Normale formatie (`AliensLeft >= 5`):** Voert de standaard 4-frame gedistribueerde taken uit via [`l2130(masked_counter)`](#l2130).
5. **Minder dan 5 aliens left:** Schakelt over naar de snellere tak via [`l2146(masked_counter)`](#l2146) zodra `state.M435E != 0`.

---

## 2. Frame Dispatches & Interleaving

### `l2130`
#### **Beschrijving**
De functie [`l2130`](../../alien_wave.c#L205-L212) (Z80 ROM: `$2130–$2145`) verdeelt de zware reken- en render-taken van de alien-formatie over 4 opeenvolgende sub-frames (interleaving modulo 4).

#### **Context & Aanroep**
Aangeroepen vanuit `l2000_alien_wave_main_loop`:
```c
l2130(masked_counter);
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l2150`](#l2150) — [`alien_wave.c:L207`](../../alien_wave.c#L207)
  - [`l2160`](#l2160) — [`alien_wave.c:L208`](../../alien_wave.c#L208)
  - [`l2170`](#l2170) — [`alien_wave.c:L209`](../../alien_wave.c#L209)
  - [`l2180`](#l2180) — [`alien_wave.c:L210`](../../alien_wave.c#L210)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2000_alien_wave_main_loop`](#l2000_alien_wave_main_loop) — [`alien_wave.c:L235`](../../alien_wave.c#L235)

#### **Stap-voor-stap werking**
Voert afhankelijk van `masked_counter` (0..3) een van de 4 specifieke taakbundels uit:
- `case 0`: Roept [`l2150`](#l2150) aan (Object RAM update & botsing met speler).
- `case 1`: Roept [`l2160`](#l2160) aan (Achtergrond, bommen, beweging & explosies).
- `case 2`: Roept [`l2170`](#l2170) aan (Sprite-animatie & dive-bomb triggers).
- `case 3`: Roept [`l2180`](#l2180) aan (VRAM-berekeningen & explosies).

---

### `l2150`
#### **Beschrijving**
De functie [`l2150`](../../alien_wave.c#L134-L138) (Z80 ROM: `$2150–$215F`) voert de eerste sub-frametaak uit van de interleaved cyclus.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`alien_data_controller`](alien-logic.md#alien_data_controller) — [`alien_logic.c#L274`](../../alien_logic.c#L274)
  - [`l3000`](#l3000) — [`alien_wave.c:L255`](../../alien_wave.c#L255)
  - `l0f00_check_alien_with_player_collision` — [`collision_detection.c#L10`](../../collision_detection.c#L10)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2130`](#l2130) — [`alien_wave.c:L207`](../../alien_wave.c#L207)

---

### `l2160`
#### **Beschrijving**
De functie [`l2160`](../../alien_wave.c#L143-L148) (Z80 ROM: `$2160–$216F`) voert de tweede sub-frametaak uit van de interleaved cyclus.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l24c4`](#l24c4) — [`alien_wave.c:L29`](../../alien_wave.c#L29)
  - `process_enemy_bombs` — [`weapon_collision.c#L17`](../../weapon_collision.c#L17)
  - [`alien_movement_update`](alien-logic.md#alien_movement_update) — [`alien_logic.c#L335`](../../alien_logic.c#L335)
  - [`handle_animations_for_killed_aliens`](alien-logic.md#handle_animations_for_killed_aliens) — [`alien_logic.c#L195`](../../alien_logic.c#L195)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2130`](#l2130) — [`alien_wave.c:L208`](../../alien_wave.c#L208)

---

### `l2170`
#### **Beschrijving**
De functie [`l2170`](../../alien_wave.c#L153-L156) (Z80 ROM: `$2170–$217F`) voert de derde sub-frametaak uit van de interleaved cyclus.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`alien_animation_update`](alien-logic.md#alien_animation_update) — [`alien_logic.c#L382`](../../alien_logic.c#L382)
  - [`l2560`](alien-logic.md#l2560) — [`alien_logic.c#L778`](../../alien_logic.c#L778)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2130`](#l2130) — [`alien_wave.c:L209`](../../alien_wave.c#L209)

---

### `l2180`
#### **Beschrijving**
De functie [`l2180`](../../alien_wave.c#L161-L166) (Z80 ROM: `$2180–$218F`) voert de vierde sub-frametaak uit van de interleaved cyclus.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l24c4`](#l24c4) — [`alien_wave.c:L29`](../../alien_wave.c#L29)
  - `process_enemy_bombs` — [`weapon_collision.c#L17`](../../weapon_collision.c#L17)
  - [`get_screen_ram_address_for_all_aliens`](alien-logic.md#get_screen_ram_address_for_all_aliens) — [`alien_logic.c#L290`](../../alien_logic.c#L290)
  - [`handle_animations_for_killed_aliens`](alien-logic.md#handle_animations_for_killed_aliens) — [`alien_logic.c#L195`](../../alien_logic.c#L195)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2130`](#l2130) — [`alien_wave.c:L210`](../../alien_wave.c#L210)

---

### `l2190` & `l21a5` & `l2146`
#### **Beschrijving**
De functies [`l2190`](../../alien_wave.c#L171-L177), [`l21a5`](../../alien_wave.c#L182-L188) en [`l2146`](../../alien_wave.c#L193-L199) (Z80 ROM: `$2146–$21B9`) vormen de gecondenseerde 2-frame updatecyclus wanneer er minder dan 5 aliens over zijn op het scherm.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`alien_data_controller`](alien-logic.md#alien_data_controller), [`alien_movement_update`](alien-logic.md#alien_movement_update), [`alien_animation_update`](alien-logic.md#alien_animation_update), [`get_screen_ram_address_for_all_aliens`](alien-logic.md#get_screen_ram_address_for_all_aliens)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2000_alien_wave_main_loop`](#l2000_alien_wave_main_loop) — [`alien_wave.c:L246`](../../alien_wave.c#L246)

---

## 3. Ronde-overgangen & Wave Completion

### `l21ba`
#### **Beschrijving**
De functie [`l21ba`](../../alien_wave.c#L104-L129) (Z80 ROM: `$21BA–$21CF`) verzorgt het afronden van de huidige alien-golf zodra alle aliens vernietigd zijn (`AliensLeft == 0`).

#### **Context & Aanroep**
Aangeroepen vanuit `l2000_alien_wave_main_loop`.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l2204`](#l2204) — [`alien_wave.c:L109`](../../alien_wave.c#L109)
  - `process_enemy_bombs` — [`weapon_collision.c#L17`](../../weapon_collision.c#L17)
  - [`handle_animations_for_killed_aliens`](alien-logic.md#handle_animations_for_killed_aliens) — [`alien_logic.c#L195`](../../alien_logic.c#L195)
  - [`l24c4`](#l24c4) — [`alien_wave.c:L115`](../../alien_wave.c#L115)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2000_alien_wave_main_loop`](#l2000_alien_wave_main_loop) — [`alien_wave.c:L230`](../../alien_wave.c#L230)

#### **Stap-voor-stap werking**
1. **Sub-frame check:** Bij even sub-frames (`(masked_counter & 1) == 0`) springt de functie direct door naar de ronde-overgang [`l2204`](#l2204).
2. **Explosies en Bommen:** Voert tijdens oneven sub-frames resterende bommen en explosies uit.
3. **Mothership escort uitzondering (`LevelAndRound == 0x0B`):** Bij de finale moederschip-escortgolf stopt het level niet als de 16 escort-aliens gedood zijn; deze functie respawnt dan direct 16 nieuwe aliens via `l0526()`.

---

### `l2204`
#### **Beschrijving**
De functie [`l2204`](../../alien_wave.c#L80-L99) (Z80 ROM: `$2204–$222B`) beheert de countdown en de overgang naar de volgende ronde.

#### **Context & Aanroep**
Aangeroepen vanuit `l21ba`.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `clear_foreground` — [`hw_video_audio.c`](../../hw_video_audio.c)
  - `phoenix_round_population` — [`phoenix_tables.c`](../../phoenix_tables.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l21ba`](#l21ba) — [`alien_wave.c:L109`](../../alien_wave.c#L109)

#### **Stap-voor-stap werking**
1. **Countdown:** Verlaagt de overgangsteller `state.M43B6--`. Zolang `state.M43B6 >= 0xA0`, keert de functie terug.
2. **Ronde ophogen:** Zet `state.GameState = GAME_STATE_INIT_ROUND`, reset het schild (`ShieldCount = 0`) en verhoogt `LevelAndRound++`.
3. **Populatie instellen:** Raadpleegt `phoenix_round_population` om de nieuwe hoeveelheid aliens (`AliensLeft`) of vogels (`BirdsLeft`) in te stellen.
4. **Scherm schonen:** Wist het voorgrondscherm via `clear_foreground()`.

---

## 4. Achtergrond & Sterren-scrolling

### `l24c4`
#### **Beschrijving**
De functie [`l24c4`](../../alien_wave.c#L29-L72) (Z80 ROM: `$24C4–$24DF`) verzorgt het bijwerken van de achtergrondweergave en sterren/planeet-scrolling voor de alien-levels.

#### **Context & Aanroep**
Aangeroepen vanuit `l2160`, `l2180` en `l21ba`.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `update_scroll_register_and_fill_background` — [`hw_video_audio.c`](../../hw_video_audio.c)
  - `stars_scroll_down` — [`hw_video_audio.c`](../../hw_video_audio.c)
  - `draw_image_c_by_b` — [`sprite_rendering.c`](../../sprite_rendering.c)
  - [`mem_read`](utilities.md#mem_read) / [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2160`](#l2160) — [`alien_wave.c:L144`](../../alien_wave.c#L144)
  - [`l2180`](#l2180) — [`alien_wave.c:L162`](../../alien_wave.c#L162)
  - [`l21ba`](#l21ba) — [`alien_wave.c:L115`](../../alien_wave.c#L115)

---

## 5. Breakout & Retarget Dispatcher

### `l3000`
#### **Beschrijving**
De functie [`l3000`](../../alien_wave.c#L255-L269) (Z80 ROM: `$3000–$3012`) is de centrale jumptable-dispatcher voor de breakout-, bomb-drop- en pattern-retarget state machine van de alien-formatie.

#### **Context & Aanroep**
Aangeroepen vanuit `l2150` en `l2190`.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l3264`](alien-logic.md#l3264) — [`alien_logic.c#L459`](../../alien_logic.c#L459)
  - [`l3028`](alien-logic.md#l3028) — [`alien_logic.c#L528`](../../alien_logic.c#L528)
  - [`l30ba`](alien-logic.md#l30ba) — [`alien_logic.c#L562`](../../alien_logic.c#L562)
  - [`l3124`](alien-logic.md#l3124) — [`alien_logic.c#L607`](../../alien_logic.c#L607)
  - [`l315a`](alien-logic.md#l315a) — [`alien_logic.c#L629`](../../alien_logic.c#L629)
  - [`l31b4`](alien-logic.md#l31b4) — [`alien_logic.c#L662`](../../alien_logic.c#L662)
  - [`l322c`](alien-logic.md#l322c) — [`alien_logic.c#L718`](../../alien_logic.c#L718)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2150`](#l2150) — [`alien_wave.c:L136`](../../alien_wave.c#L136)
  - [`l2190`](#l2190) — [`alien_wave.c:L173`](../../alien_wave.c#L173)

#### **Stap-voor-stap werking**
Leest de teller `state.Counter93`, verhoogt deze en kiest via een `switch (Counter93 & 0x07)` welke tak uit de `alien_logic.c` state machine wordt aangeroepen (0: `l3264`, 1: `l3028`, 2: `l30ba`, 3: `l3124`, 4: `l315a`, 5: `l31b4`, 6: `l322c`, 7: no-op).
