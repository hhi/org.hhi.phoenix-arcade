# Game Endings & Explosions (`state_endings.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`state_endings.c`](../../state_endings.c). Deze module beheert de eindtoestanden van *Phoenix*: spelersexplosie (GameState 4), Game Over (GameState 5), moederschip-explosie (GameState 6) en de moederschip-scoreweergave (GameState 7).

---

## Inhoudsopgave
1. [GameState 4: Spelersexplosie](#1-gamestate-4-spelersexplosie)
2. [GameState 5: Game Over](#2-gamestate-5-game-over)
3. [GameState 6 & 7: Moederschip Explosie & Score](#3-gamestate-6--7-moederschip-explosie--score)
4. [Levensbeheer & Aftrek](#4-levensbeheer--aftrek)

---

## 1. GameState 4: Spelersexplosie

### `state_4_player_ship_explosion`
#### **Beschrijving**
De functie [`state_4_player_ship_explosion`](../../state_endings.c#L33-L59) (Z80 ROM: `$0AEA–$0B0F`) regelt de stapsgewijze animatie en deeltjesfases wanneer het spelerschip vernietigd is.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `hw_write_scroll_register` — [`hw_video_audio.c`](../../hw_video_audio.c)
  - [`l0b15`](#l0b15) — [`state_endings.c#L44`](../../state_endings.c#L44)
  - [`l0ba0`](#l0ba0) — [`state_endings.c#L49`](../../state_endings.c#L49)
  - `clear_foreground` — [`hw_video_audio.c`](../../hw_video_audio.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`game_state_machine`](game-state-machine.md#game_state_machine) — [`game_state_machine.c#L39`](../../game_state_machine.c#L39)

---

## 2. GameState 5: Game Over

### `state_5_game_over_text`
#### **Beschrijving**
De functie [`state_5_game_over_text`](../../state_endings.c#L67-L94) (Z80 ROM: `$0B60–$0B9D`) toont de "GAME OVER" tekst, controleert de copyright-checksum en verwerkt de overgang terug naar attract mode of de andere speler.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `clear_background` — [`hw_video_audio.c`](../../hw_video_audio.c)
  - `print_text_lines` — [`hw_video_audio.c`](../../hw_video_audio.c)
  - `copy_memory_bank` — [`state_init.c`](../../state_init.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`game_state_machine`](game-state-machine.md#game_state_machine) — [`game_state_machine.c#L40`](../../game_state_machine.c#L40)

---

## 3. GameState 6 & 7: Moederschip Explosie & Score

### `state_6_mother_ship_explosion` & `state_7_mother_ship_score_display`
#### **Beschrijving**
- [`state_6_mother_ship_explosion`](../../state_endings.c#L126-L171) (Z80 ROM: `$2400–$244B`) voert de spectaculaire deeltjes- en tegelexplosie van het moederschip uit.
- [`state_7_mother_ship_score_display`](../../state_endings.c#L179-L201) (Z80 ROM: `$244C–$2469`) toont de behaalde bonusscore en verhoogt de ronde (`LevelAndRound += 0x10`) voor het volgende level.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`update_counters_for_mothership_explosion`](mothership-impl.md#update_counters_for_mothership_explosion) — [`mothership_impl.c#L134`](../../mothership_impl.c#L134)
  - [`erase_mothership`](mothership-logic.md#erase_mothership) — [`mothership_logic.c#L22`](../../mothership_logic.c#L22)
  - [`mothership_core_hit_check`](mothership-logic.md#mothership_core_hit_check) — [`mothership_logic.c#L48`](../../mothership_logic.c#L48)
  - [`l2085_particles`](player-explosion.md#l2085_particles) — [`player_explosion.c#L154`](../../player_explosion.c#L154)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`game_state_machine`](game-state-machine.md#game_state_machine) — [`game_state_machine.c#L41-L42`](../../game_state_machine.c#L41-L42)

---

## 4. Levensbeheer & Aftrek

### `l0b15`
#### **Beschrijving**
De functie [`l0b15`](../../state_endings.c#L208-L231) (Z80 ROM: `$0B15–$0B2D`) verlaagt het aantal spelerlevens van de actieve speler, ververst het scherm en bepaalt of het spel overgaat naar "GAME OVER" of dat een nieuwe beurt start.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `update_lives_screen` — [`hw_video_audio.c`](../../hw_video_audio.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`state_4_player_ship_explosion`](#state_4_player_ship_explosion) — [`state_endings.c#L44`](../../state_endings.c#L44)
