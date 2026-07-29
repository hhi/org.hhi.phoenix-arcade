# Phoenix Knowledge Graph Specification (`knowledge-graph.md`)

![Phoenix Knowledge Graph Architecture](knowledge_graph_meta_architecture.svg)

`knowledge-graph.json` is the machine-readable core of this documentation suite. It models seven node kinds:

- `c-function` — a function present in the C port;
- `asm-routine` — an ASM address range annotated above a C function;
- `ram-slot` — a RAM memory address referenced in documentation;
- `rom-pattern` — a visualized Cluster A or Cluster B flight pattern with ROM address and step count;
- `game-state` — a named game state or level pattern from `game_constants.h`;
- `claim` — an individual technical claim with source, status, and related nodes;
- `table-asset` — a ROM table or asset from `phoenix_tables.h`.

The graph captures automatically derived relationships:

- `implements`: C function → annotated ASM routine;
- `calls`: C function → C function, when the symbol is unique within the port;
- `uses-table`: C function → ROM table/asset;
- `handles-state`: C function → named game state or level pattern;
- `asserts`: claim → nodes associated with the claim.

Markdown documents and SVGs remain human-readable views. Their paths are stored as evidence on nodes; they are not ingested as facts into the graph without explicit evidence.

The source for semantic claims is [`knowledge-claims.json`](knowledge-claims.json). This small, hand-edited registry is kept separate from the generator: a claim is only part of the graph when it has explicit source, status, and relations.

---

## 🇳🇱 Nederlandse Beschrijving

![Phoenix Kennisgraaf Architectuur](kennisgraaf_meta_architectuur.svg)

`knowledge-graph.json` is de machineleesbare kern van deze documentatieset. Hij bevat zeven soorten nodes:

- `c-function` — een functie die werkelijk in de C-port staat;
- `asm-routine` — een ASM-range die direct boven de C-functie is geannoteerd;
- `ram-slot` — een RAM-adres dat in de bestaande documentatie wordt genoemd;
- `rom-pattern` — een gevisualiseerd Cluster A- of Cluster B-patroon met ROM-adres en aantal stappen;
- `game-state` — een benoemde game state of level pattern uit `game_constants.h`;
- `claim` — een afzonderlijke technische bewering met bron, status en gerelateerde nodes;
- `table-asset` — een ROM-tabel of asset uit `phoenix_tables.h`.

De graph legt alleen automatisch afleidbare relaties vast:

- `implements`: C-functie → geannoteerde ASM-routine;
- `calls`: C-functie → C-functie, uitsluitend wanneer de naam uniek binnen de port is;
- `uses-table`: C-functie → ROM-tabel/asset;
- `handles-state`: C-functie → benoemde game state of level pattern;
- `asserts`: claim → de nodes waarop de claim betrekking heeft.

---

## Updating and Validating / Bijwerken en Controleren

```sh
python3 tools/generate_knowledge_graph.py
python3 tools/validate_knowledge_graph.py
python3 tools/validate_documentation.py
```

Evidence priority is: **Z80 ASM/ROM → C-port → annotated documentation → visual assets**. `confirmed` means directly present in the C port or C-ASM annotation; `derived` means calculated from tables or SVG metadata; `documented` means referenced in existing documentation without semantic interpretation.
