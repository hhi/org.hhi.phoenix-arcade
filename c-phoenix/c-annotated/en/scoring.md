# Scoring Logic (`scoring.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`scoring.c`](../../scoring.c). This module handles Binary-Coded Decimal (BCD) score addition, High Score comparisons, extra life thresholds (at 3,000 and 5,000 points), and score rendering.

---

## Table of Contents
1. [BCD Score Addition](#1-bcd-score-addition)
2. [High Score & Extra Life Thresholds](#2-high-score--extra-life-thresholds)

---

## 1. BCD Score Addition

### `add_score`
#### **Description**
The function [`add_score`](../../scoring.c#L35-L85) (Z80 ROM: `$08C0–$0910`) adds points to current player score in BCD format and checks bonus life milestones.

---

## 2. High Score & Extra Life Thresholds

### `update_hi_score`
#### **Description**
The function [`update_hi_score`](../../scoring.c#L39) (Z80 ROM: `$02F0–$032D`) compares current score against all-time High Score, updating High Score RAM registers if exceeded.
