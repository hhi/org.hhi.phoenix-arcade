# Program-ROM Table Catalog

Dutch version: [rom-table-catalog.nl.md](rom-table-catalog.nl.md). Machine-readable
source: [rom-table-catalog.json](rom-table-catalog.json).

## Scope

This is the working inventory for program-ROM data used by C-Phoenix. It does
not claim that all `0x4000` program-ROM bytes are already understood. It
separates bounded lookup tables from dynamic pointer payloads and generic
ROM-to-RAM copies.

The current catalog contains **50 catalogued regions**, of which **all 50
are extracted** as named C data in `phoenix_tables.c`. **The source
contains zero direct `prg_mem` reads and zero indirect ROM reads via
`mem_read()` anywhere in the codebase** (see the `draw_bird_shape_350c`
section further below for the final two). The annotated ASM has 111 data
anchors, many of which are not lookup tables.

**A full `T-label` sweep (21 July 2026) cross-referenced all 111 `Txxxx`
labels in `code-annotated.asm` against the catalog**, complementing the
`prg_mem`-grep methodology used until now (which is structurally blind to
tables that never went through a literal `prg_mem[...]` expression). Result:
97 labels already extracted and correctly wired; 5 are Z80 `JP (HL)` jump
tables (`T040E`, `T0735`, `T0759`, `T0814`, `T3018`) correctly translated as
C `switch` statements, not data -- out of scope by design; 2 (`T0560`,
`T0B38`) were already ROM-free but lived as local `static const` arrays
inlined directly in `state_init.c`/`player_logic.c`, predating the
`phoenix_tables.c` pattern -- now centralized, see the `T0560`/`T0B38`
section below; and 4 (`T1800`, `T1BA0`, `T1D00`, `T1F00`) were genuinely
unextracted ROM tables, now all resolved (see the sections below). The sweep
also confirmed a real duplicate translation of `InitGlobalLevelData`
(`$0580`): `state_init.c` and `init_global_level_data.c` both implement it
independently, both are actually called, both hold identical data -- not a
bug today, but an unmerged duplicate that could silently diverge later.

**A follow-up full audit of all 163 `mem_read()` call sites in the codebase
(same date) found a second, previously invisible ROM-read path.**
`mem_read()` ([z80_core.h](../z80_core.h)) is the central Z80 address
decoder previously fell through to program ROM for any address `< 0x4000` --
code reading ROM through it never appeared in a `prg_mem[` grep. Of the 163
sites, all but one function turned out to operate purely
on RAM addresses (struct offsets, screen positions, all `>= 0x4000` by
construction); the one exception is `utilities.c:print_text_lines()`
(and its `draw_row()` helper), called from 6 files with fixed literal ROM
addresses (`0x1800`, `0x1960`, `0x19C0`, `0x1A00`, `0x1BA0`) -- exactly
`T1800` and `T1BA0` from the sweep above, plus three addresses
(`0x1960`/`0x19C0`/`0x1A00`) that happen to fall inside the already-
extracted `score-average-scroll-text-page`'s byte range without that
reader actually using the array.

The remaining deliberate `$3FFD` anti-piracy checksum read in
`attract_mode.c:l1ee0` was subsequently rewired to the already-extracted
`phoenix_bird_data_alt_page[0x7D]`. `mem_read()` now reports the address and
aborts on any attempted program-ROM read; no program-ROM C source remains.

This audit also **solved `stars_scroll_down`'s previously-unresolved RAM
pointer** (`M43B2:M43B3`, documented in `RAMUse.md` as targeting "T1C00 or
T1D00 or T1F00"): it's written by `init_global_level_data()`'s already-
extracted 12-byte copy (`level-data-page`), and decoding that page's own
bytes at offset 7:8 for each of its 4 source blocks gives exactly `0x1C00`,
`0x1C00`, `0x1F00` and `0x1D00` -- a fully static, provable answer, no
runtime ambiguity. `T1C00` is already extracted; `T1D00` and `T1F00` are
the two remaining pieces needed to fully resolve that read. See
`stars-scroll-down-target-tables` and `attract-mode-text-tables` in the
JSON `dynamic_or_payload_readers`/new region entries for detail. No code
was changed by either sweep -- this is inventory only.

Four of those 28 regions were added after decoding
`alien-closed-loop-pointers`' own payload (see that entry's note): the
"alien movement pattern dispatch" dynamic-reader category was found to be
a genuinely bounded pair of ROM clusters (`alien-movement-pattern-cluster-
a`/`-b`) and was extracted, not just re-catalogued. That also exposed a
separate, previously miscounted dynamic read in
`alien_logic.c:init_alien_positions` (3 reads, wrongly lumped in with the
pattern-dispatch count) which turned out to be extractable too
(`alien-position-layout-page`/`alien-position-pointer-table`) -- its
worst-case reach was confirmed, via temporary instrumentation across five
scripts, to land exactly at the page boundary (`0x15FF`) and never spill
into the neighbouring `phoenix_alien_shape_offset_page`. `alien_logic.c`
now has zero direct `prg_mem` reads.

