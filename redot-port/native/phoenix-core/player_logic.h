#ifndef PLAYER_LOGIC_H
#define PLAYER_LOGIC_H

#include "phoenix_state.h"

void player_update(void);
void copy_current_to_old_player_data(void);
void update_player_position_bullet_shield(void);
void update_player_ship_x(void);
void get_assigned_player_bullet_tile(uint8_t* bullet_state_ptr);

#endif // PLAYER_LOGIC_H
