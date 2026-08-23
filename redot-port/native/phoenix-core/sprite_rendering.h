#ifndef SPRITE_RENDERING_H
#define SPRITE_RENDERING_H

#include <stdint.h>

void update_screen_objects(uint16_t object_state_address, uint16_t object_screen_address);
void bit4_controller(uint16_t object_state_address, uint16_t object_screen_address, uint16_t scratch_address);
void bit3_controller(uint16_t object_state_address, uint16_t object_screen_address, uint16_t scratch_address);

#endif // SPRITE_RENDERING_H
