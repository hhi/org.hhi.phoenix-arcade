# Utility Subroutines (`utilities.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`utilities.c`](../../utilities.c). Deze module bevat de kern-hulpprogramma's van de game, waaronder geheugen-lees/schrijf abstracties (`mem_read`/`mem_write`), BCD-cijferweergave, tekst-rendering op het geroteerde scherm en de random number generator.

---

## Inhoudsopgave
1. [Geheugen & Input Utility](#1-geheugen--input-utility)
2. [Scherm- & Tekst-rendering](#2-scherm--tekst-rendering)
3. [VRAM Coördinaat-calculatie](#3-vram-coördinaat-calculatie)

---

## 1. Geheugen & Input Utility

### `mem_read` & `mem_write`
#### **Beschrijving**
- `mem_read(uint16_t addr)`: Leest een byte uit RAM (`$4000–$4FFF`). Retourneert 0 bij adresseringen buiten het RAM-bereik.
- `mem_write(uint16_t addr, uint8_t val)`: Schrijft een byte naar RAM/VRAM met beveiliging tegen ROM-overschrijvingen.

#### **Knowledge Graph Koppelingen**
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - Vrijwel alle spelmodules (`alien_logic.c`, `bird_logic.c`, `player_logic.c`, etc.).

---

### `check_input_bits`
#### **Beschrijving**
De functie [`check_input_bits`](../../utilities.c#L16-L22) (Z80 ROM: `$00BB–$00C3`) voert een flankdetectie uit (1 -> 0 overgang van een knop) door `state.IN0Current` te vergelijken met `state.IN0Previous`.

#### **Knowledge Graph Koppelingen**
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`move_player`](player-logic.md#move_player) — [`player_logic.c#L131`](../../player_logic.c#L131)
  - [`get_assigned_player_bullet_tile`](player-logic.md#get_assigned_player_bullet_tile) — [`player_logic.c#L177`](../../player_logic.c#L177)

---

## 2. Scherm- & Tekst-rendering

### `print_number`
#### **Beschrijving**
De functie [`print_number`](../../utilities.c#L30-L55) (Z80 ROM: `$00C4–$00E1`) drukt een BCD-getal af op de opgegeven VRAM-positie.

#### **Knowledge Graph Koppelingen**
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`mothership_core_hit_check`](mothership-logic.md#mothership_core_hit_check) — [`mothership_logic.c#L75`](../../mothership_logic.c#L75)
  - [`state_1_flashing_score`](game-state-machine.md#state_1_flashing_score) — [`game_state_machine.c#L175`](../../game_state_machine.c#L175)
  - [`update_scores_and_sound`](scoring.md#update_scores_and_sound) — [`scoring.c#L130`](../../scoring.c#L130)

---

## 3. VRAM Coördinaat-calculatie

### `right_one_column` & `left_one_column`
#### **Beschrijving**
Omdat het scherm van de *Phoenix* arcadekast 90 graden gedraaid opgesteld staat, komt 1 schermkolom naar rechts of links overeen met `DE += 0x20` of `DE -= 0x20` in VRAM.
