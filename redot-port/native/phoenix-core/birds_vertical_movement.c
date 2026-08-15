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
static void l2668(void) {
    uint8_t b = state.M436E;
    if (state.Counter9A >= 0x18) b++;
    if (state.Counter9A >= 0x10) b++;
    if (state.AliensLeft < 0x03) b++;

    uint8_t cap = phoenix_bird_descent_caps[state.B4BD6];
    uint8_t d = (b < cap) ? b : cap;

    if (state.BirdsLeft < 0x04) d++;
    if (state.BirdsLeft < 0x02) d++;
    state.B4BD5 = d;
}

/*
 * Translates L26D0
 * Scan the eight bird slots from bird 7 down to bird 0: D = first
 * occupied index, E = last occupied index. Publishes the formation
 * position (B4BD6) and height (B4BD7).
 * [ASM: 26D0-26FD]
 */
static void l26d0(void) {
    uint8_t d = 0x80; // sentinel: bit 7 set means "none found yet"
    uint8_t e = 0x00;
    uint8_t l = 0xA8;

    for (uint8_t c = 0; c < 8; c++) {
        if (mem_read(0x4B00 | l) != 0) {
            if (d & 0x80) d = c; // 26DE-26E3: RLCA / JP NC skips once set
            e = c;
        }
        l -= 8;
    }

    state.B4BD6 = (uint8_t)(state.B4BD2 + d + e) & 0x1F;
    state.B4BD7 = (uint8_t)(e - d);
}

/*
 * Translates L26AA + L2476 + L2495
 * Climb scheduling: while the timer (B4BD3) runs it only counts down.
 * Once expired it stays at zero until the formation is in the 8..15
 * band, then arms a new timer and the climb threshold B4BD1.
 * [ASM: 26AA-26CC] and [ASM: 2476-2493] and [ASM: 2495-249F]
 */
static void l26aa(void) {
    uint8_t old = state.B4BD3;
    state.B4BD3--;
    if (old != 0) return; // 26AF-26B0: RET NZ on the pre-decrement value
    state.B4BD3++;        // 26B1: undo, stays zero

    uint8_t h = state.B4BD6;
    if (h >= 0x16) return;
    if (h < 0x08) return;

    // 26BB-26CB. NB: 26BD is RLCA -- een rotate, geen shift: bit 7 van
    // (B4BD6 - B4BD7) roteert naar bit 0. Bij een negatieve delta (>=
    // 0x80) verloor de eerdere shift-vertaling dat bit, waardoor B 1 te
    // laag uitviel en de L2495-keten (c=4-pad: (B+C+3B)*2) de
    // klim-timer B4BD3 exact 8 te laag zette. Gevonden via scripted
    // lockstep (my_session, records 5831-5852).
    uint8_t diff = (uint8_t)(h - state.B4BD7);
    uint8_t b = (uint8_t)((diff << 1) | (diff >> 7));
    uint8_t v = state.M436F & 0x03;
    state.B4BD4 = v;
    uint8_t c = (uint8_t)(((~v) & 0x03) + 1);

    // L2476/L2495: A = B + C, plus B per remaining step; a fourth step
    // doubles instead
    uint8_t a = (uint8_t)(b + c);
    a = (uint8_t)(a + b);
    if (--c != 0) {
        a = (uint8_t)(a + b);
        if (--c != 0) {
            a = (uint8_t)(a + b);
            if (--c != 0) {
                a = (uint8_t)(a + a);
            }
        }
    }
    state.B4BD3 = a;

    // 247E-2493: rearm the climb threshold
    a = (uint8_t)((uint8_t)((uint8_t)(0x08 - state.BirdsLeft) << 1)
                  + state.Counter9A);
    a = (uint8_t)(a << 1);
    state.B4BD1 = (uint8_t)((state.M436F & 0x1E) + a);
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
        l2668();
        l26aa();
    } else {
        l26d0();
    }
}
