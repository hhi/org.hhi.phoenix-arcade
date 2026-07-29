# Phoenix C-Port Architectural Walkthrough (`walkthrough.md`)

This document provides a comprehensive technical walkthrough of the C-port architecture for the *Phoenix* Arcade Game (`c-phoenix`).

---

## Table of Contents
1. [Core Engine Subsystems](#1-core-engine-subsystems)
2. [Arcade Hardware Emulation](#2-arcade-hardware-emulation)

---

## 1. Core Engine Subsystems

The *Phoenix* engine is divided into 4 primary entity subsystems:
- **Alien Formations & Breakouts:** Managed by `alien_wave.c` and `alien_logic.c`.
- **Bird Swarms & AI Scripts:** Managed by `bird_logic.c` and `bird_wave_behavior.c`.
- **Mothership Descent & Core Shielding:** Managed by `mothership_impl.c` and `mothership_logic.c`.
- **Attract Mode & Title Sequencer:** Managed by `attract_mode.c`.

---

## 2. Arcade Hardware Emulation

Video rendering targets a 90° rotated 32x32 tile matrix VRAM buffer (`$4000–$433F`) combined with 44.1kHz discrete audio mixing.
