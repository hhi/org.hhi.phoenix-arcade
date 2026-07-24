# Phoenix: Game Design and Architecture

This guide describes how the current C port executes the original 8080 ROM
behaviour. It is an orientation guide, not the normative specification for a
translation change: [code-annotated.asm](code-annotated.asm), [RAMUse.md](RAMUse.md),
and `[ASM: ...]` anchors in C code take precedence on conflict.

## Purpose and Structure

Phoenix is a fixed-screen shooter for one or two players. The player moves a
ship horizontally, fires upward, and uses a temporary shield. Rounds alternate
alien and bird waves with a mothership encounter. Attract mode presents the
game and runs a demo until a coin and start selection occur.

The C port is not a newly designed game engine. It deliberately retains ROM
control flow, RAM layout, and frame routines. Consequently game rules,
animation, sound, and rendering are spread across small routines that each
represent a ROM address.

## Architecture at a Glance

```text
SDL platform (window, input, audio output, deterministic CLI)
                              |
                              v
phoenix_main_loop() -- per vblank/frame --> attract mode or game mode
                              |                         |
                              |                         v
                              |                  game_state_machine()
                              |                    |-- initialisation
                              |                    |-- play round
                              |                    |-- explosion/end
                              v
hardware layer: video RAM, scroll, palette, sound, input ports
                              ^
                              |
PhoenixState: byte-exact game RAM ($4000-$4BFF)
```

The main loop is in [`hw_video_audio.c`](../hw_video_audio.c). It waits for
vertical blanking, handles machine input, and selects the attract branch
(`splash_and_demo()` in [`attract_mode.c`](../attract_mode.c)) or play branch
(`game_state_machine()` in [`game_state_machine.c`](../game_state_machine.c)).

`PhoenixState` in [`phoenix_state.h`](../phoenix_state.h) is a byte-exact map
of game RAM. ROM, RAM, and arcade I/O are accessed through `mem_read` and
`mem_write` in [`z80_core.h`](../z80_core.h). SDL concerns, player-bank
switching, and headless replay options live in [`platform_sdl.c`](../platform_sdl.c).

## Game Cycle

```text
attract mode -> coin/start -> new game -> initialise -> play round
       ^                                              |
       +---------------- GAME OVER <------------------+
                                                      |
play round: aliens/birds -- round complete --> next round
                         |
                         +-- mothership destroyed --> score --> next round
```

`GameState` (`$43A4`) dispatches game mode:

| Value | Phase | Main implementation |
| --- | --- | --- |
| 0 | prepare new game/player switch | `game_state_machine.c` |
| 1 | blink active score, then advance round | `game_state_machine.c` |
| 2 | initialise game and round data | `state_init.c` |
| 3 | normal gameplay | `state_play.c` |
| 4 | player-ship explosion | `state_endings.c` |
| 5 | GAME OVER / return to attract mode | `state_endings.c` |
| 6 | mothership explosion | `state_endings.c` |
| 7 | show mothership score, advance round | `state_endings.c` |

The low nibble of `LevelAndRound` (`$43B8`) chooses the ROM round pattern:
`0,2` alien fade-in; `1,3,B` active aliens; `4,6,8` spiral bird build-up;
`5,7` bird fade-in; `9` mothership fade-in; and `A` mothership plus aliens.
Exact configuration remains in the ROM tables and routines, notably
[`init_global_level_data.c`](../init_global_level_data.c),
[`alien_wave.c`](../alien_wave.c), [`bird_wave_behavior.c`](../bird_wave_behavior.c),
and [`mothership_impl.c`](../mothership_impl.c).

## Core Mechanics

`player_update()` in [`player_logic.c`](../player_logic.c) handles input,
position, bullets, shield, and sprite addressing each frame. Firing is started
on an input edge; holding fire is not the same as firing every frame. The key
RAM fields are `PlayerShipX`, `PlayerState`, `ShieldCount`,
`PlayerBulletState`, and `AbovePlayerBulletState`; see [RAMUse.md](RAMUse.md).

Alien, bird, and mothership behaviour remain in separate modules to preserve
ROM routine boundaries. Collision and projectile handling are in
[`collision_detection.c`](../collision_detection.c) and
[`weapon_collision.c`](../weapon_collision.c). `AliensLeft` (`$43BA`) and
`BirdsLeft` (`$43BB`) drive transition logic. A destroyed mothership passes
through states 6 and 7 before the next round is initialised.

Scores use packed BCD: player 1 `$4381-$4383`, player 2 `$4385-$4387`, and
high score `$4389-$438B`. [`scoring.c`](../scoring.c) handles score and bonus
life thresholds. The active player is partly selected by
`GameAndDemoOrSplash` (`$43A3`); two-player mode swaps the complete player
bank so player-specific RAM can retain the ROM layout.

Sprites and tiles are written to arcade-style video registers by
[`sprite_rendering.c`](../sprite_rendering.c) and [`hw_video_audio.c`](../hw_video_audio.c).
Sound events reach sound latches from game routines; [`sound.c`](../sound.c),
[`sound_discrete.c`](../sound_discrete.c), and [`tms36xx.c`](../tms36xx.c)
provide emulation and output. Attract mode is part of game design, not merely
a menu; see [`attract_mode.c`](../attract_mode.c).

## Further Detail

- [c_files_categorization.md](c_files_categorization.md): modules by responsibility.
- [code-annotated.md](code-annotated.md): annotated ROM with C links.
- [RAMUse.md](RAMUse.md): RAM fields, addresses, and known meanings.
- [mapping/c_functions_by_address.md](mapping/c_functions_by_address.md): address-to-C mapping.
- [input-scripts/README.md](input-scripts/README.md): reproducible game and regression scenarios.

For new or unclear behaviour, follow the same rule as the port: refer to ASM
and document uncertainty instead of assuming a game rule.
