#include "game_state_machine.h"
#include "phoenix_tables.h"
#include <stdint.h>

extern PhoenixState state;

void init_global_level_data(void) {
    uint8_t index = state.LevelAndRound & 0x0F;
    uint8_t low = phoenix_level_data_pointer_table[index];
    uint16_t data_addr = (0x05 << 8) | low;

    // Copy 12 bytes from data_addr to M43AB (state + offset of M43AB)
    uint8_t* dest = &state.M43AB;
    for (int i = 0; i < 12; i++) {
        dest[i] = phoenix_level_data_page[data_addr - 0x05A8 + i];
    }
}
