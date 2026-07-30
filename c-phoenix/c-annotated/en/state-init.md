# State Init (`state_init.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`state_init.c`](../../state_init.c). This module handles level startup (State 2), round resetting, entity positioning, and RAM clearing.

---

## Table of Contents
1. [Round Initialization](#1-round-initialization)

---

## 1. Round Initialization

### `state_init_start_round`
#### **Description**
The function [`init_alien_control_states`](alien-logic.md#init_alien_control_states) — [`alien_logic.c#L19`](../../alien_logic.c#L19) (Z80 ROM: `$0220–$0280`) initializes alien/bird positions, resets player bullet slots, and transition to active play state.
