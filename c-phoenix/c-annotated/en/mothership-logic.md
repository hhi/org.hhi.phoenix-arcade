# Mothership Logic (`mothership_logic.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`mothership_logic.c`](../../mothership_logic.c). This module controls mothership descent speed tables, display clearing, and bonus score calculation.

---

## Table of Contents
1. [Mothership Descent Control](#1-mothership-descent-control)
2. [Erase & Bonus Scoring](#2-erase--bonus-scoring)

---

## 1. Mothership Descent Control

### `mothership_descent_logic`
#### **Description**
The function [`mothership_descent_logic`](../../mothership_logic.c#L30-L75) (Z80 ROM: `$1E00–$1E40`) steps through table `phoenix_mothership_tile_page` to lower the mothership vertical position per frame.

---

## 2. Erase & Bonus Scoring

### `erase_mothership`
#### **Description**
The function [`erase_mothership`](../../mothership_logic.c#L85-L120) (Z80 ROM: `$1E50–$1E80`) clears all 26x9 mothership tile graphics from background VRAM when defeated or reset.
