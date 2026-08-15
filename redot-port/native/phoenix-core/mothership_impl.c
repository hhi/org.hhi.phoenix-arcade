#include "mothership_logic.h"
#include "z80_core.h"
#include "coverage.h"
#include "game_constants.h"

extern PhoenixState state;
extern const uint8_t phoenix_mothership_explosion_pointers[0x60];

/*
 * [ASM: 2351-23C7]
 */
void l2351_mothership_animation(uint16_t de, uint16_t hl) {
    coverage_hit("mothership_animation");
    uint8_t a = mem_read(de);
    if ((a & 0x08) == 0) return;

    a = mem_read(hl);
    hl++;
    uint8_t l = mem_read(hl);
    uint8_t h = a + 0x08;
    hl = (h << 8) | l;

    a = state.CounterB9;
    a >>= 3;
    a += l;
    a &= 0x1F;
    uint8_t b = a;

    a = l;
    a &= 0xE0;
    a |= b;
    l = a;
    hl = (h << 8) | l;

    a = mem_read(hl);
    b = a;
    a &= 0xFC;
    if (a == 0x4C) {
        coverage_hit("mothership_tile_hit");
        coverage_hit("mothership_tile_4c_hit");
        a = mem_read(de);
        a &= 0xF7;
        mem_write(de, a);

        state.M4366 = 0xFF;
        a = b;
        a--;
        mem_write(hl, a);

        if (a != 0x4B) return;
        mem_write(hl, 0x00);

        hl--;
        a = mem_read(hl);
        if (a != 0x5E) return;
        mem_write(hl, 0x4F);
        return;
    }

    a &= 0xF0;
    if (a == 0x60) {
        coverage_hit("mothership_tile_hit");
        coverage_hit("mothership_tile_60_hit");
        a = mem_read(de);
        a &= 0xF7;
        mem_write(de, a);

        de += 2;
        a = mem_read(de);
        if ((a & 0x04) != 0) {
            // Inline L2030: the AND $03/CP $01 test runs on B (the tile
            // byte, reloaded into A at ASM 23A1 right before the jump),
            // not on the just-loaded de+2 status byte.
            if ((b & 0x03) == 1) {
                coverage_hit("mothership_core_window_seen");
                // L23C0: real mothership-explosion trigger. HL is
                // reloaded to $43A4 in the ASM (GameState) -- this does
                // NOT continue using the mothership-tile hl.
                uint8_t gate = mem_read(hl - 1) & 0xF0;
                if (gate == 0x70) {
                    coverage_hit("mothership_core_gate_70_seen");
                    state.GameState = GAME_STATE_MOTHERSHIP_EXPLODING;
                    coverage_hit("mothership_explosion_trigger");
                    state.CounterA5 = 0x60;
                    state.ParticleExplosion = 0xFF;
                } else {
                    coverage_hit("mothership_core_gate_not_70_seen");
                }
                return;
            }
            a = b;
            a &= 0x0F;
            a += 0x10; // 0x1B50 - 0x1B40 page base
            mem_write(hl, phoenix_mothership_explosion_pointers[a]);
            state.M4366 = 0xFF;
            return;
        }

        a = b;
        a &= 0x0C;
        if (a == 0x04) {
            coverage_hit("mothership_core_window_seen");
            // L23C0 again (reached directly, not via L2030 this time).
            uint8_t gate = mem_read(hl - 1) & 0xF0;
            if (gate == 0x70) {
                coverage_hit("mothership_core_gate_70_seen");
                state.GameState = GAME_STATE_MOTHERSHIP_EXPLODING;
                coverage_hit("mothership_explosion_trigger");
                state.CounterA5 = 0x60;
                state.ParticleExplosion = 0xFF;
            } else {
                coverage_hit("mothership_core_gate_not_70_seen");
            }
            return;
        }

        a = b;
        a &= 0x0F;
        mem_write(hl, phoenix_mothership_explosion_pointers[a]);
        state.M4366 = 0xFF;
        return;
    }
}

// l2085_draw_particles: foutieve duplicaat-vertaling van L2085-L20E2
// verwijderd (12 juli 2026): de EX (SP),HL werd gesimuleerd als een
// hl<->de-swap i.p.v. met het gestackte schermadres. De gedeelde,
// lockstep-bewezen vertaling is l2085_particles in player_explosion.c
// (zelfde asm-route als de spelersexplosie).

/*
 * [ASM: 242C-2442]
 */
uint8_t update_counters_for_mothership_explosion(uint16_t* out_de) {
    state.CounterB9 &= 0xF8;
    extern void hw_write_scroll_register(uint8_t);
    hw_write_scroll_register(state.CounterB9);
    
    uint16_t de = 0x41C6;
    uint8_t b = state.CounterB9 >> 3;
    uint8_t a = (de & 0xFF) - b;
    a &= 0x1F;
    b = a;
    
    a = de & 0xFF;
    a &= 0xE0;
    a |= b;
    de = (de & 0xFF00) | a;
    
    state.CounterA5--;
    
    if (out_de) {
        *out_de = de;
    }
    return state.CounterA5;
}

// l2260_spiral_draw/l2292_spiral_routine: dode (en deels foutieve --
// de L2292-kopie schreef naar $4BD2 i.p.v. CounterB9/$43B9 en miste de
// scroll-register-write) duplicaat-vertalingen verwijderd, 11 juli
// 2026. De levende, lockstep-geverifieerde vertalingen zijn de static
// versies in state_play.c ([ASM: 2260-2291] en [ASM: 2292-22B3]).
