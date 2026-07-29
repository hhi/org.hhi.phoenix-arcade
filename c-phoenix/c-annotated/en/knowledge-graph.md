# Phoenix Knowledge Graph

`../knowledge-graph.json` is the machine-readable core of the documentation. Its stable IDs and evidence remain language-neutral.

## Node kinds

- `c-function` — a function implemented by the C port;
- `asm-routine` — an ASM range annotated directly above a C function;
- `ram-slot` — a RAM address mentioned by the documentation;
- `rom-pattern` — a visualized Cluster A or B movement pattern;
- `game-state` — a named game state or level pattern;
- `claim` — a sourced technical statement with a certainty status;
- `table-asset` — a ROM table or asset declared in `phoenix_tables.h`.

## Relation kinds

- `implements`: C function → ASM routine;
- `calls`: C function → C function, only where the function name is unique;
- `uses-table`: C function → ROM table or asset;
- `handles-state`: C function → game state or level pattern;
- `asserts`: claim → the nodes it concerns.

The curated claims live in [`../knowledge-claims.json`](../knowledge-claims.json). A claim must name its sources, status, and related nodes before it enters the graph. `confirmed` is directly present in the C port or its ASM annotations; `derived` follows from table or SVG metadata; `documented` means an address is mentioned without the generator inferring a semantic meaning.
