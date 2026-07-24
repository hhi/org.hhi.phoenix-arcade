#include <stdbool.h>

#include "attract_mode.h"
#include <stdio.h>
#include "phoenix_hw.h"
#include "phoenix_state.h"
#include "utilities.h"
#include "z80_core.h"
#include "game_constants.h"
#include "coverage.h"
#include "phoenix_tables.h"
#include <string.h>

extern PhoenixState state;

// External dependencies
extern void draw_score_average_table_tiles(void); // L0BCA
extern void init_global_level_data(void); // L0580
extern void draw_intro_bird_animation_frame(void); // L21DC
extern void clear_background(void); // L03A0
extern void wait_vblank_coin(void); // L0080
extern void clear_foreground(void); // L0380
extern void slow_print_scroll_register_update(void); // L0078
extern void add_bc_to_mem(uint16_t hl, uint16_t bc);

/*
 * Translates SplashAndDemo
 * Handles the intro splash and the game demo.
 * [ASM: 00E3-013A]
 * [ASM: 0140-0172]
 */
void splash_and_demo(void) {
    // 00E3: LD HL,$4399
    // 00E6: CALL $0200
    add_one_to_mem(0x4399);
    
    // 00E9: LD BC,$0001
    // 00EC: CALL $0258
    // 00EF: JP Z,$01E1
    if (compare_bc_to_mem(0x4399, 0x0001)) {
        extern void print_copyright_lines(void);
        print_copyright_lines();
        return;
    }
    
    // 00F2: LD BC,$0002
    // 00F5: LD DE,$011F
    // 00F8: CALL $0260
    extern uint8_t l0260_subtract_if_enough(uint16_t, uint16_t, uint16_t);
    if (!l0260_subtract_if_enough(0x4399, 0x0002, 0x011F)) {
        slow_print_score_average_table();
        return;
    }
    
    // 00FE: LD BC,$0120
    // 0101: CALL $0258
    // 0104: JP Z,$0BCA
    if (compare_bc_to_mem(0x4399, 0x0120)) {
        draw_score_average_table_tiles();
        return;
    }
    
    // 0107: LD C,$B0 (BC is still 01xx from previous, so BC=$01B0)
    // 0109: CALL $0258
    // 010C: JP Z,$01E1
    if (compare_bc_to_mem(0x4399, 0x01B0)) {
        extern void print_copyright_lines(void);
        print_copyright_lines();
        return;
    }
    
    // 010F: LD C,$B8 (BC=$01B8)
    // 0111: CALL $0258
    // 0114: JP Z,$0580
    if (compare_bc_to_mem(0x4399, 0x01B8)) {
        init_global_level_data();
        return;
    }
    
    // 0117: LD C,$C0 (BC=$01C0)
    // 0119: LD DE,$02DF
    // 011C: CALL $0260
    if (!l0260_subtract_if_enough(0x4399, 0x01C0, 0x02DF)) {
        slow_print_scroll_register_update();
        return;
    }
    
    // 0122: LD BC,$0300
    // 0125: LD DE,$03AF
    // 0128: CALL $0260
    if (!l0260_subtract_if_enough(0x4399, 0x0300, 0x03AF)) {
        draw_intro_bird_animation_frame();
        return;
    }
    
    // 012E: LD BC,$03E6
    // 0131: LD DE,$FFFF
    // 0134: CALL $0260
    if (!l0260_subtract_if_enough(0x4399, 0x03E6, 0xFFFF)) {
        extern void check_demo_mode_player_and_alien(void); // L03B0
        check_demo_mode_player_and_alien();
        return;
    }
    
    // 013A: RET
    return;
}

/*
 * Translates L0140 (Continuation of attract mode setup)
 * [ASM: 0140-0172]
 */
