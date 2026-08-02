# Phoenix Animations & Trajectories Guide (`c-phoenix/animations`)

Welcome to the central visual archive for the *Phoenix* Arcade Game (`c-phoenix`). This directory answers two different questions: **what** each object is made of, and **where** it moves.

## Source Priority

The source of truth is, in this order: **Z80 ASM/ROM → C-port → annotated analysis → visual assets**. SVGs make ROM and C data accessible, but do not replace the underlying source code. Any conclusion without links to ASM, ROM, or C code is an interpretation requiring verification.

---

## 🗂️ On this page

- [Master overview animation](#-master-overview-animation) — three movement types at once
- [The bird, phase by phase](#-the-bird-phase-by-phase) — egg to grown bird
- [What everything is made of](#-what-everything-is-made-of) — characters, colour groups, sprite sequences
- [Flight patterns & trajectories](#-flight-patterns--trajectories) — the paths objects follow

---

## 🎬 Master Overview Animation

Three of the game's movement types at once — an alien swoop, a bird dive-bomb, and the mothership's descent — all drawn from the vectors stored in the ROM:

![Master overview animation: an alien swoop, a bird dive-bomb with its dropped bomb, and the mothership's steady descent, all generated from the original ROM movement vectors](../00_overview_flight_patterns.svg)

Source file: [`../00_overview_flight_patterns.svg`](../00_overview_flight_patterns.svg).

---

## 🦅 The bird, phase by phase

Phoenix birds are not one sprite. They hatch, grow, attack, and explode — six distinct animation phases, each reconstructed from the graphics ROM:

| Egg hatching | Small bird flapping | Full-grown wing matrix |
| --- | --- | --- |
| <img src="../01_egg_hatching.svg" width="230" alt="An egg hatching into a bird"> | <img src="../02_small_bird_flapping.svg" width="230" alt="A small bird flapping its wings, frames A and B"> | <img src="../03_grown_bird_matrix.svg" width="230" alt="The 4x4 wing position matrix of a full-grown bird"> |
| **Dive-bombing attack** | **Explosion and bonus** | **Mothership descent** |
| <img src="../04_dive_bombing_attack.svg" width="230" alt="A bird diving at the player and dropping a bomb"> | <img src="../05_bird_explosion_bonus.svg" width="230" alt="A bird exploding into particles with a 500 point bonus"> | <img src="../09_mothership_descent_trajectory.svg" width="230" alt="The mothership descending on its fixed trajectory"> |

📄 **[`bird-animations.md`](bird-animations.md)** — all six phases in detail, with the RAM slots and ROM routines behind each one.

---

## 🔡 What everything is made of

Phoenix has no sprite engine. Every object on screen is a handful of **8×8 characters** written into screen memory, and the character's own index decides its colour — bits 5-7 select one of eight colour groups in the PROM table. That is why each block of 32 characters looks like one family: letters, digits, the player ship, the birds, explosions, the shield.

There are two independent sets of 256 characters. The foreground set holds the player, the aliens, the explosions and the shield; the background set holds the starfield, the planet, the birds and the mothership.

Object sizes are not fixed. A small family of **drawNxN routines** writes two characters down a column and then steps sideways, and for some objects `sprite_rendering.c` picks `1x1`, `2x1`, `1x2` or `2x2` at runtime from the object's control byte — so the same table can produce different shapes depending on what the object is doing.

📄 **[`animation-sequences.md`](animation-sequences.md)** — the complete character set, every sprite sequence frame by frame with its character codes, the playing versions, and the C routine that draws each one.

---

## 🎨 Flight Patterns & Trajectories

Every alien formation and bird dive follows a fixed path, stored in the ROM as a short list of movement vectors. This directory holds 130 SVG files; the 78 pattern animations below are one per ROM-defined pattern, grouped by the subsystem that uses them:

- **Cluster A** (ROM `$1000–$13FF`) — patterns 01–18, orderly formation waves in alien waves 1 & 3
- **Cluster B** (ROM `$2C00–$2FFF`) — patterns 19–36, breakout aliens and mothership escorts
- **Bird AI scripts** (ROM `$3F00–$3F7F`) — 16 behaviour scripts
- **Bird dive & spawn positions** (ROM `$3DC0–$3DDF`) — 16 start and dive coordinates

📄 **[`animation-trajectory.md`](animation-trajectory.md)** — every pattern shown and explained, with the ROM cluster layout, the RAM data structures (`$4000-$4BFF`) and the vector engine behind them.

📐 **[`animation-trajectory-detailed.md`](animation-trajectory-detailed.md)** — step-by-step coordinate tables per pattern: step number, vector index, dX, dY, cumulative X/Y.

---

## 🔗 Knowledge Graph Links

Each C source file in this subsystem has an annotated counterpart in `../../c-annotated/en/`:

* [`phoenix_tables.c`](../../phoenix_tables.c) → [`phoenix-tables.md`](../../c-annotated/en/phoenix-tables.md)
* [`alien_logic.c`](../../alien_logic.c) → [`alien-logic.md`](../../c-annotated/en/alien-logic.md)
* [`bird_logic.c`](../../bird_logic.c) → [`bird-logic.md`](../../c-annotated/en/bird-logic.md)
* [`bird_wave_behavior.c`](../../bird_wave_behavior.c) → [`bird-wave-behavior.md`](../../c-annotated/en/bird-wave-behavior.md)
* [`attract_mode.c`](../../attract_mode.c) → [`attract-mode.md`](../../c-annotated/en/attract-mode.md)
