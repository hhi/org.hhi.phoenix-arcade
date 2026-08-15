#include "phoenix_state.h"
#include "phoenix_hw.h"
#include "z80_core.h"
#include <stdint.h>

extern PhoenixState state;

/*
 * Translates L211C
 * Clamps the scroll speed and sets the scroll register. Returns the
 * resulting A (CounterB9 unchanged, or the clamped 0x10) -- L20E8 uses
 * this returned value, not the CounterA5 it had in A before the call.
 * [ASM: 211C-212C]
 * Proposed C name: clamp_scroll_for_player_explosion
 */
uint8_t l211c(void) {
    uint8_t a = state.CounterB9;
    if (a < 0x10) return a;
    if (a >= 0x30) return a;

    state.CounterB9 = 0x10;
    hw_write_scroll_register(0x10);
    return 0x10;
}

/*
 * Translates L20E8
 * Player explosion part 2.
 * [ASM: 20E8-210D]
 * Proposed C name: draw_player_ship_explosion_fragment
 */
void l20e8(uint8_t a, uint8_t d, uint8_t e) {
    uint8_t b = a;
    d += 8;

    // 20E9-20EC overwrites A with D+8 before the call; L211C's return
    // value (not the original CounterA5) feeds the RRCA below.
    a = l211c();

    // RRCA x 3
    a = (a >> 3) | (a << 5);
    a += e;
    uint8_t c = a & 0x1F;
    
    a = e & 0xE0;
    a |= c;
    e = a;
    
    a = b;
    // RRCA x 2
    a = (a >> 2) | (a << 6);
    a &= 0x0E;
    a += 0x90;
    uint8_t l = a;

    // Page-relative index into phoenix_mothership_explosion_pointers
    // (base 0x1B40); l is always in [0x90, 0x9E].
    extern const uint8_t phoenix_mothership_explosion_pointers[0x60];
    uint8_t page_idx = (uint8_t)(l - 0x40);

    // 2106: LD A,(HL) -> A=mem[ptr]; 2108: LD L,(HL) at ptr+1 -> L=mem[ptr+1];
    // 2109: LD H,A -- so H (MSB) is the FIRST byte read, L (LSB) the second.
    uint8_t msb = phoenix_mothership_explosion_pointers[page_idx];
    uint8_t lsb = phoenix_mothership_explosion_pointers[page_idx + 1];
    uint16_t image_ptr = (msb << 8) | lsb;
    
    extern void draw_image_c_by_b(uint16_t hl, uint16_t de, uint8_t b, uint8_t c);
    draw_image_c_by_b(image_ptr, (d << 8) | e, 4, 4);
}

/*
 * Translates L20B0
 * Player ship particles explosion copy loop.
 * [ASM: 20B0-20E2]
 */
void l20b0_player_ship_particles_explosion(uint8_t b, uint8_t c, uint16_t de, uint16_t hl) {
    uint16_t screen = (b << 8) | c; // the stacked BC: screen address
    extern const uint8_t phoenix_explosion_particle_page[0x400];

    while (1) {
        // 20B1: control byte from T2900 (ROM)
        uint8_t a = phoenix_explosion_particle_page[hl];

        // 20B5-20C2: 8 cells; a set bit places a particle tile from T2800
        for (int i2 = 0; i2 < 8; i2++) {
            mem_write(screen, 0);
            if (a & 1) {
                mem_write(screen, phoenix_explosion_particle_page[de]);
            }
            a >>= 1; // RRCA: bit 0 first
            screen++;
            de++;
        }

        // 20C5-20C9: next control byte; odd LSB continues the same row
        hl++;
        if (hl & 1) continue;

        // 20CC-20CF: end of the 32-byte control block
        if ((hl & 0x1F) == 0) return;

        // 20D2-20DE: move the screen address back 0x30 (one row up after
        // the +8 walked right); stop when it would drop below $4000
        screen = (uint16_t)(screen - 0x30);
        if ((screen >> 8) == 0x3F) return;
    }
}

