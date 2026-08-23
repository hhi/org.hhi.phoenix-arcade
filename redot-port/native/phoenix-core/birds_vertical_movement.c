#include "bird_logic.h"
#include "phoenix_tables.h"
#include "z80_core.h"
#include <stdint.h>

extern void hw_write_scroll_register(uint8_t val);

/*
 * Translates L2668
 * Descent speed (B4BD5) from the difficulty inputs: base M436E, the
 * session counter, aliens left, capped by T3EE0 on the formation
 * height, plus a bonus when few birds remain.
 * [ASM: 2668-26A7]
 */
static void update_bird_descent_speed(void) {
    uint8_t descent_speed = state.M436E;
    if (state.Counter9A >= 0x18) descent_speed++;
    if (state.Counter9A >= 0x10) descent_speed++;
    if (state.AliensLeft < 0x03) descent_speed++;

    uint8_t descent_speed_cap = phoenix_bird_descent_caps[state.B4BD6];
    descent_speed = (descent_speed < descent_speed_cap) ? descent_speed : descent_speed_cap;

    if (state.BirdsLeft < 0x04) descent_speed++;
    if (state.BirdsLeft < 0x02) descent_speed++;
    state.B4BD5 = descent_speed;
}

/*
 * Translates L26D0
 * Scan the eight bird slots from bird 7 down to bird 0: D = first
 * occupied index, E = last occupied index. Publishes the formation
 * position (B4BD6) and height (B4BD7).
 * [ASM: 26D0-26FD]
 */
static void update_bird_formation_extent(void) {
    uint8_t first_occupied_index = 0x80; // sentinel: bit 7 set means "none found yet"
    uint8_t last_occupied_index = 0x00;
    uint8_t bird_state_low_byte = 0xA8;

    for (uint8_t bird_index = 0; bird_index < 8; bird_index++) {
        if (mem_read(0x4B00 | bird_state_low_byte) != 0) {
            if (first_occupied_index & 0x80) first_occupied_index = bird_index; // 26DE-26E3: RLCA / JP NC skips once set
            last_occupied_index = bird_index;
        }
        bird_state_low_byte -= 8;
    }

    state.B4BD6 = (uint8_t)(state.B4BD2 + first_occupied_index + last_occupied_index) & 0x1F;
    state.B4BD7 = (uint8_t)(last_occupied_index - first_occupied_index);
}

/*
 * Translates L26AA + L2476 + L2495
 * Climb scheduling: while the timer (B4BD3) runs it only counts down.
 * Once expired it stays at zero until the formation is in the 8..15
 * band, then arms a new timer and the climb threshold B4BD1.
 * [ASM: 26AA-26CC] and [ASM: 2476-2493] and [ASM: 2495-249F]
 */
static void schedule_next_bird_climb(void) {
    uint8_t previous_climb_timer = state.B4BD3;
    state.B4BD3--;
    if (previous_climb_timer != 0) return; // 26AF-26B0: RET NZ on the pre-decrement value
    state.B4BD3++;        // 26B1: undo, stays zero

    uint8_t formation_position = state.B4BD6;
    if (formation_position >= 0x16) return;
    if (formation_position < 0x08) return;

    // 26BB-26CB. NB: 26BD is RLCA -- een rotate, geen shift: bit 7 van
    // (B4BD6 - B4BD7) roteert naar bit 0. Bij een negatieve delta (>=
    // 0x80) verloor de eerdere shift-vertaling dat bit, waardoor B 1 te
    // laag uitviel en de L2495-keten (c=4-pad: (B+C+3B)*2) de
    // klim-timer B4BD3 exact 8 te laag zette. Gevonden via scripted
    // lockstep (my_session, records 5831-5852).
    uint8_t formation_position_delta = (uint8_t)(formation_position - state.B4BD7);
    uint8_t rotated_position_delta = (uint8_t)((formation_position_delta << 1)
                                                | (formation_position_delta >> 7));
    uint8_t climb_pattern = state.M436F & 0x03;
    state.B4BD4 = climb_pattern;
    uint8_t pattern_repetitions = (uint8_t)(((~climb_pattern) & 0x03) + 1);

    // L2476/L2495: A = B + C, plus B per remaining step; a fourth step
    // doubles instead
    uint8_t next_climb_timer = (uint8_t)(rotated_position_delta + pattern_repetitions);
    next_climb_timer = (uint8_t)(next_climb_timer + rotated_position_delta);
    if (--pattern_repetitions != 0) {
        next_climb_timer = (uint8_t)(next_climb_timer + rotated_position_delta);
        if (--pattern_repetitions != 0) {
            next_climb_timer = (uint8_t)(next_climb_timer + rotated_position_delta);
            if (--pattern_repetitions != 0) {
                next_climb_timer = (uint8_t)(next_climb_timer + next_climb_timer);
            }
        }
    }
    state.B4BD3 = next_climb_timer;

    // 247E-2493: rearm the climb threshold
    uint8_t birds_destroyed = (uint8_t)(0x08 - state.BirdsLeft);
    uint8_t climb_threshold_offset = (uint8_t)((birds_destroyed << 1) + state.Counter9A);
    climb_threshold_offset = (uint8_t)(climb_threshold_offset << 1);
    state.B4BD1 = (uint8_t)((state.M436F & 0x1E) + climb_threshold_offset);
}

/*
 * Translates L2600
 * Vertical movement of the bird layer via the scroll register.
 * Climbs (L2650) while B4BD1 < B4BD3, otherwise descends at the
 * speed in B4BD5. Even frames rescan the formation, odd frames update
 * speed and the climb scheduler.
 * [ASM: 2600-2664]
 */
void birds_vertical_movement_update(void) {
    // 2605-2611: scroll band for the collision code
    state.B4BD2 = (uint8_t)(((uint8_t)~state.CounterB9) >> 3) & 0x1F;

    uint8_t a;
    if (state.B4BD1 < state.B4BD3) {
        // L2650: climb: CounterB9 += T3ED0[(Counter9B*4 & C) + B4BD4]
        uint8_t l = (uint8_t)(((state.Counter9B << 2) & 0x0C)
                              + state.B4BD4 + 0xD0);
        a = (uint8_t)(state.CounterB9 + phoenix_bird_scroll_steps[l & 0x0F]);
    } else {
        // 261A-2638: descend
        uint8_t d = state.B4BD5;
        uint8_t l = (uint8_t)(((state.Counter9B << 2) & 0x0C)
                              + (d & 0x03) + 0xD0);
        d = (uint8_t)(((d >> 2) & 0x07) + phoenix_bird_scroll_steps[l & 0x0F]);
        a = (uint8_t)(state.CounterB9 - d);
    }

    // L2639
    state.CounterB9 = a;
    hw_write_scroll_register(a);

    // 263F-2649: odd frames schedule, even frames rescan
    if (state.Counter9B & 0x01) {
        update_bird_descent_speed();
        schedule_next_bird_climb();
    } else {
        update_bird_formation_extent();
    }
}
