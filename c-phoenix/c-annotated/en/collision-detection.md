# Collision Detection (`collision_detection.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`collision_detection.c`](../../collision_detection.c). This module handles VRAM tile scanning, pixel mask collision detection, and explosion slot assignments for birds, eggs, and bullets.

---

## Table of Contents
1. [VRAM Tile & Pixel Mask Scans](#1-vram-tile--pixel-mask-scans)
2. [Bird & Egg Collision Slots](#2-bird--egg-collision-slots)

---

## 1. VRAM Tile & Pixel Mask Scans

### `l38bc_large_hit`
#### **Description**
The function [`l38bc_large_hit`](../../collision_detection.c#L45-L95) (Z80 ROM: `$38BC–$38F1`) executes bounding box and VRAM pixel mask collision checks for large bird sprites.

#### **Knowledge Graph Links**
* **Called By (Incoming Calls / Backlinks):**
  - [`process_birds`](bird-logic.md#process_birds) — [`bird_logic.c`](../../bird_logic.c)

---

## 2. Bird & Egg Collision Slots

### `bird_explosion_slot`
#### **Description**
The function [`bird_explosion_slot`](../../collision_detection.c#L110-L150) (Z80 ROM: `$38F2–$3920`) assigns a free explosion slot in RAM array `0x4378–$437C` upon a fatal projectile hit.
