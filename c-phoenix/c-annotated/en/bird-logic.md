# Bird Logic Main Loop (`bird_logic.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`bird_logic.c`](../../bird_logic.c). This module controls main loop execution for bird waves (levels 5 & 7), bird movement updates, and dive triggers.

---

## Table of Contents
1. [Bird Wave Main Loop](#1-bird-wave-main-loop)
2. [Bird Flight Path & Dive Calculations](#2-bird-flight-path--dive-calculations)

---

## 1. Bird Wave Main Loop

### `process_birds`
#### **Description**
The function [`process_birds`](../../bird_logic.c#L45-L110) (Z80 ROM: `$3400–$344D`) updates all active bird slots in VRAM and RAM during levels 5 and 7.

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`update_bird_behavior`](bird-wave-behavior.md#update_bird_behavior) — [`bird_wave_behavior.c`](../../bird_wave_behavior.c)
  - [`bird_flight_path`](#bird_flight_path) — [`bird_logic.c:L85`](../../bird_logic.c#L85)
* **Called By (Incoming Calls / Backlinks):**
  - [`level_1_3_B_player_alive_aliens`](state-play.md#level_1_3_b_player_alive_aliens) — [`state_play.c#L16`](../../state_play.c#L16)

---

## 2. Bird Flight Path & Dive Calculations

### `bird_flight_path`
#### **Description**
The function [`bird_flight_path`](../../bird_logic.c#L125-L180) (Z80 ROM: `$3160–$31C5`) computes vector deltas and sine curves for diving birds.
