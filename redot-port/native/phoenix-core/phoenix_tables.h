#ifndef PHOENIX_TABLES_H
#define PHOENIX_TABLES_H

#include <stdint.h>

/*
 * [ASM: 0560-057F] T0560: default values for the player/bullet data
 * structure (grid), copied to $43C0-$43DF by
 * state_init.c:init_player_data_structure(). Centralized from a local
 * `static const` array of the same name that predated phoenix_tables.c.
 */
extern const uint8_t phoenix_player_init_data[0x20];

/*
 * [ASM: 0598-05A7] Pointer table for init_global_level_data()'s dynamic
 * lookup, indexed by LevelAndRound & 0x0F (0-15, trivially safe). Each
 * entry is OR'd with 0x0500 to form the read address into
 * phoenix_level_data_page below.
 */
extern const uint8_t phoenix_level_data_pointer_table[0x10];

/*
 * [ASM: 05A8-05D7] Full data region backing init_global_level_data()'s
 * dynamic lookup. The pointer table above only ever yields 4 distinct
 * addresses (0x05A8, 0x05B4, 0x05C0, 0x05CC -- decoded directly from the
 * table's own fixed ROM content, not empirically), each the start of a
 * 12-byte block; this array is the exact union of those 4 blocks.
 */
extern const uint8_t phoenix_level_data_page[0x30];

/*
 * [ASM: 063A-0649] Pointer table for init_alien_positions()'s dynamic
 * lookup, indexed by (LevelAndRound >> 1) & 0x0F (always 0-15, so this
 * 16-byte table is trivially safe to index directly). Values are the
 * low byte OR'd with 0x1500 to form the read address into
 * phoenix_alien_position_layout_page above; slots 6, 7, 14, 15 hold
 * 0xFF placeholders that empirically never get selected while
 * AliensLeft > 0 (see that page's comment).
 */
extern const uint8_t phoenix_alien_position_pointer_table[0x10];

/*
 * [ASM: 0A00-0A3F] T0A00: grid-to-screen-ram-address lookup for
 * utilities.c:get_screen_ram_address(), indexed by (coord & 0xF8) >> 2
 * for the MSB read and the same >> 3 for the LSB adjustment -- both
 * masks are applied to a full uint8_t, so the index is bounded to
 * [0,0x3E] by construction; no instrumentation needed.
 */
extern const uint8_t phoenix_screen_ram_address_table[0x40];

/*
 * [ASM: 0A40-0A4B] Score-average-table tile pair, fixed literal source
 * for two of draw_score_average_table_tiles()'s three draw_n_by_2()
 * calls (rows 0x42F2<-0x0A40 x4 and 0x4AD8<-0x0A48 x2); the two
 * addresses are contiguous, extracted as one 12-byte table.
 */
extern const uint8_t phoenix_score_table_tiles_a[0x0C];

/*
 * [ASM: 0B38-0B47] T0B38: player ship X position mapping, indexed by
 * (PlayerShipX & 0x07) << 1 -- always even in [0,14], plus the +1 read
 * reaches at most 15, both trivially within this 16-byte table.
 * Centralized from a local `static const` array of the same name that
 * predated phoenix_tables.c.
 */
extern const uint8_t phoenix_player_x_position_mapping[0x10];

/*
 * [ASM: 1000-13FF] Alien movement pattern cluster A: T1000 (16-byte
 * idle/reset list, values 0x01-0x02, plus a 0x00 terminator alien
 * pointers never reach -- M4395 only cycles [0,0x0F]) followed by 18
 * closed-loop movement pattern lists (T1020..T13D0), each a sequence of
 * step bytes terminated by 0x00 and padded with 0xFF. Selected by
 * phoenix_alien_closed_loop_pointers (18 of its 34 targets land here)
 * and by the M4394:M4395 idle-reset mechanism (always here). Every
 * non-0xFF byte in this range is confirmed <= 0x1F by direct inspection
 * -- the same domain phoenix_alien_direction_vectors and
 * phoenix_alien_shape_offset_page are indexed with.
 *
 * Read via a RAM-stored 16-bit pointer whose low byte free-wheels
 * (0xFF + 1 wraps to 0x00 within the same 256-byte page) while its
 * high byte only ever changes to a value written by the mechanisms
 * above, so any reachable address stays inside this array; use
 * phoenix_alien_movement_byte() below rather than indexing directly.
 */
