# State Play Level Dispatcher (`state_play.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`state_play.c`](../../state_play.c). This module dispatches active gameplay frames across 12 level phases (Wave 1 aliens, Wave 3 aliens, Wave 5 birds, Wave 7 birds, Mothership descent, etc.).

---

## Table of Contents
1. [Level Phase Dispatcher](#1-level-phase-dispatcher)

---

## 1. Level Phase Dispatcher

### `state_play_dispatcher`
#### **Description**
The function [`state_play_dispatcher`](../../state_play.c#L45-L110) (Z80 ROM: `$01A0–$0200`) checks `LevelAndRound` to route execution to `alien_wave_main_loop`, `process_birds`, or `mothership_tile_hit_check`.
