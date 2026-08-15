#include "state_endings.h"
#include <stdbool.h>
#include "game_constants.h"

extern PhoenixState state;

// Stubs for hardware and subroutine calls
extern void hw_write_scroll_register(uint8_t val);
extern void clear_foreground(void);
extern void clear_background(void);
extern void print_text_lines(uint16_t addr, uint8_t count);
extern void copy_memory_bank(uint8_t from_bank, uint8_t to_bank);
extern void update_scroll_register_and_fill_background(void);

// Logic stubs for explosions and endings
extern void l0b15(void); // 0B15
extern void l0ba0(void); // 0BA0
extern void l0bba(void); // 0BBA
extern void print_copyright_lines(void);
extern void l1df0(void); // anti-piracy check
extern void erase_mothership(void);
extern void mothership_core_hit_check(uint16_t de);
extern void l2085_particles(uint8_t counter_a5, uint16_t tile_base, uint16_t ctrl_base,
                            uint8_t b, uint8_t c);
extern uint8_t update_counters_for_mothership_explosion(uint16_t* out_de);

/*
 * Game state 4.
 * Player ship particle explosion.
 * Translates L0AEA
 * [ASM: 0AEA-0B0F]
 */
void state_4_player_ship_explosion(void) {
    state.CounterB9 &= 0xF8;
    hw_write_scroll_register(state.CounterB9);
    
    // player_ship_explosion_animation_step was just calculating DE in Z80
    // We will do it in l0bba where it is needed
    
    state.CounterA5--;
    uint8_t a = state.CounterA5;
    
    if (a == 0) {
        l0b15();
        return;
    }
    
    if (a < 0x20) {
        l0ba0();
        return;
    }
    
    if (a == 0x20) {
        clear_foreground();
        return;
    }
    
    l0bba();
}

/*
 * Game state 5.
 * 'GAME OVER'.
 * Translates L0B60
 * [ASM: 0B60-0B9D]
 */
void state_5_game_over_text(void) {
    state.CounterA5++;
    uint8_t a = state.CounterA5;
    
    if (a == 0x40) {
        clear_background();
    }
    
    if (a == 0x80) {
        state.GameState = GAME_STATE_NEW_GAME;

        // If both players have no lives, go to attract mode
        if ((state.Player1Lives | state.Player2Lives) == 0) {
            state.Counter98[0] = 0x00;
            state.Counter98[1] = 0x00;
            state.GameOrAttract = 0x00; // 'Attract mode'
            if (state.GameAndDemoOrSplash != 0) {
                state.GameAndDemoOrSplash = 0x00;
                copy_memory_bank(1, 0);
            }
        }
        return;
    }
    
    print_text_lines(0x1A00, 1); // Prints "GAME OVER"
    print_text_lines(0x1960, 3); // L01E4: prints the copyright lines
    l1df0(); // anti-piracy check on the just-printed "AMSTAR" text
}

/*
 * Translates L2552
 * Explosion sequence finished -- hand off to state 7 (mothership score
 * display).
 * [ASM: 2552-255D]
 */
static void l2552_mothership_explosion_done(void) {
    state.GameState = GAME_STATE_MOTHERSHIP_SCORE;
    state.CounterA5 = 0x40;
    state.M436B = 0xFF; // 'mother ship score display' sound flag
}

/*
 * Game state 6.
 * Mother ship explosion.
 * Translates L2400
 * [ASM: 2400-244B]
 *
 * update_counters_for_mothership_explosion() (L242C) decrements
 * CounterA5 and returns the new value, which L2400 then dispatches on
 * four ways -- the previous translation only implemented the last of
 * these (the bit0 test below), permanently skipping the CounterA5==0
 * exit that hands off to state 7. Since nothing else ever sets
 * GameState to 7, that made state 6 a terminal state: destroying the
 * mothership froze the game in its explosion animation forever
 * (reported from real play, reproduced via a --record-input= session).
 * mothership_core_hit_check()/erase_mothership() already existed,
 * fully implemented, but were unreachable dead code for the same
 * reason -- this restores the call sites the ASM actually has.
 */