extern const uint8_t phoenix_alien_movement_cluster_a[0x400];

/*
 * [ASM: 1400-1500] T14xx: player/alien "control state B" character
 * block shapes, read by sprite_rendering.c's execute_bit3_function
 * (cases 1/3/4) and by hw_video_audio.c:draw_background_2x2 when called
 * from case 4. src_hl = 0x1400 | b_val is bounded to [0x1400,0x14FF] by
 * construction (b_val is a uint8_t), but b_val's actual runtime domain
 * is NOT the 2-value set {0x60,0x6C} produced by InitAlienControlStates
 * alone -- instrumented across all 4 standard scripts, b_val ranged from
 * 0x00 to 0xDC (some other, unidentified writer touches this RAM byte
 * during play), so the full page is extracted rather than the narrower
 * range the init table alone would suggest. Sized to 0x101 bytes (one
 * past the page) to safely cover the src_hl++ second read even in the
 * untested b_val=0xFF case; that extra byte duplicates the start of
 * phoenix_alien_control_init_values/phoenix_alien_position_layout_page.
 */
extern const uint8_t phoenix_sprite_character_block_shapes[0x101];

/*
 * [ASM: 1500-151F] T1500: init values for alien control states A/B,
 * indexed by (LevelAndRound & 0x0F) * 2. Not to be confused with
 * init_alien_positions()'s unrelated "0x1500 | lsb" dynamic pointer
 * lookup, which walks into this and neighbouring tables via a separate
 * pointer table at 0x063A-0x0649 and is not this bounded region.
 */
extern const uint8_t phoenix_alien_control_init_values[0x20];

/*
 * [ASM: 1500-15FF] Full page backing init_alien_positions()'s
 * "0x1500 | lsb" dynamic lookup, where lsb is a byte read from a small
 * pointer table at 0x063A-0x0649 (16 entries: 0x40,0x60,0x80,0xA0,0xC0,
 * 0xE0 in various slots, plus 0xFF "unused" sentinels in slots 6,7,14,15
 * that empirically never occur when AliensLeft > 0 across four long,
 * varied scripts -- bird-investigation.txt, my_session.txt,
 * two_player_last_grown_bird.txt, extended_playthrough.txt, confirmed
 * via temporary instrumentation, removed after verification). The read
 * window is up to 32 bytes (AliensLeft capped at 16, 2 bytes/alien); for
 * every real (non-0xFF) lsb value the last byte touched is exactly
 * 0x15FF (lsb=0xE0, the highest real value, +31 = 0xFF), so the window
 * never spills into phoenix_alien_shape_offset_page (0x1600+). Overlaps
 * phoenix_alien_control_init_values (0x1500-0x151F) and
 * phoenix_alien_layout_pointers (0x1520-0x153F) by design -- same
 * literal ROM bytes, independently verified, kept separate because this
 * read site's own reachable range needs the full page as a safety
 * margin against the untested 0xFF slots.
 */
extern const uint8_t phoenix_alien_position_layout_page[0x100];

/*
 * [ASM: 1520-153F] T1520: pointer to alien movement pattern table,
 * indexed by (LevelAndRound & 0x0F) * 2.
 */
extern const uint8_t phoenix_alien_layout_pointers[0x20];

/*
 * [ASM: 1600-16FF] Full page combining the T1600 sprite-shape-offset
 * mega-table (originally catalogued too narrowly as 0x1600-0x161F; the
 * ASM shows dense, unlabelled sub-tables packed all the way to 0x169F)
 * and the T16A0 animation-descriptor table (also catalogued too
 * narrowly as 0x16A0-0x16CF; the ASM shows 32 entries of 3 bytes
 * running to 0x16FF, matching the proven index bound below). Used by
 * alien_animation_update/get_player_ship_animation_frame_values.
 * The list_index/idx feeding these lookups comes from the alien
 * closed-loop pattern tables at 0x1020-0x13FF, confirmed by direct
 * inspection to never exceed 0x1F (32 entries) -- matching the T16A0
 * table's real 32-entry, 96-byte extent exactly.
 */
extern const uint8_t phoenix_alien_shape_offset_page[0x100];

/*
 * [ASM: 1700-173F] T1700: alien movement direction deltas (dx,dy
 * pairs), indexed by ROL1(idx) where idx is a closed-loop pattern
 * table value, proven <= 0x1F (see phoenix_alien_shape_offset_page),
 * so ROL1(idx) = idx*2 <= 0x3E, safely within this 32-entry table.
 */
