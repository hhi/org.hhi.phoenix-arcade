# Two-player last grown bird comparison

This directory keeps the curated comparison between jphoenix and C-Phoenix for
the replay where player 1, in a 2-player game, fights one remaining grown bird.

Dutch documentation: [README.nl.md](README.nl.md).

Normally, bulk RAM dumps belong in `/tmp` or the ignored root-level `/traces/`
directory. This case is intentionally kept as an exception under
`context/traces/`, because the related replay is a concrete regression/debug
fixture.

## Scenario

Input script:

```bash
context/input-scripts/two_player_last_grown_bird.txt
```

Expected target window:

- record index `7000..7283`
- jphoenix frame headers `7521..7823`
- C-Phoenix frame headers `7001..7284`
- `player1`
- real gameplay (`GameOrAttract != 0`)
- `LevelAndRound = 0x05`
- `BirdsLeft = 1`
- exactly one active bird: slot `7`, `grown_bird`, state `0x0F`

The frame header differs between both dumps, but the record index and decoded
object state match in the target window.

## Artifacts

| File | Description | Size | SHA-256 |
| --- | --- | ---: | --- |
| `j-last-grown-bird.bin.gz` | Compressed jphoenix RAM dump, 8422 records | 511,684 bytes | `b2a6217f105fa76a4630d77ba6939620aad0e929e104b82844d2de0479667209` |
| `c-last-grown-bird.bin.gz` | Compressed C-Phoenix RAM dump, 8999 records | 509,737 bytes | `3a6070e80d71a6aec5c424ea446f83f88aff089cd332c4acccdb4fdd0db98100` |
| `last-grown-bird-diff.html.zip` | Compressed standalone visual object diff viewer with auto overlay | 1,190,094 bytes | `e728b7ae44afc306ee4724af5851b7eacec5d475c2523ff4079b9f78575cd503` |
| `c-last-grown-bird.coverage.json` | C-Phoenix coverage summary for the run | 4,057 bytes | `d852b39a45ce9639feda1e0251c609248373c4a94f3951c8eb2b8e41a498c528` |
| `j-last-grown-bird.pc-coverage.csv` | jphoenix PC coverage from `PhoenixCoverageRunner` | 103,023 bytes | `0de8bcd2385df604a06635e8d22e90451819fbef61f02d1301a70f65a873d1de` |

## Extract Curated Dumps

The raw dumps are intentionally not stored in Git. Extract them to `/tmp`
before using the comparison or tracer commands:

```bash
gzip -dc context/traces/two_player_last_grown_bird_compare/j-last-grown-bird.bin.gz > /tmp/j-last-grown-bird.bin
gzip -dc context/traces/two_player_last_grown_bird_compare/c-last-grown-bird.bin.gz > /tmp/c-last-grown-bird.bin
```

`gunzip -c` is equivalent. On native Windows, use 7-Zip or run these commands
in WSL2. The decoded SHA-256 values are respectively
`c26e1ed489ce37bb6d018f70323f71789d087e38534ece6b2d922070f66f3b54` and
`657e7f95234c393eac4c2d641aa920be993458105ac3658717efa3e599d5036c`.

## Recreate Dumps

C-Phoenix:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./c-phoenix \
  --run-frames=9000 \
  --input-script=context/input-scripts/two_player_last_grown_bird.txt \
  --ram-dump=/tmp/c-last-grown-bird.bin \
  --coverage-dump=/tmp/c-last-grown-bird.coverage.json \
  --no-render
```

jphoenix:

```bash
cd ../jphoenix-emulator-port
java \
  -Dphoenix.inputclock=poll \
  -Dphoenix.ramdump=/tmp/j-last-grown-bird.bin \
  -Dphoenix.ramdump.frames=9000 \
  -cp build/classes PhoenixCoverageRunner \
  ../c-phoenix/context/input-scripts/two_player_last_grown_bird.txt \
  /tmp/j-last-grown-bird-coverage \
  9000
cd ../c-phoenix
```

## Compare RAM

Start with gameplay/object RAM and exclude known noisy regions. Use
record-index comparison around the target window when `Counter98` repeats in a
2-player route.

```bash
python3 tools/compare_ram_dumps.py \
  /tmp/j-last-grown-bird.bin \
  /tmp/c-last-grown-bird.bin \
  --regions 438E-47FF,4B40-4BE5 \
  --stop-after 999999 \
  --max-diffs-per-frame 8
```

Result for this run:

- outside screen RAM there are 6 differing frame pairs;
- those differences are only `Counter9A/Counter9B`;
- target records `7000`, `7001`, `7283`, and `7284` have 0 differences in
  state/object RAM;
- including foreground/background screen RAM gives 30 differing frame pairs,
  mostly screen drawing/timing.

## Counter98 Alignment

`Counter98` is the 16-bit counter in RAM at `$4398:$4399`. The `--align-c98`
option does not compare record `N` with record `N`; it compares records where
both emulators had the same `Counter98` value.

This helps when jphoenix and C-Phoenix write their dumps with slightly different
frame header numbers. It is less suitable when the same counter value appears
multiple times in one replay, such as around 2-player turn switches or reset-like
transition moments.

## Dump/Timing Noise

Dump/timing noise means differences caused by taking the RAM dump just before or
just after an intermediate step, while the object state becomes equal again
later.

Typical causes:

- jphoenix executes real Z80 instructions and dumps around the interrupt/frame
  loop;
- C-Phoenix executes larger translated C routines per frame;
- some ROM routines draw/erase multiple tiles during one frame;
- turn switches can reset or reuse counters.

Mitigation:

- compare gameplay/object RAM separately from screen RAM;
- exclude hi-score and Z80 stack for functional comparisons;
- use record index plus decoded object state around a target window;
- use write-level instrumentation when an exact write address/timing must be
  investigated.

## Screen Drawing

Screen drawing means the RAM regions that represent tiles/video output:

- foreground screen: `$4000-$433F`
- background screen: `$4800-$4B3F`

A difference in these regions can be a real visual bug, but it can also be a
harmless draw/erase ordering difference or dump-timing difference. Screen RAM is
useful as a visual signal, but less reliable as first proof of gameplay
divergence.

## Use the Visual Tracer

Extract `last-grown-bird-diff.html.zip` first. See
[VISUAL-TRACER.md](VISUAL-TRACER.md) for startup instructions.

```bash
python3 tools/view_sprite_trace.py \
  /tmp/j-last-grown-bird.bin \
  --compare /tmp/c-last-grown-bird.bin \
  --reference-label jphoenix \
  --port-label c-phoenix \
  --player 1 \
  --output=context/traces/two_player_last_grown_bird_compare/last-grown-bird-diff.html
```

The generated HTML is intentionally ignored by Git; recreate the archive with
`zip -9 last-grown-bird-diff.html.zip last-grown-bird-diff.html`.

For this case, the object tracer confirms that the last grown bird stays in sync
between jphoenix and C-Phoenix throughout the target window.
