#include "game_state_machine.h"
#include "state_init.h"
#include "state_play.h"
#include "state_endings.h"
#include "coverage.h"
#include "game_constants.h"

extern PhoenixState state;

// Hardware stubs (assuming these exist in phoenix_hw.h or similar)
extern void hw_write_video_register(uint8_t val);
extern void hw_write_scroll_register(uint8_t val);

// Utility subroutines (stubs for now)
extern void clear_foreground(void);
extern void print_text_lines(uint16_t addr, uint8_t count);
#include "utilities.h"
extern void print_number(uint16_t screen_addr, uint16_t data_addr, uint8_t num_digits);
extern void delete_digits(uint16_t screen_addr, uint8_t num_digits);

// Prototypes for the individual state functions
static void state_0_new_game_start(void);
static void state_1_flashing_score(void);
static void switch_attract_mode_to_player_two(void);
extern void copy_memory_bank(uint8_t from_bank, uint8_t to_bank);

// Helper translations
static void set_bits_video_register(void);
static void reset_score_flash_screen(void);

// [ASM: 0400-041D]
void game_state_machine(void) {
    coverage_hit("game_state_machine");
    switch (state.GameState) {
        case GAME_STATE_NEW_GAME:              coverage_hit("state_0_new_game_start");              state_0_new_game_start();              break;
        case GAME_STATE_SCORE_FLASH:           coverage_hit("state_1_flashing_score");             state_1_flashing_score();             break;
        case GAME_STATE_INIT_ROUND:            coverage_hit("state_2_init_game_and_level_data");    state_2_init_game_and_level_data();    break;
        case GAME_STATE_PLAYING:               coverage_hit("state_3_normal_game_play");            state_3_normal_game_play();            break;
        case GAME_STATE_PLAYER_EXPLODING:      coverage_hit("state_4_player_ship_explosion");       state_4_player_ship_explosion();       break;
        case GAME_STATE_GAME_OVER:             coverage_hit("state_5_game_over_text");              state_5_game_over_text();              break;
        case GAME_STATE_MOTHERSHIP_EXPLODING:  coverage_hit("state_6_mother_ship_explosion");       state_6_mother_ship_explosion();       break;
        case GAME_STATE_MOTHERSHIP_SCORE:      coverage_hit("state_7_mother_ship_score_display");  state_7_mother_ship_score_display();   break;
        default: break;
    }
}

/*
 * Game state 0.
 * New game start.
 * Translates Z80 label L0430
 * [ASM: 0430-045B]
 * [ASM: 04A0-04AB]
 */
static void state_0_new_game_start(void) {
    state.GameState = GAME_STATE_SCORE_FLASH;
    state.CounterA5 = SCORE_FLASH_DURATION_INITIAL;

    uint8_t previous_mode = state.GameAndDemoOrSplash;
    state.GameAndDemoOrSplash = 0x00;

    if (previous_mode == 0x02) {
        return;
    }

    // 0440: restore GameAndDemoOrSplash (it wasn't 'intro splash')
    state.GameAndDemoOrSplash = previous_mode;

    // 0441-0445: a real one-player game in progress leaves the current
    // (already-correct) bank alone.
    if (state.GameOrAttract == 0x01) {
        return;
    }

    // 0446-0449: during the normal attract-mode demo ('game and demo for
    // player 1'), swap to the 'player 2' bank.
    if (state.GameAndDemoOrSplash == 0x00) {
        switch_attract_mode_to_player_two();
        return;
    }

    // 044C-045B: switching away from player 2's perspective back to
    // player 1's, but only if player 1 still has lives to continue with.
    if (state.Player1Lives == 0x00) {
        return;
    }
    state.GameAndDemoOrSplash = 0x00;
    if (state.GameOrAttract == 0x02) {
        coverage_hit("two_player_turn_switch");
    }
    copy_memory_bank(1, 0);
}

/*
 * Switch the attract-mode view from player 1's bank to player 2's bank.
 * Translates L04A0.
 * [ASM: 04A0-04AB]
 */
static void switch_attract_mode_to_player_two(void) {
    state.GameAndDemoOrSplash = 0x01;
    copy_memory_bank(0, 1);
}

/*
 * Set lower bits of video register for color palette, memory bank.
 * Translates Z80 label SetBitsVideoRegister (041E)
 */
static void set_bits_video_register(void) {
    uint8_t bank = state.GameAndDemoOrSplash & 0x01;
    uint8_t palette = state.LevelAndRound & 0x02;
    hw_write_video_register(bank | palette);
}

/*
 * Restore the scrolling background and palette at the midpoint of score flash.
 * Translates Z80 label L07F0, called from state 1 when CounterA5 reaches $7F.
 * [ASM: 07F0-07FA]
 */
static void reset_score_flash_screen(void) {
    hw_write_scroll_register(state.CounterB9);
    clear_foreground();
    set_bits_video_register();
}

/*
 * Game state 1.
 * Flashing of score1 or 2.
 * Translates Z80 label L04AC
 * [ASM: 04AC-04E4]
 * [ASM: 04E6-04F9]
 * [ASM: 04FB-0505]
 */
static void state_1_flashing_score(void) {
    state.CounterA5--;
    uint8_t frames_remaining = state.CounterA5;
    
    state.GameState = GAME_STATE_INIT_ROUND;
    if (frames_remaining == 0) {
        return;
    }
    
    state.GameState = GAME_STATE_SCORE_FLASH;

    // 04BA: JP Z,$07F0 -- een tail-jump: bij A == $7F vervangt L07F0 de
    // rest van dit frame volledig (een eerdere vertaling viel erna door
    // naar de flash-logica).
    if (frames_remaining == SCORE_FLASH_RESET_FRAME) {
        reset_score_flash_screen();
        return;
    }

    // Reset Counter9A and Counter9B (0x439A and 0x439B)
    state.Counter9A = 0x00;
    state.Counter9B = 0x00;

    // Every eight frames, toggle visibility.
    if ((frames_remaining & SCORE_FLASH_VISIBILITY_TOGGLE_MASK) != 0) {
        // L04E6: Hide score
        if (state.GameAndDemoOrSplash == 0) {
            delete_digits(PLAYER_ONE_SCORE_SCREEN_ADDRESS, SCORE_DIGIT_COUNT); // L04FB
        } else {
            delete_digits(PLAYER_TWO_SCORE_SCREEN_ADDRESS, SCORE_DIGIT_COUNT); // L04FB
        }
    } else {
        // 04C9: CALL $06E8 -- herprint eerst de statische headerregel
        // ("SCORE1 HI-SCORE SCORE2", rij 0 van T1800). Zo herstelt de
        // ROM headerletters die tijdens het spel overschreven raken;
        // een eerdere vertaling sloeg dit over, waardoor beschadigde
        // headertegels blijvend zichtbaar bleven. Gevonden via scripted
        // lockstep (mutated_rank_05_score_573462, record 2159).
        extern void print_text_lines(uint16_t screen_draw_info_addr, uint8_t columns);
        print_text_lines(SCORE_HEADER_TEXT_ADDRESS, 1);

        // L04DF: Show score
        if (state.GameAndDemoOrSplash == 0) {
            print_number(PLAYER_ONE_SCORE_SCREEN_ADDRESS, PLAYER_ONE_SCORE_RAM_ADDRESS, SCORE_DIGIT_COUNT); // 04DF
        } else {
            print_number(PLAYER_TWO_SCORE_SCREEN_ADDRESS, PLAYER_TWO_SCORE_RAM_ADDRESS, SCORE_DIGIT_COUNT); // 04DF
        }
    }
}

// States 4-7 are implemented in state_endings.c