extern const uint8_t phoenix_alien_direction_vectors[0x40];

/*
 * [ASM: 1740-175F] T1740: in-formation bullet hit-window table, 4 bytes
 * per tile (only the first 3 are read), indexed by (chr & 0x07) * 4
 * where chr is a background tile byte masked to the low 3 bits --
 * always 0-7, trivially safe. weapon_collision.c:l0e10.
 */
extern const uint8_t phoenix_formation_hit_window[0x20];

/* [ASM: 1760-1767] T1760: per-round alien/bird population by round index. */
extern const uint8_t phoenix_round_population[0x08];

/*
 * [ASM: 1770-17AF] T1770: shield damage-state shapes for
 * player_logic.c:draw_shields(), indexed by (ShieldCount & 0x0C) << 2 --
 * bounded to {0,0x10,0x20,0x30} by construction, each selecting a
 * 16-byte draw_image_c_by_b() block.
 */
extern const uint8_t phoenix_shield_table[0x40];

/* [ASM: 17B0-17B7] Alien explosion frame sequence image indices. */
extern const uint8_t phoenix_alien_explosion_frames[0x08];

/*
 * [ASM: 17B8-17FF] Two adjacent, independently-bounded regions kept as
 * one array. 0x17B8-0x17DB backs alien_logic.c's three drawNx2() calls
 * (corrected from an earlier, wrong "genuinely unresolved" assessment --
 * see drawNx2's own doc comment in attract_mode.c): two fixed literals
 * (0x17D0, 0x17D6) plus one derived from phoenix_alien_explosion_frames'
 * 5 possible byte values OR'd with 0x1700 -- the three sub-ranges are
 * exactly contiguous. 0x17F0-0x17FF backs player_logic.c:
 * shields_expired's fixed draw_image_c_by_b(0x17F0,...) call and is also
 * the 4th value player_explosion.c's mothership-pointer-derived
 * image_ptr can take (the other 3 values land inside the already-
 * extracted phoenix_mothership_explosion_pointers itself -- see that
 * reader, which indexes into it directly rather than duplicating it
 * here). The small gap 0x17DC-0x17EF is unused by any known reader but
 * kept for contiguity.
 */
extern const uint8_t phoenix_shield_and_drawnx2_shapes[0x48];

/*
 * [ASM: 1800-185F] Screen-ram addresses and static attract-mode/HUD text
 * for utilities.c:print_text_lines()'s 0x1800 call sites. Exact range:
 * simulating print_text_lines()/draw_row()'s address arithmetic (the
 * DE/HL page-relative "+5" step is masked to the low byte, but the
 * 26-column row-draw loop is a genuine 16-bit INC HL, not masked) for
 * every real (addr,count) pair shows the widest real call (count=3)
 * touches exactly 0x1800-0x185F -- immediately adjacent to, but not
 * overlapping, phoenix_score_average_text_page below.
 */
extern const uint8_t phoenix_attract_text_page[0x60];

/*
 * [ASM: 1860-1B5F] Full page backing slow_print_score_average_table()'s
 * two dynamic reads (attract_mode.c): a scrolling-text character lookup
 * (original ROM byte at hl_val + e) and a screen-address pointer pair
 * (original ROM bytes at hl_val/hl_val+1), where hl_val = 0x1860 +
 * ((Counter98[0] << 8) | (Counter98[1] & 0xE0)) and e = Counter98[1] &
 * 0x1F (>= 6, else the function returns early). Counter98 is a
 * free-running 16-bit counter, so this index is not mathematically
 * bounded the way the other extracted tables are -- the range above was
 * established empirically instead, via hit-count instrumentation run
 * against passive (input-less) playback at 3610, 30000, and 60000
 * frames: hl_val+e never exceeded 0x1B3F across all three run lengths
 * (2808 calls at the 30000-frame length, 5543 at 60000), a strong but
 * not proven structural bound. The extraction extends to 0x1B60, a
 * margin beyond the observed ceiling, and its last 0x20 bytes duplicate
 * the start of phoenix_mothership_explosion_pointers (0x1B40+) -- same
 * physical ROM bytes, independently verified, kept separate for the
 * same reason phoenix_alien_position_layout_page overlaps its
 * neighbours: this read site's own reachable range needs the safety
 * margin. If this empirical bound is ever found to be wrong, widening
 * this array is the fix, not adding a hard-coded cap in the reader.
 */
