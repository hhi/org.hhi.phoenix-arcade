# Alien Logic (`alien_logic.c`) - C-Annotated Knowledge Graph Documentation

This document contains an in-depth annotated analysis of all functions in [`alien_logic.c`](../../alien_logic.c) and [`alien_logic.h`](../../alien_logic.h). Each function is documented following a **Knowledge Graph approach** with outgoing calls (`Calls`) and incoming links (`Called By / Backlinks`).

---

## Table of Contents
1. [Initialization & Positions](#1-initialization--positions)
2. [Explosions & Animations for Shot Aliens](#2-explosions--animations-for-shot-aliens)
3. [Screen & RAM Updates](#3-screen--ram-updates)
4. [Movement & Frame Animations](#4-movement--frame-animations)
5. [Breakout, Bomb-drop & Pattern Schedulers](#5-breakout-bomb-drop--pattern-schedulers)
6. [Attack Logic & Dive-bomb Triggers](#6-attack-logic--dive-bomb-triggers)

---

## 1. Initialization & Positions

### `init_alien_control_states`
#### **Description**
The function [`init_alien_control_states`](../../alien_logic.c#L19-L25) (Z80 ROM: `$05EC–$05F9`) sets the initial flight and control parameters for aliens at the start of a new round or level.

#### **Context & Invocation**
Called during level initialization from the game state machine:
```c
init_alien_control_states();
```

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`init_alien_control_states_05fa`](#init_alien_control_states_05fa) — [`alien_logic.c:L24`](../../alien_logic.c#L24)
  - `phoenix_alien_control_init_values` — [`phoenix_tables.c:L265`](../../phoenix_tables.c#L265)
* **Called By (Incoming Calls / Backlinks):**
  - [`init_alien_control_states`](alien-logic.md#init_alien_control_states) — [`alien_logic.c#L19`](../../alien_logic.c#L19)

#### **Step-by-Step Functionality**
1. **Determine Index:** Calculates the lookup index via `state.LevelAndRound & 0x0F`.
2. **Retrieve Init Values:** Fetches two initial control bytes from table `phoenix_alien_control_init_values`:
   - `d`: Value for Control State A (status and animation bits).
   - `e`: Value for Control State B (sprite/shape index).
3. **Transfer to RAM:** Calls [`init_alien_control_states_05fa(d, e)`](#init_alien_control_states_05fa) to assign these values to the RAM memory block of all aliens.

---

### `init_alien_control_states_05fa`
#### **Description**
The function [`init_alien_control_states_05fa`](../../alien_logic.c#L207-L217) (Z80 ROM: `$05FA–$060D`) populates the control memory slots of all living aliens with the selected control states `d` and `e`.

#### **Context & Invocation**
Called by `init_alien_control_states`:
```c
init_alien_control_states_05fa(d, e);
```

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
* **Called By (Incoming Calls / Backlinks):**
  - [`init_alien_control_states`](#init_alien_control_states) — [`alien_logic.c:L24`](../../alien_logic.c#L24)

#### **Memory & Structure Context**
The RAM table for alien control begins at address `0x4B70`. Each alien record occupies 4 bytes:
- **Byte 0 (`HL`):** Control State A (`d`)
- **Byte 1 (`HL+1`):** Control State B (`e`)
- **Byte 2 (`HL+2`):** X coordinate on screen
- **Byte 3 (`HL+3`):** Y coordinate on screen

#### **Step-by-Step Functionality**
1. **Status Check:** Checks whether `state.AliensLeft == 0`. If so, aborts execution immediately.
2. **Fill RAM:** Loops over up to 16 aliens. Writes `d` to Control A (`0x4B70 + i*4`) and `e` to Control B (`0x4B71 + i*4`).
3. **Increment Pointer:** Advances memory address by 4 bytes per iteration (`hl += 4`).

---

### `init_alien_positions`
#### **Description**
The function [`init_alien_positions`](../../alien_logic.c#L224-L242) (Z80 ROM: `$0610–$0638`) initializes X and Y starting coordinates on the screen grid for the formation of up to 16 aliens.

#### **Context & Invocation**
Called during level initialization:
```c
init_alien_positions();
```

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
  - `phoenix_alien_position_pointer_table` — [`phoenix_tables.c`](../../phoenix_tables.c)
  - `phoenix_alien_position_layout_page` — [`phoenix_tables.c`](../../phoenix_tables.c)
* **Called By (Incoming Calls / Backlinks):**
  - [`init_alien_control_states`](alien-logic.md#init_alien_control_states) — [`alien_logic.c#L19`](../../alien_logic.c#L19)

#### **Step-by-Step Functionality**
1. **Determine Layout Page:** Calculates index `(state.LevelAndRound >> 1) & 0x0F` and looks up starting address/offset in `phoenix_alien_position_pointer_table` within page `phoenix_alien_position_layout_page`.
2. **Write Coordinates:** Loops through all living aliens (max 16) and writes sequential X and Y coordinates to RAM address `0x4B72` (offset `+2` and `+3` within 4-byte record).
3. **Increment Pointer:** Advances 3 bytes per alien written (`de += 3`), ensuring next alien coordinates land exactly at `0x4B76`, `0x4B7A`, etc.

---

## 2. Explosions & Animations for Shot Aliens

### `handle_animations_for_killed_aliens`
#### **Description**
The function [`handle_animations_for_killed_aliens`](../../alien_logic.c#L260-L315) (Z80 ROM: `$0FC0–$0FFF`) updates active explosion slots and bonus score animations for aliens destroyed by player fire.

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`draw_explosion_particles`](#draw_explosion_particles) — [`alien_logic.c:L310`](../../alien_logic.c#L310)
  - [`l3758_bonus_explosion_animation`](#l3758_bonus_explosion_animation) — [`alien_logic.c:L295`](../../alien_logic.c#L295)
* **Called By (Incoming Calls / Backlinks):**
  - [`l2000_alien_wave_main_loop`](alien-wave.md#l2000_alien_wave_main_loop) — [`alien_wave.c#L220`](../../alien_wave.c#L220)

#### **Step-by-Step Functionality**
1. **Iterate Explosion Slots:** Scans the active explosion slot array in RAM (`0x4370–$437F`).
2. **Animate Particle Grid:** Reads frame counter and calls [`draw_explosion_particles`](#draw_explosion_particles) to render 4x4 expanding particle patterns.
3. **Render Bonus Score:** When particle explosion ends, triggers [`l3758_bonus_explosion_animation`](#l3758_bonus_explosion_animation) to display score digits (100, 200, 500) over destroyed alien location.
