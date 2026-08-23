#include "alien_logic.h"
#include "utilities.h"
#include "z80_core.h"
#include "phoenix_tables.h"
#include "game_constants.h"
#include <stdio.h>
#include <stdbool.h>

extern PhoenixState state;

// Stubs for external logic routines
extern void update_screen_objects(uint16_t alien_state_addr, uint16_t screen_ram_addr); // L0718
extern void get_screen_ram_address(uint16_t alien_state_addr, uint16_t screen_ram_addr); // L09BA

/*
 * Translates L05EC
 * Initialize alien control states.
 * [ASM: 05EC-05F9]
 */
void init_alien_control_states(void) {
    uint8_t level_pattern = state.LevelAndRound & LEVEL_PATTERN_MASK;
    extern const uint8_t phoenix_alien_control_init_values[0x20];
    uint8_t initial_control_state = phoenix_alien_control_init_values[level_pattern * 2];
    uint8_t initial_control_shape = phoenix_alien_control_init_values[level_pattern * 2 + 1];
    init_alien_control_states_05fa(initial_control_state, initial_control_shape);
}

/*
 * Translates GetAnimationChrs for 'aliens fade in'
 * [ASM: 085A-0871]
 */
uint8_t get_animation_chrs_aliens_fade_in(void) {
    // The ROM selects the reverse tile sequence $6C, $6D, $6E, $6F,
    // $68 from CounterB4's countdown bands.
    uint8_t fade_frames_remaining = state.CounterB4;
    if (fade_frames_remaining >= 0x11) return 0x6C;
    if (fade_frames_remaining >= 0x0D) return 0x6D;
    if (fade_frames_remaining >= 0x09) return 0x6E;
    if (fade_frames_remaining >= 0x05) return 0x6F;
    return 0x68;
}

/*
 * [ASM: 0FD8-0FEF]
 */
static void draw_alien_explosion_frame(uint16_t explosion_state_address) {
    uint8_t frames_remaining = mem_read(explosion_state_address);
    if (frames_remaining == 0) return;

    mem_write(explosion_state_address, frames_remaining - 1); // DEC (HL)

    uint16_t screen_address_bytes = explosion_state_address + 2;
    uint8_t screen_high_byte = mem_read(screen_address_bytes);
    uint8_t screen_low_byte = mem_read(screen_address_bytes + 1);

    uint16_t screen_address = (screen_high_byte << 8) | screen_low_byte;

    screen_address = left_one_column(screen_address);

    uint8_t frame_index = (frames_remaining & 0x0E) >> 1; // RRCA on an already-even value == >>1
    extern const uint8_t phoenix_alien_explosion_frames[0x08];
    uint8_t frame_tile = phoenix_alien_explosion_frames[frame_index];
    uint16_t frame_image_address = ALIEN_EXPLOSION_FRAME_TILE_PAGE | frame_tile;

    // 0FF0: EX DE,HL -- the screen target becomes HL, and the frame source
    // becomes DE for Draw3x2 (L3540, entered via drawNx2 with n=3,
    // BC=$FFDF=-33). The earlier translation instead called
    // draw_image_c_by_b(frame_image_address, screen_address-0x21, 2, 3), which is not what this
    // ASM does at all: there is no "-0x21 to the target" step here, and
    // Draw3x2 draws 3 row-pairs (2 bytes each) stepping HL by BC=-33
    // between pairs, then blanks a trailing pair -- exactly drawNx2(n=3).
    extern void drawNx2(uint16_t de, uint16_t hl, uint16_t bc, int n);
    drawNx2(frame_image_address, screen_address, SCREEN_ROW_PAIR_STEP_BACKWARD_33, 3);
}

/*
 * Translates L37CC
 * Erases the bonus explosion animation once its counter reaches zero,
 * by blanking a full column (26 rows) of the foreground.
 * [ASM: 37CC-37E5]
 */
static void erase_bonus_explosion(uint16_t explosion_state_address) {
    uint8_t screen_low_byte = mem_read(explosion_state_address + 3);
    screen_low_byte = (uint8_t)((screen_low_byte & 0x1F) + 0x20);
    uint16_t screen_address = (uint16_t)(FOREGROUND_COLUMN_ADDRESS_BASE | screen_low_byte);

    for (uint8_t rows_remaining = 0x1A; rows_remaining != 0; rows_remaining--) {
        mem_write(screen_address, 0);
        screen_address++;
        mem_write(screen_address, 0);
        screen_address = (uint16_t)(screen_address + SCREEN_ROW_PAIR_STEP_BACKWARD_33); // ADD HL,BC (-33)
    }
}