extern const uint8_t phoenix_score_average_text_page[0x300];

/*
 * [ASM: 198C] Single-byte shape offset used by l38a1_erase_bird to form
 * the "FourByFourEmpty" bird-erase shape address (0x17DE + this byte).
 */
extern const uint8_t phoenix_bird_erase_shape_selector;

/*
 * [ASM: 1B40-1B9F] Mothership tile-hit replacement tiles (T1B40/T1B48,
 * mothership_impl.c:l2351_mothership_animation) and player-explosion
 * shape pointers (T1B60/T1B90, player_explosion.c:l20e8). Originally
 * catalogued as 0x1B00-0x1B5F, which is both too wide at the low end
 * (0x1B00-0x1B3F is unrelated data neither reader touches) and too
 * narrow at the high end (l20e8's index is always in [0x90, 0x9E],
 * reaching 0x1B9F, not covered by the old 0x1B5F ceiling).
 */
extern const uint8_t phoenix_mothership_explosion_pointers[0x60];

/*
 * [ASM: 1BA0-1BBF] "1 OR 2 PLAYERS BUTTON" static text (setA) for
 * utilities.c:print_text_lines()'s single 0x1BA0 call site. Exact range,
 * derived the same way as phoenix_attract_text_page above.
 */
extern const uint8_t phoenix_players_button_text[0x20];

/*
 * Resolves utilities.c:print_text_lines()/draw_row()'s source address to
 * its byte value. Every real call site (addr,count) pair is now proven
 * (by simulating the exact address arithmetic, not assumed) to stay
 * within one of these three ranges -- an address outside all three would
 * indicate a new, unaccounted-for caller.
 */
static inline uint8_t phoenix_text_byte(uint16_t addr) {
    if (addr >= 0x1BA0) return phoenix_players_button_text[addr - 0x1BA0];
    if (addr >= 0x1860) return phoenix_score_average_text_page[addr - 0x1860];
    return phoenix_attract_text_page[addr - 0x1800];
}

/*
 * [ASM: 1BC0-1BFF] Mothership pilot/antenna animation frames for
 * alien_wave.c's L2322 (else-branch of mothership_animation), source =
 * 0x1B00 | a where a = (((AnimationCounter & 0x07) rotated left 3) &
 * 0xFF) + 0xC0 -- bounded by construction to the 8 values
 * {0xC0,0xC8,...,0xF8}, each the start of an 8-byte draw_image_c_by_b()
 * block (4 rows x 2 cols), exactly covering this range with no gaps.
 */
extern const uint8_t phoenix_alien_wave_animation_shapes[0x40];

/*
 * [ASM: 1C00-1CFF] T1C00: starfield/background image data. Read by
 * three independent sites, all provably confined to this single page:
 * mothership_logic.c's fixed draw_image_c_by_b(0x1C00, ..., 9, 20) call
 * (180 bytes from 0x1C00); state_play.c:finish_spiral_transition, whose
 * uint8_t source index cycles through the full page and reads it multiple
 * times over its ~512-byte write loop; and
 * hw_video_audio.c:stars_scroll_down, whose hl is a RAM-persisted
 * pointer ($M43B2:M43B3). M43B2 (the page selector) is written by
 * init_global_level_data()'s copy from phoenix_level_data_page: decoding
 * that page's own bytes at offset 7 for each of its 4 source blocks
 * gives exactly 0x1C, 0x1C, 0x1F and 0x1D -- so M43B2 is always one of
 * {0x1C,0x1D,0x1F}, matching RAMUse.md's "T1C00 or T1D00 or T1F00" note
 * exactly, with no runtime ambiguity. See
 * phoenix_starfield_or_mothership_byte() below.
 */
extern const uint8_t phoenix_starfield_page[0x100];

/*
 * Resolves a utilities.c:draw_image_c_by_b() source address to its byte
 * value. Every real call site's hl parameter is now proven to fall into
 * exactly one of these five ranges (see phoenix_shield_table,
 * phoenix_shield_and_drawnx2_shapes, phoenix_mothership_explosion_pointers,
 * phoenix_alien_wave_animation_shapes, phoenix_starfield_page above) --
 * enumerated by tracing all 5 of draw_image_c_by_b's call sites
 * (mothership_logic.c, player_logic.c x2, player_explosion.c,
 * alien_wave.c), not assumed. An address outside all five ranges would
 * indicate a new, unaccounted-for caller.
 */
