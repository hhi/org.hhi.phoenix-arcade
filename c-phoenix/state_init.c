#include "state_init.h"
#include "phoenix_tables.h"
#include "z80_core.h"
#include "game_constants.h"
#include <string.h>

extern PhoenixState state;

// Stubs for functions not yet implemented but called in Phase 2
extern void set_bits_video_register(void);
extern void init_alien_control_states(void);
extern void copy_init_values_for_16_aliens(void);
extern void init_alien_positions(void);
extern void get_screen_ram_address_for_player_ship(void);
extern void get_screen_ram_address_for_all_aliens(void);
extern void l32b0(void);

// [ASM: 0580-0595] Shared with attract_mode.c's demo dispatch -- see
// init_global_level_data.c. Previously this file had its own independent
// translation (a static init_global_level_data() with local T0598/T05A8/
// T05B4/T05C0/T05CC arrays holding the identical ROM bytes); centralized
// (21 July 2026) to remove the unmerged-duplicate risk.
extern void init_global_level_data(void);

static void init_player_data_structure(void) {
    // [ASM: 0547-055A]
    memcpy(&state.PlayerState, phoenix_player_init_data, 32);
    memset(&state.OldPlayerShipMSB, 0, 32);
}

// L0532: Init alien data for a new level and round
// [ASM: 0532-0543]
static void init_alien_data_new_level(void) {
    memset(&state.M4B50, 0, 0xA0); // Clear $4B50 to $4BEF
    init_alien_control_states();
    copy_init_values_for_16_aliens();
    init_alien_positions();
}

/*
 * Translates L0506
 * Clear $4392-$4397, then re-seed M4394 with the alien movement pattern
 * table MSB ($4B50).
 * [ASM: 0506-0514]
 */
static void init_alien_movement_pointers(void) {
    memset(&state.M4392, 0, 6);
    state.M4394 = state.M4B50; // 050E-0511
}

/*
 * Translates L0526 (the tail of L0515, also jumped to directly by the
 * level-B escort-wave respawn at $21D7).
 * [ASM: 0526-0531]
 */
void l0526(void) {
    init_alien_data_new_level();
    extern void get_screen_ram_address_for_all_aliens(void);
    get_screen_ram_address_for_all_aliens();
    init_alien_movement_pointers();
    l32b0(); // 052F: JP $32B0
}

/*
 * Game state 2.
 * Initialization of game and level data.
 * Translates Z80 label L0515
 * [ASM: 0515-0531]
 */
void state_2_init_game_and_level_data(void) {
    set_bits_video_register();
    
    state.GameState = GAME_STATE_PLAYING;
    
    init_global_level_data();
    init_player_data_structure();
    
    get_screen_ram_address_for_player_ship();

    // 0526: L0515 falls straight through into L0526 -- share the same
    // translation the level-B escort respawn ($21D7) jumps to.
    l0526();
}

/*
 * Translates GetPlayerLivesFromDip
 * [ASM: 0350-0366]
 */
void get_player_lives_from_dip(void) {
    extern uint8_t read_dsw0(void); // 0x7800
    uint8_t dsw = read_dsw0();
    
    // 0353: AND $03
    // 0355: ADD $03
    uint8_t lives = (dsw & 0x03) + 3;
    
    // 0358: LD HL,$4390
    // 035B: LD (HL),B
    state.Player1Lives = lives;
    
    // 035C: LD L,$A2
    // 035E: LD A,(HL)
    // 035F: CP $01
    // 0361: JP Z,$0367
    if (state.GameOrAttract != 1) {
        // 0364: LD L,$91
        // 0366: LD (HL),B
        state.Player2Lives = lives;
    }
    
    extern void update_lives_screen(void);
    update_lives_screen();
}

/*
 * Translates UpdateHiScore
 * Copy the score to hi score if greater
 * [ASM: 02F0-032D]
 */
void update_hi_score(void) {
    // 02F0: LD DE,$4383 (score of player 1)
    // Wait, the logic is complex, it checks both scores.
    // Let's implement the basic flow from ASM.
    uint16_t ptr_p1 = 0x4383;
    uint16_t ptr_p2 = 0x4387;
    uint16_t ptr_hi = 0x438B;

    // Simplification for C port:
    uint32_t s1 = (mem_read(ptr_p1) << 16) | (mem_read(ptr_p1-1) << 8) | mem_read(ptr_p1-2);
    uint32_t s2 = (mem_read(ptr_p2) << 16) | (mem_read(ptr_p2-1) << 8) | mem_read(ptr_p2-2);
    uint32_t hi = (mem_read(ptr_hi) << 16) | (mem_read(ptr_hi-1) << 8) | mem_read(ptr_hi-2);

    uint32_t max_s = (s1 > s2) ? s1 : s2;
    if (max_s > hi) {
        mem_write(ptr_hi,   (max_s >> 16) & 0xFF);
        mem_write(ptr_hi-1, (max_s >> 8) & 0xFF);
        mem_write(ptr_hi-2, max_s & 0xFF);
    }
}
