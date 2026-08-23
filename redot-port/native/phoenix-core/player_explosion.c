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
    uint8_t scroll_value = state.CounterB9;
    if (scroll_value < 0x10) return scroll_value;
    if (scroll_value >= 0x30) return scroll_value;

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
void l20e8(uint8_t explosion_frame, uint8_t screen_high_byte, uint8_t screen_low_byte) {
    uint8_t explosion_frame_source = explosion_frame;
    screen_high_byte += 8;

    // 20E9-20EC overwrites A with D+8 before the call; L211C's return
    // value (not the original CounterA5) feeds the RRCA below.
    uint8_t scroll_value = l211c();

    // RRCA x 3
    scroll_value = (scroll_value >> 3) | (scroll_value << 5);
    scroll_value += screen_low_byte;
    uint8_t scrolled_low_five_bits = scroll_value & 0x1F;
    
    screen_low_byte &= 0xE0;
    screen_low_byte |= scrolled_low_five_bits;
    
    uint8_t explosion_tile_offset = explosion_frame_source;
    // RRCA x 2
    explosion_tile_offset = (explosion_tile_offset >> 2) | (explosion_tile_offset << 6);
    explosion_tile_offset &= 0x0E;
    explosion_tile_offset += 0x90;

    // Page-relative index into phoenix_mothership_explosion_pointers
    // (base 0x1B40); l is always in [0x90, 0x9E].
    extern const uint8_t phoenix_mothership_explosion_pointers[0x60];
    uint8_t explosion_pointer_index = (uint8_t)(explosion_tile_offset - 0x40);

    // 2106: LD A,(HL) -> A=mem[ptr]; 2108: LD L,(HL) at ptr+1 -> L=mem[ptr+1];
    // 2109: LD H,A -- so H (MSB) is the FIRST byte read, L (LSB) the second.
    uint8_t image_high_byte = phoenix_mothership_explosion_pointers[explosion_pointer_index];
    uint8_t image_low_byte = phoenix_mothership_explosion_pointers[explosion_pointer_index + 1];
    uint16_t image_address = (image_high_byte << 8) | image_low_byte;
    
    extern void draw_image_c_by_b(uint16_t hl, uint16_t de, uint8_t b, uint8_t c);
    draw_image_c_by_b(image_address, (screen_high_byte << 8) | screen_low_byte, 4, 4);
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
void l2070(uint8_t screen_high_byte, uint8_t screen_low_byte) {
    // SUB $0A; ADD $C0; ADC D,$00. Only the ADD's carry reaches the
    // high byte, exactly as on the Z80.
    uint16_t low_byte_subtraction = screen_low_byte - 0x0A;
    uint16_t low_byte_sum = (low_byte_subtraction & 0xFF) + 0xC0;
    uint8_t carry_after_low_byte_add = low_byte_sum > 0xFF ? 1 : 0;
    
    uint8_t particle_low_byte = low_byte_sum & 0xFF;
    uint8_t particle_high_byte = screen_high_byte + carry_after_low_byte_add;
    
    // Page-relative offsets into phoenix_explosion_particle_page (base 0x2800):
    // tile table T2800 -> 0x000, control table T2900 -> 0x100.
    l2085_particles(state.CounterA5, 0x000, 0x100, particle_high_byte, particle_low_byte);
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
