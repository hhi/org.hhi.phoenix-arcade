# Sound Dispatcher (`sound_dispatcher.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`sound_dispatcher.c`](../../sound_dispatcher.c). This module implements the per-frame Z80 sound dispatcher (`$3A10`), siren audio triggers, and intro tune sequencers.

---

## Table of Contents
1. [Sound Routine Dispatcher](#1-sound-routine-dispatcher)

---

## 1. Sound Routine Dispatcher

### `l3a10`
#### **Description**
The function [`l3a10`](../../sound_dispatcher.c#L265) (Z80 ROM: `$3A10–$3A80`) evaluates sound control registers ($5800–$7800) to trigger explosion noises, sirens, and laser pitch shifts.