static inline uint8_t phoenix_image_byte(uint16_t addr) {
    if (addr >= 0x1C00) return phoenix_starfield_page[addr - 0x1C00];
    if (addr >= 0x1BC0) return phoenix_alien_wave_animation_shapes[addr - 0x1BC0];
    if (addr >= 0x1B60) return phoenix_mothership_explosion_pointers[addr - 0x1B40];
    if (addr >= 0x17B8) return phoenix_shield_and_drawnx2_shapes[addr - 0x17B8];
    return phoenix_shield_table[addr - 0x1770];
}

/*
 * [ASM: 1D00-1DFF] T1D00: mothership object tiles (26x9, upside down --
 * the mothership scrolls down from the top of the screen). Second of
 * stars_scroll_down's three possible M43B2 pages, see
 * phoenix_starfield_page's comment above.
 */
extern const uint8_t phoenix_mothership_tile_page[0x100];

/*
 * [ASM: 1E00-1E1F] T1E00: planet shape source image, read by
 * hw_video_audio.c:draw_background_2x2() when called from
 * add_planets_to_background(). The T1E60 sub-table (part of
 * phoenix_planet_galaxy_page below) doesn't hold a direct data byte --
 * it holds an INDEX (all 32 entries confirmed multiples of 4 in
 * [0,0x1C]) that becomes draw_background_2x2's own hl source parameter
 * via 0x1E00 | index; that function reads 4 consecutive bytes from hl,
 * so the 8 possible index values (spaced exactly 4 apart) cover this
 * whole 32-byte range contiguously with no gaps. Found via a real
 * lockstep divergence (BackgroundScreen bytes at $4852/$4853/$4872/
 * $4873 from frame 580 in the passive script) after an initial
 * rewiring mistakenly assumed this sub-table's bytes were consumed
 * directly rather than as a further indirection.
 */
extern const uint8_t phoenix_planet_shape_page[0x20];

/*
 * [ASM: 1E20-1EDF] T1E20/T1E60/T1E80/T1EA0/T1EC0: planet and galaxy
 * background decoration tables for hw_video_audio.c's
 * add_planets_to_background() and add_galaxies_to_background(). Every
 * index into this region is masked with & 0x1F before use, so each
 * 32-byte sub-table is bounded by construction; the six 32-byte slices
 * are exactly contiguous, extracted as one page.
 */
extern const uint8_t phoenix_planet_galaxy_page[0xC0];

/*
 * Resolves a hw_video_audio.c:draw_background_2x2() source address to
 * its byte value. Its only 2 real callers are
 * add_planets_to_background() (hl in phoenix_planet_shape_page or
 * phoenix_planet_galaxy_page's range, see phoenix_planet_shape_page's
 * comment for why there are two here) and sprite_rendering.c's case 4
 * (hl in phoenix_sprite_character_block_shapes' range) -- none of the
 * three source ranges overlap or abut, so simple thresholds distinguish
 * them.
 */
static inline uint8_t phoenix_background_2x2_byte(uint16_t addr) {
    if (addr >= 0x1E20) return phoenix_planet_galaxy_page[addr - 0x1E20];
    if (addr >= 0x1E00) return phoenix_planet_shape_page[addr - 0x1E00];
    return phoenix_sprite_character_block_shapes[addr - 0x1400];
}

/*
 * [ASM: 1F00-1FFF] T1F00: starfield background without planets. Third of
 * stars_scroll_down's three possible M43B2 pages, see
 * phoenix_starfield_page's comment above.
 */
extern const uint8_t phoenix_starfield_no_planets_page[0x100];

/*
 * Resolves hw_video_audio.c:stars_scroll_down()'s hl (M43B2:M43B3) to its
 * byte value. M43B2 is proven to always be 0x1C, 0x1D or 0x1F (see
 * phoenix_starfield_page's comment); any other high byte would indicate
 * an unaccounted-for writer of M43B2/M43B3.
 */
static inline uint8_t phoenix_starfield_or_mothership_byte(uint16_t addr) {
    if (addr >= 0x1F00) return phoenix_starfield_no_planets_page[addr - 0x1F00];
    if (addr >= 0x1D00) return phoenix_mothership_tile_page[addr - 0x1D00];
    return phoenix_starfield_page[addr - 0x1C00];
}