void clear_fore_and_background(void) {
    // 0140: CALL $03A0
    clear_background();
    
    // 0143: CALL $0080
    wait_vblank_coin();
    
    // 0146: CALL $0380
    clear_foreground();
    
    // 0149: LD HL,$43A3
    // 014C: LD (HL),$02
    // 014E: INC L
    // 014F: LD (HL),$00
    state.GameAndDemoOrSplash = 0x02;
    state.GameState = GAME_STATE_NEW_GAME;
    
    // 0154: LD L,$B8
    // 0156: LD B,$08
    // 0158: CALL $05D8
    // Clear 8 bytes from $43B8 (LevelAndRound to $43BF)
    memset(&state.LevelAndRound, 0, 8);
    
    // 015B: LD L,$BA
    // 015D: LD (HL),$10
    state.AliensLeft = 0x10;
    
    // 015F: LD L,$BE
    // 0161: LD A,($7800)
    // 0164: AND $0C
    // 0166: RLCA
    // 0167: RLCA
    // 0168: ADD $30
    // 016A: LD (HL),A
    // Wait, DSW0 is mapped at 7800. Let's assume we have a read_dsw0() function.
    extern uint8_t read_dsw0(void);
    uint8_t dsw = read_dsw0();
    // RLCA twice = multiply by 4: 0000_1100 -> 0011_0000
    state.BonusLivesAt = ((dsw & 0x0C) << 2) + 0x30;
    
    // 016B: LD H,$58
    // 016D: LD (HL),$00
    // Wait, $58xx is scroll register.
    extern void hw_write_scroll_register(uint8_t);
    hw_write_scroll_register(0x00);
    
    // 016F: CALL $0080
    wait_vblank_coin();
    
    // 0172: RET
}

/*
 * Translates GetPlayerInputsForDemo
 * [ASM: 0173-0195]
 */
uint8_t get_player_inputs_for_demo(void) {
    uint8_t a = state.Counter98[1]; // Counter98+1 (LSB)
    a &= 0x7F;
    uint8_t b = 0xCE; // 1100_1110 (move right)
    
    if (a < 0x1F) return b;
    b = 0xFE; // 1111_1110 (push fire)
    if (a == 0x1F) return b;
    
    b = 0xAE; // 1010_1110 (move left)
    if (a < 0x5F) return b;
    
    b = 0xFE; // push fire
    if (a == 0x5F) return b;
    
    b = 0xCE; // move right
    if (a < 0x7F) return b;
    
    b = 0xFE; // push fire
    uint8_t msb = state.Counter98[0];
    if (msb != 0x09) return b;
    
    return 0x7E; // 0111_1110 (push shield)
}

/*
 * Translates SlowPrintScoreAverageTable
 * [ASM: 0196-01CD]
 */
void slow_print_score_average_table(void) {
    uint8_t a = state.Counter98[1]; // LSB
    uint8_t e = a & 0x1F;
    if (e < 0x06) return;
    
    uint8_t c = a & 0xE0;
    uint8_t b = state.Counter98[0]; // MSB
    
    uint16_t hl_val = (b << 8) | c;
    hl_val += 0x1860;

    // Save to M43A8/A9
    state.M43A8 = hl_val >> 8;
    state.M43A9 = hl_val & 0xFF;

    // Read the character to print from hl_val + e
    uint8_t char_val = phoenix_score_average_text_page[hl_val + e - 0x1860];

    // Z80 explicitly loads D from hl_val and E from hl_val + 1
    // D is the high byte, E is the low byte
    // 01B3: LD D,(HL) -> D = prg_mem[hl_val]
    // 01B5: LD E,(HL+1) -> E = prg_mem[hl_val+1]
    uint16_t de = (phoenix_score_average_text_page[hl_val - 0x1860] << 8)
                | phoenix_score_average_text_page[hl_val + 1 - 0x1860];
    
    if (e > 0x06) {
        uint8_t loop_count = e - 0x06;
        while (loop_count > 0) {
            de -= 0x20; // 0217 (RightOneColumn)
            loop_count--;
        }
    }
    
    mem_write(de, char_val);

    extern void check_coin_event(uint16_t de, uint16_t rom_addr);
    check_coin_event(de, hl_val + e);
}

/*
 * Translates SlowPrintScrollRegisterUpdate
 * [ASM: 0078-007D]
 */
void slow_print_scroll_register_update(void) {
    slow_print_score_average_table(); // 0196
    extern void l06f0(void); // 06F0
    l06f0();
}

/*

 * Translates GameDemo
 * [ASM: 03B0-03FD]
 */
void check_demo_mode_player_and_alien(void) {
    uint16_t c98 = (state.Counter98[0] << 8) | state.Counter98[1];
    
    if (c98 == 0x07A0) {
        state.GameState = GAME_STATE_SCORE_FLASH;
        state.LevelAndRound = 4;
        state.AliensLeft = 0;
        state.BirdsLeft = 8;
        return;
    } else if (c98 == 0x0B60) {
        state.GameState = GAME_STATE_SCORE_FLASH;
        state.LevelAndRound = 8;
        state.AliensLeft = 0x10;
        state.BirdsLeft = 0;
        return;
    }
    
    // L03CE
    uint8_t demo_input = get_player_inputs_for_demo();
    state.IN0Current = (state.IN0Current & 0x01) | demo_input;
    
    extern void game_state_machine(void); // 0400
    game_state_machine();
}

