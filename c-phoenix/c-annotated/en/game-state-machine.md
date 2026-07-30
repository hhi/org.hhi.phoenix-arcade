# Game State Machine (`game_state_machine.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`game_state_machine.c`](../../game_state_machine.c). This module implements the central game state machine loop (States 0 through 7) controlling game lifecycle transitions.

---

## Table of Contents
1. [Central State Machine Loop](#1-central-state-machine-loop)

---

## 1. Central State Machine Loop

### `game_state_machine`
#### **Description**
The function [`game_state_machine`](../../game_state_machine.c#L35-L95) (Z80 ROM: `$0400–$041D`) evaluates current state enum `GameState` and dispatches execution to active state handlers.

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`splash_and_demo`](attract-mode.md#splash_and_demo) — [`attract_mode.c`](../../attract_mode.c)
  - [`init_alien_control_states`](alien-logic.md#init_alien_control_states) — [`alien_logic.c#L19`](../../alien_logic.c#L19)
  - [`level_1_3_B_player_alive_aliens`](state-play.md#level_1_3_b_player_alive_aliens) — [`state_play.c#L16`](../../state_play.c#L16)
  - [`state_4_player_ship_explosion`](state-endings.md#state_4_player_ship_explosion) — [`state_endings.c#L33`](../../state_endings.c#L33)
