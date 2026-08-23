#include "state_play.h"
#include "phoenix_tables.h"
#include "z80_core.h"
#include "coverage.h"
#include "game_constants.h"

extern PhoenixState state;

/* Shared gameplay routines implemented by other core modules. */
extern void update_scroll_register_and_fill_background(void); // L06F0
extern uint8_t get_animation_chrs_aliens_fade_in(void); // L085A
extern void init_alien_control_states_05fa(uint8_t control_state,
                                           uint8_t animation_tile); // L05FA
extern void alien_data_controller(void); // L0A50

/* Dispatch the active alien waves for game levels 1, 3 and B. [ASM: 2000] */
static void level_1_3_B_player_alive_aliens(void) {
    coverage_hit("level_1_3_B_player_alive_aliens");
    extern void l2000_alien_wave_main_loop(void);
    l2000_alien_wave_main_loop();
}
enum {
    SPIRAL_FOREGROUND_RAM_START = 0x4000,
    SPIRAL_FOREGROUND_RAM_END   = 0x4400,
    SPIRAL_ROW_WIDTH            = 0x20,
    SPIRAL_ADDRESS_LOW_BASE     = 0xB0,
    SPIRAL_ADDRESS_HIGH_BASE    = 0x41,
    SPIRAL_FILL_TILE            = 0x1F,
    SPIRAL_ERASE_TILE           = 0x00,
    SPIRAL_ROTATED_STEP_MASK    = 0x3F,
    SPIRAL_TRANSITION_END_STEP  = 0x0D,
    SPIRAL_ERASE_STEP_OFFSET    = 0x0E,
    SPIRAL_STARFIELD_LEVEL_FLAG = 0x08,
    SPIRAL_STARFIELD_SCROLL     = 0x71,
    SPIRAL_BACKGROUND_SCROLL    = 0x00,
    SPIRAL_BACKGROUND_LAST_ADDR = 0x4B3F,
    SPIRAL_BACKGROUND_STOP_PAGE = 0x47,
    MOTHERSHIP_PARTIAL_FADE_COUNTER  = 0x28,
    MOTHERSHIP_PARTIAL_FADE_FLAG     = 0xFF,
    MOTHERSHIP_ALIEN_FADE_START      = 0xC0,
    MOTHERSHIP_ALIEN_FADE_COUNTER    = 0x30,
    MOTHERSHIP_ALIEN_FADE_INIT_VALUE = 0x3F,
    ALIEN_FADE_DRAW_THRESHOLD        = 0x15,
    ALIEN_FADE_CONTROL_DRAW_FLAG     = 0x08,
};

/*
 * Draw one frame of the level-transition spiral.
 *
 * Each call draws an expanding, stepped column of `tile` values into the
 * foreground tile RAM. Successive calls with increasing `spiral_step` values
 * form the spiral that fills the bird-wave background; later calls use the
 * empty tile to erase the same pattern.
 *
 * `spiral_step` determines both the column's screen origin and its width.
 * [ASM: 2260-2291]
 */
static void draw_spiral_column(uint8_t spiral_step, uint8_t tile) {
    // Three Z80 RRCA instructions split the step into address-byte inputs.
    const uint8_t rotated_step        = (spiral_step >> 3) | (spiral_step << 5);
    const uint8_t address_high_source = rotated_step & 0x1F;
    const uint8_t address_low_source  = rotated_step & 0xE0;

    // Build the initial foreground-RAM address. The carry from the low-byte
    // addition feeds the high byte, matching Z80 ADD ...,$B0; ADC ...,$41.
    const uint16_t low_byte_sum        = address_low_source + SPIRAL_ADDRESS_LOW_BASE;
    const uint8_t screen_low_byte      = low_byte_sum & 0xFF;
    const uint8_t carry_from_low_byte  = low_byte_sum > 0xFF ? 1 : 0;
    const uint16_t high_byte_sum       =
        address_high_source + SPIRAL_ADDRESS_HIGH_BASE
        + carry_from_low_byte;
    const uint8_t screen_high_byte     = high_byte_sum & 0xFF;
    uint16_t screen_address            = (screen_high_byte << 8) | screen_low_byte;

    // Shift the first column left by the current spiral width.
    const uint8_t tile_pairs_per_row = spiral_step + 1;
    uint8_t       initial_low_byte   = screen_address & 0xFF;
    initial_low_byte -= spiral_step;
    screen_address = (screen_address & 0xFF00) | initial_low_byte;

    uint8_t rows_remaining = (tile_pairs_per_row << 1) | (tile_pairs_per_row >> 7);

    // The original guard is narrower than mem_write's RAM bound: only the
    // visible foreground plane ($4000-$43FF) receives spiral tiles.
    while (rows_remaining > 0) {
        uint8_t tile_pairs_remaining = tile_pairs_per_row;

        while (tile_pairs_remaining > 0) {
            if (screen_address >= SPIRAL_FOREGROUND_RAM_START
                && screen_address < SPIRAL_FOREGROUND_RAM_END) {
                mem_write(screen_address, tile);
            }
            screen_address++;
            if (screen_address >= SPIRAL_FOREGROUND_RAM_START
                && screen_address < SPIRAL_FOREGROUND_RAM_END) {
                mem_write(screen_address, tile);
            }
            screen_address++;
            tile_pairs_remaining--;
        }

        // Move back two columns and up one foreground row. The high byte
        // borrows when the final low-byte subtraction crosses a row boundary.
        uint8_t next_low_byte = screen_address & 0xFF;
        next_low_byte -= tile_pairs_per_row;
        next_low_byte -= tile_pairs_per_row;
        uint8_t borrow_from_row_step = next_low_byte < SPIRAL_ROW_WIDTH ? 1 : 0;
        next_low_byte -= SPIRAL_ROW_WIDTH;

        uint8_t next_high_byte = screen_address >> 8;
        next_high_byte -= borrow_from_row_step;
        screen_address = (next_high_byte << 8) | next_low_byte;

        rows_remaining--;
    }
}

