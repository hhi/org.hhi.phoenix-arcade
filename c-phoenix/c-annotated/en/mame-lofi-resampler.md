# MAME Lo-Fi Resampler (`mame_lofi_resampler.c`) - C-Annotated Knowledge Graph Documentation

This document contains an annotated analysis of all functions in [`mame_lofi_resampler.c`](../../mame_lofi_resampler.c). This module implements a 4-point cubic polynomial resampler for arcade audio sample conversion.

---

## Table of Contents
1. [Cubic Resampler Logic](#1-cubic-resampler-logic)

---

## 1. Cubic Resampler Logic

### `mame_lofi_resampler_next`
#### **Description**
The function [`mame_lofi_resampler_next`](../../mame_lofi_resampler.c#L66) interpolates raw audio streams to match target platform sample rates.
