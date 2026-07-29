# Hardware Video & Audio (`hw_video_audio.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`hw_video_audio.c`](../../hw_video_audio.c). This module implements the Z80 reset entry point (`RESET`), 60Hz VBlank interrupt handling, VRAM video buffer synchronization, and audio mixing calls.

---

## Table of Contents
1. [VBlank Interrupt & Main Loop](#1-vblank-interrupt--main-loop)

---

## 1. VBlank Interrupt & Main Loop

### `vblank_interrupt_handler`
#### **Description**
The function [`vblank_interrupt_handler`](../../hw_video_audio.c#L45-L95) (Z80 ROM: `$0000–$0038`) triggers 60 times per second to update VRAM video pages `$4000–$433F` and sound dispatchers.
