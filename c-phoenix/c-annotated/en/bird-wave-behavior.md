# Bird Wave Behavior & AI Scripts (`bird_wave_behavior.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`bird_wave_behavior.c`](../../bird_wave_behavior.c). This module controls bird AI state machines, egg hatching, wing flapping cycles, and dive-bombing triggers.

---

## Table of Contents
1. [Bird AI State Machine](#1-bird-ai-state-machine)
2. [Egg Hatching & Growth Logic](#2-egg-hatching--growth-logic)
3. [Dive Bombing & Swoop Attacks](#3-dive-bombing--swoop-attacks)

---

## 1. Bird AI State Machine

### `update_bird_behavior`
#### **Description**
The function [`update_bird_behavior`](../../bird_wave_behavior.c#L35-L95) (Z80 ROM: `$35B0–$35DB`) evaluates active bird AI scripts from table `phoenix_bird_behaviour_scripts` (ROM `$3F00–$3F7F`).

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - `phoenix_bird_behaviour_scripts` — [`phoenix_tables.c`](../../phoenix_tables.c)
* **Called By (Incoming Calls / Backlinks):**
  - [`process_birds`](bird-logic.md#process_birds) — [`bird_logic.c`](../../bird_logic.c)

---

## 2. Egg Hatching & Growth Logic

### `update_bird_behavior`
#### **Description**
The function [`update_bird_behavior`](../../bird_wave_behavior.c#L218) (Z80 ROM: `$35B0–$35DB`) advances one bird through its behaviour script, including the egg-to-bird transformation, by dispatching on the script entry held in the bird record.

---

## 3. Dive Bombing & Swoop Attacks

### `l370a_grow_or_dive`
#### **Description**
The function [`l370a_grow_or_dive`](../../bird_wave_behavior.c#L195) rolls the random gate (`M436F`) that turns a growing bird into a diving one; the spawn decision itself lives in [`try_spawn_bird_dive_bomb`](bird-logic.md#try_spawn_bird_dive_bomb).