/*
 * [ASM: 233A-2359] T233A: intro bird animation frame index, indexed by
 * ((Counter98[1] & 0xF8) >> 3) + 0x3A -- Counter98[1] is a free-running
 * byte, so the index legitimately covers all 32 values in [0x3A,0x59],
 * not just the 23-byte T233A table's own extent (0x233A-0x2350). Bytes
 * 0x2351-0x2359 are the opcodes for l2351_mothership_animation
 * (mothership_impl.c), already translated there as ordinary code --
 * same "table abuts code, out-of-range index reads it as data" pattern
 * as phoenix_bird_hitmask_page; the full 32-byte range is kept for the
 * same reason. attract_mode.c:draw_intro_bird_animation_frame.
 */
extern const uint8_t phoenix_intro_bird_anim_frames[0x20];

/*
 * [ASM: 2800-2BFF] Full page combining T2800/T2900 (player explosion
 * tiles/control, l2085_particles) and T2A00/T2B00 (mothership
 * explosion tiles/control, same shared l2085_particles route called
 * from state_endings.c). The control-table walk index (hl) advances by
 * 2 per loop iteration for a data-dependent number of iterations before
 * an SBC-style bounds check breaks the loop; that iteration count is
 * not proven tightly bounded, so the whole page is kept rather than
 * assuming the originally catalogued 0x2800-0x29FF (player only) always
 * holds -- this also correctly covers the previously-uncatalogued
 * mothership variant with the same extraction.
 */
extern const uint8_t phoenix_explosion_particle_page[0x400];

/*
 * [ASM: 2C00-2FFF] Alien movement pattern cluster B: 18 more closed-loop
 * patterns (labelled 18-35 in the ASM, a separate numbering restart from
 * cluster A's 18), same 0x00-terminator/0xFF-padding structure and same
 * proven <= 0x1F value domain. 16 of its pattern addresses come from
 * phoenix_alien_closed_loop_pointers; the remaining two entry points
 * (0x2E00, 0x2E40 -- patterns 26 and 28) come only from
 * alien_logic.c:l3028's breakout scheduler, not from that table.
 */
extern const uint8_t phoenix_alien_movement_cluster_b[0x400];

/*
 * Resolves a RAM-stored alien movement/animation pattern pointer to its
 * byte value. addr is always in [0x1000,0x13FF] or [0x2C00,0x2FFF] --
 * proven by enumerating every writer of the pointer fields ($4B50-$4B6F,
 * M4351/M4352, M4394/M4395): the initial value (phoenix_alien_layout_pointers,
 * always 0x1000), the closed-loop retarget (phoenix_alien_closed_loop_pointers,
 * 34 values split across both clusters), and the breakout retarget
 * (l3028, always 0x2E00 or 0x2E40).
 */
static inline uint8_t phoenix_alien_movement_byte(uint16_t addr) {
    if (addr >= 0x2C00) return phoenix_alien_movement_cluster_b[addr - 0x2C00];
    return phoenix_alien_movement_cluster_a[addr - 0x1000];
}

/*
 * [ASM: 3300-3307] T3300: closed-loop distance band, indexed by
 * (playerDistance >> 5) & 0x07 (l31b4).
 */
extern const uint8_t phoenix_alien_distance_bands[0x08];

/*
 * [ASM: 3310-332F] T3310: closed-loop pattern selector, indexed by
 * rotated-distance-band + side + 0x10 (l31b4). Confirmed bounded: side
 * contributes {0,4,8,0xC,0x10,0x14,0x18,0x1C}, and the height/breakout
 * band (M4357, bounds-checked < 3 elsewhere) contributes 0-3.
 */
extern const uint8_t phoenix_alien_pattern_selectors[0x20];

/*
 * [ASM: 3330-33FF] T3330: closed-loop movement pattern pointers,
 * indexed by a T3310 entry (always a multiple of 8 in [0x30, 0xF8])
 * plus (random & 0x06) (l31b4).
 */
extern const uint8_t phoenix_alien_closed_loop_pointers[0xD0];