/*
 * Translates L3796
 * Draws the left part of the bonus explosion animation.
 * [ASM: 3796-37AA]
 */
static void draw_bonus_explosion_left(uint8_t frame_offset, uint16_t screen_address) {
    extern void drawNx2(uint16_t de, uint16_t hl, uint16_t bc, int n);

    uint16_t left_half_address = (uint16_t)(((uint16_t)frame_offset + 0x60) + screen_address);
    if ((uint32_t)left_half_address + 0xBCC0 > 0xFFFF) return; // RET C: out of range, skip

    drawNx2(BONUS_EXPLOSION_LEFT_IMAGE_ADDRESS, left_half_address, SCREEN_ROW_PAIR_STEP_BACKWARD_33, 3); // Draw3x2, left part
}

/*
 * Translates the tail of L3758 (3772-3792)
 * Draws the right part of the bonus explosion animation.
 * [ASM: 3772-3792]
 */
static void draw_bonus_explosion_right(uint8_t frame_offset, uint16_t screen_address) {
    extern void drawNx2(uint16_t de, uint16_t hl, uint16_t bc, int n);

    uint16_t right_half_address = (uint16_t)(screen_address - frame_offset);
    if ((uint32_t)right_half_address + 0xBFA0 <= 0xFFFF) return; // RET NC: out of range, skip

    mem_write(right_half_address, 0);
    right_half_address++;
    mem_write(right_half_address, 0);
    right_half_address = (uint16_t)(right_half_address + SCREEN_ROW_PAIR_STEP_BACKWARD_33); // ADD HL,BC (-33)

    drawNx2(BONUS_EXPLOSION_RIGHT_IMAGE_ADDRESS, right_half_address, SCREEN_ROW_PAIR_STEP_BACKWARD_33, 3); // Draw3x2, right part
}

/*
 * Translates L37B0
 * Prints the score value in the middle of the bonus explosion
 * animation. The first two digits come from the stored score byte;
 * the last digit is always '0'.
 * [ASM: 37B0-37C6]
 */
static void print_bonus_explosion_score(uint16_t explosion_state_address) {
    extern uint16_t left_one_column(uint16_t de);
    extern uint16_t right_one_column(uint16_t de);
    extern void print_number(uint16_t screen_addr, uint16_t data_addr, uint8_t digits);

    uint16_t score_address = explosion_state_address + 1;
    uint8_t score_bcd = mem_read(score_address);
    // DAA: flags coming in are always N=0, H=0, C=0 (from the caller's RRCA)
    if ((score_bcd & 0x0F) > 0x09) score_bcd = (uint8_t)(score_bcd + 0x06);
    if (score_bcd > 0x99) score_bcd = (uint8_t)(score_bcd + 0x60);
    mem_write(score_address, score_bcd);

    uint8_t screen_high_byte = mem_read(explosion_state_address + 2);
    uint8_t screen_low_byte = mem_read(explosion_state_address + 3);
    uint16_t screen_address = (uint16_t)((screen_high_byte << 8) | screen_low_byte);

    screen_address = right_one_column(screen_address);
    if (screen_address >= FOREGROUND_SCREEN_START_ADDRESS
        && screen_address < FOREGROUND_SCREEN_END_ADDRESS) mem_write(screen_address, 0x20); // rightmost digit is always '0'
    screen_address = left_one_column(screen_address);

    print_number(screen_address, score_address, 2);
}

/*
 * Translates L3758
 * Advances the bonus explosion animation for a killed (grown) bird.
 * base is 0x4378 or 0x437C. While the counter is odd, draws the
 * left/right explosion halves; on even counts, prints the score;
 * once it reaches zero, erases the animation.
 * [ASM: 3758-37CC]
 */
static void update_bonus_explosion_animation(uint16_t explosion_state_address) {
    if (mem_read(explosion_state_address) == 0) return;

    mem_write(explosion_state_address, mem_read(explosion_state_address) - 1);
    uint8_t frames_remaining = mem_read(explosion_state_address);
    if (frames_remaining == 0) {
        erase_bonus_explosion(explosion_state_address);
        return;
    }

    if ((frames_remaining & 0x01) == 0) {
        print_bonus_explosion_score(explosion_state_address);
        return;
    }

    uint8_t frame_offset = (uint8_t)(((0x0F - frames_remaining) & 0x0E) << 4);
    uint8_t screen_high_byte = mem_read(explosion_state_address + 2);
    uint8_t screen_low_byte = mem_read(explosion_state_address + 3);
    uint16_t screen_address = (uint16_t)((screen_high_byte << 8) | screen_low_byte);

    draw_bonus_explosion_left(frame_offset, screen_address);
    draw_bonus_explosion_right(frame_offset, screen_address);
}

