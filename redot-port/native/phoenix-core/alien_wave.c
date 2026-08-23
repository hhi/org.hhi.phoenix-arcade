#include "phoenix_state.h"
#include "z80_core.h"
#include "coverage.h"
#include "game_constants.h"
#include <stdint.h>

extern PhoenixState state;

// External function prototypes
extern void player_update(void);
extern void check_enemy_bullet_to_player_collision(void);
extern void l24a0(void);
extern void alien_data_controller(void);
extern void l3000(void);
extern void l0f00_check_alien_with_player_collision(void);
extern void l24c4(void);
extern void process_enemy_bombs(void);
extern void alien_movement_update(void);
extern void handle_animations_for_killed_aliens(void);
extern void alien_animation_update(void);
extern void l2560(void);
extern void get_screen_ram_address_for_all_aliens(void);
extern void clear_foreground(void);
extern void update_scroll_register_and_fill_background(void);

/*
 * [ASM: 24C4-24DF]
 */
void l24c4(void) {
    if ((state.LevelAndRound & LEVEL_PATTERN_MASK) < LEVEL_PATTERN_BIRDS_SPIRAL_8) {
        update_scroll_register_and_fill_background();
        return;
    }
    
    // Inline L24E0
    if ((state.M43AA & 0x0F) == 0 && state.CounterB9 >= 0xA0) {
        extern void stars_scroll_down(void);
        stars_scroll_down();
    }
    
    state.M43AA++;
    if ((state.M43AA & 0x03) == 0) {
        // Inline L22FA
        uint16_t animation_tile_address = 0x4AAA;
        uint8_t previous_tile = mem_read(0x488A);
        for (int row = 0; row < 18; row++) {
            uint8_t low_animation_bits = previous_tile & 0x03;
            low_animation_bits = (low_animation_bits << 2) | (low_animation_bits >> 6); // RLCA twice
            previous_tile = mem_read(animation_tile_address);
            uint8_t high_animation_bits = previous_tile & 0x0C;
            high_animation_bits = (high_animation_bits >> 2) | (high_animation_bits << 6); // RRCA twice [ASM 230D-230E]
            uint8_t animation_tile = high_animation_bits | low_animation_bits | 0x60; // [ASM 2310]
            mem_write(animation_tile_address, animation_tile);
            animation_tile_address -= 0x20; // [ASM 2313-231A: SUB $20 on L, borrow decrements H]
        }
    } else {
        // Inline L2322
        state.AnimationCounter++;
        uint8_t animation_frame = state.AnimationCounter & 0x07;
        animation_frame = (animation_frame << 3) | (animation_frame >> 5); // RLCA 3 times
        animation_frame += 0xC0;
        uint16_t animation_source_address = 0x1B00 | animation_frame;
        extern void draw_image_c_by_b(uint16_t hl, uint16_t de, uint8_t b, uint8_t c);
        draw_image_c_by_b(animation_source_address, 0x49A6, 4, 2); // B=0x04 rows, C=0x02 columns
    }
}

/*
 * Translates L2204
 * Shared round-transition countdown (M43B6).
 * [ASM: 2204-222B]
 * Proposed C name: advance_round_transition
 */
void l2204(void) {
    state.M43B6--;
    if (state.M43B6 >= 0xA0) return;
    
    state.GameState = GAME_STATE_INIT_ROUND;
    state.ShieldCount = 0;
    state.LevelAndRound++;
    
    uint8_t round_population_index = (state.LevelAndRound & 0x0E) >> 1;
    extern const uint8_t phoenix_round_population[0x08];
    uint8_t round_population = phoenix_round_population[round_population_index];
    
    if ((round_population & 0x80) == 0) {
        state.AliensLeft = round_population; // Positive, use AliensLeft
    } else {
        state.BirdsLeft = round_population & 0x7F; // Negative, use BirdsLeft
    }
    
    clear_foreground(); // 0380
}

/*
 * [ASM: 21BA-21CF]
 */
