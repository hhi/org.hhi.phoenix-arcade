# Phoenix Animations & Trajectories Guide (`c-phoenix/animations`)

Welcome to the central visual archive for the *Phoenix* Arcade Game (`c-phoenix`). This directory contains functional, memory, and visual analyses of both **bird animations** and **vectorial flight trajectories** for aliens, birds, and the mothership.

## Source Priority

The source of truth is, in this order: **Z80 ASM/ROM → C-port → annotated analysis → visual assets**. SVGs make ROM and C data accessible, but do not replace the underlying source code. Any conclusion without links to ASM, ROM, or C code is an interpretation requiring verification.

---

## 🗂️ Table of Contents

1. 🚀 [`animation-trajectory.md`](animation-trajectory.md) — **In-depth analysis of prescribed flight patterns, RAM data structures (`$4000-$4BFF`), Z80 ROM cluster layout, master overview flight animation, and 128 SVG animations.**
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

## 🔡 What everything is actually made of

The diagrams above are interpretations. The sheets below are not: they are rendered straight from the decoded graphics ROM and colour PROM, using the same palette arithmetic as the running game.

Phoenix has no sprite engine. Every object on screen is a handful of **8×8 characters** written into screen memory, and the character's own index decides its colour — bits 5-7 select one of eight colour groups in the PROM table. That is why each block of 32 characters looks like one family:

![The complete 256-character foreground set, arranged in eight colour groups, showing that the character index selects the colour family](../sprites/character-set-foreground.svg)

Stars, planets, the mothership and the aliens come from a second, independent set:

![The complete 256-character background set, arranged in eight colour groups](../sprites/character-set-background.svg)

### The sequences, with their character composition

Phoenix has a small family of **drawNxN routines**, and which one draws an object decides its size and the order its characters are written. They all work the same way: two characters fill one column top to bottom, then the routine steps sideways to the next column. Each sheet below states the routine it used.

Underneath every frame are the **character codes** it is assembled from — cross-reference them with the sets above to see exactly which pixels the hardware fetched.

**The player ship** — eight poses, four characters each, drawn as a 2×2 block from `phoenix_sprite_character_block_shapes`:

![The eight poses of the player ship, each built from four 8x8 characters in a 2x2 block, with the character codes listed underneath](../sprites/sequence-player-ship.svg)

<img src="../sprites/animation-player-ship.svg" width="300" alt="The eight player-ship poses cycling as an animation">

**The formation alien** — and it is not one sprite. As it drifts, climbs and dives, the game switches between *different block sizes*: `sprite_rendering.c` picks `1x1`, `2x1`, `1x2` or `2x2` at runtime from the object's control byte. No table holds that size, so these poses were read out of the foreground screen memory of the committed recording `c-last-grown-bird.bin.gz`.

Flying level, two characters side by side:

![Six level-flight poses of the formation alien, each two characters wide](../sprites/sequence-alien-level.svg)

<img src="../sprites/animation-alien-level.svg" width="240" alt="The alien's level-flight poses playing">

Climbing, one character wide and two tall — the same creature seen head-on:

![Six climbing poses of the formation alien, each one character wide and two tall](../sprites/sequence-alien-climb.svg)

<img src="../sprites/animation-alien-climb.svg" width="200" alt="The alien's climbing poses playing">

Diving and banking, its widest form:

![Eight diving and banking poses of the formation alien, each a 2x2 block](../sprites/sequence-alien-dive.svg)

<img src="../sprites/animation-alien-dive.svg" width="240" alt="The alien's diving poses playing">

The same scan over the same recording also produced the 3×2 explosion blocks shown below, which is an independent check that this way of reading the dump is sound.

Grouping poses by size tells you which shapes exist, but not the order the game shows them in. Following *one* object frame by frame does — here is a single alien leaving the formation and dropping fourteen rows onto the player, with its block size changing as it goes:

![One alien followed through a dive, its pose and block size changing in sequence](../sprites/sequence-alien-dive-order.svg)

<img src="../sprites/animation-alien-dive-order.svg" width="240" alt="One alien's dive playing in the order it happened">

**The mothership's pilot** — the tallest block any of these routines draws, four rows by two columns:

![The eight animation frames of the mothership pilot and antenna, each eight background characters](../sprites/sequence-mothership-pilot.svg)

<img src="../sprites/animation-mothership-pilot.svg" width="260" alt="The mothership pilot's eight frames playing as an animation">

