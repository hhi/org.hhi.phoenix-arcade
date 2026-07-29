# Sprite Rendering (`sprite_rendering.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`sprite_rendering.c`](../../sprite_rendering.c). Deze module beheert de weergave en opschoning van 1x1, 2x1, 1x2 en 2x2 tegelmatrix-objecten op het voorgrondscherm.

---

## Inhoudsopgave
1. [Scherm-object Update Engine](#1-scherm-object-update-engine)
2. [Tegels Wis- & Teken-controllers](#2-tegels-wis---teken-controllers)

---

## 1. Scherm-object Update Engine

### `update_screen_objects`
#### **Beschrijving**
De functie [`update_screen_objects`](../../sprite_rendering.c#L215-L223) (Z80 ROM: `$0718–$071F`) is de centrale routine die voor een scherm-object (zoals aliens, kogels en de speler) eerst de oude positie wist (via `bit4_controller`) en vervolgens het nieuwe sprite-frame tekent (via `bit3_controller`).

#### **Context & Aanroep**
Aangeroepen vanuit `alien_data_controller`, `player_data_controller` en `enemy_bullet_data_controller`.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`bit4_controller`](#bit4_controller) — [`sprite_rendering.c#L219`](../../sprite_rendering.c#L219)
  - [`bit3_controller`](#bit3_controller) — [`sprite_rendering.c#L222`](../../sprite_rendering.c#L222)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`alien_data_controller`](alien-logic.md#alien_data_controller) — [`alien_logic.c#L279`](../../alien_logic.c#L279)
  - [`player_data_controller`](player-logic.md#player_data_controller) — [`player_logic.c#L255`](../../player_logic.c#L255)
  - `enemy_bullet_data_controller` — [`weapon_collision.c#L152`](../../weapon_collision.c#L152)

---

## 2. Tegels Wis- & Teken-controllers

### `bit4_controller` & `bit3_controller`
#### **Beschrijving**
- [`bit4_controller`](../../sprite_rendering.c#L150-L173) (Z80 ROM: `$0720–$073F`): Inspecteert bit 4 van de controlestate. Indien actief, wist deze de oude tegelposities (1x1, 2x1, 1x2 of 2x2) uit VRAM.
- [`bit3_controller`](../../sprite_rendering.c#L179-L208) (Z80 ROM: `$0740–$07EE`): Inspecteert bit 3 van de controlestate. Indien actief, haalt deze de tegel-ID's op uit `phoenix_sprite_character_block_shapes` en schrijft het nieuwe sprite-frame naar VRAM.
