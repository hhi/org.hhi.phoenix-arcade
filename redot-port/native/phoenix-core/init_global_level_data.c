#include "game_state_machine.h"
#include "phoenix_tables.h"
#include "game_constants.h"
#include <stdint.h>

extern PhoenixState state;

void init_global_level_data(void) {
    uint8_t level_pattern = state.LevelAndRound & LEVEL_PATTERN_MASK;
    uint8_t level_data_low_byte = phoenix_level_data_pointer_table[level_pattern];
    uint16_t level_data_address = 0x0500 | level_data_low_byte;

    // L058D-L0592: copy the twelve bytes of level timing/behaviour data
    // into $43AB-$43B6 for the active round.
    uint8_t *level_runtime_data = &state.M43AB;
    for (int byte_index = 0; byte_index < 12; byte_index++) {
        level_runtime_data[byte_index] = phoenix_level_data_page[level_data_address - 0x05A8 + byte_index];
    }
}
