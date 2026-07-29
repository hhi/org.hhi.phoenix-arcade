# State Init (`state_init.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`state_init.c`](../../state_init.c). This module handles level startup (State 2), round resetting, entity positioning, and RAM clearing.

---

## Table of Contents
1. [Round Initialization](#1-round-initialization)

---

## 1. Round Initialization

### `state_init_start_round`
#### **Description**
The function [`state_init_start_round`](../../state_init.c#L45-L95) (Z80 ROM: `$0220–$0280`) initializes alien/bird positions, resets player bullet slots, and transition to active play state.
