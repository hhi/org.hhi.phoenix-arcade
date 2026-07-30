# Platform SDL Layer (`platform_sdl.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`platform_sdl.c`](../../platform_sdl.c). This module handles SDL2 window creation, keyboard event loops, texture blitting, and audio device callbacks.

---

## Table of Contents
1. [SDL2 Window & Event Loop](#1-sdl2-window--event-loop)

---

## 1. SDL2 Window & Event Loop

### `main`
#### **Description**
The function [`main`](../../platform_sdl.c#L476) creates the SDL2 window and renderer, initialises the keyboard key map, and starts 44.1kHz audio streaming before entering [`phoenix_main_loop`](hw-video-audio.md#phoenix_main_loop).
