# Hardware Video & Audio (`hw_video_audio.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`hw_video_audio.c`](../../hw_video_audio.c). This module implements the Z80 reset entry point (`RESET`), 60Hz VBlank interrupt handling, VRAM video buffer synchronization, and audio mixing calls.

---

## Table of Contents
1. [VBlank Interrupt & Main Loop](#1-vblank-interrupt--main-loop)

---

## 1. VBlank Interrupt & Main Loop

### `phoenix_main_loop`
#### **Description**
The function [`phoenix_main_loop`](../../hw_video_audio.c#L123) (Z80 ROM: `$0000–$004F`) triggers 60 times per second to update VRAM video pages `$4000–$433F` and sound dispatchers.
