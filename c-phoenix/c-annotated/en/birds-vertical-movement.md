# Birds Vertical Movement (`birds_vertical_movement.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`birds_vertical_movement.c`](../../birds_vertical_movement.c). This module manages vertical scrolling speed registers and formation descent routines for bird waves.

---

## Table of Contents
1. [Vertical Scroll Registers & Formation Descent](#1-vertical-scroll-registers--formation-descent)

---

## 1. Vertical Scroll Registers & Formation Descent

### `birds_vertical_movement_update`
#### **Description**
The function [`birds_vertical_movement_update`](../../birds_vertical_movement.c#L112) (Z80 ROM: `$2600–$2664`) updates vertical scroll registers (`B4BD2`) and shifts bird formation rows downward.

#### **Knowledge Graph Links**
* **Called By (Incoming Calls / Backlinks):**
  - [`process_birds`](bird-logic.md#process_birds) — [`bird_logic.c`](../../bird_logic.c)