/*
 * Complete the spiral transition by restoring the background and scroll state.
 *
 * Levels with bit 3 set restore the starfield by cycling its 256-byte page
 * backwards through the background RAM. Earlier levels clear that RAM instead.
 * Both paths initialize CounterB9, the free-running backward scroll counter,
 * and write the same initial value to the hardware scroll register.
 * [ASM: 2292-22B3]
 */
static void finish_spiral_transition(void) {
    extern void clear_background(void);
    extern void hw_write_scroll_register(uint8_t);

    uint8_t initial_scroll_value;
    if (state.LevelAndRound & SPIRAL_STARFIELD_LEVEL_FLAG) {
        // The source index wraps after every 256 bytes, just as Z80 INC L
        // keeps the original source pointer within page $1C00.
        uint8_t starfield_source_index = 0;
        uint16_t background_write_address = SPIRAL_BACKGROUND_LAST_ADDR;

        while ((background_write_address >> 8) != SPIRAL_BACKGROUND_STOP_PAGE) {
            mem_write(background_write_address,
                      phoenix_starfield_page[starfield_source_index]);
            starfield_source_index++;
            background_write_address--;

            mem_write(background_write_address,
                      phoenix_starfield_page[starfield_source_index]);
            starfield_source_index++;
            background_write_address--;
        }
        initial_scroll_value = SPIRAL_STARFIELD_SCROLL;
    } else {
        clear_background();
        initial_scroll_value = SPIRAL_BACKGROUND_SCROLL;
    }

    state.CounterB9 = initial_scroll_value;
    hw_write_scroll_register(initial_scroll_value);
}

/*
 * Advance one frame of the spiral transition used by game levels 4, 6 and 8.
 *
 * The ROM phase counter at M439C is incremented before being rotated into a
 * six-bit spiral step. Early steps draw asterisks, later steps erase them,
 * and the terminal step completes the background transition. Once the erase
 * pass ends, the next level is initialized.
 * [ASM: 2230-225F]
 */
static void level_4_6_8_spiral_fill(void) {
    coverage_hit("level_4_6_8_spiral_fill");
    uint8_t spiral_step = state.M439C;
    state.M439C++;

    // Z80 RRCA, then AND $3F.
    spiral_step = (spiral_step >> 1) | (spiral_step << 7);
    spiral_step &= SPIRAL_ROTATED_STEP_MASK;

    if (spiral_step == SPIRAL_TRANSITION_END_STEP) {
        finish_spiral_transition();
        return;
    }

    uint8_t spiral_tile = SPIRAL_FILL_TILE;
    if (spiral_step < SPIRAL_TRANSITION_END_STEP) {
        draw_spiral_column(spiral_step, spiral_tile);
        return;
    }

    spiral_tile = SPIRAL_ERASE_TILE;
    spiral_step -= SPIRAL_ERASE_STEP_OFFSET;
    if (spiral_step != SPIRAL_TRANSITION_END_STEP) {
        draw_spiral_column(spiral_step, spiral_tile);
        return;
    }

    state.LevelAndRound++;
    state.GameState = GAME_STATE_INIT_ROUND;
}
/* Dispatch the bird-wave controller for game levels 5 and 7. [ASM: 3400] */
static void level_5_7_birds_fade_in(void) {
    coverage_hit("level_5_7_birds_fade_in");
    extern void process_birds(void);
    process_birds();
}

static void level_0_and_2_aliens_fade_in(void);