/*
 * Translates L0FC0
 * Handles explosion animations for killed aliens
 * [ASM: 0FC0-0FFF]
 */
void handle_animations_for_killed_aliens(void) {
    draw_alien_explosion_frame(ALIEN_EXPLOSION_ONE_STATE_ADDRESS);
    draw_alien_explosion_frame(ALIEN_EXPLOSION_TWO_STATE_ADDRESS);
    update_bonus_explosion_animation(BONUS_EXPLOSION_ONE_STATE_ADDRESS);
    update_bonus_explosion_animation(BONUS_EXPLOSION_TWO_STATE_ADDRESS);
}

/*
 * Translates L05FA
 * Initialize alien control states (continuation).
 * [ASM: 05FA-060D]
 */
void init_alien_control_states_05fa(uint8_t initial_control_state, uint8_t initial_control_shape) {
    if (state.AliensLeft == 0) return;
    
    uint16_t alien_state_address = ALIEN_CONTROL_DATA_ADDRESS;
    int alien_count = state.AliensLeft > ALIENS_PER_WAVE ? ALIENS_PER_WAVE : state.AliensLeft;
    for (int alien_index = 0; alien_index < alien_count; alien_index++) {
        mem_write(alien_state_address, initial_control_state);
        mem_write(alien_state_address + 1, initial_control_shape);
        alien_state_address += 4;
    }
}

/*
 * Translates L0610
 * Load alien screen coordinates (X,Y grid), for a new level and round.
 * [ASM: 0610-0638]
 */
void init_alien_positions(void) {
    if (state.AliensLeft == 0) return;
    
    uint8_t formation_index = (state.LevelAndRound >> 1) & LEVEL_PATTERN_MASK;
    uint8_t position_data_offset = phoenix_alien_position_pointer_table[formation_index];

    uint16_t alien_position_address = ALIEN_POSITION_DATA_ADDRESS;

    int alien_count = state.AliensLeft > ALIENS_PER_WAVE ? ALIENS_PER_WAVE : state.AliensLeft;
    for (int alien_index = 0; alien_index < alien_count; alien_index++) {
        mem_write(alien_position_address, phoenix_alien_position_layout_page[position_data_offset]);
        alien_position_address++;
        position_data_offset++;
        mem_write(alien_position_address, phoenix_alien_position_layout_page[position_data_offset]);
        alien_position_address += 3;
        position_data_offset++;
    }
}

/*
 * Translates L0650
 * Copy init values for 16 aliens.
 * [ASM: 0650-0679]
 */
void copy_init_values_for_16_aliens(void) {
    if (state.AliensLeft == 0) return;
    
    uint8_t level_pattern = state.LevelAndRound & LEVEL_PATTERN_MASK;
    extern const uint8_t phoenix_alien_layout_pointers[0x20];
    uint8_t pattern_pointer_high_byte = phoenix_alien_layout_pointers[level_pattern * 2];
    uint8_t pattern_pointer_low_byte  = phoenix_alien_layout_pointers[level_pattern * 2 + 1];
    
    uint16_t alien_pattern_address = ALIEN_PATTERN_TABLE_ADDRESS;

    int alien_count = state.AliensLeft > ALIENS_PER_WAVE ? ALIENS_PER_WAVE : state.AliensLeft;
    for (int alien_index = 0; alien_index < alien_count; alien_index++) {
        mem_write(alien_pattern_address, pattern_pointer_high_byte);
        mem_write(alien_pattern_address + 1, pattern_pointer_low_byte);
        alien_pattern_address += 2;
    }
}

/*
 * Translates L0A50
 * Handle alien control states for all aliens.
 * Loop goes 20 times for 16 aliens. But bit 3 or 4 is not set at
 * UpdateScreenObjects. So luckily no effect.
 * [ASM: 0A50-0A6B]
 */
