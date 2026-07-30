# Sprite Rendering Engine (`sprite_rendering.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`sprite_rendering.c`](../../sprite_rendering.c). This module handles sprite drawing for 1x1, 2x1, 1x2, and 2x2 tile matrices into rotated 32x32 VRAM pages (`$4000–$433F`).

---

## Table of Contents
1. [Sprite Matrix Rendering](#1-sprite-matrix-rendering)

---

## 1. Sprite Matrix Rendering

### `update_screen_objects`
#### **Description**
The function [`update_screen_objects`](../../sprite_rendering.c#L215) (Z80 ROM: `$0718–$071F`) writes an object's tile data into the VRAM cells addressed by its screen-RAM record, dispatching through [`bit4_controller`](#bit4_controller) and [`bit3_controller`](#bit3_controller).