void l2085_particles(uint8_t counter_a5, uint16_t tile_base, uint16_t ctrl_base,
                     uint8_t b, uint8_t c);

/*
 * Translates L2070
 * Player ship particles explosion setup.
 * [ASM: 2070-2084]
 * Proposed C name: setup_player_ship_particle_explosion
 */
void l2070(uint8_t d, uint8_t e) {
    uint8_t a = e - 0x0A;
    a += 0xC0;
    uint8_t c = a;
    
    a = d + 0; // ADC 0 (assuming carry from ADD C0? No, from SUB 0A. Wait! SUB 0A sets carry if E < 0A)
    // We must handle carry correctly:
    uint16_t sub_res = e - 0x0A;
    uint16_t add_res = (sub_res & 0xFF) + 0xC0;
    uint8_t carry_after_add = (add_res > 0xFF) ? 1 : 0;
    
    c = add_res & 0xFF;
    
    // ADC 0 adds carry_after_add (actually, Z80 ADD/ADC preserves carry unless it's an INC/DEC)
    // Wait, D6 0A is SUB 0A. C6 C0 is ADD C0. ADD C0 modifies carry!
    // So ADC 0 uses the carry from ADD C0!
    a = d + carry_after_add;
    uint8_t b = a;
    
    // Page-relative offsets into phoenix_explosion_particle_page (base 0x2800):
    // tile table T2800 -> 0x000, control table T2900 -> 0x100.
    l2085_particles(state.CounterA5, 0x000, 0x100, b, c);
}

/*
 * Translates L2085-L20E2 (gedeelde staart): de particle-teken-route die
 * zowel de spelersexplosie (L2070 -> JP $2085, tabellen T2800/T2900) als
 * de mothership-explosie (L2400 $2426 -> JP $2085, tabellen T2A00/T2B00)
 * gebruikt. Een eerdere aparte mothership-vertaling
 * (l2085_draw_particles in mothership_impl.c) simuleerde o.a. de
 * EX (SP),HL verkeerd (wisselde de control- met de tile-pointer i.p.v.
 * met het gestackte schermadres); die is vervangen door deze gedeelde,
 * lockstep-bewezen route. Gevonden via scripted lockstep
 * (mutated_rank_01_score_3092917, record 11235).
 * [ASM: 2085-20AA]
 */
void l2085_particles(uint8_t counter_a5, uint16_t tile_base, uint16_t ctrl_base,
                     uint8_t b, uint8_t c) {
    // L2085: A enters as CounterA5 (207A: LD A,(HL) with HL=$43A5);
    // it selects the animation phase block inside the control table.
    uint8_t a = (uint8_t)(counter_a5 - 0x20);
    a = (uint8_t)((a << 2) | (a >> 6)); // RLCA x2
    a &= 0xE0;
    uint16_t hl = ctrl_base | (uint8_t)(0xE0 - a);
    uint16_t de = tile_base;

    while (1) {
        // L2091:
        uint16_t val1 = 0x3F - c;
        uint16_t val2 = 0x43 - b - ((val1 > 0xFF) ? 1 : 0); // SBC
        if (!(val2 > 0xFF)) { // JP NC
            l20b0_player_ship_particles_explosion(b, c, de, hl);
            break;
        }

        hl += 2;

        // 209C-209F: LD A,E / ADD $10 / LD E,A -- E is the low byte of
        // DE, the particle-tile pointer: each skipped entry advances the
        // tile data by 16.
        de = (de & 0xFF00) | ((de + 0x10) & 0xFF);

        uint16_t sub_res = c - 0x20;
        uint8_t borrow = (sub_res > 0xFF) ? 1 : 0;
        c = sub_res & 0xFF;
        b = (uint8_t)(b - borrow);

        // JP 2091
    }
}