void alien_data_controller(void) {
    uint16_t bc = ALIEN_CONTROL_DATA_ADDRESS; // alien data structure (grid)
    uint16_t de = ALIEN_SCREEN_DATA_ADDRESS; // alien data structure (screen ram)
    
    for (int i = 0; i < 20; i++) {
        update_screen_objects(bc, de);
        bc += 4;
        de += 4;
    }
}

/*
 * Translates L0A6C
 * Get screen ram adress for all aliens.
 * [ASM: 0A6C-0A99]
 */
void get_screen_ram_address_for_all_aliens(void) {
    uint16_t bc = ALIEN_CONTROL_DATA_ADDRESS; // data structure for alien control and screen coordinate
    uint16_t de = ALIEN_SCREEN_DATA_ADDRESS + 3; // data structure for alien screen ram address
    
    for (int i = 0; i < 20; i++) {
        // Read the alien control state byte
        uint8_t a = mem_read(bc);

        if ((a & 0x18) != 0) { // mask out 0001_1000
            // The following simulates the history shift:
            // LD D,(HL) where HL=alien screen address byte 3
            // DEC HL
            // LD E,(HL) where HL=alien screen address byte 2
            // DEC HL
            // LD (HL),D where HL=alien screen address byte 1
            // DEC HL
            // LD (HL),E where HL=alien screen address byte 0

            uint8_t d = mem_read(de);
            uint8_t e = mem_read(de - 1);
            mem_write(de - 2, d);
            mem_write(de - 3, e);

            // INC DE, INC DE, INC BC, INC BC -> DE+2, BC+2
            // CALL L09BA
            get_screen_ram_address(bc + 2, de - 1); // 4BB3 - 1 = 4BB2
        }
        bc += 4;
        de += 4;
    }
}

// spiral_fill_animation: dode duplicaat-stub verwijderd (11 juli 2026);
// de levende vertaling van L2230/$2230-225F is level_4_6_8_spiral_fill
// in state_play.c.

// l0c00_bonus_explosion_scoring: dode duplicaat-stub verwijderd
// (11 juli 2026); de levende vertaling van L0C00/$0C00-0C23 is
// l0c00_kill_score.

/*
 * Translates L0D1C
 * Alien movement update.
 * [ASM: 0D1C-0D67]
 */
void alien_movement_update(void) {
    for (int i = 0; i < 16; i++) {
    uint16_t ptr_addr = ALIEN_PATTERN_TABLE_ADDRESS + i * 2; // pattern pointer, MSB:LSB
    uint16_t grid = ALIEN_CONTROL_DATA_ADDRESS + i * 4;     // control A, B, X, Y

        // 0D32-0D37: only aliens with bit 3 of control state A set
        if ((mem_read(grid) & 0x08) == 0) continue;

        // 0D30/0D38: pattern pointer is stored big-endian (4B50=MSB)
        uint16_t pattern = (mem_read(ptr_addr) << 8) | mem_read(ptr_addr + 1);
        uint8_t idx = phoenix_alien_movement_byte(pattern);

        // 0D3B-0D3F: T1700 lookup stays within the $17xx page (L=A)
        uint8_t l = (uint8_t)((idx << 1) | (idx >> 7)); // RLCA
        extern const uint8_t phoenix_alien_direction_vectors[0x40];
        uint8_t dir = l;

        uint8_t xd = phoenix_alien_direction_vectors[dir];
        uint8_t a; // last updated coordinate, as in register A
        if (xd == 0) {
            // 0D43 -> 0D4F: no X movement, Y only
            a = (uint8_t)(mem_read(grid + 3) + phoenix_alien_direction_vectors[dir + 1]);
            mem_write(grid + 3, a);
        } else if (phoenix_alien_direction_vectors[dir + 1] == 0) {
            // 0D48 -> 0D5E: X movement only
            a = (uint8_t)(mem_read(grid + 2) + xd);
            mem_write(grid + 2, a);
        } else {
            // 0D4B-0D53: X then Y
            mem_write(grid + 2, mem_read(grid + 2) + xd);
            a = (uint8_t)(mem_read(grid + 3) + phoenix_alien_direction_vectors[dir + 1]);
            mem_write(grid + 3, a);
        }

        // 0D55-0D59 / 0D62-0D66: advance the movement list pointer (LSB)
        // when the last updated coordinate crosses an 8-pixel grid border
        if ((a & 0x07) == 0) {
            mem_write(ptr_addr + 1, mem_read(ptr_addr + 1) + 1);
        }
    }
}

