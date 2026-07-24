# C2-Phoenix scenario coverage

Dutch version: [SCENARIOS.nl.md](SCENARIOS.nl.md).

This page records what the current semantic C2 contract has actually been
exercised against. It is scenario evidence, not a claim that every Phoenix
object or rule has been modeled.

## 1. `bird-investigation`

The interactive recording is stored in
[`c-phoenix/context/input-scripts/bird-investigation.txt`](../c-phoenix/context/input-scripts/bird-investigation.txt).
Regenerate its paired lockstep dumps from the monorepo root:

```sh
make -C c-phoenix tracerun \
  COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt \
  COMPARE_FRAMES=13935 \
  COMPARE_NAME=bird-investigation \
  COMPARE_STOP_AFTER=999999
```

Then, from `c2-phoenix/`, check C2 semantic coverage and C2-to-C2 parity:

```sh
make summary SCENARIO=bird-investigation \
  SUMMARY_ARGS='--require-kind alien --require-kind bird --require-kind mothership --require-kind player_explosion --require-kind shield_segments --require-event impact_observed --require-event score_changed --require-event lives_changed'
make compare SCENARIO=bird-investigation
```

Recorded result: 13,934 C-Phoenix records; active player and enemy bullets,
aliens, birds, bird/player explosions, shield segments, and mothership state.
It includes score, life, level/round, game-state, activation/deactivation, and
observed-impact events. The semantic comparison has 13,934 shared records,
2,530 reference-only records, zero port-only records, and no differences in
the shared records. The reference-only tail is reported as alignment context,
not silently discarded.

## 2. `last-grown-bird`

This is the curated two-player trace. Its input fixture and scenario notes are
in [the C-Phoenix trace directory](../c-phoenix/context/traces/two_player_last_grown_bird_compare/README.md).
The checked-in dumps are compressed. Create temporary copies before C2 use:

```sh
gzip -dc ../c-phoenix/context/traces/two_player_last_grown_bird_compare/j-last-grown-bird.bin.gz > /tmp/ref_last-grown-bird.bin
gzip -dc ../c-phoenix/context/traces/two_player_last_grown_bird_compare/c-last-grown-bird.bin.gz > /tmp/port_last-grown-bird.bin
make summary SCENARIO=last-grown-bird \
  SUMMARY_ARGS='--require-kind bird --require-event impact_observed'
make compare SCENARIO=last-grown-bird
```

Recorded result: 8,999 C-Phoenix records; players `intro`, `player1`, and
`player2`; alien, bird, explosion, ship, and projectile families; and score,
life, state, level/round, activation/deactivation, and observed-impact events.
The semantic comparison has 8,422 shared records, no reference-only records,
577 port-only records, and no differences in the shared records.

## Reading the results

`make summary` proves that an object or event family occurred in one exported
recording. `make compare` checks that the JPhoenix and C-Phoenix semantic
frames agree for paired records. Neither command proves ROM-faithful gameplay
by itself; lockstep RAM comparison remains the independent equivalence check.

The current renderer draws only objects with documented visual anchors. The
mothership has semantic phase/status but no independently established grid
coordinate, so it appears in the side panel rather than at a fabricated
location on the canvas.
