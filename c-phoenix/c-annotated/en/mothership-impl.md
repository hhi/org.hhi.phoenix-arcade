# Mothership Implementation (`mothership_impl.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`mothership_impl.c`](../../mothership_impl.c). This module manages the 26x9 tile matrix of the alien mothership, shield tile destruction, central core penetration, and core explosion routines.

---

## Table of Contents
1. [Mothership Tile Matrix & Hit Scanning](#1-mothership-tile-matrix--hit-scanning)
2. [Shield Destruction & Core Explosion](#2-shield-destruction--core-explosion)

---

## 1. Mothership Tile Matrix & Hit Scanning

### `mothership_tile_hit_check`
#### **Description**
The function [`mothership_tile_hit_check`](../../mothership_impl.c#L45-L95) (Z80 ROM: `$1D40–$1D90`) detects player bullet impacts against mothership shield tiles, replacing hit tiles with destroyed tile graphics.

#### **Knowledge Graph Links**
* **Called By (Incoming Calls / Backlinks):**
  - [`state_play_dispatcher`](state-play.md#state_play_dispatcher) — [`state_play.c`](../../state_play.c)

---

## 2. Shield Destruction & Core Explosion

### `mothership_core_hit_check`
#### **Description**
The function [`mothership_core_hit_check`](../../mothership_impl.c#L110-L160) (Z80 ROM: `$1DA0–$1DF0`) checks whether a player bullet penetrates the central core window, triggering mothership destruction and level victory.
