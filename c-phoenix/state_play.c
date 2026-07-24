#include "state_play.h"
#include "phoenix_tables.h"
#include "z80_core.h"
#include "coverage.h"
#include "game_constants.h"

extern PhoenixState state;

// Stubs for game logic
extern void update_scroll_register_and_fill_background(void); // L06F0
extern uint8_t get_animation_chrs_aliens_fade_in(void); // L085A
extern void init_alien_control_states_05fa(uint8_t d, uint8_t e); // L05FA
extern void alien_data_controller(void); // L0A50

// Stubs for the various level types
static void level_1_3_B_player_alive_aliens(void) {
    coverage_hit("level_1_3_B_player_alive_aliens");
    extern void l2000_alien_wave_main_loop(void);
    l2000_alien_wave_main_loop();
} // L2000
/*
 * Translates L2260
 * Draws one spiral column step.
 * [ASM: 2260-2291]
 */
static void l2260_spiral_draw(uint8_t a, uint8_t b) {
    uint8_t c = a;
    uint8_t d_reg = (a >> 3) | (a << 5); // RRCA 3x
    uint8_t e = d_reg & 0x1F;
    a = d_reg & 0xE0;
    
    // ADD $B0
    uint16_t add_res = a + 0xB0;
    uint8_t l = add_res & 0xFF;
    uint8_t carry = (add_res > 0xFF) ? 1 : 0;
    
    // ADC $41
    uint16_t adc_res = e + 0x41 + carry;
    uint8_t h = adc_res & 0xFF;
    
    uint16_t hl = (h << 8) | l;
    
    // SUB C (on L)
    uint8_t a_l = (hl & 0xFF);
    a_l -= c;
    hl = (hl & 0xFF00) | a_l;
    
    c++;
    uint8_t e_count = (c << 1) | (c >> 7); // RLCA
    
    // Guard is narrower than mem_write's own RAM bound (hl must land
    // specifically in the $4000-$43FF foreground screen) -- preserved
    // rather than widened.
    while (e_count > 0) {
        uint8_t d_count = c;

        while (d_count > 0) {
            if (hl >= 0x4000 && hl < 0x4400) mem_write(hl, b);
            hl++;
            if (hl >= 0x4000 && hl < 0x4400) mem_write(hl, b);
            hl++;
            d_count--;
        }
        
        uint8_t a_reg = hl & 0xFF;
        a_reg -= c;
        a_reg -= c;
        uint8_t carry_sub = (a_reg < 0x20) ? 1 : 0;
        a_reg -= 0x20;
        
        uint8_t h_reg = hl >> 8;
        h_reg -= carry_sub; // SBC 00
        hl = (h_reg << 8) | a_reg;
        
        e_count--;
    }
}

/*
 * Translates L2292
 * Spiral end: restore starfield (level >= 8) or clear background.
 * [ASM: 2292-22B3]
 */
static void l2292_spiral_routine(void) {
    extern void clear_background(void);
    extern void hw_write_scroll_register(uint8_t);
    uint8_t a;

    if (state.LevelAndRound & 0x08) {
        // 229B-22B0: restore the starfield (T1C00) over the mothership,
        // writing the background backwards from $4B3F down to $4800
        uint16_t hl = 0x1C00;
        uint16_t de = 0x4B3F;
        while ((de >> 8) != 0x47) {
            mem_write(de, phoenix_starfield_page[hl - 0x1C00]);
            hl = (hl & 0xFF00) | ((hl + 1) & 0xFF); // INC L: stays in page
            de--;
            mem_write(de, phoenix_starfield_page[hl - 0x1C00]);
            hl = (hl & 0xFF00) | ((hl + 1) & 0xFF);
            de--;
        }
        a = 0x71; // L22E0
    } else {
        // L22F0
        clear_background();
        a = 0x00;
    }

    // L22E2
    state.CounterB9 = a;
    hw_write_scroll_register(a);
}

/*
 * Translates L2230
 * Game level 4, 6 and 8: the 'spiral fill' animation.
 * [ASM: 2230-225F]
 */
static void level_4_6_8_spiral_fill(void) {
    coverage_hit("level_4_6_8_spiral_fill");
    uint8_t a = state.M439C;
    state.M439C++;
    
    // RRCA
    a = (a >> 1) | (a << 7);
    a &= 0x3F;
    
    if (a == 0x0D) {
        l2292_spiral_routine();
        return;
    }
    
    uint8_t b = 0x1F; // Asterisk
    if (a < 0x0D) {
        l2260_spiral_draw(a, b);
        return;
    }
    
    b = 0x00; // Space
    a -= 0x0E;
    if (a != 0x0D) {
        l2260_spiral_draw(a, b);
        return;
    }
    
    state.LevelAndRound++;
    state.GameState = GAME_STATE_INIT_ROUND;
}
static void level_5_7_birds_fade_in(void) {
    coverage_hit("level_5_7_birds_fade_in");
    extern void process_birds(void);
    process_birds();
}

