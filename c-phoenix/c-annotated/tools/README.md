# `c-annotated/tools` — Reference / Naslag

Nine scripts that build and guard the Phoenix knowledge base. They live here
rather than in the monorepo-wide `tools/` because they operate exclusively on
data inside `c-annotated`. `tools/validate_documentation.py` stays at repo
level because it also covers `animations/` and the root READMEs.

**All scripts are run from the repository root**, not from this directory:

```sh
python3 c-phoenix/c-annotated/tools/<script>.py
```

Conceptual background — what the graph is for, when to write a claim — is in
[`../knowledge-base-guide.md`](../knowledge-base-guide.md). This file is the
operational reference: what each script checks, what it deliberately does
*not* check, and what to do when it fails.

Nederlands: zie [§ Naslag](#-naslag).

---

## At a glance

| Script | Role | Exit 1 on | In `make verify` |
|---|---|---|:-:|
| `generate_knowledge_graph.py` | generator | — (writes) | no |
| `validate_knowledge_graph.py` | structure | malformed graph | yes |
| `check_knowledge_graph_drift.py` | structure | graph ≠ regeneration | yes |
| `check_asm_annotations.py` | content | unreachable `[ASM:]` tag | yes |
| `check_prose_rom_ranges.py` | content | prose cites wrong ROM | yes |
| `check_symbol_links.py` | content | link to non-existent symbol | yes |
| `check_against_asm_crossref.py` | content | `Phoenix.md` stale | yes |
| `report_claim_coverage.py` | growth | only with `--fail-under` | no |
| `propose_claims.py` | growth | never | no |

Make targets: `make kg-generate`, `make kg-check` (all seven checks),
`make kg-drift`, `make kg-annotations` (content checks, strict),
`make kg-coverage`.

### Related tools outside this directory

Two scripts write into `c-annotated` but live elsewhere, because they also
serve the wider repository:

| Script | Produces | Target |
|---|---|---|
| `c-phoenix/tools/generate_knowledge_graph_visual.py` | the two architecture SVGs here, from one template with live counts | `make knowledge-graph-visual` |
| `tools/validate_documentation.py` | all SVG and Markdown link checking, repo-wide | `make documentation-check` |

The two architecture SVGs in `../` are **generated** — edit the template, not
the output. The verification-pipeline pair is hand-maintained. See
[`../knowledge-base-guide.md`](../knowledge-base-guide.md#visual-assets).

---

## Generator

### `generate_knowledge_graph.py`

Rebuilds `../knowledge-graph.json` from scratch on every run. Nodes and
relations sorted by id so diffs stay reviewable.

Extracts six node kinds mechanically from the sources, and reads
`../knowledge-claims.json` passively to add `claim` nodes plus `asserts`
relations. It invents nothing.

**Key implementation detail.** ASM ranges come from `annotation_block()`,
which reads *only* the comment block directly adjacent to a declaration —
either a `/* ... */` block or a contiguous run of `//` lines. An earlier
version scanned a fixed 800/2400-character window backwards, which reached
across preceding declarations and attributed their ranges to the wrong node
(155 of 333 functions and 49 of 50 tables were affected). If you touch this
function, re-run the full check suite: the structural validator cannot detect
misattribution, only malformation.

**Conservative by design:** a `calls` edge is emitted only when the callee
name is unique across the whole port. Ambiguous names produce no edge rather
than a wrong one.

Run it after any change to a `.c` or `.h` file, and commit the result — or
the drift check will fail.

---

## Structural checks

### `validate_knowledge_graph.py`

Schema conformance of the generated graph: `schema_version`, the node-kind
set, unique ids, a name and a valid `status` on every node, `source.path`
resolving to a real file, relation endpoints existing as nodes, relation
kinds within the allowed set, and — for claims — `statement`, `sources` and
`relates_to` present with every source file existing on disk.

**Does not check** whether a fact is *correct*. A misattributed `implements`
edge still has two valid endpoints and passes. That gap is what the content
checks below exist for.

*Failure:* the message names the node or relation. Most often a claim's
`relates_to` points at an id that is not a node — check spelling, and note
that `LEVEL_PATTERN_MASK` is deliberately excluded from `game-state` nodes.

### `check_knowledge_graph_drift.py`

Re-runs `build_graph()` in memory and compares the result with the committed
JSON. Writes nothing.

On failure it lists nodes added, removed, or changed in content, plus
relation counts per side.

*Failure:* run `make kg-generate` and commit the regenerated file. If the
diff surprises you, the source changed in a way you did not expect — read the
node list before regenerating.

---

## Content checks

Each of these exists because it caught a real defect. They test claims that
a schema cannot express.

### `check_asm_annotations.py`

Finds `[ASM: ...]` tags the generator can never see:

- **in-body** — the tag sits inside a function body, typically as the first
  line after the opening brace, instead of above the declaration;
- **orphaned** — the tag is in a comment preceding no declaration at all.

Prose notes pointing at code that lives elsewhere are recognised and allowed
(they name another file, or carry a marker like *lives in* / *verwijderd*).

*Failure:* move the tag above the declaration. Both comment styles work.

### `check_prose_rom_ranges.py`

Compares ROM ranges quoted in documentation prose — `(Z80 ROM: `$0400–$041D`)`
— against the routine's actual `[ASM:]` annotation.

- **disjoint** (blocks): the prose points at unrelated ROM;
- **coarse** (`--strict` only): overlaps but not exact, e.g. one summarising
  span where the source annotates several. Legitimate style, not an error.

*Failure:* the annotation is authoritative. Correct the prose. Cross-check
with the Dutch counterpart and `context/Phoenix.md` before editing — when
these last disagreed, the English text was wrong in all eight cases.

### `check_symbol_links.py`

Every link whose label is a bare function name is checked against the symbols
actually declared or defined in the C sources — regardless of whether the link
targets a `.md` or a `.c`. `validate_documentation.py` only checks `.c`
targets, which is how fabricated names survived in both language sets.

Labels that are data rather than functions (`phoenix_*` tables, `state.*`,
ALL-CAPS constants, `M4xxx` RAM slots) are skipped.

*Failure:* the name does not exist. Do not simply rename — a fabricated name
usually comes with a fabricated description. Find the real routine via
`context/Phoenix.md` and rewrite the section.

### `check_against_asm_crossref.py`

Verifies that `context/Phoenix.md` still agrees with the sources: every
*Ported to C* routine must carry an `[ASM:]` annotation, and every ROM range
it lists must still be annotated.

Because `Phoenix.md` is generated from `Phoenix.asm` plus the annotations, it
can only contain real symbols — which makes it the fastest way to find which
routine truly occupies a given ROM range.

*Failure:* run `make c-asm-docs` and commit the regenerated file.

---

## Growth tools

Neither blocks the build. Claims grow by deliberate effort; forcing that with
a gate produces inventory padding rather than knowledge.

### `report_claim_coverage.py`

Per node kind: how many nodes are asserted by a *verified* claim, how many by
an *inventory* claim, the total, and the verified percentage.

The split matters. A claim carrying `"kind": "inventory"` merely restates
what the generator already extracted; counting it as verification would
inflate the number that is supposed to mean *a human checked this*.

```sh
python3 c-phoenix/c-annotated/tools/report_claim_coverage.py
python3 c-phoenix/c-annotated/tools/report_claim_coverage.py --fail-under 5
```

`--fail-under` exits 1 below the given percentage. Useful as a ratchet once
you have a plateau worth defending — not before.

### `propose_claims.py`

Two modes, deliberately different.

```sh
# default: worklist for real claims
python3 c-phoenix/c-annotated/tools/propose_claims.py --mode candidates --limit 10

# mechanical restatements, ready to paste
python3 c-phoenix/c-annotated/tools/propose_claims.py --mode inventory --kind table-asset
```

**`--mode candidates`** lists functions that are both described in prose and
annotated with an ASM range — where documentation can silently drift from
implementation — ranked by relation count, because a wrong belief about a
heavily-called routine propagates furthest. It writes no statement on
purpose: deciding what the two sources jointly assert is the work.

**`--mode inventory`** emits paste-ready claims restating extracted facts,
marked `"kind": "inventory"`. Accepts `--kind rom-pattern | table-asset |
game-state | all`.

Neither mode writes to `knowledge-claims.json`. Review, paste, then
`make kg-generate && make kg-check`.

---

## Recipes

**After editing a `.c` or `.h` file**
```sh
make kg-generate && make kg-check
```

**After editing documentation**
```sh
make kg-check && make documentation-check
```

**Adding a claim**
```sh
python3 c-phoenix/c-annotated/tools/propose_claims.py --mode candidates --limit 10
# read the prose against the implementation; if they agree in substance,
# add an entry to knowledge-claims.json
make kg-generate && make kg-check && make kg-coverage
```

**Full sweep, strictest setting**
```sh
make kg-annotations
python3 c-phoenix/c-annotated/tools/check_prose_rom_ranges.py --strict
```

---

## 🇳🇱 Naslag

Negen scripts die de kennisbank bouwen en bewaken. Ze staan hier en niet in
de repo-brede `tools/` omdat ze uitsluitend werken op data binnen
`c-annotated`. Alle scripts worden **vanuit de repository-root** gedraaid.

Achtergrond — waar de graph voor dient, wanneer een claim loont — staat in
[`../knowledge-base-guide.md`](../knowledge-base-guide.md). Dit bestand is de
operationele naslag: wat elk script controleert, wat het bewust *niet*
controleert, en wat te doen bij een failure.

### Generator

`generate_knowledge_graph.py` bouwt `../knowledge-graph.json` bij elke run
volledig opnieuw op. ASM-bereiken komen uit `annotation_block()`, die
uitsluitend het commentaarblok direct naast een declaratie leest — `/* */`
of een aaneengesloten reeks `//`-regels. Een eerdere versie las een vast
tekenvenster terug en wees daardoor bereiken van voorgaande declaraties toe
aan de verkeerde node. Pas je die functie aan, draai dan de volledige
controleketen: de structurele validator ziet misattributie niet.

Draai het na elke wijziging in een `.c`- of `.h`-bestand en commit het
resultaat, anders faalt de driftcontrole.

### Structurele controles

`validate_knowledge_graph.py` controleert schemaconformiteit: unieke ids,
geldige kinds en statussen, bestaande bronpaden, relatie-eindpunten die als
node bestaan, en voor claims dat statement, sources en relates_to aanwezig
zijn met bestaande bronbestanden. Het ziet **geen onjuist feit**, alleen een
misvormd feit — daarvoor zijn de inhoudelijke controles.

`check_knowledge_graph_drift.py` herbouwt de graph in het geheugen en
vergelijkt met het gecommitte bestand, zonder te schrijven. Bij een failure:
`make kg-generate` en het resultaat committen.

### Inhoudelijke controles

`check_asm_annotations.py` vindt tags die de generator nooit ziet: ín een
functiebody, of in commentaar dat aan geen enkele declaratie voorafgaat.
Kruisverwijzingsnotities worden herkend en toegestaan.

`check_prose_rom_ranges.py` vergelijkt ROM-adressen in de proza met de
werkelijke annotatie. Disjunct blokkeert; overlappend-maar-niet-exact alleen
met `--strict`. De annotatie is leidend — corrigeer de proza, en toets eerst
tegen de Nederlandse versie en `context/Phoenix.md`.

`check_symbol_links.py` controleert elk functie-achtig link-label tegen de
echte symbolen, ongeacht of de link naar `.md` of `.c` wijst. Bij een
failure: niet zomaar hernoemen — een verzonnen naam gaat meestal samen met
een verzonnen beschrijving. Zoek de echte routine via `context/Phoenix.md`.

`check_against_asm_crossref.py` bewaakt `context/Phoenix.md` tegen de bron.
Bij een failure: `make c-asm-docs` en het resultaat committen.

### Groeigereedschap

`report_claim_coverage.py` splitst geverifieerde van inventory-claims per
node-type, zodat het percentage *een mens heeft dit gecontroleerd* niet
opgeblazen kan worden. `--fail-under` maakt er optioneel een ondergrens van.

`propose_claims.py --mode candidates` levert een werklijst van functies met
zowel proza als ASM-annotatie, gesorteerd op aantal relaties. Het schrijft
bewust geen statement: dat oordeel is het werk. `--mode inventory` levert wel
kant-en-klare, als inventory gemarkeerde herhalingen.

Geen van beide schrijft naar `knowledge-claims.json`.