/*
 * Translates L0D70
 * Alien animation update.
 * [ASM: 0D70-0DB5] and [ASM: 0DBB-0DC6] and [ASM: 0DCC-0DEE]
 */
void alien_animation_update(void) {
    uint16_t bc = ALIEN_CONTROL_DATA_ADDRESS; // Alien control state A
    uint16_t hl = ALIEN_PATTERN_TABLE_ADDRESS; // Alien movement pattern table

    for (int i = 0; i < 16; i++) {
        uint8_t d = mem_read(hl);
        hl++;
        uint8_t e = mem_read(hl);
        hl++;

        uint8_t ctrl_a = mem_read(bc);
        // 0D8A-0D8D: AND $08 / RET Z -- only bit 3 gates the animation
        if (ctrl_a & 0x08) {
            // 0D86/0D88: pattern pointer is big-endian (4B50=MSB, 4B51=LSB)
            uint16_t pattern_ptr = (d << 8) | e;

            uint8_t list_index = phoenix_alien_movement_byte(pattern_ptr);

            if (list_index == 0) {
                // L0DDE
                uint16_t orig_de = hl - 2;
                uint8_t m4394 = state.M4394;
                mem_write(orig_de, m4394); // MSB
                uint8_t m4395 = state.M4395;
                mem_write(orig_de + 1, m4395); // LSB

                pattern_ptr = (m4394 << 8) | m4395;
                list_index = phoenix_alien_movement_byte(pattern_ptr);
            }

            extern const uint8_t phoenix_alien_shape_offset_page[0x100];
            uint16_t anim_offset = 0xA0 + (list_index * 3);
            uint8_t anim_byte1 = phoenix_alien_shape_offset_page[anim_offset];
            mem_write(bc, (ctrl_a & 0xF8) | anim_byte1); // set new control state A

            uint8_t anim_byte2 = phoenix_alien_shape_offset_page[anim_offset + 1];
            uint8_t anim_byte3 = phoenix_alien_shape_offset_page[anim_offset + 2];

            uint8_t res_a;
            if (anim_byte2 & 0x01) {
                // L0DBB
                uint8_t y = mem_read(bc + 3);
                y = (y >> 1) & 0x03;
                y += anim_byte3;
                uint8_t x = mem_read(bc + 2);
                x &= 0x04;
                res_a = x + y;
            } else if (anim_byte2 & 0x02) {
                // L0DCC
                uint8_t x = mem_read(bc + 2);
                x = (x >> 1) & 0x03;
                res_a = x + anim_byte3;
            } else {
                // anim_byte2 == 0x04
                uint8_t y = mem_read(bc + 3);
                y = (y >> 1) & 0x03;
                res_a = y + anim_byte3;
            }

            // L0DD2
            uint8_t t1600_val = phoenix_alien_shape_offset_page[res_a];
            mem_write(bc + 1, t1600_val); // set control state B
        }

        // Loop increment: C += 4
        bc = (bc & 0xFF00) | (((bc & 0xFF) + 4) & 0xFF);
    }
}

/*
 * Translates L3264
 * Rotate the alien movement start-value pointer LSB (0..15) and, every
 * time $4350 reaches 5, retarget all aliens still running the old
 * pattern (M4394:old LSB) to the new pattern (M4351:M4352) in the
 * pattern pointer table at $4B50-$4B6F.
 * [ASM: 3264-32AF]
 */
void l3264(void) {
    // 3264-326E: save old LSB in M4356, advance LSB modulo 16
    uint8_t old_lsb = state.M4395;
    state.M4356 = old_lsb;
    state.M4395 = (old_lsb + 1) & 0x0F;

    // 326F-3275: only continue every 5th time
    if (state.M4350 < 5) return;
    state.M4350 = 0;

    // 3277-328E: HL = 4B00|M4354, C pairs to scan, B pairs until wrap
    uint8_t c = state.M4353;
    uint8_t l = state.M4354;
    uint8_t d = state.M4356;   // old pattern LSB
    uint8_t e = state.M4394;   // pattern MSB
    uint8_t b = 0x10 - (uint8_t)((uint8_t)(l - 0x50) >> 1);

    if (c == 0) return; // DEC C on 0 would scan 256 pairs; be safe

    // 328F-32AE
    do {
        uint8_t msb_pos = l;
        uint8_t msb = mem_read(ALIEN_RUNTIME_DATA_PAGE | l);
        l++;
        uint8_t lsb = mem_read(ALIEN_RUNTIME_DATA_PAGE | l);
        if (msb == e && lsb == d) {
            mem_write(ALIEN_RUNTIME_DATA_PAGE | msb_pos, state.M4351);
            mem_write(ALIEN_RUNTIME_DATA_PAGE | l, state.M4352);
        }
        l++;
        b--;
        if (b == 0) l = 0x50; // wrap back to $4B50
        c--;
    } while (c != 0);
}