void l21ba(uint8_t masked_counter) {
    // 21BB-21BC: RRCA; JP NC,$2204 -- go straight to the round-transition
    // countdown on an EVEN masked_counter (carry clear after the rotate
    // means bit0 was 0).
    if ((masked_counter & 1) == 0) {
        l2204();
        return;
    }

    process_enemy_bombs(); // L0C40
    handle_animations_for_killed_aliens(); // L0FC0
    l24c4(); // UpdateAlienWaveAudio

    // 21C8-21CF: CP $0B; JP C,$2204 -- every normal sub-level (<0x0B) also
    // advances via L2204. Only the final wave (0x0B, the mothership's
    // escort aliens) skips the transition and just respawns another 16
    // aliens in place -- that wave doesn't end by running out of aliens,
    // it ends when the mothership itself is destroyed.
    if ((state.LevelAndRound & LEVEL_PATTERN_MASK) < LEVEL_PATTERN_ALIENS_ACTIVE_B) {
        l2204();
    } else {
        state.AliensLeft = ALIENS_PER_WAVE;
        extern void l0526(void);
        l0526(); // init alien data
    }
}

/*
 * [ASM: 2150-215F]
 */
void l2150(void) {
    alien_data_controller();
    l3000();
    l0f00_check_alien_with_player_collision();
}

/*
 * [ASM: 2160-216F]
 */
void l2160(void) {
    l24c4();
    process_enemy_bombs();
    alien_movement_update();
    handle_animations_for_killed_aliens();
}

/*
 * [ASM: 2170-217F]
 */
void l2170(void) {
    alien_animation_update();
    l2560();
}

/*
 * [ASM: 2180-218F]
 */
void l2180(void) {
    l24c4();
    process_enemy_bombs();
    get_screen_ram_address_for_all_aliens();
    handle_animations_for_killed_aliens();
}

/*
 * [ASM: 2190-21A4]
 */
void l2190(void) {
    alien_data_controller();
    l3000();
    l0f00_check_alien_with_player_collision();
    l2560();
    process_enemy_bombs();
}

/*
 * [ASM: 21A5-21B9]
 */
void l21a5(void) {
    alien_movement_update();
    alien_animation_update();
    get_screen_ram_address_for_all_aliens();
    handle_animations_for_killed_aliens();
    l24c4();
}

/*
 * [ASM: 2146-214F]
 */
void l2146(uint8_t masked_counter) {
    if ((masked_counter & 1) == 0) {
        l2190();
    } else {
        l21a5();
    }
}

/*
 * Translates L2130
 * [ASM: 2130-2145]
 */
void l2130(uint8_t masked_counter) {
    switch (masked_counter) {
        case 0: l2150(); break;
        case 1: l2160(); break;
        case 2: l2170(); break;
        case 3: l2180(); break;
    }
}

/*
 * Translates L2000
 * Main loop for levels 1, 3, B: player alive with aliens
 * [ASM: 2000-202A]
 */

void l2000_alien_wave_main_loop(void) {
    coverage_hit("l2000_alien_wave_main_loop");
    player_update();
    check_enemy_bullet_to_player_collision();
    l24a0();

    uint8_t masked_counter = state.M435F & 0x03;
    state.M435F++;

    if (state.AliensLeft == 0) {
        l21ba(masked_counter);
        return;
    }

    if (state.AliensLeft >= 5) {
        l2130(masked_counter);
        return;
    }

    if (masked_counter == 0) {
        state.M435E = 0xFF;
    }

    if (state.M435E == 0) {
        l2130(masked_counter);
    } else {
        l2146(masked_counter);
    }
}

/*
 * Translates L3000
 * Breakout/dive-bomb dispatcher via jumptable T3018 (Counter93).
 * [ASM: 3000-3012]
 */
void l3000(void) {
    uint8_t breakout_phase = state.Counter93;
    state.Counter93++;
    breakout_phase &= 0x07;
    switch (breakout_phase) {
        case 0: { extern void l3264(void); l3264(); break; }
        case 1: { extern void l3028(void); l3028(); break; }
        case 2: { extern void l30ba(void); l30ba(); break; }
        case 3: { extern void l3124(void); l3124(); break; }
        case 4: { extern void l315a(void); l315a(); break; }
        case 5: { extern void l31b4(void); l31b4(); break; }
        case 6: { extern void l322c(void); l322c(); break; }
        case 7: { return; }
    }
}
