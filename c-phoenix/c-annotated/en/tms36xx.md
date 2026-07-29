# TMS36XX Organ Synthesizer Emulation (`tms36xx.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`tms36xx.c`](../../tms36xx.c). This module emulates Texas Instruments TMS3615 / MM6221AA custom music synthesizers used for background audio.

---

## Table of Contents
1. [TMS3615 Synthesizer Emulation](#1-tms3615-synthesizer-emulation)

---

## 1. TMS3615 Synthesizer Emulation

### `tms36xx_update`
#### **Description**
The function [`tms36xx_update`](../../tms36xx.c#L45-L95) synthesizes organ footages (8', 4', 2') and decay envelopes for arcade background melodies.
