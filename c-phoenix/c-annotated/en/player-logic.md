# Player Logic (`player_logic.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`player_logic.c`](../../player_logic.c). This module manages player ship movement controls (left/right joystick), shield force field activation (5-second duration counter), player bullet firing, and speed throttling.

---

## Table of Contents
1. [Player Movement & Joystick Control](#1-player-movement--joystick-control)
2. [Force Field Shield Activation](#2-force-field-shield-activation)
3. [Player Bullet Spawning](#3-player-bullet-spawning)

---

## 1. Player Movement & Joystick Control

### `player_update`
#### **Description**
The function [`player_update`](../../player_logic.c#L45-L110) (Z80 ROM: `$0A20–$0A90`) reads player input ports ($5000) and updates player ship X position on screen (`$43C0`).

#### **Knowledge Graph Links**
* **Called By (Incoming Calls / Backlinks):**
  - [`l2000_alien_wave_main_loop`](alien-wave.md#l2000_alien_wave_main_loop) — [`alien_wave.c`](../../alien_wave.c)

---

## 2. Force Field Shield Activation

### `update_player_shield`
#### **Description**
The function [`update_player_shield`](../../player_logic.c#L125-L165) (Z80 ROM: `$0AA0–$0AD0`) manages the 5-second shield timer `ShieldCount`. When active, it protects the player ship from collisions and enemy fire.

---

## 3. Player Bullet Spawning

### `spawn_player_bullet`
#### **Description**
The function [`spawn_player_bullet`](../../player_logic.c#L180-L220) (Z80 ROM: `$0AE0–$0B20`) spawns player bullet objects in RAM when fire button inputs are detected.
