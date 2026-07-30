# Mothership Implementation (`mothership_impl.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`mothership_impl.c`](../../mothership_impl.c). This module manages the 26x9 tile matrix of the alien mothership, shield tile destruction, central core penetration, and core explosion routines.

---

## Table of Contents
1. [Mothership Tile Matrix & Hit Scanning](#1-mothership-tile-matrix--hit-scanning)
2. [Shield Destruction & Core Explosion](#2-shield-destruction--core-explosion)

---

## 1. Mothership Tile Matrix & Hit Scanning

### `l2351_mothership_animation`
#### **Description**
The function [`l2351_mothership_animation`](../../mothership_impl.c#L12) (Z80 ROM: `$2351–$23C7`) drives the mothership animation and handles bullet impacts against its shield and core tiles, replacing hit tiles with destroyed tile graphics.

#### **Knowledge Graph Links**
* **Called By (Incoming Calls / Backlinks):**
  - [`level_1_3_B_player_alive_aliens`](state-play.md#level_1_3_b_player_alive_aliens) — [`state_play.c#L16`](../../state_play.c#L16)

---

## 2. Shield Destruction & Core Explosion

### `mothership_core_hit_check`
#### **Description**
The function [`mothership_core_hit_check`](../../mothership_impl.c#L110-L160) (Z80 ROM: `$2520–$254F`) checks whether a player bullet penetrates the central core window, triggering mothership destruction and level victory.