static void level_0_and_2_aliens_fade_in(void);

/*
 * Translates L22B4
 * Game level 9: Mothership 'fade in' (stars scroll down while the
 * mothership shape gets written into the background).
 * [ASM: 22B4-22C5]
 */
static void level_9_mothership_fade_in(void) {
    coverage_hit("level_9_mothership_fade_in");
    extern void stars_scroll_down(void);
    stars_scroll_down();

    state.CounterB4--;

    if (state.CounterB4 == 0x28) {
        state.M4367 = 0xFF; // Mothership partially faded in
        return;
    }

    // L0848 tail: advance to next level/state once the counter hits 0
    if (state.CounterB4 != 0) {
        return;
    }
    state.LevelAndRound++;
    state.GameState = GAME_STATE_INIT_ROUND;
}

/*
 * Translates L22CA
 * Game level A: Mothership and aliens 'fade in'.
 * [ASM: 22CA-22DD]
 */
static void level_A_mothership_and_aliens_fade_in(void) {
    coverage_hit("level_A_mothership_and_aliens_fade_in");
    if (state.CounterB4 != 0xC0) {
        level_0_and_2_aliens_fade_in(); // JP L0834
        return;
    }

    state.CounterB4 = 0x30;
    state.M4367 = 0xFF;  // Mothership partially faded in
    state.M43BC = 0x3F;
}

/*
 * Translates L0834
 * Game level 0 and 2: Stars scrolling down and 'aliens fade in'
 * [ASM: 0834-0859]
 */
static void level_0_and_2_aliens_fade_in(void) {
    coverage_hit("level_0_and_2_aliens_fade_in");
    update_scroll_register_and_fill_background();

    state.CounterB4--;

    if (state.CounterB4 >= 0x15) {
        return;
    }

    uint8_t e_val = get_animation_chrs_aliens_fade_in();
    extern void init_alien_control_states_05fa(uint8_t d, uint8_t e);
    // 085A: LD DE,$086C -- D (control state A) is 0x08 in every branch:
    // the draw bit, so the fading aliens actually get drawn
    init_alien_control_states_05fa(0x08, e_val);
    alien_data_controller();

    if (state.CounterB4 != 0) {
        return;
    }

    // Counter is 0, advance to next level/state
    state.LevelAndRound++;
    state.GameState = GAME_STATE_INIT_ROUND;
}

/*
 * Game state 3.
 * Normal game play.
 * Translates L0800 and its jump table T0814.
 * [ASM: 0800-0833]
 */
void state_3_normal_game_play(void) {
    // The jump table index is based on bits 0-3 of LevelAndRound.
    uint8_t level = state.LevelAndRound & LEVEL_PATTERN_MASK;
    
    switch (level) {
        case LEVEL_PATTERN_ALIENS_FADE_IN_0: level_0_and_2_aliens_fade_in(); break;
        case LEVEL_PATTERN_ALIENS_ACTIVE_1: level_1_3_B_player_alive_aliens(); break;
        case LEVEL_PATTERN_ALIENS_FADE_IN_2: level_0_and_2_aliens_fade_in(); break;
        case LEVEL_PATTERN_ALIENS_ACTIVE_3: level_1_3_B_player_alive_aliens(); break;
        case LEVEL_PATTERN_BIRDS_SPIRAL_4: level_4_6_8_spiral_fill(); break;
        case LEVEL_PATTERN_BIRDS_FADE_IN_5: level_5_7_birds_fade_in(); break;
        case LEVEL_PATTERN_BIRDS_SPIRAL_6: level_4_6_8_spiral_fill(); break;
        case LEVEL_PATTERN_BIRDS_FADE_IN_7: level_5_7_birds_fade_in(); break;
        case LEVEL_PATTERN_BIRDS_SPIRAL_8: level_4_6_8_spiral_fill(); break;
        case LEVEL_PATTERN_MOTHERSHIP_FADE_IN_9: level_9_mothership_fade_in(); break;
        case LEVEL_PATTERN_MOTHERSHIP_AND_ALIENS_A: level_A_mothership_and_aliens_fade_in(); break;
        case LEVEL_PATTERN_ALIENS_ACTIVE_B: level_1_3_B_player_alive_aliens(); break;
        case 0x0C: 
        case 0x0D:
        case 0x0E:
        case 0x0F:
            // "not used in this context" according to T0814
            break;
    }
}