/*
 * Translates CoinChecking
 * [ASM: 17E0-17ED]
 */
uint8_t coin_checking(void) {
    uint8_t dsw0 = hw_read_dsw();
    if ((dsw0 & 0x10) == 0) {
        return state.CoinCount; // 1 coin = 1 play
    }
    return (state.CoinCount >> 1) & 0x0F; // 2 coins = 1 play
}

/*
 * Translates L0288
 * [ASM: 0288-02EE]
 */
void prompt_for_start_game(void) {
    extern void clear_fore_and_background(void); // 0140
    extern void print_text_lines(uint16_t screen_draw_info_addr, uint8_t columns);
    extern uint8_t coin_checking(void); // 17E0
    extern void update_hi_score(void);
    extern void clear_and_print_scores(void);
    extern void get_player_lives_from_dip(void);
    extern void hw_write_scroll_register(uint8_t);
    
    clear_fore_and_background();
    
    // 028B: LD HL,$19C0
    // 028E: LD C,$02
    print_text_lines(0x19C0, 2);
    
    // 0293: LD C,$02
    coin_checking(); // This sets A to number of credits
    
    uint8_t c_reg = 2;
    if (state.CoinCount >= 2) {
        // 029D: LD HL,$1BA0
        // 02A0: LD C,$01
        print_text_lines(0x1BA0, 1);
        c_reg = 6;
    }
    
    // 02A7: L02A7 - get start buttons
    extern uint8_t read_in0(void); // 0x7000
    uint8_t a = read_in0();
    a = ~a;
    a &= c_reg; // mask for start 1 or 2
    if (a == 0) return;
    
    // 02AD: CALL $02CB DecrementCoins
    extern void decrement_coins(uint8_t start_buttons);
    decrement_coins(a);
    
    // 02B0: CALL $02F0 UpdateHiScore
    update_hi_score();
    
    // 02B3: CALL $032E ClearAndPrintScores
    clear_and_print_scores();
    
    // 02B6: CALL $0350 GetPlayerLivesFromDip
    get_player_lives_from_dip();
    
    // 02B9: CALL $0140 ClearForeAndBackground (in bank 0)
    clear_fore_and_background();

    // 02BC-02BE: LD H,$50; LD (HL),$01 -- $50xx is the VIDEO register
    // (bit 0 = RAM bank), not the scroll register: switch to bank 1 so
    // the second clear initialises player 2's bank (screen wipe,
    // AliensLeft=16 and the DSW bonus-life threshold at $43BE all
    // happen inside ClearForeAndBackground). A previous translation
    // wrote the scroll register here, leaving player 2's bank
    // uninitialised -- player 2 could never earn a bonus life. Found
    // via scripted lockstep vs jphoenix.
    extern void hw_write_video_register(uint8_t);
    hw_write_video_register(0x01);

    // 02C0: CALL $0140 ClearForeAndBackground (in bank 1)
    clear_fore_and_background();
    coverage_hit("player_2_bank_initialized");

    // 02C3-02C5: back to bank 0
    hw_write_video_register(0x00);
}

/*
 * Translates DecrementCoins
 * Updates GameOrAttract and subtracts coins
 * [ASM: 02CB-02EF]
 */
void decrement_coins(uint8_t start_buttons) {
    uint8_t c = 1; // 1 player mode
    if (start_buttons != 2) {
        c = 2; // 2 players mode
    }
    
    state.GameOrAttract = c; // Leave attract mode
    coverage_hit("coin_accepted");
    coverage_hit(c == 2 ? "two_player_game_started" : "one_player_game_started");
    
    extern uint8_t read_dsw0(void);
    uint8_t dsw = read_dsw0();
    if ((dsw & 0x10) != 0) {
        // 02E0: LD A,C; RLCA; LD C,A
        c *= 2;
    }
    
    // 02E3: LD L,$8F
    // 02E5: LD A,(HL)
    // 02E6: SUB C
    state.CoinCount -= c;
    
    // update coins on screen
    mem_write(0x4142, state.CoinCount + 0x20);
}

// game_demo: dode duplicaat-stub verwijderd (11 juli 2026); de levende
// vertaling van GameDemo/$03B0-03FD is check_demo_mode_player_and_alien
// hierboven.

