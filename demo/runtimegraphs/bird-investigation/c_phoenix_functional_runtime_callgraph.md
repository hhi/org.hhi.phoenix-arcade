# Functional runtime decomposition

This recording groups executed C functions by their gameplay or engine responsibility. Edge labels in the graph are observed call counts between areas; calls within an area are deliberately folded into its node.

![Functional runtime callgraph](c_phoenix_functional_runtime_callgraph.svg)

| Functional area | Responsibility | Executed functions | Incoming calls |
| --- | --- | ---: | ---: |
| Frame loop & cabinet | frame timing, input and hardware I/O | 26 | 135741 |
| Game flow & attract | attract mode, game states and round setup | 40 | 61348 |
| Player, laser & shield | player control, projectile and explosion | 17 | 109646 |
| Birds & alien waves | formations, bird movement, dives and enemy fire | 65 | 156069 |
| Mothership | mothership approach, combat and scoring phase | 4 | 2436 |
| Collisions & scoring | hit detection, damage, score and bonus lives | 25 | 109227 |
| Video & sprites | tile drawing, palette, scroll and sprite composition | 10 | 715028 |
| Audio | sound controls, synthesis and sample generation | 61 | 1185560052 |
| Utilities & state data | RAM helpers, tables and shared support | 35 | 259560807 |

The per-function membership and measured call totals are in `c_phoenix_functional_runtime_functions.csv`. The existing `c_phoenix_runtime_callgraph.svg` remains the drill-down view.
