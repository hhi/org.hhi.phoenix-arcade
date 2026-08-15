#ifndef ALIEN_LOGIC_H
#define ALIEN_LOGIC_H

#include "phoenix_state.h"

void alien_data_controller(void);
void init_alien_control_states(void);
void init_alien_control_states_05fa(uint8_t d, uint8_t e);
void init_alien_positions(void);
void get_screen_ram_address_for_all_aliens(void);

#endif // ALIEN_LOGIC_H