/*
 * [ASM: 3B00-3BFF] Full page backing the T3B60 bird-hit-mask lookups.
 * l3844_small_bird_hit's index (b + 0x60) never dips below 0x3B60 (b in
 * [0,0x4F], index stays in [0x3B60,0x3BAF]) -- no wrap possible there.
 * l38bc_large_hit's index (b + 0xB0) does wrap below 0x60 for b in
 * [0x50,0x6F] (grown-bird tiles 0xE0-0xFF), into the code bytes
 * preceding T3B60 (0x3B00-0x3B5F). Confirmed, not just theoretically
 * possible: instrumented and run against bird-investigation.txt (13935
 * frames), the wrap fired 27 times across 12 distinct tile values (e.g.
 * tile=0xE3 -> index 0x03, landing inside l3b02's own function body).
 * The whole page is kept to preserve that confirmed wrap exactly.
 *
 * Bytes 0x00-0x5F are NOT unclassified: they are the Z80 opcodes for
 * l3b02/l3b1b/l3b28/l3b33/l3b43 in sound_dispatcher.c, already
 * translated and called there as ordinary code. This array is a
 * separate, deliberate duplicate of the same physical ROM bytes for
 * their unrelated use as inert lookup data on the bird-hit wrap path
 * above -- do not "clean up" the overlap by deriving one from the
 * other; a C function's compiled bytes bear no relation to the
 * original Z80 opcodes, so only the literal ROM copy here is valid
 * for the data-read use.
 */
extern const uint8_t phoenix_bird_hitmask_page[0x100];

/*
 * [ASM: 3C00-3C0B] Fixed literal source for
 * draw_score_average_table_tiles()'s third draw_n_by_2() call
 * (0x4B15<-0x3C00 x6 rows). Part of the much larger, still-uncatalogued
 * $3C00-$3DB7 shape-data region (see attract-mode text/shapes note),
 * but this specific 12-byte slice is the only part this fixed call site
 * touches -- extracted narrowly rather than the whole region.
 */
extern const uint8_t phoenix_score_table_tiles_b[0x0C];

/*
 * [ASM: 3C00-3DB7] Bird shape bitmap data for attract_mode.c:
 * draw_bird_shape_350c(), read via a `shape` pointer built either from
 * phoenix_bird_shape_pointers (drawbirdobject's normal draw path) or a
 * fixed $17F0 literal (l38a1_erase_bird's erase path, which stays
 * entirely within the already-extracted phoenix_shield_and_drawnx2_
 * shapes -- see phoenix_bird_shape_data_byte() below). Not
 * mathematically bounded (row count and clip depth both depend on free
 * RAM state), so established empirically: hit-count instrumentation
 * across all 4 standard scripts (3610 to 13935 frames, 1009-8084 draw
 * calls each) found the drawbirdobject path's reachable range stable
 * at exactly $3C00-$3DB7 in every run -- conveniently also exactly
 * where the already-extracted phoenix_egg_transformation_types begins
 * ($3DB8), a natural boundary. First 12 bytes duplicate
 * phoenix_score_table_tiles_b above -- same physical ROM bytes,
 * independently verified, kept separate per that table's own note.
 */
extern const uint8_t phoenix_bird_shape_data_page[0x1B8];

/*
 * Resolves attract_mode.c:draw_bird_shape_350c()'s `shape` pointer to
 * its byte value. Its two real sources (drawbirdobject's normal path
 * and l38a1_erase_bird's erase path, via draw_bird_shape_34de) are
 * proven -- by hit-count instrumentation, not assumed -- to stay
 * entirely within phoenix_bird_shape_data_page or
 * phoenix_shield_and_drawnx2_shapes respectively; the two ranges don't
 * overlap or abut, so a single threshold distinguishes them.
 */
static inline uint8_t phoenix_bird_shape_data_byte(uint16_t addr) {
    if (addr >= 0x3C00) return phoenix_bird_shape_data_page[addr - 0x3C00];
    return phoenix_shield_and_drawnx2_shapes[addr - 0x17B8];
}

/*
 * [ASM: 3DB8-3DBF] Egg-transformation bird types, indexed by
 * (idx | side) + 0xB8 in collision_detection.c's l38bc_large_hit,
 * where idx = egg_type - 0x0B is in [0,2] and side is 0 or 4 -- always
 * one of indices {0,1,2,4,5,6}; 3 and 7 (bytes 0xFF) are unreachable.
 */
extern const uint8_t phoenix_egg_transformation_types[0x08];

/*
 * [ASM: 3DC0-3DDF] T3DC0: bird dive-bomb spawn positions, indexed by
 * (B4BD2 & 0x1E) + 0xC0 - 0xC0 (try_spawn_bird_dive_bomb). B4BD2 & 0x1E
 * is always even in [0, 0x1E], keeping the index within this table.
 */
