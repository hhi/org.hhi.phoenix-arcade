# Phoenix ROM Tables (`phoenix_tables.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all ROM lookup tables in [`phoenix_tables.c`](../../phoenix_tables.c) and [`phoenix_tables.h`](../../phoenix_tables.h).

---

## Table of Contents
1. [Alien Flight Vector Tables (Clusters A & B)](#1-alien-flight-vector-tables-clusters-a--b)
2. [Hit Window & Spawn Tables](#2-hit-window--spawn-tables)

---

## 1. Alien Flight Vector Tables (Clusters A & B)

### `phoenix_alien_movement_cluster_a` & `phoenix_alien_movement_cluster_b`
#### **Description**
Vector step lookup tables stored in Z80 ROM (`$1000–$13FF` and `$2C00–$2FFF`) defining alien diving trajectories and formation paths.