/*
 * Translates L3074
 * Difficulty value for the breakout scheduler: higher levels and fewer
 * aliens give a smaller value (faster breakouts), plus a random 0-7.
 * [ASM: 3074-30A8]
 */
static uint8_t l3074_breakout_delay(void) {
    extern uint8_t get_random_number(void);
    uint8_t lvl = state.LevelAndRound;

    // 3077-3080: C = 7 - (level bits 1-3)
    uint8_t c = (uint8_t)(7 - ((lvl >> 1) & 0x07));

    // 3081-3094: C += 7 - (round nibble, capped at $70 for rounds >= 8)
    uint8_t a = (lvl >= 0x80) ? 0x70 : lvl;
    c = (uint8_t)(c + 7 - ((a >> 4) & 0x07));

    // 3095-30A0: C += AliensLeft - 5, or $10 when fewer than 5 left
    a = state.AliensLeft;
    c = (uint8_t)(c + ((a < 5) ? 0x10 : (uint8_t)(a - 5)));

    // 30A1-30A7: C += random 0-7
    return (uint8_t)(c + (get_random_number() & 0x07));
}

/*
 * Translates L3028 (l3000 dispatch when Counter93 & 7 == 1)
 * Breakout scheduler: counts down M4358 and, when it expires, arms the
 * pattern retargeting that L3264 performs (M4350=4; scan all 16 pattern
 * pointers at $4B50; new pattern MSB M4351=$2E, LSB M4352 depending on
 * the player X parity). At most 3 aliens (M4357) fly out per wave pass.
 * [ASM: 3028-3059] and [ASM: 305C-306D]
 */
void l3028(void) {
    if (state.M4357 >= 3) return;
    if (state.M4350 >= 4) return;

    if (state.M4358 != 0) {
        // 303C-3059: countdown; on expiry arm the retarget pass
        state.M4358--;
        if (state.M4358 != 0) return;
        state.M4357++;
        state.M4350 = 0x04;
        state.M4353 = 0x10;
        state.M4354 = 0x50;
        state.M4351 = 0x2E;
        state.M4352 = 0x00;
        // 3052-3057: RRCA / RET C -- odd player X keeps M4352 at 0
        if ((state.PlayerShipX & 0x01) == 0) {
            state.M4352 = 0x40;
        }
        return;
    }

    // 305C-306D: schedule the next countdown
    uint8_t c = l3074_breakout_delay();
    uint8_t a = state.M4357;
    a = (uint8_t)((a << 2) | (a >> 6)); // RLCA x2
    state.M4358 = (uint8_t)(a + c + 0x07);
}

/*
 * Translates L30BA (l3000 dispatch when Counter93 & 7 == 2)
 * Bomb-drop scheduler. M4359-M435B are three per-bomb countdown slots;
 * M4355 delays arming M4350=1 (which triggers the actual drop pass).
 * [ASM: 30BA-30D8] and [ASM: 30E4-310F] and [ASM: 3112-3121]
 */
void l30ba(void) {
    // 30BD-30C5 (L30DA x3): tick down the nonzero bomb timers
    if (state.M4359 != 0) state.M4359--;
    if (state.M435A != 0) state.M435A--;
    if (state.M435B != 0) state.M435B--;

    // 30C6-30CA: nothing to schedule while a pass is armed
    if (state.M4350 != 0) return;

    if (state.M4355 != 0) {
        // 30D2-30D8: countdown; on expiry arm the drop pass
        state.M4355--;
        if (state.M4355 != 0) return;
        state.M4350 = 0x01;
        return;
    }

    // L30E4: compute the next delay
    uint8_t c = l3074_breakout_delay();
    uint8_t a = state.Counter9A;
    if (a >= 0x10) a = 0x0F;
    c = (uint8_t)(c + 0x0F - a);

    // L3112 x3: give the first free timer slot 0x0C; each free slot
    // seen halves the delay value
    uint8_t b = 1;
    uint8_t* slots[3] = { &state.M4359, &state.M435A, &state.M435B };
    for (int i = 0; i < 3; i++) {
        if (*slots[i] != 0) continue;
        c >>= 1; // RRCA; AND $7F
        if (b == 0) continue;
        b--;
        *slots[i] = 0x0C;
    }

    // 3105-310F
    state.M4355 = (uint8_t)(((c >> 2) & 0x3F) + 1);
}

