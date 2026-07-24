# Phoenix C-Port - Logical Architecture

This document provides a logical grouping of all C files in the Phoenix project, categorizing them by their architectural domain and responsibility within the emulator/port.

## 1. Core Architecture & Hardware Abstraction
Files that form the bridge between the original arcade hardware and the modern OS.

- [`platform_sdl.c`](../platform_sdl.c) - Modern system bindings: SDL2 event loop, input handling, and final screen rendering.
- [`hw_video_audio.c`](../hw_video_audio.c) - Arcade hardware abstraction: Video RAM mapping, palette setup, and I/O writes.
- [`phoenix_tables.c`](../phoenix_tables.c) - Named game-data tables derived
  from the original program ROM.
- `phoenix_state.h` - Defines the monolithic `PhoenixState` struct, representing the 4KB RAM and hardware registers.
- `phoenix_hw.h` / `z80_core.h` - Hardware definitions, constants, and `mem_read`/`mem_write` abstractions.

## 2. Game State Management
The high-level control flow of the game, dictating what mode the arcade machine is currently in.

- [`game_state_machine.c`](../game_state_machine.c) - The central brain switching between attract mode, gameplay, and endings.
- [`attract_mode.c`](../attract_mode.c) - The splash screen, coin prompt, and demo playback.
- [`state_init.c`](../state_init.c) - Setting up the board when a new game or level starts.
- [`state_play.c`](../state_play.c) - The main loop that runs while the player is actively fighting.
- [`state_endings.c`](../state_endings.c) - Handling what happens when a level is cleared or the player dies.

## 3. Audio Subsystem
Everything responsible for generating the iconic arcade sounds.

- [`sound.c`](../sound.c) - High-level sound control: triggering effects based on game events.
- [`sound_discrete.c`](../sound_discrete.c) - Emulation of the discrete analog sound circuitry (oscillators, noise generators).
- [`tms36xx.c`](../tms36xx.c) - Emulation of the specific TMS3615 sound chip used for music.
- [`mame_lofi_resampler.c`](../mame_lofi_resampler.c) - Audio buffering and resampling utilities (borrowed from MAME).

## 4. Entity Logic & Behaviors
The AI, movement, and logic for all objects moving around the screen.

- [`player_logic.c`](../player_logic.c) - Player ship movement, shield logic, and firing.
- [`player_explosion.c`](../player_explosion.c) - The specific animation logic when the player is destroyed.
- [`bird_logic.c`](../bird_logic.c) - High-level logic and state management for the bird enemies.
- [`birds_vertical_movement.c`](../birds_vertical_movement.c) - Specific flight paths and swooping math for birds.
- [`bird_wave_behavior.c`](../bird_wave_behavior.c) - Complex/miscellaneous bird logic (egg hatching, formations).
- [`alien_logic.c`](../alien_logic.c) / [`alien_wave.c`](../alien_wave.c) - Behaviors for the smaller alien waves in early levels.
- [`mothership_logic.c`](../mothership_logic.c) / [`mothership_impl.c`](../mothership_impl.c) - AI and mechanics for the final boss encounter.

## 5. Collision & Mechanics
Interaction between entities, hitting targets, and scoring.

- [`collision_detection.c`](../collision_detection.c) - Detecting overlaps between player, enemies, and shields.
- [`weapon_collision.c`](../weapon_collision.c) - Dedicated logic for bullet-vs-enemy math.
- [`scoring.c`](../scoring.c) - Awarding points, drawing scores to the screen, and extra lives.

## 6. Rendering
- [`sprite_rendering.c`](../sprite_rendering.c) - Translating entity states into hardware sprite registers and tile maps.

## 7. Utilities & Infrastructure
- [`utilities.c`](../utilities.c) - Common math, random number generation, and bitwise helpers.
- [`coverage.c`](../coverage.c) - Instrumentation for tracking which C functions are actually executed.
- [`init_global_level_data.c`](../init_global_level_data.c) - Hardcoded lookup tables for level configuration.
- [`misc_logic.c`](../misc_logic.c) - Miscellaneous routines that span multiple domains.
- [`rom_compat_stubs.c`](../rom_compat_stubs.c) - ROM-compatibiliteitsstubs voor nog onduidelijke of bewust behouden routines.