**An explosion** — eight frames from `phoenix_alien_explosion_frames`, and here the indirection matters. Those bytes are *not* character codes: `alien_logic.c` turns each one into an address with `0x1700 | byte`, then calls `drawNx2` with n=3, which reads six characters from `phoenix_shield_and_drawnx2_shapes`. So one frame is a 3×2 block, not one character:

![The eight explosion frames, each a 3x2 block of six characters resolved through an address table, with the character codes listed underneath](../sprites/sequence-explosion.svg)

<img src="../sprites/animation-explosion.svg" width="330" alt="The explosion's eight frames playing as an animation">

**The bonus explosion** — the same 3×2 routine, but called twice with fixed addresses, once for each half of a wider burst:

![The two halves of the bonus explosion, each a 3x2 block of six characters, with the character codes listed underneath](../sprites/sequence-bonus-explosion.svg)

<img src="../sprites/animation-bonus-explosion.svg" width="330" alt="The two bonus-explosion halves alternating as an animation">

### The birds

Birds take a third route. `drawbirdobject` looks up a **width** for the bird's shape type in `phoenix_bird_draw_entries`, then a **pointer** to its character data in `phoenix_bird_shape_pointers`, and `draw_bird_shape_350c` walks that data two characters at a time. So a bird is between three and seven columns wide depending only on its type — the egg and the grown bird are the same routine with a different column count:

![Eight bird shape types side by side, from a small round egg through a hatching bird to a grown bird with a full wingspan](../sprites/sequence-bird-growth.svg)

<img src="../sprites/animation-bird-growth.svg" width="420" alt="The bird shape types playing in width order, from egg to full wingspan">

Each type has four frames of its own. **The small bird**, six characters wide:

![The four animation frames of the small bird, with the character codes listed underneath](../sprites/sequence-bird-small.svg)

<img src="../sprites/animation-bird-small.svg" width="380" alt="The small bird's four frames playing as an animation">

**The grown bird**, seven characters wide — the widest sprite the routine draws:

![The four animation frames of the grown bird, with the character codes listed underneath](../sprites/sequence-bird-grown.svg)

<img src="../sprites/animation-bird-grown.svg" width="420" alt="The grown bird's four frames playing as an animation">

### Regenerating these sheets

All of them come out of one script, run from the repository root:

```sh
python3 c-phoenix/tools/generate_sprite_sheets.py
```

It reads `phoenix_render_assets.h` and `phoenix_tables.c` for everything that *is* in a table, and the committed recording `c-last-grown-bird.bin.gz` for the objects whose size is only decided at runtime. Each run prints which recording it used.

That default recording contains no mothership and no multi-character shield. To cover those, produce the richer bird-investigation session first and point the script at it — again from the repository root:

```sh
make -C c-phoenix tracerun \
  COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt \
  COMPARE_FRAMES=13935 \
  COMPARE_NAME=bird-investigation \
  COMPARE_STOP_AFTER=999999

python3 c-phoenix/tools/generate_sprite_sheets.py \
  --dump /tmp/port_bird-investigation.bin
```

`tracerun` runs `comparerun` first, so the sibling JPhoenix project must be built (JDK 11+). It writes `/tmp/port_bird-investigation.bin` — note the underscore after `port` — plus `/tmp/ref_bird-investigation.bin` for the emulator side. Dumps deliberately stay in `/tmp`; see [`context/traces/README.md`](../../context/traces/README.md) for why they are not committed.

**The player shield** — sixteen characters in a 4×4 block, the largest single sprite in the game. Like the alien its size is a runtime decision, so this too was read out of a recording:

![The player shield as drawn in a recorded session, a 4x4 block of sixteen characters, with the character codes listed](../sprites/sequence-shield.svg)

> **Still open: the mothership.** Scanning background RAM by colour group cannot tell a mothership hull from a grown bird — both live in the same upper groups, and that scan produced birds labelled as a hull, twice. Identifying the object needs its RAM slot rather than its colours, which is a job for the visual tracer.

The still sheets and the playing versions are all regenerated by [`tools/generate_sprite_sheets.py`](../../tools/generate_sprite_sheets.py) from `phoenix_render_assets.h` and `phoenix_tables.c`. Nothing in them is hand-drawn; if the ROM data changes, the sheets change with it.

> **Still to add:** the mothership explosion. It draws from `phoenix_shield_and_drawnx2_shapes` like the explosions do, but its call site has not been traced yet, so it is left out rather than guessed at.

---

## 🎨 Flight Patterns & Trajectories

This directory holds 128 SVG files: the 78 flight patterns below plus the sprite sheets from the previous section. They are listed rather than shown because there are so many; open any file to watch it.

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
