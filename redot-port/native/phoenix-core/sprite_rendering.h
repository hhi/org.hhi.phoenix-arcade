#ifndef SPRITE_RENDERING_H
#define SPRITE_RENDERING_H

#include <stdint.h>

void update_screen_objects(uint16_t alien_state_addr, uint16_t screen_ram_addr);
void bit4_controller(uint16_t bc, uint16_t de, uint16_t hl);
void bit3_controller(uint16_t bc, uint16_t de, uint16_t hl);

#endif // SPRITE_RENDERING_H
