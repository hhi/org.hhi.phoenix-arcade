# Weapon Collision (`weapon_collision.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`weapon_collision.c`](../../weapon_collision.c). This module manages collision detection for player bullets, enemy bullets, shields, and direct collisions between the player ship and flying aliens.

---

## Table of Contents
1. [Player Bullets versus Aliens](#1-player-bullets-versus-aliens)
2. [Enemy Bombs & Bullets](#2-enemy-bombs--bullets)
3. [Alien-Player Direct Collisions](#3-alien-player-direct-collisions)
4. [Player Death & Status Routines](#4-player-death--status-routines)

---

## 1. Player Bullets versus Aliens

### `l0e10`
#### **Description**
The function [`l0e10`](../../weapon_collision.c#L233-L294) (Z80 ROM: `$0E10–$0E9D`) executes collision detection for player bullets against aliens (both inside formation and in free diving flight).

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../../coverage.c#L12)
  - `phoenix_formation_hit_window` — [`phoenix_tables.c`](../../phoenix_tables.c)
  - [`l0c00_kill_score`](#l0c00_kill_score) — [`weapon_collision.c#L214`](../../weapon_collision.c#L214)
  - [`l0ea4_with_score`](#l0ea4_with_score) — [`weapon_collision.c#L301`](../../weapon_collision.c#L301)
  - [`mem_read`](utilities.md#mem_read) — [`utilities.c:L22`](../../utilities.c#L22)
* **Called By (Incoming Calls / Backlinks):**
  - [`check_enemy_bullet_to_player_collision`](#check_enemy_bullet_to_player_collision) — [`weapon_collision.c#L191-L192`](../../weapon_collision.c#L191-L192)

#### **Step-by-Step Functionality**
1. **Bullet Active Check:** Checks whether the player bullet is active (`mem_read(bc) & 0x08 != 0`).
2. **Tile Inspection:** Reads the VRAM cell directly above the bullet. Processes only alien tiles (`$60` through `$BF`).
3. **Alien Outside Formation (`chr >= 0x68`):** Scans the 16 alien records. If the bullet frame overlaps a diving alien, calls [`l0c00_kill_score`](#l0c00_kill_score) and destroys the alien via [`l0ea4_with_score`](#l0ea4_with_score).
4. **Alien In Formation (`chr < 0x68`):** Consults the hit window table `phoenix_formation_hit_window` for the specific tile shape. Upon a hit, 20 points are awarded (`score = 0x0C02`) and [`l0ea4_with_score`](#l0ea4_with_score) is called.

---

### `l0ea4_with_score`
#### **Description**
The function [`l0ea4_with_score`](../../weapon_collision.c#L301-L345) (Z80 ROM: `$0EA4–$0EE5`) registers the destruction of an alien, updates bullet and alien control states, awards score, and initializes an explosion slot.

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../../coverage.c#L12)
  - [`mem_read`](utilities.md#mem_read) / [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
* **Called By (Incoming Calls / Backlinks):**
  - [`l0e10`](#l0e10) — [`weapon_collision.c#L265`](../../weapon_collision.c#L265), [`L291`](../../weapon_collision.c#L291)
  - [`l0f00_check_alien_with_player_collision`](#l0f00_check_alien_with_player_collision) — [`weapon_collision.c#L411`](../../weapon_collision.c#L411), [`L446`](../../weapon_collision.c#L446)

---

## 2. Enemy Bombs & Bullets

### `process_enemy_bombs`
#### **Description**
The function [`process_enemy_bombs`](../../weapon_collision.c#L163-L169) (Z80 ROM: `$0C40–$0C51`) manages the per-frame updating of all 5 enemy bomb slots.

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`l0c84_enemy_bullet_movement`](#l0c84_enemy_bullet_movement) — [`weapon_collision.c#L63`](../../weapon_collision.c#L63)
  - `update_screen_objects` — [`hw_video_audio.c`](../../hw_video_audio.c)
  - `get_screen_ram_address` — [`hw_video_audio.c`](../../hw_video_audio.c)
* **Called By (Incoming Calls / Backlinks):**
  - [`l2160`](alien-wave.md#l2160) — [`alien_wave.c#L145`](../../alien_wave.c#L145)
  - [`l2180`](alien-wave.md#l2180) — [`alien_wave.c#L163`](../../alien_wave.c#L163)
  - [`process_birds`](bird-logic.md#process_birds) — [`bird_logic.c#L48`](../../bird_logic.c#L48)

---

### `l0c84_enemy_bullet_movement`
#### **Description**
The function [`l0c84_enemy_bullet_movement`](../../weapon_collision.c#L63-L98) (Z80 ROM: `$0C84–$0CB3`) moves an enemy bullet downward (`Y += 4`), toggles its animation frame and checks for hits on the player ship or player force field.

---

## 3. Alien-Player Direct Collisions

### `l0f00_check_alien_with_player_collision`
#### **Description**
The function [`l0f00_check_alien_with_player_collision`](../../weapon_collision.c#L380-L454) (Z80 ROM: `$0F00–$0FB9`) checks physical collisions between diving aliens and the player ship (or the player force field).

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../../coverage.c#L12)
  - [`l0f56_screen_ram_collision`](#l0f56_screen_ram_collision) — [`weapon_collision.c#L352`](../../weapon_collision.c#L352)
  - [`l0cc4_player_killed`](#l0cc4_player_killed) — [`weapon_collision.c#L442`](../../weapon_collision.c#L442)
  - [`l0ea4_with_score`](#l0ea4_with_score) — [`weapon_collision.c#L411`](../../weapon_collision.c#L411), [`L446`](../../weapon_collision.c#L446)
* **Called By (Incoming Calls / Backlinks):**
  - [`l2150`](alien-wave.md#l2150) — [`alien_wave.c#L137`](../../alien_wave.c#L137)
  - [`l2190`](alien-wave.md#l2190) — [`alien_wave.c#L174`](../../alien_wave.c#L174)

#### **Step-by-Step Functionality**
1. **Active Force Field (`ShieldCount >= 0xC0`):** Checks via [`l0f56_screen_ram_collision`](#l0f56_screen_ram_collision) whether an alien hits the shield. If so: destroys the alien without damaging the player (`l0ea4_with_score(0x0D02, ...)`).
2. **No Force Field:** If an alien hits the ship: destroys the player ship via [`l0cc4_player_killed`](#l0cc4_player_killed) and destroys the alien via [`l0ea4_with_score`](#l0ea4_with_score).

---

## 4. Player Death & Status Routines

### `l0cc4_player_killed`
#### **Description**
The function [`l0cc4_player_killed`](../../weapon_collision.c#L51-L56) (Z80 ROM: `$0CC4–$0CD3`) is called upon a fatal hit on the player ship.

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../../coverage.c#L12)
* **Called By (Incoming Calls / Backlinks):**
  - [`l0cb4_check_bullet_hit_player`](#l0cb4_check_bullet_hit_player) — [`weapon_collision.c#L43`](../../weapon_collision.c#L43)
  - [`l0f00_check_alien_with_player_collision`](#l0f00_check_alien_with_player_collision) — [`weapon_collision.c#L442`](../../weapon_collision.c#L442)
