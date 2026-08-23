#include "bird_logic.h"
#include "z80_core.h"
#include "coverage.h"
#include "phoenix_tables.h"
#include <stdint.h>
#include <stdio.h>

extern PhoenixState state;

extern void draw_bird_shape_350c(uint8_t entry, uint16_t hl, uint16_t shape);

/*
 * Translates L38A1
 * Erase a hit bird from the background: draws the empty 4x4 shape.
 * The shape address is formed from the letter 'R' of the on-ROM
 * " AMSTAR ELECTRONICS CORP. " copyright text -- another piracy trap:
 * change that letter and dead birds leave garbage on screen.
 * [ASM: 38A1-38B5]
 */
static void erase_hit_bird(uint16_t bird_state_address) {
    uint8_t bird_screen_high_byte = mem_read(bird_state_address + 1);
    uint8_t bird_screen_low_byte  = mem_read(bird_state_address + 2);
    // 38A9-38AF: 'R' ($12) + $DE = $F0 -> $17F0, the FourByFourEmpty shape
    extern const uint8_t phoenix_bird_erase_shape_selector;
    uint8_t empty_shape_low_byte = (uint8_t)(phoenix_bird_erase_shape_selector + 0xDE);
    // 38B1: CALL $34DE -- the clip-guarded entry, NOT the bare $350C tail
    extern void draw_bird_shape_34de(uint8_t entry, uint16_t screen, uint16_t shape);
    uint16_t bird_screen_address = (bird_screen_high_byte << 8) | bird_screen_low_byte;
    draw_bird_shape_34de(0x20, bird_screen_address, 0x1700 | empty_shape_low_byte);
}

/*
 * Translates L38F8/L38FB/L3906
 * Store a bird explosion in a free slot pair. Normal kills enter at
 * $38F8 (slots $4370/$4374); bonus kills enter at $38FB with HL already
 * on $4378 (slots $4378/$437C).
 * [ASM: 38F8-391B]
 */
static void queue_bird_explosion(uint16_t explosion_slot_address, uint8_t animation_counter, uint8_t score) {
    if (mem_read(explosion_slot_address) != 0) {
        explosion_slot_address += 4;
        if (mem_read(explosion_slot_address) != 0) return; // both slots busy
    }
    mem_write(explosion_slot_address, animation_counter);
    mem_write(explosion_slot_address + 1, score);
    mem_write(explosion_slot_address + 2, state.PlayerBulletMSB);
    mem_write(explosion_slot_address + 3, state.PlayerBulletLSB);
    state.PlayerBulletState &= 0xF7; // bullet is used up
}

/*
 * Translates L3844 (small bird tiles, tile-$90 < $50)
 * Returns 1 when the bird was killed (the original pops the return
 * address and returns straight to L3800's caller).
 * [ASM: 3844-388D] and [ASM: 3894-389C]
 */
static uint8_t check_small_bird_hit(uint8_t bird_tile_index, uint8_t bullet_pixel_mask, uint16_t bird_state_address) {
    // 3844-384B: pixel mask from T3B60
    if ((phoenix_bird_hitmask_page[(uint8_t)(bird_tile_index + 0x60)] & bullet_pixel_mask) == 0) return 0;
    coverage_hit("small_bird_hit");

    erase_hit_bird(bird_state_address);

    // 384F-3857: take the bird type, clear the struct entry
    uint8_t bird_type = mem_read(bird_state_address);
    mem_write(bird_state_address, 0);
    uint8_t bird_height = mem_read(bird_state_address + 4);

    state.BirdsLeft--;

    if (bird_type < 0x0B) {
        // L3894: plain bird, score 050
        state.M4364 = 0xFF;
        queue_bird_explosion(0x4370, 0x0D, 0x05);
        return 1;
    }

    // 3862-388D: grown bird, bonus explosion; score depends on type and
    // the height byte at struct+4
    state.M4369 = 0xFF;
    coverage_hit("grown_bird_bonus_explosion");
    uint8_t score = 0x10; // score 100 nibble pair (B=0x10, C=0x10)
    if (bird_type != 0x0F) {
        score = (uint8_t)(((bird_height >> 1) & 0x7C) + 0x30);
        if (bird_type != 0x0E) {
            score >>= 1;
            if (bird_type < 0x0C) score >>= 1;
        }
    }
    queue_bird_explosion(0x4378, 0x10, score);
    return 1;
}

/*
 * Translates L38BC (large tiles, tile-$90 >= $20: eggs and grown birds)
 * An egg (type $0B/$0C) transforms into a bird via table T3DB8 instead
 * of dying.
 * [ASM: 38BC-38F1]
 */
