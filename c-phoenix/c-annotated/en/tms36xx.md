# TMS36XX Organ Synthesizer Emulation (`tms36xx.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`tms36xx.c`](../../tms36xx.c). This module emulates Texas Instruments TMS3615 / MM6221AA custom music synthesizers used for background audio.

---

## Table of Contents
1. [TMS3615 Synthesizer Emulation](#1-tms3615-synthesizer-emulation)

---

## 1. TMS3615 Synthesizer Emulation

### `tms36xx_render_internal_sample`
#### **Description**
The function [`tms36xx_render_internal_sample`](../../tms36xx.c#L260) synthesises the organ footages (8', 4', 2') and applies the per-voice decay envelopes for the arcade background melodies.
