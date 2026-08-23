#include "mothership_logic.h"
#include "z80_core.h"
#include "coverage.h"
#include "game_constants.h"

extern PhoenixState state;
extern const uint8_t phoenix_mothership_explosion_pointers[0x60];

/*
 * [ASM: 2351-23C7]
 */
void l2351_mothership_animation(uint16_t bullet_state_address, uint16_t bullet_screen_address_address) {
    coverage_hit("mothership_animation");
    uint8_t bullet_state = mem_read(bullet_state_address);
    if ((bullet_state & PLAYER_BULLET_ACTIVE_FLAG) == 0) return;

    uint8_t bullet_screen_high_byte = mem_read(bullet_screen_address_address);
    bullet_screen_address_address++;
    uint8_t bullet_screen_low_byte = mem_read(bullet_screen_address_address);
    uint8_t mothership_page = bullet_screen_high_byte + 0x08;
    uint16_t mothership_tile_address = (mothership_page << 8) | bullet_screen_low_byte;

    uint8_t scroll_tile_offset = state.CounterB9 >> 3;
    scroll_tile_offset += bullet_screen_low_byte;
    scroll_tile_offset &= 0x1F;

    uint8_t adjusted_low_byte = bullet_screen_low_byte & 0xE0;
    adjusted_low_byte |= scroll_tile_offset;
    mothership_tile_address = (mothership_page << 8) | adjusted_low_byte;

    uint8_t mothership_tile = mem_read(mothership_tile_address);
    uint8_t original_tile = mothership_tile;
    mothership_tile &= 0xFC;
    if (mothership_tile == 0x4C) {
        coverage_hit("mothership_tile_hit");
        coverage_hit("mothership_tile_4c_hit");
        bullet_state &= (uint8_t)~PLAYER_BULLET_ACTIVE_FLAG;
        mem_write(bullet_state_address, bullet_state);

        state.M4366 = 0xFF;
        mothership_tile = original_tile - 1;
        mem_write(mothership_tile_address, mothership_tile);

        if (mothership_tile != 0x4B) return;
        mem_write(mothership_tile_address, 0x00);

        mothership_tile_address--;
        mothership_tile = mem_read(mothership_tile_address);
        if (mothership_tile != 0x5E) return;
        mem_write(mothership_tile_address, 0x4F);
        return;
    }

    mothership_tile &= 0xF0;
    if (mothership_tile == 0x60) {
        coverage_hit("mothership_tile_hit");
        coverage_hit("mothership_tile_60_hit");
        bullet_state &= (uint8_t)~PLAYER_BULLET_ACTIVE_FLAG;
        mem_write(bullet_state_address, bullet_state);

        bullet_state_address += 2;
        uint8_t bullet_shape = mem_read(bullet_state_address);
        if ((bullet_shape & 0x04) != 0) {
            // Inline L2030: the AND $03/CP $01 test runs on B (the tile
            // byte, reloaded into A at ASM 23A1 right before the jump),
            // not on the just-loaded de+2 status byte.
            if ((original_tile & 0x03) == 1) {
                coverage_hit("mothership_core_window_seen");
                // L23C0: real mothership-explosion trigger. HL is
                // reloaded to $43A4 in the ASM (GameState) -- this does
                // NOT continue using the mothership-tile hl.
                uint8_t gate = mem_read(mothership_tile_address - 1) & 0xF0;
                if (gate == 0x70) {
                    coverage_hit("mothership_core_gate_70_seen");
                    state.GameState = GAME_STATE_MOTHERSHIP_EXPLODING;
                    coverage_hit("mothership_explosion_trigger");
                    state.CounterA5 = PLAYER_EXPLOSION_INITIAL_DURATION;
                    state.ParticleExplosion = 0xFF;
                } else {
                    coverage_hit("mothership_core_gate_not_70_seen");
                }
                return;
            }
            uint8_t explosion_tile_index = (original_tile & 0x0F) + 0x10; // 0x1B50 - 0x1B40 page base
            mem_write(mothership_tile_address, phoenix_mothership_explosion_pointers[explosion_tile_index]);
            state.M4366 = 0xFF;
            return;
        }

        if ((original_tile & 0x0C) == 0x04) {
            coverage_hit("mothership_core_window_seen");
            // L23C0 again (reached directly, not via L2030 this time).
            uint8_t gate = mem_read(mothership_tile_address - 1) & 0xF0;
            if (gate == 0x70) {
                coverage_hit("mothership_core_gate_70_seen");
                state.GameState = GAME_STATE_MOTHERSHIP_EXPLODING;
                coverage_hit("mothership_explosion_trigger");
                state.CounterA5 = PLAYER_EXPLOSION_INITIAL_DURATION;
                state.ParticleExplosion = 0xFF;
            } else {
                coverage_hit("mothership_core_gate_not_70_seen");
            }
            return;
        }

        uint8_t explosion_tile_index = original_tile & 0x0F;
        mem_write(mothership_tile_address, phoenix_mothership_explosion_pointers[explosion_tile_index]);
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
uint8_t update_counters_for_mothership_explosion(uint16_t *out_mothership_screen_address) {
    state.CounterB9 &= 0xF8;
    extern void hw_write_scroll_register(uint8_t);
    hw_write_scroll_register(state.CounterB9);
    
    uint16_t mothership_screen_address = 0x41C6;
    uint8_t scroll_tile_offset = state.CounterB9 >> 3;
    uint8_t adjusted_low_byte = (mothership_screen_address & 0xFF) - scroll_tile_offset;
    adjusted_low_byte &= 0x1F;

    uint8_t screen_low_byte = mothership_screen_address & 0xE0;
    screen_low_byte |= adjusted_low_byte;
    mothership_screen_address = (mothership_screen_address & 0xFF00) | screen_low_byte;
    
    state.CounterA5--;
    
    if (out_mothership_screen_address) {
        *out_mothership_screen_address = mothership_screen_address;
    }
    return state.CounterA5;
}

// draw_spiral_column/finish_spiral_transition: dode (en deels foutieve --
// de L2292-kopie schreef naar $4BD2 i.p.v. CounterB9/$43B9 en miste de
// scroll-register-write) duplicaat-vertalingen verwijderd, 11 juli
// 2026. De levende, lockstep-geverifieerde vertalingen zijn de static
// versies in state_play.c ([ASM: 2260-2291] en [ASM: 2292-22B3]).