The "weapon collision pattern lookup" category was similarly found to be
partly a duplicate: of its 4 reads, only 3 belong to a genuinely new
table (`formation-hit-window`, `0x1740-0x175F`); the fourth
(`weapon_collision.c:l0c00_kill_score`) reads the same alien movement
pattern pointer already covered by `alien-movement-pattern-cluster-a`/
`-b`, confirmed by tracing its index arithmetic to the identical
`$4B50-$4B6F` addressing scheme used elsewhere, and now calls
`phoenix_alien_movement_byte()` instead of duplicating a table.
`weapon_collision.c` now has zero direct `prg_mem` reads.

The bird-sound-cadence entry was resolved from `partial` to `extracted`:
its index (`B4BD6`) is masked with `& 0x1F` at its only writer, the same
field already used to index the extracted `phoenix_bird_descent_caps`
table, so it never exceeds `0x1F`.

The mothership-and-player-explosion-pointers entry was originally
catalogued as `0x1B00-0x1B5F`, which was both too wide (`0x1B00-0x1B3F`
is unrelated data neither reader touches) and too narrow (the player
explosion reader's index reaches `0x1B9F`). It is now `0x1B40-0x1B9F`,
resolved from `partial` to `extracted`.

The player-explosion-tiles and player-explosion-control entries were
originally catalogued as two disjoint, player-only ranges. Their reader,
`l2085_particles`, is actually shared with the mothership explosion
(called from `state_endings.c` with base `0x2A00`/`0x2B00`, previously
uncatalogued), and its control-table walk index is not tightly proven
bounded. The two entries were merged into one 1024-byte page spanning
both variants; see the JSON `note` field for detail.

The sprite-shape-offsets and alien-animation-descriptors entries were
originally catalogued as two disjoint, narrow ranges (`0x1600-0x161F` and
`0x16A0-0x16CF`). Both were far too small: the ASM shows a dense,
unlabelled "T1600" mega-table running all the way to `0x169F`, and the
"T16A0" table is actually 32 entries of 3 bytes running to `0x16FF` --
confirmed by directly inspecting the alien closed-loop pattern tables
(`0x1020-0x13FF`), whose values (the index into both tables) never exceed
`0x1F`. The two entries were merged into one 256-byte page; see the JSON
`note` field for detail.

The bird-shape-pointers entry was originally catalogued as `0x3E08-0x3E7F`.
Its index is provably `>= 0x08` for realistic type/frame values, but `frame`
is an unbounded RAM byte, so the full `0x3E00-0x3E7F` page (overlapping the
already-extracted `T3E00` bullet-pixel-mask bytes) is kept rather than
assuming the narrower range always holds -- same reasoning as the
bird-hit-mask-page entry above.

The bird-hit-mask entry was originally catalogued as two disjoint 32-byte
ranges. `l3844_small_bird_hit`'s index (`b + 0x60`) never dips below
`0x3B60`: `b` is in `[0, 0x4F]`, so the index stays within `[0x3B60,
0x3BAF]`, always inside the `T3B60` data table -- no wrap possible there.
`l38bc_large_hit`'s index (`b + 0xB0`) does wrap below `0x60` for `b` in
`[0x50, 0x6F]` (grown-bird tiles `0xE0-0xFF`), landing in the code bytes
preceding `T3B60` (`0x3B00-0x3B5F`). This is not a theoretical edge case:
instrumented and run against `bird-investigation.txt` (13,935 frames), the
wrap fired **27 times across 12 distinct tile values** (e.g.
`tile=0xE3 -> index 0x03`, `tile=0xE8 -> index 0x08`,
`tile=0xF9 -> index 0x19`), landing squarely inside `l3b02`'s function
body (`$3B02-$3B19`) among others. The two ranges were merged into one
256-byte page entry to preserve that confirmed wrap exactly; see the JSON
`note` field for detail. Those code bytes (`0x3B00-0x3B5F`) are not
unclassified: they are the opcodes for
`l3b02`/`l3b1b`/`l3b28`/`l3b33`/`l3b43`, already translated and called as
ordinary functions in `sound_dispatcher.c`. `phoenix_bird_hitmask_page` is
a deliberate byte-for-byte duplicate of the same physical ROM bytes for
their separate, unrelated use as inert lookup data on the wrap path above
-- a compiled C function's object bytes bear no relation to the original
Z80 opcodes, so only this literal copy is valid for the data-read use.

The alien-closed-loop-pointers entry's own note (index bound on `0x30-
0xF8` plus a random offset) was correct but incomplete: it described how
the table is *indexed*, not what its *payload* points to. Decoding the
table's 104 MSB:LSB pairs reveals 34 distinct target addresses, only 18
of which land in the 0x1020-0x13FF cluster this entry's `owner`/`readers`
fields implied. The other 16 land in a second, physically disjoint
1024-byte pattern-list cluster at `0x2C00-0x2FFF` -- same `0x00`-
terminator/`0xFF`-padding structure, same proven `<=0x1F` value bound,
confirmed by direct byte inspection of every non-`0xFF` byte in that
range. Two further addresses in that cluster (`0x2E00`, `0x2E40`) are
reached only via a separate mechanism (`alien_logic.c:l3028`, the
breakout scheduler), not through this table. Both clusters' pattern
bytes are now extracted too (see `alien-movement-pattern-cluster-a`/`-b`
below) -- `alien_logic.c`'s `alien_movement_update` and
`alien_animation_update` read them via `phoenix_alien_movement_byte()`
rather than `prg_mem`.

Verification note: temporary hit-counting instrumentation (removed after
use) showed that the passive run and `extended_playthrough.txt` never
reach cluster B at all (0 hits each), despite both passing byte-identical
-- a byte-identical dump does not by itself prove a code path was
exercised. `my_session.txt` (2286 hits) and `bird-investigation.txt`
(3266 hits) are the scripts that actually cover cluster B; both are
included in the evidence for the cluster-a/-b entries below as a result.

Six of the ten "attract-mode text/shapes" dynamic reads were resolved into
four new tables. `draw_score_average_table_tiles()`'s three `draw_n_by_2()`
calls all use fixed (non-runtime-computed) source addresses -- the helper's
signature changed from `(hl, de, rows)` to `(hl, const uint8_t *src, rows)`
so the literal bytes could be passed as arrays: `score-average-table-
tiles-a` (`0x0A40-0x0A4B`, shared by calls 1 and 3) and `score-average-
table-tiles-b` (`0x3C00-0x3C0B`, call 2). `draw_intro_bird_animation_frame`'s
index is a free-running RAM byte, legitimately covering all 32 values in
`[0x3A,0x59]`, not just T233A's own 23-byte extent -- the same
table-abuts-code situation as bird-hit-mask-page, since bytes
`0x2351-0x2359` are the opcodes for `mothership_impl.c:l2351_mothership_
animation`; extracted as `intro-bird-animation-frames` (`0x233A-0x2359`,
full range). `slow_print_score_average_table`'s two reads are indexed via
`Counter98`, a free-running 16-bit counter with no mathematical bound;
extracted as `score-average-scroll-text-page` (`0x1860-0x1B5F`) after
temporary hit-counting instrumentation on passive runs of 3610, 30000, and
60000 frames showed the reached address never exceeding `0x1B3F` at any
length. The remaining four reads (`drawNx2`'s own two, `draw_bird_shape_
350c`'s two) are shared generic helpers called with a mix of fixed and
unbounded runtime-computed addresses across multiple files, and are not
resolvable via table extraction alone -- see Dynamic Data below.

`drawNx2`'s "genuinely unresolved" assessment above was **wrong** and has
been corrected. Re-tracing its only 3 real call sites (all in
`alien_logic.c`) found every one of them bounded: two pass a fixed
literal (`0x17D0`, `0x17D6`), and the third derives its address from
`phoenix_alien_explosion_frames`' 5 possible byte values OR'd with
`0x1700` -- not an unbounded runtime value at all, just an
already-extracted table the earlier pass didn't trace back far enough.
Extracted as `shield-and-drawnx2-shapes` (`0x17B8-0x17FF`), which also
covers `player_logic.c:shields_expired`'s fixed call and one of
`player_explosion.c`'s mothership-pointer-derived values.

Nearly all of the "generic ROM-to-RAM/screen copy helpers" category (22
of 23 reads) turned out to be bounded too, once every call site of each
generic helper was traced individually rather than accepting the
category's blanket "address is a caller parameter" description. Notable
findings: `utilities.c:draw_image_c_by_b`'s 5 call sites resolve to
`shield-table`, `shield-and-drawnx2-shapes`, three values already inside
`mothership-and-player-explosion-pointers`, `alien-wave-animation-
shapes`, and `starfield-page`; `sprite_rendering.c`'s 4 reads share one
page (`sprite-character-block-shapes`) whose index domain was verified
empirically (`0x00-0xDC` observed, not the 2-value set the init table
alone would suggest); `init_global_level_data.c`'s two-level pointer
lookup resolves to an exhaustive, statically-known 4-address set decoded
directly from the ROM's own pointer-table bytes; and `misc_logic.c:l32b0`'s
reachable range is provably constant regardless of `BirdsLeft` (the
`-8n`/`+8n` terms in its address arithmetic cancel exactly). See the new
region entries below for detail on each.

One extraction in this pass initially introduced a real regression,
caught by the standard RAM-dump lockstep check rather than by review: a
first version of `add_planets_to_background`'s rewiring assumed the
`T1E60` sub-table's bytes were consumed directly, when they are actually
an *index* into a still-further, previously-unextracted 32-byte region
(`0x1E00-0x1E1F`) via `hl = 0x1E00 | T1E60_byte`. The passive script
diverged at frame 580 (`BackgroundScreen` bytes at `$4852`/`$4853`/
`$4872`/`$4873`); extracting that region as `planet-shape-page` and
fixing the dispatch resolved it, confirmed byte-identical again across
all 4 standard scripts. Kept as a reminder that "the reader's own
index is bounded" and "the byte the reader returns IS the final answer"
are two separate claims -- the second failed silently here until the
lockstep check caught it.

`hw_video_audio.c:stars_scroll_down`'s previously-remaining read is now
resolved: see the `T1D00`/`T1F00` section below. The 5 indirect
`mem_read()`-based ROM reads found by the audit are also resolved: see the
`T1800`/`T1BA0` section further below. The last 2 reads,
`attract_mode.c:draw_bird_shape_350c`'s own, are resolved too: see the
`draw_bird_shape_350c` section near the end of this document.

### `T1D00`/`T1F00` extracted, `stars_scroll_down` fully resolved (21 July 2026)

Following the audit above, `T1D00` ("Mother ship object 26x9 tiles") and
`T1F00` ("starfield background without planets") were extracted as full
pages (`mothership-tile-page`, `starfield-no-planets-page`), using the
same low-byte-free-wheeling reasoning as `starfield-page`. A new dispatch
helper, `phoenix_starfield_or_mothership_byte()`, routes on the high
address byte (`0x1C`/`0x1D`/`0x1F`) to the correct one of the three pages;
`stars_scroll_down` now uses it instead of `prg_mem`. Verified with
byte-identical RAM dumps across all 4 standard scripts, plus temporary
hit-counting instrumentation (removed after use) confirming all three
pages are genuinely reached and no other high byte ever occurs:
`0x1C` 2682-8696 hits, `0x1D` 234 hits (three of the four scripts; zero in
`extended_playthrough.txt`), `0x1F` 0-4426 hits, `other` 0 across all 4
scripts. `hw_video_audio.c` now has zero direct `prg_mem` reads.

### `T1800`/`T1BA0` extracted, `print_text_lines()` fully resolved (21 July 2026)

Following the `mem_read()` audit above, `T1800` and `T1BA0` were extracted
as `phoenix_attract_text_page` and `phoenix_players_button_text`. Their
exact ranges were not guessed: `print_text_lines()`/`draw_row()`'s address
arithmetic was simulated precisely for every real `(addr,count)` call-site
pair (the row-draw loop is a genuine unmasked 16-bit `INC HL`, unlike most
other extracted tables' low-byte-only free-wheeling), confirming the
widest real call (`0x1800`, count=3) touches exactly `0x1800-0x185F` --
immediately adjacent to, but not overlapping, `phoenix_score_average_
text_page`. A new dispatch helper, `phoenix_text_byte()`, routes across
all three ranges (`phoenix_attract_text_page`, `phoenix_score_average_
text_page`, `phoenix_players_button_text`); `print_text_lines()`/
`draw_row()` now use it instead of `mem_read()`. Verified with
byte-identical RAM dumps across all 4 standard scripts, plus temporary
hit-counting instrumentation (removed after use) confirming all three
ranges are genuinely reached and no address ever falls outside them:
`attract` 4424-15008 hits, `score_avg` 16184-53508 hits, `players_btn`
0-2408 hits (only in `my_session.txt`, which includes a coin-insert/start
sequence), `other` 0 across all 4 scripts. There are no remaining ROM
reads via `mem_read()` anywhere in the codebase.

### `T0560`/`T0B38` centralized (21 July 2026)

The two locally-inlined-but-uncatalogued tables from the sweep were moved
into `phoenix_tables.c` as `phoenix_player_init_data` and `phoenix_player_
x_position_mapping`, with `[ASM:]` doc comments and byte-for-byte tests.
This was a pure relocation -- the translations were already ROM-free and
correct, so `state_init.c:init_player_data_structure()` and `player_logic.c:
map_player_ship_position()` simply reference the centralized arrays
instead of their own local `static const` copies. Verified with
byte-identical RAM dumps across all 4 standard scripts (no dispatch logic
was introduced, so no hit-counting instrumentation was needed here).

### `InitGlobalLevelData` duplicate translation resolved (21 July 2026)

The last open item from the T-label sweep: `state_init.c`'s independent
`static init_global_level_data()` (with its own local `T0598`/`T05A8`/
`T05B4`/`T05C0`/`T05CC` arrays) was deleted, and `state_init.c` now calls
the shared external `init_global_level_data()` from `init_global_level_
data.c` (which already used `level-data-pointer-table`/`level-data-page`)
-- the same function `attract_mode.c`'s demo dispatch already called.
Both translations held identical ROM bytes, so this was a pure
de-duplication, not a behaviour change. Verified with byte-identical RAM
dumps across all 4 standard scripts. See the `known_issues` entry in the
JSON catalog, now marked `resolved`.

### `draw_bird_shape_350c` shape data extracted -- the last two reads (21 July 2026)

The final holdout from the very first extraction pass: `attract_mode.c:
draw_bird_shape_350c()`'s `shape` pointer comes from two sources.
`l38a1_erase_bird`'s erase path passes a *fixed* literal
(`0x1700 | (phoenix_bird_erase_shape_selector + 0xDE)` = `0x17F0`,
clip-adjustable by up to `+6`) that turned out to be entirely within the
already-extracted `shield-and-drawnx2-shapes` (`$17B8-$17FF`) -- no new
table needed there, just a dispatch that routes to it.
`drawbirdobject`'s normal draw path derives `shape` from the
already-extracted `bird-shape-pointers` table, whose content is only ever
`0x3Cxx`/`0x3Dxx` past its bullet-mask prefix, landing in the much larger,
previously-uncatalogued `$3C00-$3DB7` shape-data region. That range is
not mathematically provable (row count and clip depth both depend on free
RAM state), so it was established empirically: temporary hit-count
instrumentation across all 4 standard scripts (1009-8084 draw calls per
run) found the reachable range stable at *exactly* `$3C00-$3DB7` in every
run -- which also happens to be exactly where the already-extracted
`egg-transformation-types` begins (`$3DB8`), a natural, non-arbitrary
boundary rather than a guessed safety margin. Extracted as
`phoenix_bird_shape_data_page`, with a new `phoenix_bird_shape_data_byte()`
dispatch helper routing between it and `shield-and-drawnx2-shapes`.

Verified with byte-identical RAM dumps across all 4 standard scripts,
plus the hit-count instrumentation above (removed after use) confirming
both paths' ranges precisely, not just the combined dump result.

**The codebase now has zero direct `prg_mem` reads and zero indirect ROM
reads via `mem_read()` anywhere** -- the entire program-ROM data
dependency this catalog set out to eliminate is now fully centralized in
`phoenix_tables.c`.

## Status

| Status | Meaning |
| --- | --- |
| `extracted` | Named C data, a byte-for-byte source test, and lockstep replay evidence. |
| `mapped` | Address range, reader, and purpose are understood; the gamecore still uses `prg_mem`. |
| `partial` | A stable range or reader is known, but its complete structure requires more analysis. |

## Catalogued Regions

| ROM region | Family | Owner | Reader module | Status |
| --- | --- | --- | --- | --- |
| `$1500-$151F` | Alien control-state pointers | Alien initialization | `alien_logic.c` | extracted |
| `$1520-$153F` | Alien initial-layout pointers | Alien initialization | `alien_logic.c` | extracted |
| `$1600-$16FF` | Shape offsets, animation descriptors (full page, see note below) | Alien/player movement | `alien_logic.c`, `player_logic.c` | extracted |
| `$1700-$173F` | Alien direction vectors | Alien movement | `alien_logic.c` | extracted |
| `$1760-$1767`, `$17B0-$17B7` | Round population, alien explosion sequence | Wave/explosion | `alien_wave.c`, `alien_logic.c` | extracted |
| `$1B40-$1B9F`, `$198C` | Mothership/player-explosion pointers (corrected from `$1B00-$1B5F`; see note above), bird erase selector | Rendering/collision | `mothership_impl.c`, `player_explosion.c`, `collision_detection.c` | extracted |
| `$2800-$2BFF` | Player and mothership explosion tiles/control bytes (full page, see note below) | Player/mothership explosion | `player_explosion.c`, `state_endings.c` | extracted |
| `$3300-$33FF` | Alien closed-loop movement selection | Alien movement | `alien_logic.c` | extracted |
| `$3B00-$3BFF` | Small/large bird hit masks (full page, see note below) | Bird collision | `collision_detection.c` | extracted |
| `$3DB8-$3DBF`, `$3DC0-$3DDF`, `$3DE0-$3DFF` | Egg transforms, dive spawns, bird sound cadence | Bird wave/collision/sound | `collision_detection.c`, `bird_wave_behavior.c`, `sound_dispatcher.c` | extracted |
| `$3E00-$3E07` | Player bullet bitmasks | Bird collision | `collision_detection.c` | extracted |
| `$3E00-$3ECF` | Bird shape pointers (full page, see note below), formation parameters, draw entries | Bird rendering/wave | `attract_mode.c`, `bird_wave_behavior.c` | extracted |
| `$3ED0-$3EDF` | Bird vertical scroll steps | Bird movement | `birds_vertical_movement.c` | extracted |
| `$3EE0-$3EFF` | Bird descent caps | Bird movement | `birds_vertical_movement.c` | extracted |
| `$3F00-$3F7F` | Bird behavior scripts (corrected from originally catalogued `$3F00-$3FFF`; see JSON note) | Bird wave | `bird_wave_behavior.c` | extracted |
| `$1000-$13FF` | Alien movement pattern cluster A: T1000 idle/reset list plus 18 closed-loop patterns (previously uncatalogued, see note above) | Alien movement | `alien_logic.c` | extracted |
| `$2C00-$2FFF` | Alien movement pattern cluster B: 18 more closed-loop patterns, physically disjoint from cluster A (previously uncatalogued, see note above) | Alien movement | `alien_logic.c` | extracted |
| `$1500-$15FF` | Alien position layout page for `init_alien_positions`'s dynamic lookup (full page, overlaps two already-extracted tables by design, see note above) | Alien initialization | `alien_logic.c` | extracted |
| `$063A-$0649` | Pointer table for the alien position layout lookup, 16 entries indexed 0-15 | Alien initialization | `alien_logic.c` | extracted |
| `$1740-$175F` | Formation bullet hit-window, 4 bytes/tile indexed by `chr & 0x07` (see note above) | Player bullet collision | `weapon_collision.c` | extracted |
| `$0A40-$0A4B` | Score-average-table tile pair for `draw_n_by_2()` calls 1 and 3 (fixed source) | Attract-mode text rendering | `attract_mode.c` | extracted |
| `$3C00-$3C0B` | Score-average-table tile pair for `draw_n_by_2()` call 2 (fixed source) | Attract-mode text rendering | `attract_mode.c` | extracted |
| `$3C00-$3DB7` | Bird shape bitmap data for `draw_bird_shape_350c()` (empirically bounded, ends exactly at `egg-transformation-types` -- see note above) | Attract-mode/bird rendering | `attract_mode.c` | extracted |
| `$233A-$2359` | Intro bird animation frame index (full range, table abuts code, see note above) | Attract-mode bird animation | `attract_mode.c` | extracted |
| `$1860-$1B5F` | Score-average scrolling text/pointer data (empirically bounded, see note above) | Attract-mode text rendering | `attract_mode.c` | extracted |
| `$0598-$05A7` | Level-data pointer table, 16 entries indexed by `LevelAndRound & 0x0F` | Level initialization | `init_global_level_data.c` | extracted |
| `$05A8-$05D7` | Level-data page: 4 statically-decoded 12-byte blocks (see note above) | Level initialization | `init_global_level_data.c` | extracted |
| `$0A00-$0A3F` | Grid-to-screen-ram-address table, bitmask-bounded | Screen coordinate mapping | `utilities.c` | extracted |
| `$1400-$1500` | Sprite/alien character block shapes (full page + 1 byte, see note above) | Sprite/alien rendering | `sprite_rendering.c`, `hw_video_audio.c` | extracted |
| `$1770-$17AF` | Shield damage-state shapes, bitmask-bounded | Player shield rendering | `player_logic.c` | extracted |
| `$17B8-$17FF` | Shield-expired and `drawNx2` shapes (corrected from "genuinely unresolved", see note above) | Player shield / alien explosion rendering | `attract_mode.c`, `player_logic.c`, `player_explosion.c` | extracted |
| `$1BC0-$1BFF` | Mothership pilot/antenna animation frames, bitmask-bounded | Mothership animation | `alien_wave.c` | extracted |
| `$1C00-$1CFF` | Starfield/background image data (full page) | Background starfield | `mothership_logic.c`, `state_play.c` | extracted |
| `$1E00-$1E1F` | Planet shape source image (found via a real lockstep regression, see note above) | Attract/background planet decoration | `hw_video_audio.c` | extracted |
| `$1E20-$1EDF` | Planet and galaxy decoration tables, bitmask-bounded | Attract/background decoration | `hw_video_audio.c` | extracted |
| `$3F80-$3FFF` | "Level 3/8 initial bird data" (provably constant reach, see note above) | Bird wave initialization | `misc_logic.c` | extracted |
| `$0560-$057F` | Player/bullet struct init data, centralized from a local `T0560` array in `state_init.c` (see note above) | Player/bullet initialization | `state_init.c` | extracted |
| `$0B38-$0B47` | Player ship X position mapping, centralized from a local `T0B38` array in `player_logic.c` (see note above) | Player rendering | `player_logic.c` | extracted |
| `$1800-$185F` | Attract-mode/HUD text (score/hi-score headers) for `print_text_lines()` (see note above) | Attract-mode/HUD text | `utilities.c` | extracted |
| `$1BA0-$1BBF` | "1 OR 2 PLAYERS BUTTON" static text for `print_text_lines()` (see note above) | Attract-mode/HUD text | `utilities.c` | extracted |
| `$1D00-$1DFF` | Mothership object tiles (`stars_scroll_down`'s 2nd target page, see note above) | Background starfield / mothership fade-in | `hw_video_audio.c` | extracted |
| `$1F00-$1FFF` | Starfield without planets (`stars_scroll_down`'s 3rd target page, see note above) | Background starfield / mothership fade-in | `hw_video_audio.c` | extracted |

## Dynamic Data

None. Every read that once fell outside the bounded-table count has been
resolved into a named, tested array (or into a dispatch across two or
more such arrays) -- see the sections above, especially `draw_bird_
shape_350c` for the last two. The JSON `dynamic_or_payload_readers` array
is now empty; kept in the schema for future regressions, not as a claim
that dynamic reads can never recur.

## Known Issues

None currently open. The one entry found during the T-label sweep --
duplicate `InitGlobalLevelData` translations in `state_init.c` and
`init_global_level_data.c` -- was resolved on 21 July 2026 (see the
section above); the JSON `known_issues` array keeps a `resolved` record
of it for history.

## Extraction Rule

Move one region at a time into a named `const` array in `phoenix_tables.c`,
declare it from `phoenix_tables.h`, retain its ASM range, add a byte-for-byte
test against `roms/assembled/program.rom`, then run a deterministic lockstep replay. The JSON
catalog is updated in the same change.

Both `phoenix_tables.c` and `phoenix_tables.h` are kept sorted by ASM start
address -- insert new extractions at the correct position rather than
appending. When two entries share a start address (a deliberate overlap,
e.g. a narrow table and a full-page duplicate covering it), the narrower
one comes first. Helper functions that depend on multiple tables (e.g.
`phoenix_alien_movement_byte()`) are placed immediately after the last
table they depend on, since they have no ASM address of their own.