/*
 * Advance the level-9 mothership fade-in.
 *
 * Stars scroll every frame. When CounterB4 reaches the partial-fade
 * threshold, the mothership becomes visible. The following frames keep
 * scrolling until the counter reaches zero, then initialize the next level.
 * [ASM: 22B4-22C5]
 */
static void level_9_mothership_fade_in(void) {
    coverage_hit("level_9_mothership_fade_in");
    extern void stars_scroll_down(void);
    stars_scroll_down();

    state.CounterB4--;

    if (state.CounterB4 == MOTHERSHIP_PARTIAL_FADE_COUNTER) {
        state.M4367 = MOTHERSHIP_PARTIAL_FADE_FLAG;
        return;
    }

    // L0848 tail: only a zero countdown advances the level.
    if (state.CounterB4 != 0) {
        return;
    }
    state.LevelAndRound++;
    state.GameState = GAME_STATE_INIT_ROUND;
}

/*
 * Start the combined mothership-and-alien fade-in for game level A.
 *
 * Until CounterB4 reaches the start marker, this reuses the alien fade-in
 * path. At the marker it starts the mothership countdown and enables both
 * mothership and alien fade state.
 * [ASM: 22CA-22DD]
 */
static void level_A_mothership_and_aliens_fade_in(void) {
    coverage_hit("level_A_mothership_and_aliens_fade_in");
    if (state.CounterB4 != MOTHERSHIP_ALIEN_FADE_START) {
        level_0_and_2_aliens_fade_in(); // JP L0834
        return;
    }

    state.CounterB4 = MOTHERSHIP_ALIEN_FADE_COUNTER;
    state.M4367 = MOTHERSHIP_PARTIAL_FADE_FLAG;
    // $43BC participates in the original mothership/alien fade sequence;
    // its precise game-level meaning is not yet confirmed.
    state.M43BC = MOTHERSHIP_ALIEN_FADE_INIT_VALUE;
}

/*
 * Advance one frame of the level-0/2 alien fade-in.
 *
 * Every frame scrolls and fills the background, then decrements CounterB4.
 * Once the counter is below the draw threshold, it selects an animation tile,
 * initializes every alien's control state with the draw bit, and updates the
 * aliens. A zero counter advances to the next level.
 * [ASM: 0834-0859]
 */
static void level_0_and_2_aliens_fade_in(void) {
    coverage_hit("level_0_and_2_aliens_fade_in");
    update_scroll_register_and_fill_background();

    state.CounterB4--;

    if (state.CounterB4 >= ALIEN_FADE_DRAW_THRESHOLD) {
        return;
    }

    uint8_t animation_tile = get_animation_chrs_aliens_fade_in();
    init_alien_control_states_05fa(ALIEN_FADE_CONTROL_DRAW_FLAG,
                                   animation_tile);
    alien_data_controller();

    if (state.CounterB4 != 0) {
        return;
    }

    state.LevelAndRound++;
    state.GameState = GAME_STATE_INIT_ROUND;
}

/*
 * Run one normal-gameplay frame by dispatching the current level pattern.
 *
 * The low nibble of LevelAndRound selects the original T0814 jump-table
 * target. The high nibble stays available to mechanics that use it for
 * round-specific behavior.
 * [ASM: 0800-0833]
 */
void state_3_normal_game_play(void) {
    uint8_t level_pattern = state.LevelAndRound & LEVEL_PATTERN_MASK;

    switch (level_pattern) {
        case LEVEL_PATTERN_ALIENS_FADE_IN_0:
        case LEVEL_PATTERN_ALIENS_FADE_IN_2:
            level_0_and_2_aliens_fade_in();
            break;

        case LEVEL_PATTERN_ALIENS_ACTIVE_1:
        case LEVEL_PATTERN_ALIENS_ACTIVE_3:
        case LEVEL_PATTERN_ALIENS_ACTIVE_B:
            level_1_3_B_player_alive_aliens();
            break;

        case LEVEL_PATTERN_BIRDS_SPIRAL_4:
        case LEVEL_PATTERN_BIRDS_SPIRAL_6:
        case LEVEL_PATTERN_BIRDS_SPIRAL_8:
            level_4_6_8_spiral_fill();
            break;

        case LEVEL_PATTERN_BIRDS_FADE_IN_5:
        case LEVEL_PATTERN_BIRDS_FADE_IN_7:
            level_5_7_birds_fade_in();
            break;

        case LEVEL_PATTERN_MOTHERSHIP_FADE_IN_9:
            level_9_mothership_fade_in();
            break;

        case LEVEL_PATTERN_MOTHERSHIP_AND_ALIENS_A:
            level_A_mothership_and_aliens_fade_in();
            break;

        default:
            // T0814 marks patterns C-F as unused in normal gameplay.
            break;
    }
}