extern const uint8_t phoenix_bird_dive_spawn_positions[0x20];

/*
 * [ASM: 3DE0-3DFF] T3DE0: bird sound decay thresholds, indexed by
 * B4BD6 (l3ad0 in sound_dispatcher.c). B4BD6 is always masked with
 * & 0x1F at its only writer (birds_vertical_movement.c), so the index
 * never exceeds 0x1F.
 */
extern const uint8_t phoenix_bird_sound_cadence[0x20];

/* [ASM: 3E00-3E07] T3E00: single-bit pixel mask by bullet X within a cell. */
extern const uint8_t phoenix_bullet_pixel_masks[0x08];

/*
 * [ASM: 3E00-3E7F] Full page backing the T3E08 bird shape data pointer
 * lookup, indexed by (ROL3(type) + frame) & 0x7E (drawbirdobject). Type
 * is always >= 1, so in practice the index stays at 0x08 or above (the
 * T3E08 table), but frame is an unbounded RAM byte, so the index is not
 * provably bounded away from the T3E00 bullet-pixel-mask table just
 * below -- the whole page is kept so any index value reads correctly,
 * matching phoenix_bird_hitmask_page's approach for the same reason.
 */
extern const uint8_t phoenix_bird_shape_pointers[0x80];

/*
 * [ASM: 3E80-3EBF] Per-formation flight parameter byte, indexed by a
 * value built from LevelAndRound/BirdsLeft/Counter9A/random bits, always
 * in [0x80, 0xBE] before the 0x3E00 page base (refresh_bird_flight_parameters).
 */
extern const uint8_t phoenix_bird_formation_params[0x40];

/*
 * [ASM: 3EC0-3ECF] T3EC0: LSB of the DrawNx2 entry point, indexed by
 * bird type (drawbirdobject). Type is always >= 1, byte 0 (0xFF) is an
 * unused placeholder.
 */
extern const uint8_t phoenix_bird_draw_entries[0x10];

/* [ASM: 3ED0-3EDF] Per-phase vertical scroll increments for bird climbs. */
extern const uint8_t phoenix_bird_scroll_steps[0x10];

/* [ASM: 3EE0-3EFF] Maximum descent speed for each bird formation position. */
extern const uint8_t phoenix_bird_descent_caps[0x20];

/*
 * [ASM: 3F00-3F7F] T3F00: per-bird-type behaviour scripts (16 entries
 * of 8 bytes: two data words, two continuation-routine addresses),
 * indexed by type * 8 (update_bird_behavior). Type is bounded to
 * [0x00, 0x0F] by every writer: BM_SET(0, ...) in this file only ever
 * stores byte values already present in this table, and the egg
 * transform in collision_detection.c only ever writes 0x0C-0x0E from
 * the T3DB8 table. The ASM's own data ends here; 0x3F80 onward is an
 * unrelated "level 3/8 initial bird data" table, not part of T3F00 --
 * the catalog originally (incorrectly) extended this region to 0x3FFF.
 * That adjacent table is now itself extracted, see
 * phoenix_bird_data_alt_page below.
 */
extern const uint8_t phoenix_bird_behaviour_scripts[0x80];

/*
 * [ASM: 3F80-3FFF] "Level 3/8 initial bird data" -- the table adjacent
 * to phoenix_bird_behaviour_scripts flagged but not catalogued in that
 * table's own note above. Read by misc_logic.c:l32b0, whose hl formula
 * (0x3F00 | (0xC0 - 8*BirdsLeft), optionally +0x40) combined with its
 * read-loop count (8*BirdsLeft bytes) makes the highest byte touched
 * PROVABLY CONSTANT regardless of BirdsLeft (the -8n/+8n terms cancel):
 * exactly 0x3FBF without the LevelAndRound adjustment, exactly 0x3FFF
 * (the literal last byte of the 16 KB ROM) with it. Combined reachable
 * range is 0x3F40-0x3FFF; the low end (0x3F40-0x3F7F) duplicates the
 * tail of phoenix_bird_behaviour_scripts, so only the previously-
 * uncatalogued 0x3F80-0x3FFF half is extracted here -- l32b0's reader
 * indexes into whichever of the two arrays its computed address falls
 * into.
 */
extern const uint8_t phoenix_bird_data_alt_page[0x80];

#endif /* PHOENIX_TABLES_H */
