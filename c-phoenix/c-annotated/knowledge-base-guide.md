# Phoenix Knowledge Base — Guide / Handleiding

![Phoenix Knowledge Base Verification Pipeline](knowledge_base_pipeline.svg)

This guide explains what the knowledge base is for, which node type to reach
for, what a claim is (and is not), and which checks keep the whole thing
honest. For the schema itself see [`knowledge-graph.md`](knowledge-graph.md).

Nederlandse versie: zie [§ Nederlandse Handleiding](#-nederlandse-handleiding).

---

## What this is for

The C port of Phoenix is a translation of Z80 arcade ROM. Three questions
keep coming back while working on it:

1. **What does this routine correspond to in the original ROM?**
2. **What calls this, and what does it call?**
3. **Do we actually know that, or does it just say so somewhere?**

The knowledge base answers all three, and keeps the answers separate by how
strongly they are established. `knowledge-graph.json` answers 1 and 2 by pure
extraction from the sources. `knowledge-claims.json` answers 3, and only where
a human has checked it.

Current size: **735 nodes, 850 relations, 9 claims** across 116 annotated
documents and 78 SVG assets.

---

## The two data files

### `knowledge-graph.json` — generated, never hand-edited

Rebuilt from scratch by `tools/generate_knowledge_graph.py` on every run.
Anything written into it by hand is lost on the next regeneration, and
`check_knowledge_graph_drift.py` will fail the build if the committed file
does not match a fresh regeneration.

### `knowledge-claims.json` — hand-written, small on purpose

The only place where interpretation may enter the system. Every entry needs
a `statement`, a `status`, concrete `sources` (file plus line range), and the
`relates_to` node ids it supports. The generator reads it passively and turns
each entry into a `claim` node plus `asserts` relations. It invents nothing.

---

## Node types, and when to use them

| Type | Count | What it is | Reach for it when |
|---|---:|---|---|
| `c-function` | 333 | A function in the C port | Tracing call paths, or asking what implements a ROM routine |
| `asm-routine` | 236 | A ROM address range annotated above a C declaration | Going from a ROM address back to the port |
| `ram-slot` | 51 | A RAM address referenced in documentation | Finding which routines touch a memory location |
| `table-asset` | 50 | A ROM table or asset from `phoenix_tables.h` | Asking which code reads a given lookup table |
| `rom-pattern` | 36 | A visualised Cluster A/B flight pattern | Relating a movement animation to its ROM data |
| `game-state` | 20 | A `GAME_STATE_*` or `LEVEL_PATTERN_*` constant | Following state dispatch |
| `claim` | 9 | A human-verified assertion | Asking what we actually know for certain |

Note the asymmetry: the first six are extracted mechanically and are therefore
complete by construction. `claim` is the only type that grows by deliberate
human effort, which is why its coverage is low and why that is not a defect.

### Relation types

| Relation | Count | Derived from |
|---|---:|---|
| `calls` | 495 | A unique function name appearing in another function's body |
| `implements` | 241 | The `[ASM: ...]` block directly above a declaration |
| `uses-table` | 49 | A ROM table name appearing in a function body |
| `handles-state` | 41 | A state constant appearing in a function body |
| `asserts` | 24 | A claim's `relates_to` list |

`calls` is deliberately conservative: an edge is only emitted when the callee
name is unique across the whole port, so ambiguous names produce no edge
rather than a wrong one.

---

## What a claim is

A claim earns its place when it records a judgement **no script can make** —
typically that two independent sources assert the same thing in different
words, where disagreement was possible.

The model case is `claim:vector-offset-formula`. The documentation says
`vector_offset = step_byte × 2`; the C port says `(idx << 1) | (idx >> 7)`,
an RLCA rotate. Those are equivalent, but only a human can say so. Recording
it means a later reader does not have to re-derive it, and a later editor
cannot quietly break the correspondence without contradicting a sourced claim.

By contrast, this is **not** worth recording:

> `phoenix_alien_direction_vectors` is a ROM table of 64 bytes, declared in
> `phoenix_tables.h` and defined in `phoenix_tables.c`.

The generator already extracted every word of that. Writing it as a claim
raises the coverage percentage without verifying anything.

Both kinds are supported, and kept apart. A claim may carry
`"kind": "inventory"` to mark it as a restatement;
`report_claim_coverage.py` then counts it in a separate column so it cannot
inflate the figure that is supposed to mean *a human checked this*.

### Status values

- `confirmed` — directly present in the C port or its ASM annotation;
- `derived` — calculated from tables or SVG metadata;
- `documented` — referenced in documentation without semantic interpretation.

### Two kinds of claim, and how each is kept honest

Not every judgement is equally re-checkable, and the register treats the two
cases differently.

**Countable claims** assert something a script can re-derive: *eight state
constants, each dispatched to exactly one handler*. Such a claim should not
rest on "someone checked it once", so it carries an optional `assertion`
object which `check_claim_assertions.py` re-evaluates on every run:

```json
"assertion": {
  "counts":   [{"file": "game_constants.h", "pattern": "GAME_STATE_[A-Z_]+\\s*=", "expect": 8}],
  "distinct": [{"file": "state_play.c", "pattern": "case LEVEL_PATTERN_[A-Z0-9_]+:\\s*([a-zA-Z_0-9]+)\\(\\);", "expect": 6}]
}
```

Only two operators exist, and deliberately so. An assertion is itself code,
and four separate scripts in this repository were found to share one look-back
bug; an assertion too complex to eyeball has merely moved the trust problem.
Anything beyond counting belongs in a purpose-built check.

**Semantic claims** assert an equivalence no script can evaluate — that an
RLCA rotate means the same as a multiplication by two. These carry no
assertion and rest on human verification. That is a legitimate state, not a
gap to be closed by force.

### Citing a source: anchors over line numbers

Three locator forms are accepted after the `#`:

| Form | Example | Behaviour |
|---|---|---|
| Line range | `alien_logic.c#L348-L366` | Fragile — shifts on any edit above it |
| Anchor text | `alien_logic.c#"(idx << 1) \| (idx >> 7)"` | Survives line shifts; fails when the construct changes |
| Heading | `bird-logic.md#process_birds` | Checked against the document's headings |

Prefer an anchor when citing a *specific construct*: a line range only records
where the evidence was, an anchor records what it was, and fails precisely
when that thing changes — which is the event worth hearing about. A line range
remains appropriate for citing a *block*, such as a whole function body or an
enum, and `check_claim_sources.py --strict` lists those as advice, never as an
error.

Moving two ASM annotations during this session shifted every line below them
in `game_state_machine.c` and `state_init.c`. Nothing broke, but only because
the ranges happened to be checked by hand afterwards.

### Where a claim is worth writing

Use `propose_claims.py --mode candidates`. It lists functions that are both
described in prose and annotated with an ASM range — the places where the
documentation can silently drift from the implementation — ranked by how
connected the function is, because a wrong belief about a heavily-called
routine propagates furthest. It deliberately writes no statement: deciding
what the two sources jointly assert is the point of the exercise.

Where a validator already enforces agreement mechanically, a claim adds
little. Claims are for what cannot be checked by code.

---

## The verification suite

Evidence priority throughout is:
**Z80 ASM/ROM → C-port → annotated documentation → visual assets.**

Each check exists because it caught something real.

| Check | Guards against |
|---|---|
| `check_asm_annotations.py` | `[ASM: ...]` tags the generator cannot see — inside a function body, or attached to no declaration |
| `check_prose_rom_ranges.py` | Prose quoting a ROM range that is disjoint from the routine's actual annotation |
| `check_symbol_links.py` | Documentation linking a function name that exists nowhere in the sources |
| `check_against_asm_crossref.py` | `context/Phoenix.md` drifting out of step with the sources |
| `validate_knowledge_graph.py` | Structural integrity: unique ids, valid kinds and statuses, relation endpoints that exist, claim sources that exist on disk |
| `check_knowledge_graph_drift.py` | A committed graph that no longer matches a fresh regeneration |
| `report_claim_coverage.py` | (informational) Verified versus inventory coverage per node kind |

A structural validator cannot catch a *wrong* fact, only a malformed one:
a misattributed `implements` edge still has two valid endpoints. That is why
the content checks above exist alongside `validate_knowledge_graph.py`.

Per-tool operational detail — what each script checks, what it deliberately
does not, and how to resolve a failure — is in
[`tools/README.md`](tools/README.md).

`context/Phoenix.md` deserves special mention. It is generated from
`Phoenix.asm` plus the `[ASM: ...]` markers and carries a *Ported to C* line
per routine. Because it is derived from the sources it can only contain real
symbols, which makes it an independent cross-check on the hand-written
documents — and the fastest way to find out which routine really occupies a
given ROM range.

---

## Visual assets

Two categories, with very different provenance. Confusing them leads to
hand-editing a generated file, whose changes are silently lost on the next
regeneration.

### Architecture diagrams — generated

`kennisgraaf_meta_architectuur.svg` and `knowledge_graph_meta_architecture.svg`
are rendered from a single template inside
`c-phoenix/tools/generate_knowledge_graph_visual.py`, which substitutes live
counts (`{{NODE_KIND_COUNT}}`, `{{RELATION_KIND_COUNT}}`, `{{DOCUMENT_COUNT}}`,
`{{SVG_COUNT}}`) and applies a Dutch→English translation table for the
`en` variant.

**Do not edit these two files.** Change the template and run:

```sh
make knowledge-graph-visual
```

Note that `{{DOCUMENT_COUNT}}` counts documents in *one* language plus the
shared README (59), not the bilingual total (116). Both are correct in their
own context; the diagram describes one language pane at a time.

`kennisbank_verificatieketen.svg` and `knowledge_base_pipeline.svg` — the
verification-pipeline pair — are currently hand-maintained. They carry counts
that will go stale; check them against `make kg-coverage` when the numbers
matter.

### Animation SVGs — committed artifacts

The 78 files under `animations/` (18 Cluster A patterns, 18 Cluster B, 16 bird
scripts, 16 dive spawns, 10 top-level) have no generator in the repository.
They are versioned artifacts, edited as source.

Each pattern SVG carries a title of the exact form
`Cluster A Pattern 01 (ROM $1020, 64 Steps)`. That string is not decoration:
`generate_knowledge_graph.py` parses it to build the `rom-pattern` nodes, and
`validate_documentation.py` cross-checks it against `animation-trajectory.md`.
Changing the title format silently removes patterns from the graph.

### How the SVGs are validated

All SVG checking lives in the repo-wide `tools/validate_documentation.py`
(`make documentation-check`), not in `c-annotated/tools`:

- `validate_svg_xml_syntax` — every SVG under `animations/` and
  `c-annotated/` must parse as XML;
- `validate_svg_count` — the count stated in the animations README must match
  the number of files on disk;
- `validate_pattern_metadata` — ROM address and step count must agree between
  each pattern SVG and `animation-trajectory.md`, in both directions.

That last check is why a `rom-pattern` claim adds little: the agreement it
would record is already enforced by code.

---

## Workflows

```sh
make kg-generate     # rebuild knowledge-graph.json after a source change
make kg-check        # full verification (also runs inside `make verify`)
make kg-coverage     # claim coverage report, informational
make kg-annotations  # annotation and cross-reference checks, strict mode
make c-asm-docs      # regenerate context/Phoenix.md and the ASM viewer
```

Adding a claim: run `propose_claims.py --mode candidates`, pick a function,
read its prose against its implementation, and only if they agree in substance
add an entry to `knowledge-claims.json`. Then `make kg-generate && make
kg-check`.

After changing any `.c` or `.h` file, run `make kg-generate` and commit the
regenerated graph, or the drift check will fail.

---

## 🇳🇱 Nederlandse Handleiding

![Phoenix Kennisbank Verificatieketen](kennisbank_verificatieketen.svg)

### Waarvoor dit dient

De C-port van Phoenix is een vertaling van Z80-arcade-ROM. Drie vragen komen
steeds terug: waar komt deze routine vandaan in de ROM, wat roept wat aan, en
weten we dat eigenlijk wel of staat het alleen ergens opgeschreven?

De kennisbank beantwoordt alle drie, en houdt de antwoorden gescheiden naar
hoe hard ze zijn. `knowledge-graph.json` beantwoordt de eerste twee door pure
extractie uit de bron. `knowledge-claims.json` beantwoordt de derde, en
uitsluitend waar een mens het heeft nagelopen.

Huidige omvang: **735 nodes, 850 relaties, 9 claims**, over 116 geannoteerde
documenten en 78 SVG-bestanden.

### De twee databestanden

`knowledge-graph.json` wordt bij elke run volledig opnieuw opgebouwd door
`tools/generate_knowledge_graph.py`. Handmatige wijzigingen gaan bij de
volgende regeneratie verloren, en `check_knowledge_graph_drift.py` laat de
build falen zodra het gecommitte bestand afwijkt van een verse regeneratie.

`knowledge-claims.json` is de enige plek waar interpretatie het systeem in
mag. Elke claim heeft een `statement`, een `status`, concrete `sources`
(bestand plus regelbereik) en de `relates_to` node-ids waarop hij betrekking
heeft. De generator leest dit passief in en verzint niets.

### Node-typen inzetten

De zes geëxtraheerde typen (`c-function`, `asm-routine`, `ram-slot`,
`table-asset`, `rom-pattern`, `game-state`) zijn per definitie volledig: ze
volgen mechanisch uit de bron. `claim` is het enige type dat groeit door
bewuste inspanning — vandaar de lage dekking, en vandaar dat dat geen gebrek
is.

Gebruik `c-function` en `calls` voor aanroeppaden, `asm-routine` en
`implements` om van een ROM-adres terug naar de port te komen, `table-asset`
met `uses-table` om te zien welke code een opzoektabel leest, en `game-state`
met `handles-state` om statusafhandeling te volgen.

### Wat een claim is

Een claim verdient zijn plaats wanneer hij een oordeel vastlegt dat **geen
script kan vellen** — meestal dat twee onafhankelijke bronnen hetzelfde
beweren in andere bewoordingen, terwijl ze hadden kunnen afwijken.

Het modelgeval is `claim:vector-offset-formula`: de documentatie zegt
`vector_offset = step_byte × 2`, de C-port doet `(idx << 1) | (idx >> 7)`.
Dat is equivalent, maar alleen een mens kan dat vaststellen.

Niet de moeite waard is een herhaling van wat de generator al extraheerde
("tabel X is N bytes, gedeclareerd in de header"). Zulke claims mogen wel,
maar dan met `"kind": "inventory"`, zodat `report_claim_coverage.py` ze apart
telt en ze het percentage *een mens heeft dit gecontroleerd* niet opblazen.

Gebruik `propose_claims.py --mode candidates` om te zien wáár een claim loont:
functies die zowel in proza beschreven zijn als een ASM-annotatie hebben, dus
waar documentatie en implementatie uit elkaar kunnen lopen.

### De verificatieketen

Bewijsvolgorde: **Z80 ASM/ROM → C-port → geannoteerde documentatie → visuele
assets.**

Elke controle bestaat omdat hij iets echts heeft gevangen. Een structurele
validator kan een *onjuist* feit niet zien, alleen een misvormd feit: een
verkeerd toegewezen `implements`-relatie heeft nog steeds twee geldige
eindpunten. Daarom staan de inhoudelijke controles naast
`validate_knowledge_graph.py`.

`context/Phoenix.md` is daarbij bijzonder: hij wordt gegenereerd uit
`Phoenix.asm` plus de `[ASM: ...]`-markers en bevat per routine een
*Ported to C*-regel. Omdat hij uit de bron volgt kan hij alleen echte symbolen
bevatten — een onafhankelijke kruiscontrole op de handgeschreven documenten,
en de snelste manier om te achterhalen welke routine werkelijk op een bepaald
ROM-adres zit.

### Werkwijzen

```sh
make kg-generate     # graph opnieuw opbouwen na een bronwijziging
make kg-check        # volledige verificatie (draait ook in `make verify`)
make kg-coverage     # dekkingsrapport, informatief
make kg-annotations  # annotatie- en kruisverwijzingscontroles, streng
make c-asm-docs      # context/Phoenix.md en de ASM-viewer regenereren
```

Na elke wijziging in een `.c`- of `.h`-bestand: `make kg-generate` draaien en
de geregenereerde graph meecommitten, anders faalt de driftcontrole.

Operationele details per script — wat elk controleert, wat bewust niet, en
wat te doen bij een failure — staan in [`tools/README.md`](tools/README.md).

### Visuele assets

Twee categorieën met verschillende herkomst. Ze verwarren leidt ertoe dat je
een gegenereerd bestand met de hand bewerkt, waarna je wijziging bij de
volgende regeneratie stil verdwijnt.

De twee **architectuurdiagrammen** (`kennisgraaf_meta_architectuur.svg` en de
Engelse tegenhanger) worden gerenderd uit één template in
`c-phoenix/tools/generate_knowledge_graph_visual.py`, met levende tellingen
als placeholders. Bewerk deze bestanden niet — pas de template aan en draai
`make knowledge-graph-visual`. Let op dat `{{DOCUMENT_COUNT}}` per taal telt
plus de gedeelde README (59), niet het tweetalige totaal (116).

De **verificatieketen-SVG's** (`kennisbank_verificatieketen.svg` en
`knowledge_base_pipeline.svg`) worden momenteel met de hand onderhouden en
bevatten tellingen die verouderen.

De **78 animatie-SVG's** onder `animations/` hebben geen generator in de
repository; het zijn versiebeheerde artefacten. Hun titelregel
(`Cluster A Patroon 01 (ROM $1020, 64 Stappen)`) is geen opmaak maar data:
`generate_knowledge_graph.py` leest daaruit de `rom-pattern`-nodes. Wijzig je
het formaat, dan verdwijnen patronen stil uit de graph.

Alle SVG-controles zitten in de repo-brede `tools/validate_documentation.py`
(`make documentation-check`): XML-geldigheid, het aantal in de README versus
de schijf, en de kruiscontrole van ROM-adres en stapaantal tussen elke
patroon-SVG en `animation-trajectory.md`.
