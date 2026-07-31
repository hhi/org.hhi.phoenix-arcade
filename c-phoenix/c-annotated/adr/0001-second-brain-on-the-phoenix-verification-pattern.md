# ADR-0001: Second brain built on the Phoenix verification pattern

**Status:** Proposed
**Date:** 2026-07-30
**Deciders:** Project maintainers
**Scope:** A separate knowledge vault, informed by `c-phoenix/c-annotated`

---

## Context

Two knowledge systems are in play.

**The Phoenix knowledge base** (this directory) models a C port of Z80 arcade
ROM: 735 nodes, 850 relations, 9 claims, 116 annotated documents, 78 SVG
assets. Its defining property is a hard split between what is *extracted
mechanically* and what a *human has judged*. Six node kinds are generated
deterministically from the sources and are complete by construction; the
seventh, `claim`, is the only place interpretation may enter, and every claim
carries a statement, a status, and file-plus-line sources. Seven checks run in
`make verify`.

**The second-brain skillset** (based on Karpathy's LLM Wiki pattern) proposes
`raw/ → wiki/ → output/` with four verbs — setup,
ingest, query, lint — where an LLM reads raw sources and compiles them into an
interlinked wiki of source, entity, concept and synthesis pages.

### Current state of the vault

The target vault is an **empty shell**: onboarding has created the directory
structure and made the workflow skills and supporting CLI tooling available.
No sources have been ingested and no wiki pages exist.

This is the decisive fact for timing. Every correction made to the Phoenix
base today was retrofitted onto documentation that already existed, and the
sequencing mattered: fabricated prose had to be repaired *before* claims could
be written on top of it, because claims inherit the fabrication of what they
summarise. A vault at zero pages can have its verification layer installed as
a precondition rather than as a repair.

The question is whether the second-brain description can serve as a summary of
what we built here, or whether it is better used as inspiration.

**It cannot serve as a summary. The two systems have opposite trust models,
and this session produced direct evidence of why that distinction matters.**

### Evidence from 2026-07-30

While hardening the Phoenix base, the newly added content checks found, in
documentation that had passed every existing structural check:

| Defect | Count | Nature |
|---|---:|---|
| Prose citing a ROM range disjoint from the routine's actual annotation | 8 | `game_state_machine` documented as `$0020–$0080`; real annotation `$0400–$041D` |
| Function names linked in the graph that exist nowhere in the sources | 23 | With invented line numbers (`state_play.c#L105`) and plausible names (`update_player_shield`) |
| `implements` relations attributed to the wrong routine | 247 of 485 | Generator bug: a fixed look-back window crossed declaration boundaries |

Two findings are decisive for this ADR:

1. **The fabrications lived exclusively in the hand-written `.md` layer.**
   `context/Phoenix.md`, which is *generated* from the assembly plus source
   annotations, contained zero fabricated symbols. Anything derived
   mechanically was clean; anything composed in prose was not.

2. **Structural validation could not see any of it.** `validate_knowledge_graph.py`
   passed the whole time. A misattributed `implements` edge still has two valid
   endpoints; a link to a non-existent function still has valid Markdown
   syntax. Detecting these required four *content* checks that compare
   assertions against the sources.

The second-brain `lint` skill, as described, performs structural checks:
broken wikilinks, orphan pages, index consistency, missing cross-references.
It also lists "contradictions" and "outdated claims", but between *wiki pages*
— not between a wiki page and the raw source it summarises. Nothing in the
described design would have caught any of the 31 defects above.

---

## Decision

**Adopt the second-brain folder discipline and four-verb workflow. Do not
adopt its trust model. Add a source-anchored claim layer and content
validation before ingesting anything whose correctness matters.**

Concretely: `raw/ → wiki/ → output/` and setup/ingest/query/lint are kept as
the operating shape. On top of that, wiki pages are treated as *prose views*,
never as facts; assertions that must be relied upon are recorded in a claims
register with explicit sources; and lint is extended from structural checking
to source-anchored checking.

---

## Options Considered

### Option A — Adopt second-brain as described

| Dimension | Assessment |
|---|---|
| Complexity | Low — installable today, wizard-driven |
| Cost | Minimal setup effort |
| Scalability | Good; retrieval tooling handles >100 pages |
| Team familiarity | High; conventional Obsidian vault |
| **Correctness guarantee** | **None beyond structural integrity** |

**Pros:** working immediately; mature conventions (frontmatter, kebab-case,
wikilinks); agent-portable across Claude Code, Codex, Cursor, Gemini;
contradiction *noticing* is already part of ingest.

**Cons:** every wiki page is LLM-compiled prose with no mechanical tie back to
its source. The failure mode is precisely the one observed today — confident,
plausible, wrong, and invisible to lint. Risk compounds: synthesis pages are
built from source pages, so one fabricated detail propagates and gains
apparent corroboration.

### Option B — Port the Phoenix pattern wholesale

| Dimension | Assessment |
|---|---|
| Complexity | High — needs deterministic extractors per source type |
| Cost | Substantial per-domain engineering |
| Scalability | Poor for heterogeneous sources |
| Team familiarity | Low |
| **Correctness guarantee** | **Strong, where extraction is possible** |

**Pros:** the strongest guarantee; drift detection makes staleness a build
failure.

**Cons:** Phoenix's extractors work because its sources are *structured code*
with a machine-readable annotation convention. A second brain ingests PDFs,
articles, meeting notes and web pages, from which no equivalent deterministic
graph can be derived. Enforcing this would mean ingesting almost nothing.

### Option C — Second-brain shape, Phoenix trust model (**chosen**)

| Dimension | Assessment |
|---|---|
| Complexity | Medium — one extra file plus lint rules |
| Cost | Modest; the discipline is a habit, not a build |
| Scalability | Good; effort scales with what you choose to rely on |
| Team familiarity | High; standard vault plus one convention |
| **Correctness guarantee** | **Strong for what is claimed, honest about the rest** |

**Pros:** keeps the low-friction ingest path for exploratory material, while
anything load-bearing must be pinned to a source. Mirrors the split that makes
the Phoenix base trustworthy: complete-by-extraction versus selective-by-
judgement. The 2.9% claim coverage in Phoenix is not a defect but an honest
measurement — the same honesty transfers.

**Cons:** two-speed system requires discipline about which mode you are in;
the claims register needs its own validator; coverage will look low, which is
uncomfortable but accurate.

---

## Trade-off Analysis

The real trade-off is **ingest throughput versus assertion reliability**, and
it is resolvable because the two are needed for different material.

Most of what enters a knowledge vault is exploratory: a paper skimmed, a talk
noted, a tool evaluated. For that, the second-brain flow is ideal and a
mistaken paraphrase is cheap. A minority is load-bearing: a figure quoted in a
report, an API contract relied upon, a decision justified to others. For that,
"the LLM read it and wrote this" is not sufficient provenance.

Option A optimises entirely for throughput and leaves no mechanism to raise
reliability later — the wiki has no place to record *what has been checked*.
Option B optimises entirely for reliability at a throughput that makes the
vault pointless. Option C keeps throughput as the default and adds a
deliberate, visible promotion path from "noted" to "verified".

The Phoenix session also shows the *sequencing* matters. We spent the day
fixing fabricated documentation before adding claims, because claims built on
fabricated prose inherit the fabrication. A second brain should therefore have
its verification layer in place *before* bulk ingest, not bolted on after a
thousand pages exist.

---

## What transfers from the second-brain description

Adopted as-is — these are genuinely good and map cleanly onto what already
works here:

| Second-brain convention | Phoenix equivalent | Note |
|---|---|---|
| `raw/` read-only, never edited | Evidence priority: ASM/ROM → C-port → docs → visuals | Same principle: sources are not editable by the layer that consumes them |
| `wiki/log.md` append-only | Drift detection and git history | Provenance must be reconstructable |
| "Update existing pages over creating new" | Regenerate, never hand-edit generated files | Today's session violated this and paid for it |
| Contradiction noted with *both* sources | `claim.sources[]` with file plus line range | Recording disagreement beats silently picking a winner |
| `wiki/index.md` as catalogue | `knowledge-graph.json` as machine-readable index | A catalogue the tooling reads, not just humans |
| Lint after every 10 ingests, monthly, before synthesis | `make kg-check` inside `make verify` | Better: make it a gate, not a reminder |
| Curator/librarian split | Generated graph versus hand-written claims | The clearest shared idea in both systems |

Deliberately **not** adopted:

- **Wiki pages as the knowledge substrate.** They are views. The substrate is
  `raw/` plus the claims register.
- **Lint as sufficient verification.** Structural checks are necessary, not
  sufficient — demonstrated 31 times today.
- **Entity/concept/synthesis as the only typology.** Useful for organising
  prose, but it carries no notion of evidential status. Phoenix's
  `confirmed | derived | documented` does, and is orthogonal to it.

---

## What the installed tooling implies

The three CLI tools are useful, and each touches the trust boundary in a way
worth stating before first use.

**A summarizer** compresses a link, file or medium before you read it.
As triage — is this source worth ingesting? — it is exactly right. The risk is
that its output becomes the thing that gets ingested, producing a summary of a
summary with the original never entering `raw/`. Every compression step is a
place where detail is silently dropped or invented, and two stacked steps
cannot be audited back to anything.

*Rule:* summary output is a reading aid and may inform the discussion
during ingest. The artefact placed in `raw/` is the original source. A claim
never cites a summary.

**A Markdown indexer** indexes the wiki markdown. Note precisely what that means
for provenance: it searches the *LLM-compiled prose layer*, not `raw/`. A
query answered from its results inherits whatever the wiki got wrong —
which, in the Phoenix analogue, is the layer where all 31 defects lived and
none of the generated artefacts did.

*Rule:* the indexer is retrieval, not verification. When a query result will be
relied upon, follow the wikilinks to the claim, and the claim to `raw/`.
Consider indexing `raw/` as a second corpus so the original text is
searchable alongside the paraphrase.

**A web-content fetcher** fetches web content, which is the least stable
source class in the vault: a page can change or vanish between ingest and the
moment a claim is questioned. Phoenix never had this problem — ROM bytes do
not move — so the discipline has no equivalent here and must be added.

*Rule:* web sources are snapshotted into `raw/` with the retrieval date, and
the claim cites the snapshot rather than the live URL. A claim whose only
source is a URL is not re-verifiable.

---

## What must be decided now, and what can wait

Option B is not a live alternative — deterministic extractors cannot be built
for PDFs, articles and notes. The real choice is A versus C, and it reduces to
a single question: is there a claim register alongside the wiki?

That question does not have to be answered now. A claim register is an
*addition*, not a different foundation: adding it at page 5 or page 500 costs
the same per page written afterwards. There is no migration and no
restructuring.

**One decision is irreversible.** Originals must be preserved in `raw/`, with
a retrieval date for anything fetched from the web. A page summarised but not
stored may have changed or vanished a year later; a PDF processed only through
the summarizer cannot be re-read. With the originals present, any verification
discipline can be introduced afterwards. Without them, option C becomes
permanently unreachable for everything collected up to that point — not
because the work is large, but because the evidence is gone.

### The synchronisation cost of adding later

Adding a claim register does introduce synchronisation problems. Three,
distinguishable, and only one of them depends on timing:

| Problem | Timing-dependent | Severity |
|---|:-:|---|
| **Coverage inconsistency** — pages written before the register lack claims | yes | Low. Accept "claims run from date X", or backfill selectively. |
| **Claim-versus-page drift** — ingest later updates a page, which may now contradict a claim about it | no | High, and inherent to claims beside mutable pages. Starting early does not shrink it. |
| **Claim-versus-source drift** — a cited `raw/` file is replaced by a newer edition, breaking the locator | no | Medium, contained only if `raw/` is genuinely never edited. |

The second problem is the one that shapes the schema, and it is why the
anchoring rule below is not a detail.

### Anchoring rule (schema correction)

A claim's evidential anchor is the **source**, never the wiki page:

- `sources` — locators into `raw/`. This is what makes the claim checkable.
- `relates_to` — wikilinks. **Navigational only.** They say where the claim is
  relevant, not why it is true.

A claim must remain valid if the entire wiki is deleted and regenerated from
`raw/`. If it does not, it was anchored to the wrong layer.

This mirrors why the nine Phoenix claims survived today's clean-up untouched
while 31 defects were found in the prose layer: claims cite
`alien_logic.c#L348-L366` and relate to graph nodes derived from that source,
not to the `.md` narrative. Had they been anchored to the documentation, the
fabricated ROM addresses would have corrupted them too.

**Known gap, stated honestly.** Phoenix does not fully solve claim-versus-page
drift either. Nothing verifies that the prose at a cited line range still says
what the claim asserts; only the trajectory formula has a bespoke guard, and
that was hand-written. A vault whose pages are updated on every ingest will hit
this sooner and harder than a codebase does. Treat periodic re-reading of
claims against their sources as manual work that does not yet have a tool.

---

## Required additions before bulk ingest

1. **`wiki/claims.json`** — the second-brain analogue of
   `knowledge-claims.json`. Every entry: `statement`, `status`
   (`confirmed | derived | documented`), `sources` (raw file plus locator —
   page, timestamp, heading), `relates_to` (wikilinks). Hand-written only.
   Per the anchoring rule above, `sources` carries the evidence and
   `relates_to` is navigation; a claim that cannot be checked without the wiki
   is anchored wrongly.

2. **Source-anchored lint** — extend the eight structural checks with at least
   one content check: every claim's `sources` must resolve to a file that
   exists in `raw/`, and the cited locator must exist within it. This is the
   direct analogue of `validate_knowledge_graph.py`'s claim-source check, which
   caught a bad reference within minutes of being written today.

3. **A quotation convention.** Any figure, date, name or verbatim statement in
   a wiki page carries either an inline source locator or a claim id.
   Unattributed assertions are readable as *the LLM's paraphrase*, not as
   fact. Today's fabricated ROM addresses looked authoritative precisely
   because nothing distinguished paraphrase from citation.

4. **Coverage reporting.** The analogue of `report_claim_coverage.py`: how
   many pages contain at least one sourced claim. Expect a low number. Low and
   known beats high and false — and the verified/inventory split should be
   carried over so restating what is already extracted cannot inflate it.

---

## Consequences

**Easier**

- Exploratory ingest stays fast; no ceremony for material you are only
  browsing.
- Anything relied upon has traceable provenance, so a future reader — or a
  future you — can re-verify without re-deriving.
- Contradictions between sources become recorded data rather than a silent
  overwrite.
- The pattern is portable: the same discipline applies to any vault, not just
  this domain.

**Harder**

- Two modes to hold in mind: noting versus claiming. Mis-sorting is the main
  risk.
- The claims register is manual work with no shortcut. Any tool that generates
  claims automatically has, by definition, removed the judgement that made
  them worth anything.
- Coverage metrics will look poor next to a wiki that asserts everything
  confidently. That discomfort is the point.

**To revisit**

- Whether `wiki/synthesis/` pages should be permitted to cite only claims
  rather than arbitrary pages. Synthesis is where fabrication compounds
  fastest, and Phoenix's experience suggests the highest-traffic nodes deserve
  the strictest sourcing.
- Whether ingest should refuse to run when lint is failing, mirroring
  `make verify`.
- Whether retrieval at scale (>100 pages) changes the calculus — retrieval
  quality may matter more than page structure at that size.

---

## Action Items

The vault is at zero pages, so all of the following are preconditions rather
than migrations. Items 1–3 should land before the first `/second-brain-ingest`.

1. [x] ~~Inspect the target vault for an existing structure~~ — confirmed an
       empty shell: structure scaffolded and workflow tooling present.
2. [ ] Add `wiki/claims.json` with the four-field schema
       (`statement`, `status`, `sources`, `relates_to`).
3. [ ] Write the three tooling rules and the quotation convention into
       the vault instructions, so they bind every ingest from the first one:
       originals into `raw/` (never summary output), the indexer as retrieval not
       verification, web sources snapshotted with a date.
4. [ ] Extend `second-brain-lint` with the claim-source existence check —
       every `sources` entry must resolve to a file in `raw/`, and the locator
       must exist within it. Treat as blocking.
5. [ ] Decide the vault's domain scope. A narrow domain makes source-anchored
       claims tractable; a broad one does not. Worth settling before ingest,
       because the tag vocabulary chosen at onboarding encodes it.
6. [ ] Ingest three sources of deliberately different types (a PDF, a web page,
       a set of notes), then run lint and coverage. The point is to calibrate
       how much of a real source ends up claim-backed before committing to a
       cadence.
7. [ ] Consider indexing `raw/` as a second retrieval corpus, so the original text
       is searchable alongside the paraphrase.
8. [ ] Revisit this ADR after ~50 pages; the throughput/reliability balance is
       an empirical question and the current answer is a prediction.

---

## References

- [`../knowledge-base-guide.md`](../knowledge-base-guide.md) — what the
  Phoenix knowledge base is for, node types, what a claim is
- [`../tools/README.md`](../tools/README.md) — the seven checks, what each
  guards against
- [`../knowledge-graph.md`](../knowledge-graph.md) — schema and evidence
  priority
- Karpathy, *LLM Wiki pattern* — the curator/librarian split this builds on
- The second-brain skillset under assessment
