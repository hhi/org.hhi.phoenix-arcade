# Init Global Level Data (`init_global_level_data.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`init_global_level_data.c`](../../init_global_level_data.c). This module copies 12 configuration bytes per level pattern into RAM registers during level transitions.

---

## Table of Contents
1. [Global Level Data Transfer](#1-global-level-data-transfer)

---

## 1. Global Level Data Transfer

### `init_global_level_data`
#### **Description**
The function [`init_global_level_data`](../../init_global_level_data.c#L25-L65) sets up speed parameters and alien counts for the active round.
