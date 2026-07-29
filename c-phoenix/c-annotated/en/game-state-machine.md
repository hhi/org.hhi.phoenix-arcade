# Game State Machine (`game_state_machine.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`game_state_machine.c`](../../game_state_machine.c). This module implements the central game state machine loop (States 0 through 7) controlling game lifecycle transitions.

---

## Table of Contents
1. [Central State Machine Loop](#1-central-state-machine-loop)

---

## 1. Central State Machine Loop

### `game_state_machine`
#### **Description**
The function [`game_state_machine`](../../game_state_machine.c#L35-L95) (Z80 ROM: `$0020–$0080`) evaluates current state enum `GameState` and dispatches execution to active state handlers.

#### **Knowledge Graph Links**
* **Calls (Outgoing Calls):**
  - [`splash_and_demo`](attract-mode.md#splash_and_demo) — [`attract_mode.c`](../../attract_mode.c)
  - [`state_init_start_round`](state-init.md#state_init_start_round) — [`state_init.c`](../../state_init.c)
  - [`state_play_dispatcher`](state-play.md#state_play_dispatcher) — [`state_play.c`](../../state_play.c)
  - [`handle_player_explosion_state`](state-endings.md#handle_player_explosion_state) — [`state_endings.c`](../../state_endings.c)
