# Bird Logic

[`bird_logic.c`](../../bird_logic.c) contains the bird-wave update entry point, the flight-path wrapper, and the routines that render the two banks of bird records.

## `process_birds`

[`process_birds`](../../bird_logic.c#L27-L67) is the bird-wave update loop. It is annotated with the original Z80 ranges `$3400–$3436` and `$3438–$344D`.

The routine updates the player and collision state, applies bird vertical movement, then branches on `state.BirdsLeft`. With four or more birds alive it interleaves the first and second banks using `state.Counter9B`; with fewer birds it updates both banks in the same frame.

Graph evidence:

- C node: `c:bird_logic:process_birds` (`confirmed`)
- ASM nodes: `asm:3400-3436`, `asm:3438-344D` (`confirmed`)
- Claim: `claim:bird-process-loop` (`confirmed`)

## Bird record banks

`draw_first_4_bird_objects` and `update_first_four_birds` walk the records from `0x4B70` through `0x4B8F` in 8-byte steps. The second-bank counterparts use `0x4B90` through `0x4BAF`.

Graph evidence:

- RAM node: `ram:$4B70` (`documented`)
- Claim: `claim:ram-4b70-bird-records` (`confirmed`)

## Related material

- [Dutch full annotation](../nl/bird-logic.md)
- [Bird animation guide](../../animations/nl/bird-animations.md)
- [Movement trajectories](../../animations/nl/animation-trajectory.md)
