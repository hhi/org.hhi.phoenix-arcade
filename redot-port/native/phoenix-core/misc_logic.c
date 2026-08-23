#include "phoenix_state.h"
#include "phoenix_tables.h"
#include "z80_core.h"
#include "game_constants.h"
#include <string.h>

extern PhoenixState state;

/*
 * [ASM: 06F0-0701]
 * Proposed C name: update_scroll_register_and_fill_background
 */
void l06f0(void) {
    extern void stars_scroll_down(void);
    stars_scroll_down();
    extern void add_galaxies_to_background(void);
    add_galaxies_to_background();
    extern void add_planets_to_background(void);
    add_planets_to_background();
}

/*
 * [ASM: 01E1-01EB]
 */
void l01e1(void) {
    extern void clear_foreground(void);
    extern void clear_background(void);
    clear_foreground();
    clear_background();
    extern void print_text_lines(uint16_t addr, uint8_t count);
    print_text_lines(0x1960, 3);
}

/*
 * Translates L24A0
 * [ASM: 24A0-24BB]
 */
void l24a0(void) {
    if ((state.LevelAndRound & LEVEL_PATTERN_MASK) < LEVEL_PATTERN_BIRDS_SPIRAL_8) return;
    extern void l2351_mothership_animation(uint16_t de, uint16_t hl);
    l2351_mothership_animation(0x43C4, 0x43E6);
    if ((state.Counter9B & 0x03) != 0x03) return;
    extern void l24f2(void);
    l24f2();
}

/*
 * Translates L24F2
 * Random enemy bomb-drop trigger: a random X position (get_random_number
 * + 0x60), gated by a ~1-in-8 chance against Counter9B, fires an enemy
 * bullet at the player's current position when that random X falls
 * within the player ship's width.
 * [ASM: 24F2-251C]
 * Proposed C name: trigger_random_enemy_bomb_drop
 */
void l24f2(void) {
    extern uint8_t get_random_number(void);
    uint8_t candidate_bomb_x = (uint8_t)(get_random_number() + 0x60);
    if ((candidate_bomb_x & 0x0E) & state.Counter9B) return;
    if (state.M439E >= candidate_bomb_x) return;
    if (state.M439F < candidate_bomb_x) return;

    uint8_t bomb_x = (uint8_t)(candidate_bomb_x - 0x04);
    uint8_t neg_counter_b9 = (uint8_t)(0 - state.CounterB9);
    uint8_t bomb_y = (uint8_t)((neg_counter_b9 & 0xF8) + 0x48);

    extern void l25b7(uint8_t b, uint8_t c);
    l25b7(bomb_x, bomb_y);
}

/*
 * [ASM: 32B0-32EB]
 */
void l32b0(void) {
    memset(&state.M4350, 0, 0x30); // 4350 to 437F
    memset(&state.Counter9A, 0, 4); // 439A to 439D
    
    if (state.BirdsLeft == 0) return;
    
    uint8_t bird_data_byte_count = state.BirdsLeft << 3;
    memset(&state.B4B70, 0, 0x40); // B4B70 to B4BAF
    
    uint16_t bird_data_source_address = 0x3F00 | (0x40 - bird_data_byte_count + 0x70 + 0x10);
    uint16_t bird_data_destination_address = 0x4B00 | (0x40 - bird_data_byte_count + 0x70);
    
    // 32DE-32E3: RRCA x2 / JP NC -- the carry after the second RRCA is
    // bit 1 of LevelAndRound; set -> use the second table at +0x40
    if (state.LevelAndRound & 0x02) {
        bird_data_source_address += 0x40;
    }
    for (uint8_t byte_index = 0; byte_index < bird_data_byte_count; byte_index++) {
        uint16_t source_address = bird_data_source_address + byte_index;
        uint8_t bird_data_byte = (source_address >= 0x3F80)
            ? phoenix_bird_data_alt_page[source_address - 0x3F80]
            : phoenix_bird_behaviour_scripts[source_address - 0x3F00];
        mem_write(bird_data_destination_address + byte_index, bird_data_byte);
    }
}
