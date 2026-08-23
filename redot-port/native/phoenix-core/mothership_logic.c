#include "mothership_logic.h"

extern PhoenixState state;

extern void clear_foreground(void);
extern void add_score(uint16_t score_bcd);
extern void print_number(uint16_t screen_addr, uint16_t data_addr, uint8_t digits);
extern void draw_image_c_by_b(uint16_t screen_addr, uint16_t image_addr, uint8_t rows, uint8_t columns);

extern void l2351_mothership_animation(uint16_t de, uint16_t hl);

void mothership_descent_logic(void) {
    // Calls L2351 to process the downward scroll of the mothership and animation
    l2351_mothership_animation(0x43C4, 0x43E6);
}

/*
 * Translates L246A
 * Erase the mothership
 * [ASM: 246A-2475]
 */
void erase_mothership(void) {
    // 246A-2473: BC=$0914 (20 kolommen x 9 rijen), DE=$4AC6 (scherm),
    // HL=$1C00 (sterrenveld-ROM). NB: draw_image_c_by_b(hl=bron,
    // de=scherm, ...) -- een eerdere aanroep had bron en bestemming
    // verwisseld, waardoor elke write een no-op in ROM-gebied was en de
    // mothership nooit echt gewist werd. Gevonden via scripted lockstep
    // (mutated_rank_01_score_3092917, records 11299-11467).
    draw_image_c_by_b(0x1C00, 0x4AC6, 0x09, 0x14);
}

void mothership_barrier_collision(void) {
    // Left empty for now, as it wasn't hooked up anyway.
}

/*
 * Translates L2520
 * Mothership-kern geraakt: bereken de bonus-score uit CounterB9 en de
 * ronde-bits, zet hem als BCD in $439D:$439E en print hem op het
 * scherm (DE - $5E). De optelling bij de spelersscore gebeurt NIET
 * hier maar elke state-6-frame in de L2700-keten
 * (update_scores_and_sound). Een eerdere vertaling verzon een
 * BirdsLeft-berekening, riep add_score() direct aan en printte vanaf
 * ROM $1E00 -- gevonden via scripted lockstep
 * (mutated_rank_01_score_3092917, record 11298).
 * [ASM: 2520-254F]
 */
void mothership_core_hit_check(uint16_t mothership_screen_address) {
    clear_foreground(); // 2521 (PUSH/POP DE eromheen)

    // 2525-252B: A = (CounterB9 + $60) rechts-geroteerd
    uint8_t score_seed = (uint8_t)(state.CounterB9 + 0x60);
    score_seed = (uint8_t)((score_seed >> 1) | (score_seed << 7)); // RRCA

    // 252C-253C: + ronde-bits; klem op $90 bij carry of >= $90
    uint16_t score_sum = (uint16_t)(state.LevelAndRound & 0xF0) + score_seed;
    if (score_sum > 0xFF || (score_sum & 0xFF) >= 0x90) {
        score_seed = 0x90;
    } else {
        score_seed = (uint8_t)score_sum;
    }

    // 253D-253F: XOR A (wist carry/half-carry); LD A,B; DAA
    uint8_t score_bcd = score_seed;
    if ((score_bcd & 0x0F) > 9) score_bcd = (uint8_t)(score_bcd + 0x06);
    if ((score_bcd >> 4) > 9) score_bcd = (uint8_t)(score_bcd + 0x60);

    // 2540-2545: $439D = BCD-score, $439E = 00
    state.M439D = score_bcd;
    state.M439E = 0x00;

    // 2547-254D: print 4 digits op scherm DE - $5E (alleen E, geen borrow)
    uint16_t score_screen_address = (mothership_screen_address & 0xFF00)
                                  | (uint8_t)((mothership_screen_address & 0xFF) - 0x5E);
    print_number(score_screen_address, 0x439E, 4);
}
