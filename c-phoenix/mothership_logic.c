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
void mothership_core_hit_check(uint16_t de) {
    clear_foreground(); // 2521 (PUSH/POP DE eromheen)

    // 2525-252B: A = (CounterB9 + $60) rechts-geroteerd
    uint8_t a = (uint8_t)(state.CounterB9 + 0x60);
    a = (uint8_t)((a >> 1) | (a << 7)); // RRCA
    uint8_t b = a;

    // 252C-253C: + ronde-bits; klem op $90 bij carry of >= $90
    uint16_t sum = (uint16_t)(state.LevelAndRound & 0xF0) + b;
    if (sum > 0xFF || (sum & 0xFF) >= 0x90) {
        b = 0x90;
    } else {
        b = (uint8_t)sum;
    }

    // 253D-253F: XOR A (wist carry/half-carry); LD A,B; DAA
    a = b;
    if ((a & 0x0F) > 9) a = (uint8_t)(a + 0x06);
    if ((a >> 4) > 9) a = (uint8_t)(a + 0x60);

    // 2540-2545: $439D = BCD-score, $439E = 00
    state.M439D = a;
    state.M439E = 0x00;

    // 2547-254D: print 4 digits op scherm DE - $5E (alleen E, geen borrow)
    uint16_t screen = (de & 0xFF00) | (uint8_t)((de & 0xFF) - 0x5E);
    print_number(screen, 0x439E, 4);
}
