# Phoenix Animations & Trajectories Guide (`c-phoenix/animations`)

Welcome to the central visual archive for the *Phoenix* Arcade Game (`c-phoenix`). This directory contains functional, memory, and visual analyses of both **bird animations** and **vectorial flight trajectories** for aliens, birds, and the mothership.

## Source Priority

The source of truth is, in this order: **Z80 ASM/ROM → C-port → annotated analysis → visual assets**. SVGs make ROM and C data accessible, but do not replace the underlying source code. Any conclusion without links to ASM, ROM, or C code is an interpretation requiring verification.

---

## 🗂️ Table of Contents

1. 🚀 [`animation-trajectory.md`](animation-trajectory.md) — **In-depth analysis of prescribed flight patterns, RAM data structures (`$4000-$4BFF`), Z80 ROM cluster layout, master overview flight animation, and 78 SVG animations.**
2. 📐 [`animation-trajectory-detailed.md`](animation-trajectory-detailed.md) — **Detailed step-by-step coordinate tables per individual flight pattern (step #, vector index, dX, dY, cumulative X/Y).**
3. 🦅 [`bird-animations.md`](bird-animations.md) — **Visual guide for all 6 bird animation phases (egg hatching to grown bird and bonus explosion).**

---

## 🏛️ Why Separate ROM Clusters & Chapter Organization?

- **Cluster A (ROM `$1000–$13FF` / EPROM Chip 1):** Contains **Patterns 01 through 18** for orderly formation waves in **Alien Wave 1 & 3**.
- **Cluster B (ROM `$2C00–$2FFF` / EPROM Chip 3):** Contains **Patterns 19 through 36** for **Breakout aliens** and **Mothership escorts** (Levels 9, 10, 11).
- **Chapter Organization:** Follows the exact 4 physical game entity subsystems of the Arcade Z80 engine (Wave 1/3 Aliens, Breakout/Escort Aliens, Wave 5/7 Bird AI & Dive spawns, Mothership & Attract Mode).

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

---

## 🎨 Flight Patterns & Trajectories (78 SVG Assets)

Every entry below is an animation of one ROM-defined movement pattern. They are listed rather than shown because there are 78 of them; open any file to watch it.

### 👾 Alien Cluster A: Wave 1 & 3 Patterns (ROM `$1000–$13FF`)
- [`../07_alien_closed_loop_cluster_a.svg`](../07_alien_closed_loop_cluster_a.svg) — Cluster A overview animation
- [`../cluster_a/pattern_01.svg`](../cluster_a/pattern_01.svg) through [`../cluster_a/pattern_18.svg`](../cluster_a/pattern_18.svg) — 18 closed-loop flight patterns.

### 🛸 Alien Cluster B: Breakout & Escort Patterns (ROM `$2C00–$2FFF`)
- [`../08_alien_breakout_cluster_b.svg`](../08_alien_breakout_cluster_b.svg) — Cluster B overview animation
- [`../cluster_b/pattern_19.svg`](../cluster_b/pattern_19.svg) through [`../cluster_b/pattern_36.svg`](../cluster_b/pattern_36.svg) — 18 breakout & escort attack patterns.

### 🪶 Bird AI Behavior Scripts (ROM `$3F00–$3F7F`)
- [`../bird_scripts/bird_script_00.svg`](../bird_scripts/bird_script_00.svg) through [`../bird_scripts/bird_script_15.svg`](../bird_scripts/bird_script_15.svg) — 16 AI behavior scripts.

### 🎯 Bird Dive & Spawn Positions (ROM `$3DC0–$3DDF`)
- [`../bird_dive_spawns/dive_spawn_00.svg`](../bird_dive_spawns/dive_spawn_00.svg) through [`../bird_dive_spawns/dive_spawn_15.svg`](../bird_dive_spawns/dive_spawn_15.svg) — 16 start & dive coordinates.

### 🦅 Bird & Mothership Animations
- 🥚 [`../01_egg_hatching.svg`](../01_egg_hatching.svg) — Egg to bird hatching transformation
- 🪶 [`../02_small_bird_flapping.svg`](../02_small_bird_flapping.svg) — Wing flapping cycles (Frame A & B)
- 🦅 [`../03_grown_bird_matrix.svg`](../03_grown_bird_matrix.svg) — Full-grown bird 4x4 wing matrix
- 💣 [`../04_dive_bombing_attack.svg`](../04_dive_bombing_attack.svg) — Dive bombing attack flight
- 💥 [`../05_bird_explosion_bonus.svg`](../05_bird_explosion_bonus.svg) — Particle explosion & 500pt bonus score
- 🎬 [`../06_intro_splash_bird.svg`](../06_intro_splash_bird.svg) — Intro splash bird (Attract Mode)
- 🚀 [`../09_mothership_descent_trajectory.svg`](../09_mothership_descent_trajectory.svg) — Mothership steady descent trajectory

---

## 🔗 Knowledge Graph Links

All documents and animations in this directory are 1-to-1 linked with C source files and the Knowledge Graph in `../../c-annotated/en/`:
* [`phoenix_tables.c`](../../phoenix_tables.c) → [`phoenix-tables.md`](../../c-annotated/en/phoenix-tables.md)
* [`alien_logic.c`](../../alien_logic.c) → [`alien-logic.md`](../../c-annotated/en/alien-logic.md)
* [`bird_logic.c`](../../bird_logic.c) → [`bird-logic.md`](../../c-annotated/en/bird-logic.md)
* [`bird_wave_behavior.c`](../../bird_wave_behavior.c) → [`bird-wave-behavior.md`](../../c-annotated/en/bird-wave-behavior.md)
* [`attract_mode.c`](../../attract_mode.c) → [`attract-mode.md`](../../c-annotated/en/attract-mode.md)
