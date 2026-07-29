# Phoenix Animation Trajectories

Phoenix movement is driven by static Z80 ROM lookup tables rather than dynamic physics. The port exposes Cluster A at `$1000–$13FF`, Cluster B at `$2C00–$2FFF`, and direction deltas at `$1700–$173F` through [`phoenix_tables.c`](../../phoenix_tables.c) and [`phoenix_tables.h`](../../phoenix_tables.h).

The graph distinguishes `rom-pattern` nodes from the visual explanation: pattern 01, for example, is `rom-pattern:01`, starts at `$1020`, has 64 visualized steps, and is marked `derived` from the table and SVG metadata.

## Reading the material

- [Dutch complete trajectory analysis](../nl/animation-trajectory.md)
- [Dutch detailed coordinate tables](../nl/animation-trajectory-detailed.md)
- [Dutch bird animation guide](../nl/bird-animations.md)
- [Knowledge graph](../../c-annotated/en/knowledge-graph.md)