/*
 * Helper for DrawNx2 used in attract mode.
 * Draws N rows of 2 characters.
 * HL points to screen memory, src points to the ROM data (now a
 * literal C array; draw_n_by_2's only 3 callers all use fixed ROM
 * addresses, so its former uint16_t de/prg_mem indexing has been
 * replaced with a direct source pointer).
 * BC is the row offset (usually -33).
 */
static void draw_n_by_2(uint16_t hl, const uint8_t *src, uint8_t rows) {
    for (uint8_t i = 0; i < rows; i++) {
        mem_write(hl, *src++);
        hl++;
        mem_write(hl, *src++);
        hl -= 33; // ADD HL, $FFDF
    }
}

/*
 * Translates DrawScoreAverageTableTiles
 * Draws the character tiles for the score average table.
 * [ASM: 0BCA-0BF1]
 */
void draw_score_average_table_tiles(void) {
    uint16_t hl = 0x42D0;
    mem_write(hl, 0x64); // left part of alien shape #3
    hl -= 33;
    hl++;
    mem_write(hl, 0x65); // right part of alien shape #3

    // Draw4x2 (was 0x0A40)
    draw_n_by_2(0x42F2, phoenix_score_table_tiles_a, 4);

    // Draw6x2 (was 0x3C00)
    draw_n_by_2(0x4B15, phoenix_score_table_tiles_b, 6);

    // Draw2x2 (was 0x0A48, i.e. phoenix_score_table_tiles_a + 8)
    draw_n_by_2(0x4AD8, phoenix_score_table_tiles_a + 8, 2);
}

/*
 * Translates the DrawNx2 chain ($3520-$355D): copies n row-pairs from
 * ROM (de) to screen RAM (hl, stepping by bc after each pair), then
 * blanks a trailing row. Entering at $3540 (Draw3x2) is n=3.
 *
 * de's only 3 real call sites (all in alien_logic.c) are provably
 * bounded to $17B8-$17DB -- two fixed literals ($17D0, $17D6) plus one
 * derived from phoenix_alien_explosion_frames' 5 possible values OR'd
 * with $1700 -- so de indexes phoenix_shield_and_drawnx2_shapes rather
 * than prg_mem directly. (Corrected from an earlier, wrong "genuinely
 * unresolved" assessment that didn't trace img_addr back to its source
 * table.)
 */
void drawNx2(uint16_t de, uint16_t hl, uint16_t bc, int n) {
    for (int i = 0; i < n; i++) {
        mem_write(hl, phoenix_shield_and_drawnx2_shapes[de - 0x17B8]);
        de++;
        hl++;
        mem_write(hl, phoenix_shield_and_drawnx2_shapes[de - 0x17B8]);
        de++;
        hl = (hl + bc) & 0xFFFF;
    }
    mem_write(hl, 0);
    hl++;
    mem_write(hl, 0);
}

void draw_bird_shape_350c(uint8_t entry, uint16_t hl, uint16_t shape);

/*
 * Translates DrawBirdObject
 * Draws (or clips) a bird shape at the position in the bird structure.
 * The original computes a jump into the DrawNx2 chain at $3520-$3557;
 * every 8 bytes of entry offset means one row less to draw.
 * [ASM: 34C0-355D]
 */
void drawbirdobject(uint16_t bird_struct_addr) {
    uint8_t idx = mem_read(bird_struct_addr);
    if (idx == 0) return;

    // 34C4-34CA: LSB of the DrawNx2 entry point ($35xx) from T3EC0
    extern const uint8_t phoenix_bird_draw_entries[0x10];
    uint8_t entry = phoenix_bird_draw_entries[idx];

    uint8_t d = mem_read(bird_struct_addr + 1); // screen MSB
    uint8_t e = mem_read(bird_struct_addr + 2); // screen LSB
    uint8_t frame = mem_read(bird_struct_addr + 3);

    // 34D0-34DD: shape data pointer from the table at $3E00,
    // indexed by (idx*8 + frame) & 0x7E
    uint8_t a = (uint8_t)((uint8_t)(idx << 3) | (idx >> 5)); // RLCA x3
    a = (uint8_t)(a + frame) & 0x7E;
    extern const uint8_t phoenix_bird_shape_pointers[0x80];
    uint16_t shape = (phoenix_bird_shape_pointers[a] << 8)
                    | phoenix_bird_shape_pointers[a + 1];

    // 34DE-350B: clip rows while the bird sticks out above the
    // background top ($4B50); each step: one row less, shape data +2
    if (d == 0x4B && e >= 0x50) {
        uint8_t b = 0x08;
        shape = (shape & 0xFF00) | ((shape + 2) & 0xFF);
        e -= 0x20;
        if (e >= 0x50) {
            b = 0x10;
            shape = (shape & 0xFF00) | ((shape + 2) & 0xFF);
            e -= 0x20;
            if (e >= 0x50) {
                b = 0x18;
                shape = (shape & 0xFF00) | ((shape + 2) & 0xFF);
                e -= 0x20;
            }
        }
        entry += b;
    }

    draw_bird_shape_350c(entry, (d << 8) | e, shape);
}

