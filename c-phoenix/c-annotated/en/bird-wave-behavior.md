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
The function [`update_bird_behavior`](../../bird_wave_behavior.c#L35-L95) (Z80 ROM: `$35E0–$3635`) evaluates active bird AI scripts from table `phoenix_bird_behaviour_scripts` (ROM `$3F00–$3F7F`).

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - `phoenix_bird_behaviour_scripts` — [`phoenix_tables.c`](../../phoenix_tables.c)
* **Called By (Incoming Calls / Backlinks):**
  - [`process_birds`](bird-logic.md#process_birds) — [`bird_logic.c`](../../bird_logic.c)

---

## 2. Egg Hatching & Growth Logic

### `l3250_egg_hatching`
#### **Description**
The function [`l3250_egg_hatching`](../../bird_wave_behavior.c#L110-L150) (Z80 ROM: `$3250–$3278`) transforms an egg tile into a small bird sprite upon hit or timer expiration.

---

## 3. Dive Bombing & Swoop Attacks

### `l3210_bird_dive_bomb`
#### **Description**
The function [`l3210_bird_dive_bomb`](../../bird_wave_behavior.c#L165-L210) (Z80 ROM: `$3210–$3245`) triggers dive-bombing swoop attacks targeted at player ship coordinates.
