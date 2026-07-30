# Phoenix Bird Animations & Visual Analysis (`bird-animations.md`)

This document provides a functional and visual analysis of all bird-related animations in *Phoenix* (levels 5 & 7), including exact C routines, Z80 ROM address ranges, RAM data structures, and **individual animated SVG assets**.

---

## Table of Contents
1. [Overview of Bird Phases](#1-overview-of-bird-phases)
2. [1. Egg & Hatching Transformation](#1-egg--hatching-transformation)
3. [2. Small Bird Flapping & Gliding](#2-small-bird-flapping--gliding)
4. [3. Full-Grown / Large Bird](#3-full-grown--large-bird)
5. [4. Dive Bombing & Attack Flight Path](#4-dive-bombing--attack-flight-path)
6. [5. Bird Explosion & Bonus Score](#5-bird-explosion--bonus-score)
7. [6. Attract Mode Intro Bird](#6-attract-mode-intro-bird)

---

## 1. Overview of Bird Phases

In levels 5 and 7 of *Phoenix*, birds are controlled via a dynamic state machine. The bird animation loop transitions through multiple phases: from egg hatching to small bird, full-grown bird, and dive-bombing attacks.

#### **Knowledge Graph Links**
* **Relevant C Source Files:**
  - [`bird_logic.c`](../../bird_logic.c) → [`bird-logic.md`](../../c-annotated/en/bird-logic.md)
  - [`bird_wave_behavior.c`](../../bird_wave_behavior.c) → [`bird-wave-behavior.md`](../../c-annotated/en/bird-wave-behavior.md)
  - [`birds_vertical_movement.c`](../../birds_vertical_movement.c) → [`birds-vertical-movement.md`](../../c-annotated/en/birds-vertical-movement.md)
  - [`collision_detection.c`](../../collision_detection.c) → [`collision-detection.md`](../../c-annotated/en/collision-detection.md)
  - [`attract_mode.c`](../../attract_mode.c) → [`attract-mode.md`](../../c-annotated/en/attract-mode.md)

---

## 1. Egg & Hatching Transformation

### **Description & Code**
* **Routines:** [`l38bc_large_hit`](../../c-annotated/en/collision-detection.md#l38bc_large_hit) (Z80 ROM: `$38BC–$38F1`) & [`l3250_egg_hatching`](../../c-annotated/en/bird-wave-behavior.md#l3250_egg_hatching)
* **RAM Slots:** `bird_struct + 0` (type `0x0B` or `0x0C`), `bird_struct + 5` (hatching threshold).
* **Functionality:** Eggs float in formation. Upon being hit (or when the hatching timer reaches the threshold value), the egg transforms directly into a bird via the `phoenix_egg_transformation_types` table.

![Egg & Hatching Transformation Animation](../01_egg_hatching.svg)

---

## 2. Small Bird (Flapping & Gliding)

### **Description & Code**
* **Routines:** [`drawbirdobject`](../../c-annotated/en/attract-mode.md#drawbirdobject) (Z80 ROM: `$34C0–$355D`)
* **Tile Pointers:** `phoenix_bird_draw_entries` & `phoenix_bird_shape_pointers`
* **Functionality:** After hatching, the small bird flaps with 2 alternating wing frames (wings up in frame A, wings down in frame B) while flying in formation.

![Small Bird Flapping Animation](../02_small_bird_flapping.svg)

---

## 3. Full-Grown / Large Bird

### **Description & Code**
* **Routines:** [`l327c_grown_bird_behavior`](../../c-annotated/en/bird-wave-behavior.md#l327c_grown_bird_behavior) (Z80 ROM: `$327C–$32A0`)
* **Functionality:** If a small bird survives long enough on the playfield, it grows via `bird_struct + 4` into a full-size bird with a wide 4x4 tile matrix wingspan.

![Grown Bird Matrix Animation](../03_grown_bird_matrix.svg)

---

## 4. Dive Bombing & Attack Flight Path

### **Description & Code**
* **Routines:** [`bird_flight_path`](../../c-annotated/en/bird-logic.md#bird_flight_path) (Z80 ROM: `$3160`) & [`l3210_bird_dive_bomb`](../../c-annotated/en/bird-wave-behavior.md#l3210_bird_dive_bomb)
* **Functionality:** Selected birds break formation and execute an accelerated dive-bombing run in a sine trajectory toward the player ship while dropping bombs.

![Dive Bombing Attack Animation](../04_dive_bombing_attack.svg)

---

## 5. Bird Explosion & Bonus Score

### **Description & Code**
* **Routines:** [`bird_explosion_slot`](../../c-annotated/en/collision-detection.md#bird_explosion_slot) & [`l3758_bonus_explosion_animation`](../../c-annotated/en/alien-logic.md#l3758_bonus_explosion_animation)
* **RAM Slot:** `0x4378` / `0x437C` (bonus explosion array).
* **Functionality:** Upon a direct hit, the bird bursts into a 4x4 particle grid (`phoenix_explosion_particle_page`). Subsequently, a bonus score (e.g. **100**, **200**, or **500** points) appears at the hit location.

![Particle Explosion & Score Animation](../05_bird_explosion_bonus.svg)

---

## 6. Attract Mode Intro Bird

### **Description & Code**
* **Routines:** [`draw_intro_bird_animation_frame`](../../c-annotated/en/attract-mode.md#draw_intro_bird_animation_frame) (Z80 ROM: `$21DC`)
* **Functionality:** During the attract mode screen (title demo), a special animated bird glides across the top of the screen as a demonstration.

![Intro Splash Bird Animation](../06_intro_splash_bird.svg)
