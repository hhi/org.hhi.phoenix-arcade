#include "game_state_machine.h"
#include "z80_core.h"
#include "sound.h"
#include "game_constants.h"
#include "coverage.h"
#include <stdint.h>

extern PhoenixState state;
extern uint8_t hw_read_dsw(void);

/*
 * Adds two packed-BCD bytes plus carry and returns the adjusted packed-BCD
 * result. Used by add_score so score RAM stays in the same decimal encoding
 * the original display routines expect.
 */
static uint8_t bcd_add(uint8_t value, uint8_t addend, uint8_t *carry) {
    uint16_t sum = value + addend + *carry;
    uint8_t carry_out = 0;
    
    // Half-carry for lower nibble
    if ((value & 0x0F) + (addend & 0x0F) + *carry > 0x09) {
        sum += 0x06;
    }
    // Carry for upper nibble
    if (sum > 0x99) {
        sum += 0x60;
        carry_out = 1;
    }
    
    *carry = carry_out;
    return (uint8_t)sum;
}

/*
 * Updates the three-byte high score from the larger of player 1 and player 2.
 * The score bytes are packed BCD, but bytewise comparison is valid because the
 * high/mid/low ordering matches decimal magnitude.
 */
static void update_hi_score(void) {
    // 02F0: LD DE,$4383 ; Score1low
    // 02F3: LD HL,$438B ; HiScorelow
    
    uint32_t player_one_score = (state.Score1high << 16) | (state.Score1mid << 8) | state.Score1low;
    uint32_t player_two_score = (state.Score2high << 16) | (state.Score2mid << 8) | state.Score2low;
    uint32_t current_score    = player_one_score > player_two_score ? player_one_score : player_two_score;
    uint32_t high_score       = (state.HiScorehigh << 16) | (state.HiScoremid << 8) | state.HiScorelow;
    
    if (current_score > high_score) {
        if (current_score == player_one_score) {
            state.HiScorehigh = state.Score1high;
            state.HiScoremid = state.Score1mid;
            state.HiScorelow = state.Score1low;
        } else {
            state.HiScorehigh = state.Score2high;
            state.HiScoremid = state.Score2mid;
            state.HiScorelow = state.Score2low;
        }
    }
}

/*
 * Adds a packed-BCD score amount to the active player's score and refreshes
 * the high score. GameAndDemoOrSplash selects the player bank: bit 0 maps to
 * player 1/player 2 score storage.
 */
void add_score(uint16_t score_bcd) {
    uint8_t active_player = state.GameAndDemoOrSplash & 1; // 0 = P1, 1 = P2
    uint8_t *high_score_byte = active_player ? &state.Score2high : &state.Score1high;
    uint8_t *middle_score_byte = active_player ? &state.Score2mid : &state.Score1mid;
    uint8_t *low_score_byte = active_player ? &state.Score2low : &state.Score1low;
    
    uint8_t carry = 0;
    uint8_t low_bcd_addend  = score_bcd & 0xFF;
    uint8_t high_bcd_addend = (score_bcd >> 8) & 0xFF;
    
    *low_score_byte    = bcd_add(*low_score_byte, low_bcd_addend, &carry);
    *middle_score_byte = bcd_add(*middle_score_byte, high_bcd_addend, &carry);
    *high_score_byte   = bcd_add(*high_score_byte, 0, &carry);
    
    update_hi_score();
}

extern void print_number(uint16_t screen_addr, uint16_t data_addr, uint8_t digits);
extern void update_lives_screen(void);
extern void hw_write_sound_a(uint8_t val);
extern void hw_write_sound_b(uint8_t val);

/*
 * Per-frame score/audio service routine. It consumes queued score awards,
 * redraws score digits when needed, checks the bonus-life threshold, then
 * pushes the current sound latches before running the sound dispatcher.
 */