/*
 * Translates L3124 (l3000 dispatch when Counter93 & 7 == 3)
 * Phase 1 -> 2 of the pattern retarget: decide how many pattern pairs
 * (M4353) the scan in L3264 may touch, based on the round and a random.
 * [ASM: 3124-314E]
 */
void l3124(void) {
    extern uint8_t get_random_number(void);
    if (state.M4350 != 1) return;
    state.M4350 = 0x02;

    // 312D-313B: 5 + round nibble, capped back to 5 at 0x11
    uint8_t a = (uint8_t)(((state.LevelAndRound >> 2) & 0x0F) + 5);
    if (a >= 0x11) a = 0x05;

    uint8_t b = (uint8_t)(a - state.M4357);
    a = (uint8_t)(get_random_number() + 1);
    if (a >= b) a = 0x01;
    state.M4353 = a;
}

/*
 * Translates L315A + L3192 (l3000 dispatch when Counter93 & 7 == 4)
 * Phase 2 -> 3: starting from a random alien, find the first active
 * alien still on the old pattern (M4394:M4356) and remember its pattern
 * pointer position in M4354.
 * [ASM: 315A-318E] and [ASM: 3192-31AD]
 */
void l315a(void) {
    extern uint8_t get_random_number(void);
    if (state.M4350 != 2) return;

    uint8_t rnd = get_random_number();          // 0-15
    uint8_t l = (uint8_t)(rnd * 2 + 0x50);
    uint8_t e = (uint8_t)(rnd * 4 + 0x70);
    uint8_t b = (uint8_t)(0x10 - rnd);          // pairs until wrap

    for (int c = 0x10; c > 0; c--) {
        // L3192
        if (mem_read(ALIEN_RUNTIME_DATA_PAGE | e) & 0x08) {
            if (state.M4394 == mem_read(ALIEN_RUNTIME_DATA_PAGE | l) &&
                state.M4356 == mem_read(ALIEN_RUNTIME_DATA_PAGE | (uint8_t)(l + 1))) {
                state.M4354 = l;
                state.M4350 = 0x03;
                return; // 31AC: POP HL / RET -- leaves the whole scan
            }
        }
        e += 4;
        l += 2;
        b--;
        if (b == 0) { e = 0x70; l = 0x50; }     // wrap to alien 0
    }
}

/*
 * Translates L31B4 + L3210 (l3000 dispatch when Counter93 & 7 == 5)
 * Phase 3 -> 5: pick the new closed-loop movement pattern for the
 * selected alien from the T3300/T3310/T3330 tables, based on its
 * distance/side relative to the player, its height band and a random.
 * [ASM: 31B4-320D] and [ASM: 3210-3228]
 */
void l31b4(void) {
    extern uint8_t get_random_number(void);
    if (state.M4350 != 3) return;

    // 31BA-31C7: grid X/Y of the alien selected by L315A
    uint8_t l = (uint8_t)(((uint8_t)(state.M4354 - 0x50) << 1) + 0x72);
    uint8_t ax = mem_read(ALIEN_RUNTIME_DATA_PAGE | l);
    uint8_t ay = mem_read(ALIEN_RUNTIME_DATA_PAGE | (uint8_t)(l + 1));

    // 31C8-31D6: distance to the player; C=4 when the player is right
    uint8_t a = state.PlayerShipX;
    uint8_t c, diff;
    if (a >= ax) { c = 4; diff = (uint8_t)(a - ax); }
    else         { c = 0; diff = (uint8_t)(ax - a); }

    // 31D7-31E1: T3300 lookup on the distance band (32-pixel steps)
    extern const uint8_t phoenix_alien_distance_bands[0x08];
    uint8_t t = phoenix_alien_distance_bands[(diff >> 5) & 0x07];

    // 31E2-31E5: C = rotate-left-2 of (band value + side)
    a = (uint8_t)(t + c);
    c = (uint8_t)((a << 2) | (a >> 6));

    // 31E9-31EC + L3210: B from M4357, or the alien height band when
    // only one pattern pair is in play (M4353 == 1)
    uint8_t b = state.M4357;
    if (state.M4353 == 1) {
        if (ay < 0x58)      b = 0;
        else if (ay < 0x78) b = 1;
        else if (ay < 0x98) b = 2;
        else                b = 3;
    }

    // 31F0-31F7: T3310 lookup
    extern const uint8_t phoenix_alien_pattern_selectors[0x20];
    uint8_t lsb = (uint8_t)(c + b + 0x10);
    c = phoenix_alien_pattern_selectors[lsb - 0x10];

    // 31F8-3203: random entry from the closed-loop base table T3330
    extern const uint8_t phoenix_alien_closed_loop_pointers[0xD0];
    lsb = (uint8_t)((get_random_number() & 0x06) + c);
    uint8_t msb_new = phoenix_alien_closed_loop_pointers[lsb - 0x30];
    uint8_t lsb_new = phoenix_alien_closed_loop_pointers[(uint8_t)(lsb + 1) - 0x30];

    // 3204-320D: phase 5, publish the new pattern for L3264
    state.M4350 = 0x05;
    state.M4351 = msb_new;
    state.M4352 = lsb_new;
}

