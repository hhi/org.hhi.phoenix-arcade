#ifndef UTILITIES_H
#define UTILITIES_H

#include <stdint.h>
#include "phoenix_state.h"

uint8_t check_input_bits(uint8_t mask);
void print_number(uint16_t screen_addr, uint16_t data_addr, uint8_t digits);
void clear_fore_and_background(void);
void clear_b_bytes_at_hl(uint16_t hl, uint8_t b);
void copy_b_bytes_hl_to_de(uint16_t hl, uint16_t de, uint8_t b);

void print_text_lines(uint16_t addr, uint8_t count);
void print_score_column(void);
void print_copyright_lines(void);
void get_screen_ram_address(uint16_t bc, uint16_t de);
void get_screen_ram_address_for_player_ship(void);
void draw_row(uint16_t* hl, uint16_t* de, uint8_t b);

void add_one_to_mem(uint16_t hl);
void add_bc_to_mem(uint16_t hl, uint16_t bc);
uint8_t compare_bc_to_mem(uint16_t hl, uint16_t bc);
uint8_t l0260_subtract_if_enough(uint16_t hl, uint16_t bc, uint16_t de);
uint8_t l0270_subtract_from_memory(uint16_t hl, uint16_t bc);
uint8_t l0277_subtract_to_memory(uint16_t hl, uint16_t de);

void draw_image_c_by_b(uint16_t hl, uint16_t de, uint8_t b, uint8_t c);
uint16_t left_one_column(uint16_t de);
uint16_t right_one_column(uint16_t de);
void delete_digits(uint16_t screen_addr, uint8_t num_digits);
void phoenix_init(void);
void add_to_score(uint16_t hl, uint16_t bc);

#endif // UTILITIES_H