static uint8_t check_large_bird_or_egg_hit(uint8_t bird_tile_index, uint8_t bullet_pixel_mask, uint16_t bird_state_address) {
    if ((phoenix_bird_hitmask_page[(uint8_t)(bird_tile_index + 0xB0)] & bullet_pixel_mask) == 0) return 0;
    coverage_hit("large_bird_or_egg_hit");

    erase_hit_bird(bird_state_address);

    // 38C7-38E8: egg types transform into a bird type from T3DB8
    uint8_t bird_type = mem_read(bird_state_address);
    uint8_t egg_type_index = (uint8_t)(bird_type - 0x0B);
    if (egg_type_index < 0x03) {
        uint8_t split_x_threshold = mem_read(bird_state_address + 5);
        // 38D8-38DF: CP (HL) sets carry = (PlayerBulletX < threshold);
        // RLA folds that carry into bit0 of PlayerBulletX, then two RLCAs
        // rotate it up to bit2 -- i.e. AND $04 isolates exactly the
        // "PlayerBulletX < threshold" flag, giving side=4 when true.
        uint8_t split_side_index = (state.PlayerBulletX < split_x_threshold) ? 4 : 0;
        uint8_t transformation_index = (uint8_t)(egg_type_index | split_side_index);
        extern const uint8_t phoenix_egg_transformation_types[0x08];
        mem_write(bird_state_address, phoenix_egg_transformation_types[transformation_index]);
    }

    // L38E9
    state.M4366 = 0xFF;
    queue_bird_explosion(0x4370, 0x07, 0x02);
    return 1;
}

/*
 * Translates L3800
 * Player bullet versus bird collision. The bullet position is looked
 * up in the scroll-corrected background; bird tiles start at $90.
 * [ASM: 3800-3841] and [ASM: 391C-3922]
 */
void collision_detection_for_birds(void) {
    coverage_hit("collision_detection_for_birds");
    if ((state.PlayerBulletState & 0x08) == 0) return;

    // 3806-381E: background cell for the bullet, corrected for the
    // vertical scroll position of the bird layer (B4BD2)
    uint8_t background_high_byte = (uint8_t)(state.PlayerBulletMSB + 0x08);
    uint8_t background_low_byte = (uint8_t)(((state.PlayerBulletLSB - state.B4BD2) & 0x1F)
                                           | (state.PlayerBulletLSB & 0xE0));
    uint16_t background_cell_address = (background_high_byte << 8) | background_low_byte;
    // An out-of-range cell reads as 0 via mem_read, which the tile<0x90
    // check just below rejects the same way the old explicit range guard
    // did -- same early exit, one less redundant bound check.
    uint8_t tile = mem_read(background_cell_address);

    // 381F-3822: bird tiles are $90 and up
    if (tile < 0x90) return;
    uint8_t bird_tile_index = (uint8_t)(tile - 0x90);

    // 3824-382E: pixel mask for the bullet X within the cell (T3E00)
    uint8_t bullet_pixel_mask = phoenix_bullet_pixel_masks[state.PlayerBulletX & 0x07];

    // 382F-3839: bird structure address from the cell row
    uint8_t bird_row_offset = (uint8_t)((background_low_byte & 0x0E) << 2);
    uint16_t bird_state_address = 0x4B00 | (uint8_t)(0xA8 - bird_row_offset);

    // 383B-3841 + L391C: small-tile test, then large-tile test
    if (bird_tile_index < 0x50) {
        if (check_small_bird_hit(bird_tile_index, bullet_pixel_mask, bird_state_address)) return;
    }
    if (bird_tile_index >= 0x20) {
        check_large_bird_or_egg_hit(bird_tile_index, bullet_pixel_mask, bird_state_address);
    }
}

/*
 * Translates L3462
 * No birds left: rate-limited (every other call, via Counter9B bit 0)
 * bomb/animation upkeep, then hand off to L2204's shared round-transition
 * countdown (M43B6) -- the same path the alien-wave end (l21ba) uses.
 * [ASM: 3462-346D]
 */
void finish_bird_wave_if_empty(void) {
    coverage_hit("no_birds_left");
    // 3462-3466: LD A,(Counter9B); RRCA; RET C
    if ((state.Counter9B & 0x01) != 0) return;

    extern void process_enemy_bombs(void); // 0C40
    extern void handle_animations_for_killed_aliens(void); // 0FC0
    extern void l2204(void); // 2204
    process_enemy_bombs();
    handle_animations_for_killed_aliens();
    l2204();
}