/*
 * Translates L322C (l3000 dispatch when Counter93 & 7 == 6)
 * Phase 4 -> 6: only when every active alien runs exactly the pattern
 * (M4394:M4356) does the pass advance; any deviating alien aborts.
 * [ASM: 322C-325E]
 */
void l322c(void) {
    if (state.M4350 != 4) return;

    uint8_t b = state.M4394;
    uint8_t c = state.M4356;
    for (int i = 0; i < 16; i++) {
        if (mem_read(ALIEN_CONTROL_DATA_ADDRESS + i * 4) & 0x08) {
            if (mem_read(ALIEN_PATTERN_TABLE_ADDRESS + i * 2) != b) return;
            if (mem_read(ALIEN_PATTERN_TABLE_ADDRESS + 1 + i * 2) != c) return;
        }
    }
    state.M4350 = 0x06;
}

/*
 * Translates L2596
 * Per-candidate check for an alien dive-bomb trigger: is this alien
 * slot active, within the right shape range, and within the player's
 * position window? On success falls through to L25B7 to claim an
 * enemy bullet slot.
 * Returns true once L25B7 is reached (regardless of whether a free
 * bullet slot was actually found there) -- in the original this is a
 * fallthrough into a routine whose double-POP trampoline unconditionally
 * aborts the caller's (L2560's) scan.
 * [ASM: 2596-25B6]
 */
static bool l2596(uint16_t hl, uint8_t b, uint8_t c, uint8_t d) {
    uint8_t a = mem_read(hl);
    if ((a & 0x08) == 0) return false;

    hl++;
    a = mem_read(hl);
    if (a == 0x08) return false;
    if (a >= 0x88) return false;

    hl++;
    a = mem_read(hl);
    if (a < b) return false;
    if (a >= c) return false;

    hl++;
    a = mem_read(hl);
    if (a >= d) return false;
    if (a < 0x80) return false;

    uint8_t new_c = a;
    uint8_t new_b = mem_read(hl - 1);

    extern void l25b7(uint8_t b, uint8_t c);
    l25b7(new_b, new_c);
    return true;
}

/*
 * Translates L2560
 * Scans 8 alien candidates (bird0/bird1-style 4-byte-stride records,
 * base $4B70 or $4B90 depending on Counter93 bit 0) for a dive-bomb
 * trigger. Stops at the first candidate that reaches L25B7.
 * [ASM: 2560-2595]
 */
void l2560(void) {
    uint8_t a = (uint8_t)(state.Counter93 & 0x01);
    a = (uint8_t)(a << 5); // RLCA x5 on a 0/1 value: safe as a shift
    a = (uint8_t)(a + 0x70);
    uint16_t hl = (uint16_t)(ALIEN_RUNTIME_DATA_PAGE | a);

    a = (uint8_t)(state.M4357 << 3); // RLCA x3; M4357 is bounds-checked <3 elsewhere
    uint8_t d = (uint8_t)(a + 0xAD);

    uint8_t c = (uint8_t)(state.M439F + 0x03);
    uint8_t b = (uint8_t)(state.M439E - 0x0A);

    for (uint8_t e = 0x08; e != 0; e--) {
        if (l2596(hl, b, c, d)) return;
        hl += 4;
    }
}