void update_scores_and_sound(void) {
    if (state.GameOrAttract == 0) return;
    uint8_t active_player = state.GameAndDemoOrSplash & 1;
    
    state.M4397 = 0xFF;
    
    // Process M4370..M437F (L2717/L2748: 4 slots of 4 bytes each --
    // trigger byte, score byte, then 2 unused bytes -- not 3-byte
    // records; the caller's "CALL L2748; INC E x3" advances DE by 4
    // total (L2748 itself does one INC E before returning).
    uint8_t *score_event_slots = &state.M4370;
    for (int slot_offset = 0; slot_offset < 16; slot_offset += 4) {
        if (score_event_slots[slot_offset] == 1 && score_event_slots[slot_offset + 1] != 0) {
            uint8_t score_event = score_event_slots[slot_offset + 1];
            uint8_t swapped = (score_event >> 4) | (score_event << 4);
            uint16_t bcd = ((swapped & 0x0F) << 8) | (swapped & 0xF0);
            add_score(bcd);
            score_event_slots[slot_offset + 1] = 0;
            state.M4397 = 0;
        }
    }
    
    // 2725-2736: mothership score. NB: de asm heeft GEEN nul-guard op
    // $439D -- zolang GameState 6 is wordt elke frame (DE)=$439D
    // opgeteld (na het eerste frame is dat 0), gewist, en $4397 op 0
    // gezet, wat verderop de score-herprint (L2768) triggert. Een
    // eerdere vertaling deed dit alleen als M439D != 0, waardoor de
    // herprint-toestand tijdens de hele mothership-explosie afweek.
    // Gevonden via scripted lockstep (mutated_rank_01_score_3092917,
    // record 11234).
    if (state.GameState == GAME_STATE_MOTHERSHIP_EXPLODING) {
        add_score(state.M439D << 8); // e.g. 0x50 -> 0x5000
        state.M439D = 0;
        state.M4397 = 0;
    }
    
    if (state.M4397 == 0) {
        if (active_player == 0) print_number(PLAYER_ONE_SCORE_SCREEN_ADDRESS, PLAYER_ONE_SCORE_RAM_ADDRESS, SCORE_DIGIT_COUNT);
        else print_number(PLAYER_TWO_SCORE_SCREEN_ADDRESS, PLAYER_TWO_SCORE_RAM_ADDRESS, SCORE_DIGIT_COUNT);
        
        if (state.M43BD != 0 || state.BonusLivesAt != 0) {
            // Check threshold
            uint8_t *high_score_byte = active_player ? &state.Score2high : &state.Score1high;
            uint8_t *middle_score_byte = active_player ? &state.Score2mid : &state.Score1mid;
            uint8_t *low_score_byte = active_player ? &state.Score2low : &state.Score1low;
            
            // L0314: 3-byte subtraction Threshold - Score, computed
            // *least*-significant byte first with the borrow chaining
            // forward into the more significant bytes -- standard
            // multi-byte subtraction convention, but easy to get
            // backwards when translating a flat SUB/SBC/SBC sequence.
            // Getting the byte order swapped (most-significant first)
            // makes the final carry depend on the LOW byte's own borrow
            // instead of the overall 3-byte magnitude comparison: since
            // M43BF/M43BD both start at 0, any nonzero score_low then
            // borrows unconditionally and awards a bonus life almost
            // immediately, regardless of the real (much higher) score
            // threshold -- exactly the "3 lives become 5 by ~2000
            // points, then never again" bug this fixes (the second,
            // equally premature award leaves M43BD/BonusLivesAt both 0,
            // which then permanently disables the outer guard above).
            //   least-significant: M43BF - low
            //   middle:            BonusLivesAt - mid
            //   most-significant:  M43BD - high  (final carry = result)
            int16_t temp;
            uint8_t carry = 0;

            temp = state.M43BF - *low_score_byte;
            carry = (temp < 0) ? 1 : 0;

            temp = state.BonusLivesAt - *middle_score_byte - carry;
            carry = (temp < 0) ? 1 : 0;

            temp = state.M43BD - *high_score_byte - carry;
            carry = (temp < 0) ? 1 : 0;
            
            if (carry) { // If Threshold < Score (borrow occurred), add a life!
                uint8_t *active_player_lives = active_player ? &state.Player2Lives : &state.Player1Lives;
                (*active_player_lives)++;
                coverage_hit("bonus_life_awarded");
                update_lives_screen();
                state.M436A = 0xFF; // sound trigger?
                
                uint8_t bonus_life_threshold_middle_byte = state.BonusLivesAt;
                state.BonusLivesAt = 0;
                state.M43BD = (bonus_life_threshold_middle_byte >> 4) | (bonus_life_threshold_middle_byte << 4);
            }
        }
    }
    
    // UpdateSoundControlHW (L27A8): push the current values to hardware
    // BEFORE mutating them, then force SoundControlB's low nibble on and
    // reset SoundControlA to 0x0F so the per-frame dispatcher below
    // (L3A10) starts from a clean slate.
    sound_set_frame_sample_index(SOUND_FRAME_END_SAMPLE);
    hw_write_sound_a(state.SoundControlA);
    hw_write_sound_b(state.SoundControlB);
    state.SoundControlB |= 0x0F;
    state.SoundControlA = 0x0F;

    extern void l3a10(void);
    l3a10();
}

/*
 * Applies the coin-related foreground tile writes used by the attract/coin
 * display path. The ROM address selects the literal tile value, while DE is
 * still constrained to foreground screen RAM as in the original guard.
 */
void check_coin_event(uint16_t screen_address, uint16_t rom_address) {
    if ((hw_read_dsw() & COIN_DISPLAY_DIP_MASK) == 0) return;
    
    // Original guard is narrower than mem_write's own RAM bound (the address must
    // land specifically in the $4000-$43FF foreground screen): preserved
    // here rather than widened, since these three fixed writes should
    // never legitimately target $4400-$4BFF.
    if (screen_address < FOREGROUND_SCREEN_START_ADDRESS
        || screen_address >= FOREGROUND_SCREEN_END_ADDRESS) return;

    if (rom_address == COIN_TEXT_TILE_ROM_ADDRESS) {
        mem_write(screen_address, COIN_TEXT_TILE);
    } else if (rom_address == COIN_INSERT_TILE_ROM_ADDRESS) {
        mem_write(screen_address, COIN_INSERT_TILE);
    } else if (rom_address == COIN_CREDIT_TILE_ROM_ADDRESS) {
        mem_write(screen_address, COIN_CREDIT_TILE);
    }
}