/*
 * The draw tail of DrawBirdObject, also entered directly by L38A1
 * (bird erase) with its own entry/screen/shape values.
 * [ASM: 350C-355D]
 */
void draw_bird_shape_350c(uint8_t entry, uint16_t hl, uint16_t shape) {
    // 350C-3519: blank two chars at the position, then move up-left
    mem_write(hl, 0);
    hl++;
    mem_write(hl, 0);
    hl = (uint16_t)(hl + 0xFFDF); // ADD HL,-33

    // 3520-3557: DrawNx2 ($3520=7 rows ... $3550=1 row)
    int rows = 7 - (int)((uint8_t)(entry - 0x20) >> 3);
    for (int i = 0; i < rows; i++) {
        mem_write(hl, phoenix_bird_shape_data_byte(shape));
        shape++;
        hl++;
        mem_write(hl, phoenix_bird_shape_data_byte(shape));
        shape++;
        hl = (uint16_t)(hl + 0xFFDF);
    }

    // 3558-355D: blank the row below the shape
    mem_write(hl, 0);
    hl++;
    mem_write(hl, 0);
}

/*
 * Translates L34DE
 * Clip-guard in front of the L350C draw tail, used by the bird erase
 * (L38A1): when the bird's screen address has walked past the end of
 * the background screen into $4B50+ -- the bird-structure area -- the
 * draw is shifted back one row per step (E -= $20, two shape bytes
 * skipped, entry += 8 = one row less) up to three times, so the erase
 * never writes through the bird structs. A previous translation
 * omitted this guard entirely (the l34de stub was empty), so erasing a
 * partially off-screen bird zeroed bytes of a neighbouring bird
 * structure. Found via scripted lockstep vs jphoenix (my_session,
 * record 3659).
 * [ASM: 34DE-350B]
 */
void draw_bird_shape_34de(uint8_t entry, uint16_t screen, uint16_t shape) {
    uint8_t d = (uint8_t)(screen >> 8);
    uint8_t e = (uint8_t)screen;
    if (d == 0x4B && e >= 0x50) {
        uint8_t b = 0x08;
        shape += 2;
        e -= 0x20;
        if (e >= 0x50) {
            b = 0x10;
            shape += 2;
            e -= 0x20;
            if (e >= 0x50) {
                b = 0x18;
                shape += 2;
                e -= 0x20;
            }
        }
        entry = (uint8_t)(entry + b);
    }
    draw_bird_shape_350c(entry, (uint16_t)((d << 8) | e), shape);
}

/*
 * Translates L1EE0
 * [ASM: 1EE0-1EFA]
 */
void l1ee0(void) {
    uint16_t de = 0x433D;
    uint8_t c = 0x1A;
    uint8_t b = 0x00;
    extern uint16_t right_one_column(uint16_t);
    do {
        uint8_t a = mem_read(de);
        a += b;
        b = a;
        de = right_one_column(de);
        c--;
    } while (c != 0);

    // After 26 column steps DE has walked past the screen into ROM
    // ($3FFD); the original anti-piracy checksum deliberately reads that
    // ROM byte so the total sums to 0 for an unmodified copyright line.
    // mem_read already routes <$4000 to prg_mem, matching that.
    uint8_t a = mem_read(de);
    a += b;
    a += 0x27;
    mem_write(0x4389, mem_read(0x4389) + a);
}

void draw_intro_bird_animation_frame(void) {
    uint8_t a = state.Counter98[1];

    uint16_t hl = 0x4B73;
    mem_write(hl, a & 0x07);

    hl--;
    mem_write(hl, 0xEF);

    hl--;
    mem_write(hl, 0x49);

    hl--;

    a = (a & 0xF8) >> 3;
    a += 0x3A;

    uint16_t de = (0x23 << 8) | a;
    mem_write(hl, phoenix_intro_bird_anim_frames[de - 0x233A]);

    drawbirdobject(0x4B70);
    l1ee0();
}
