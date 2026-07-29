# Utility Helpers (`utilities.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`utilities.c`](../../utilities.c) and [`utilities.h`](../../utilities.h). This module provides RAM memory access wrappers (`mem_read`, `mem_write`) and BCD arithmetic helpers.

---

## Table of Contents
1. [Memory Read/Write Wrappers](#1-memory-readwrite-wrappers)

---

## 1. Memory Read/Write Wrappers

### `mem_read` & `mem_write`
#### **Description**
The functions [`mem_read`](../../utilities.c#L22) and [`mem_write`](../../utilities.c#L35) provide bounds-checked memory access across Arcade RAM (`$4000–$4BFF`) and VRAM pages.
