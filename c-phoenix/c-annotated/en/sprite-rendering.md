# Sprite Rendering Engine (`sprite_rendering.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`sprite_rendering.c`](../../sprite_rendering.c). This module handles sprite drawing for 1x1, 2x1, 1x2, and 2x2 tile matrices into rotated 32x32 VRAM pages (`$4000–$433F`).

---

## Table of Contents
1. [Sprite Matrix Rendering](#1-sprite-matrix-rendering)

---

## 1. Sprite Matrix Rendering

### `draw_sprite_matrix`
#### **Description**
The function [`draw_sprite_matrix`](../../sprite_rendering.c#L45-L95) (Z80 ROM: `$0400–$0480`) converts 8x8 pixel tile data from ROM into VRAM memory cells.
