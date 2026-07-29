# Attract Mode & Title Screen (`attract_mode.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`attract_mode.c`](../../attract_mode.c). This module controls title splash sequencing, credit counter, coin insertion, high score display, and demonstration gameplay.

---

## Table of Contents
1. [Attract Mode Sequencer](#1-attract-mode-sequencer)
2. [Coin & Credit Management](#2-coin--credit-management)
3. [Intro Bird Animation](#3-intro-bird-animation)

---

## 1. Attract Mode Sequencer

### `splash_and_demo`
#### **Description**
The function [`splash_and_demo`](../../attract_mode.c#L32-L107) (Z80 ROM: `$00E3–$0145`) manages the frame sequence for title screen displays, copyright text, high score tables, and automated demonstration gameplay.

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`draw_intro_bird_animation_frame`](#draw_intro_bird_animation_frame) — [`attract_mode.c:L85`](../../attract_mode.c#L85)
  - `draw_high_score_table` — [`scoring.c`](../../scoring.c)
* **Called By (Incoming Calls / Backlinks):**
  - [`game_state_machine`](game-state-machine.md#game_state_machine) — [`game_state_machine.c:L30`](../../game_state_machine.c#L30)

---

## 2. Coin & Credit Management

### `check_coin_inputs`
#### **Description**
The function [`check_coin_inputs`](../../attract_mode.c#L120-L155) (Z80 ROM: `$0150–$0180`) monitors arcade coin chute inputs ($5000 I/O port) and increments credit counters.

---

## 3. Intro Bird Animation

### `draw_intro_bird_animation_frame`
#### **Description**
The function [`draw_intro_bird_animation_frame`](../../attract_mode.c#L170-L210) (Z80 ROM: `$21DC–$2210`) renders the 32-step intro bird animation gliding across the top title screen.