void state_6_mother_ship_explosion(void) {
    uint16_t de;
    uint8_t a = update_counters_for_mothership_explosion(&de);

    if (a == 0) {
        l2552_mothership_explosion_done();
        return;
    }

    if (a < 0x20) {
        erase_mothership();
        return;
    }

    if (a == 0x20) {
        mothership_core_hit_check(de);
        return;
    }

    // 240E-2412: RRCA tests bit0 of A without disturbing A (LD B,A ..
    // RRCA .. LD A,B) -- NC (bit0 clear) means an even CounterA5.
    // NB: L20E8 krijgt hier DE uit L242C mee (de scroll-gecorrigeerde
    // $41C6-mothership-positie), NIET de spelerspositie -- een eerdere
    // vertaling gaf PlayerShipMSB/LSB door, waardoor de mothership-
    // explosiedeeltjes op spelersgerelateerde adressen werden getekend.
    // Gevonden via scripted lockstep (mutated_rank_01_score_3092917,
    // record 11236).
    if ((a & 0x01) == 0) {
        extern void l20e8(uint8_t a, uint8_t d, uint8_t e);
        l20e8(a, (uint8_t)(de >> 8), (uint8_t)de);
        return;
    }

    // 2415-241E: C = E - 5 + $C0; B = D + carry van de ADD $C0 (de ADC
    // was in een eerdere vertaling weggelaten).
    uint8_t e_reg = (uint8_t)((de & 0xFF) - 5);
    uint16_t sum = (uint16_t)e_reg + 0xC0;
    uint8_t c = (uint8_t)sum;
    uint8_t b = (uint8_t)((de >> 8) + (sum > 0xFF ? 1 : 0));
    uint16_t bc = (b << 8) | c;

    (void)bc;
    // Page-relative offsets into phoenix_explosion_particle_page (base 0x2800):
    // tile table T2A00 -> 0x200, control table T2B00 -> 0x300.
    l2085_particles(state.CounterA5, 0x200, 0x300, b, c);
}

/*
 * Game state 7.
 * Mother ship score display.
 * Translates L244C
 * [ASM: 244C-2469]
 */
void state_7_mother_ship_score_display(void) {
    state.CounterA5--;
    uint8_t a = state.CounterA5;
    
    if ((a & 0x01) != 0) {
        update_scroll_register_and_fill_background();
        return;
    }
    
    if ((a >> 1) != 0) {
        return;
    }
    
    state.GameState = GAME_STATE_INIT_ROUND;
    
    uint8_t round = state.LevelAndRound;
    round &= 0xF0;
    round += 0x10; // next round
    state.LevelAndRound = round;
    
    state.AliensLeft = 0x10; // 16 aliens left
    clear_foreground();
}

/*
 * Translates L0B15
 * Deduct player life, handle GAME OVER or new round.
 * [ASM: 0B15-0B2D]
 */
void l0b15(void) {
    state.GameState = GAME_STATE_GAME_OVER;

    // 0B18-0B1C: A = GameAndDemoOrSplash + 0x90, used as the low byte of
    // the RAM pointer -- 0x90 selects Player1Lives, 0x91 Player2Lives.
    // Not GameOrAttract ($43A2): that's the 0/1/2 attract-vs-1p-vs-2p mode,
    // a different byte at $43A3.
    uint8_t* lives_ptr = (state.GameAndDemoOrSplash == 0) ? &state.Player1Lives : &state.Player2Lives;

    if (*lives_ptr == 0) {
        return;
    }
    
    (*lives_ptr)--;
    
    extern void update_lives_screen(void); // L0367
    update_lives_screen();
    
    if (*lives_ptr == 0) {
        return;
    }
    
    state.GameState = GAME_STATE_NEW_GAME;
}

/*
 * Translates L0BA0
 * Handle explosion timer reset for level < 9.
 * [ASM: 0BA0-0BB2]
 */
void l0ba0(void) {
    uint8_t a = state.LevelAndRound & 0x0F;
    if (a < 4) return;
    if (a >= 9) return;
    
    state.CounterB9 = 0;
    extern void hw_write_scroll_register(uint8_t val);
    hw_write_scroll_register(0);
    
    extern void clear_background(void); // 03A0
    clear_background();
}

/*
 * Translates L0BBA
 * Branching logic during player explosion.
 * [ASM: 0BBA-0BC4]
 */
void l0bba(void) {
    uint8_t a = state.CounterA5;
    if ((a & 1) == 0) {
        extern void handle_animations_for_killed_aliens(void); // 0FC0
        handle_animations_for_killed_aliens();
    } else {
        uint16_t de = (state.PlayerShipMSB << 8) | state.PlayerShipLSB;
        de += 0x001F; // LeftOneColumn (+0x20) and DEC DE (-1)
        
        uint8_t d = de >> 8;
        uint8_t e = de & 0xFF;
        
        if ((a & 2) != 0) {
            extern void l2070(uint8_t d, uint8_t e);
            l2070(d, e);
        } else {
            extern void l20e8(uint8_t a, uint8_t d, uint8_t e);
            l20e8(a, d, e);
        }
    }
}

/*
 * clear_stale_copyright_line() stond hier: een niet-ASM-correctie
 * (kopie van jphoenix commit 684ebcd) die de "PHOENIX AZ. U.S.A."-regel
 * wegveegde tijdens gameplay -- een echte bug in de originele 1980-ROM.
 * jphoenix heeft die correctie zelf teruggedraaid (commit a755f63,
 * Revert "Clear stale copyright line during gameplay"), waardoor de
 * kopie hier de poort van de referentie liet afwijken: een aanhoudende
 * lockstep-divergentie van 1591/3491 frames in de attract-cyclus (de
 * regel werd ook gewist waar hij legitiem hoort te staan, omdat
 * GameState tijdens de demo in het 2-7-bereik valt). Verwijderd op
 * 11 juli 2026 om het authentieke ROM-gedrag (inclusief de originele
 * ROM-bug) te herstellen, in lijn met de referentie-emulator.
 */
