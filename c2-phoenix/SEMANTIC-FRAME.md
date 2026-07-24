# Semantic Frame Contract v1

Dutch version: [SEMANTIC-FRAME.nl.md](SEMANTIC-FRAME.nl.md).

The export is one JSON document:

```json
{
  "schema": "org.hhi.phoenix.c2.semantic-frame/v1",
  "source": {"adapter": "c2-phoenix", "frame_count": 1},
  "frames": [
    {
      "frame": 945,
      "sequence": 0,
      "timeline": {"tick": 123},
      "game": {"player": "player1", "level": 1, "round": 0,
               "state": "normal_gameplay",
               "scores": {"player1": 1200, "player2": 0},
               "lives": {"player1": 3, "player2": 3}},
      "objects": [
        {"key": "alien:0", "kind": "alien", "slot": 0,
         "active": true, "position": {"x": 71, "y": 32},
         "appearance": {"family": "alien", "variant": "standard",
                        "motion": "active"}}
      ]
    }
  ]
}
```

The coordinate system is a 208 by 256 logical playfield with origin at the
top-left. `position` is omitted when an object has no known visual anchor.
Coordinates are already presentation coordinates; consumers must not interpret
them as RAM bytes, screen addresses, or sprite offsets.

`sequence` is the export order and is the comparison key for paired lockstep
dumps. `timeline.tick` is a logical temporal context value; it may repeat and
must not be used as a unique alignment key. Consumers must not interpret it as
an address or an instruction count.

`kind` is one of `player_ship`, `player_bullet`, `above_player_bullet`,
`enemy_bullet`, `alien`, `bird`, `bird_explosion`, `player_explosion`,
`mothership`, or `shield_segments`. Effects without an established visual
anchor retain their semantic state but omit `position`. `key` is stable per
player, kind, and slot. `appearance` is deliberately descriptive and may be
rendered with any original C2 artwork or theme.

`active` reports the observed object-slot lifecycle. `visible` is a separate
presentation decision. In particular, a projectile whose slot retains its last
position during a player-death transition remains `active` but is not
`visible`; C2 must not draw it as a frozen projectile.

When the next semantic frame makes a projectile invisible, C2 also suppresses
the final two visible projectile frames. This prevents a terminal coordinate
from appearing as a pause at a collision or screen boundary.

`game.scores` and `game.lives` are presentation values, decoded from their
documented game-state storage. `events` is a list of observed transitions from
the immediately preceding exported frame. Event names state only what was
observed, such as `score_changed`, `lives_changed`, `level_round_changed`,
`game_state_changed`, `object_activated`, and `object_deactivated`; they do
not infer an undocumented cause.

`impact_observed` is emitted only when an active projectile and a nearby active
alien or bird both deactivate in the same exported frame. Its position is the
target's last known position. It is a bounded presentation inference used for
the C2 impact flash, not a claim about a ROM collision routine.

The bridge adapter derives this contract from the existing validated trace
decoder. The contract intentionally excludes raw slot state, addresses,
graphics indices, PROM values, and ROM provenance.
