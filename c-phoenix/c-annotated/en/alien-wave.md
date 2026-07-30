# Alien Wave Main Loop (`alien_wave.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`alien_wave.c`](../../alien_wave.c). This module controls the main game loop, frame interleaving, player updates, and round progression for alien waves (levels 1, 3, and B).

---

## Table of Contents
1. [Main Loop of Alien Wave](#1-main-loop-of-alien-wave)
2. [Frame Interleaving & Task Scheduling](#2-frame-interleaving--task-scheduling)
3. [Round Transition & Screen Clearing](#3-round-transition--screen-clearing)

---

## 1. Main Loop of Alien Wave

### `l2000_alien_wave_main_loop`
#### **Description**
The function [`l2000_alien_wave_main_loop`](../../alien_wave.c#L35-L95) (Z80 ROM: `$2000–$2060`) executes the central game loop per VBlank frame for Waves 1, 3, and B.

#### **Context & Invocation**
Called from the main game state machine while playing an alien wave:
```c
l2000_alien_wave_main_loop();
```

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`player_update`](player-logic.md#player_update) — [`player_logic.c`](../../player_logic.c)
  - [`process_enemy_bombs`](weapon-collision.md#process_enemy_bombs) — [`weapon_collision.c`](../../weapon_collision.c)
  - [`handle_animations_for_killed_aliens`](alien-logic.md#handle_animations_for_killed_aliens) — [`alien_logic.c`](../../alien_logic.c)
  - [`l2130`](#l2130) — [`alien_wave.c:L58`](../../alien_wave.c#L58)
  - [`l2150`](#l2150) — [`alien_wave.c:L65`](../../alien_wave.c#L65)
  - [`l2160`](#l2160) — [`alien_wave.c:L70`](../../alien_wave.c#L70)
  - [`l2180`](#l2180) — [`alien_wave.c:L75`](../../alien_wave.c#L75)
  - [`l2190`](#l2190) — [`alien_wave.c:L80`](../../alien_wave.c#L80)
  - [`l21ba`](#l21ba) — [`alien_wave.c:L85`](../../alien_wave.c#L85)
* **Called By (Incoming Calls / Backlinks):**
  - [`level_1_3_B_player_alive_aliens`](state-play.md#level_1_3_b_player_alive_aliens) — [`state_play.c#L16`](../../state_play.c#L16)

#### **Step-by-Step Functionality**
1. **Player & Collisions:** Processes player controls via [`player_update`](player-logic.md#player_update) and updates explosions via [`handle_animations_for_killed_aliens`](alien-logic.md#handle_animations_for_killed_aliens).
2. **Task Interleaving:** Based on counter `state.FrameInterleaveCounter & 3`, executes one of four specific task bundles per frame:
   - `case 0`: Calls [`l2150`](#l2150) (Object RAM update & collision with player).
   - `case 1`: Calls [`l2160`](#l2160) (Enemy bombs & alien pattern scheduler).
   - `case 2`: Calls [`l2180`](#l2180) (Enemy bombs & dive-bomb attack triggers).
   - `case 3`: Calls [`l2190`](#l2190) (Collision check & breakout triggers).
3. **Background Scrolling:** Calls [`l2130`](#l2130) to update starfield scrolling speed and registers.
