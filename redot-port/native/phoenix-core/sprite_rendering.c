#include "sprite_rendering.h"
#include "phoenix_state.h"
#include "phoenix_tables.h"
#include "z80_core.h"
#include <stdbool.h>

extern PhoenixState state;
extern uint16_t right_one_column(uint16_t de);

/*
 * Helper to jump into the Bit4 / Bit3 jump table logic.
 */
static void execute_bit4_function(uint8_t func_idx, uint16_t bc, uint16_t de, uint16_t hl) {
    (void)bc; (void)hl;
    extern uint16_t right_one_column(uint16_t de);

    switch (func_idx) {
        case 0: // 0001_xxxx (L0763) Delete 1x1 screen objects
            {
                uint8_t d = mem_read(de);
                uint8_t e = mem_read(de + 1);
                uint16_t target_de = (d << 8) | e;
                if (target_de >= 0x4000 && target_de < 0x4400) {
                    mem_write(target_de, 0);
                }
            }
            break;

        case 1: // 0011_xxxx (L0779) Delete 2x1 screen objects
            {
                uint8_t d = mem_read(de);
                uint8_t e = mem_read(de + 1);
                uint16_t target_de = (d << 8) | e;

                if (target_de >= 0x4000 && target_de < 0x4400) mem_write(target_de, 0); // delete left part
                target_de = right_one_column(target_de);
                if (target_de >= 0x4000 && target_de < 0x4400) mem_write(target_de, 0); // delete right part
            }
            break;

        case 3: // 0111_xxxx (L079E) Delete 1x2 screen objects
            {
                uint8_t d = mem_read(de);
                uint8_t e = mem_read(de + 1);
                uint16_t target_de = (d << 8) | e;

                if (target_de >= 0x4000 && target_de < 0x4400) mem_write(target_de, 0); // delete upper part
                target_de = (target_de & 0xFF00) | ((target_de + 1) & 0xFF); // INC E actually.
                if (target_de >= 0x4000 && target_de < 0x4400) mem_write(target_de, 0); // delete lower part
            }
            break;

        case 4: // 1001_xxxx (L07BE) Delete 2x2 screen objects
            {
                uint8_t d = mem_read(de);
                uint8_t e = mem_read(de + 1);
                uint16_t target_de = (d << 8) | e;

                if (target_de >= 0x4000 && target_de < 0x4400) mem_write(target_de, 0); // delete upper left part
                uint16_t next_de = (target_de & 0xFF00) | ((target_de + 1) & 0xFF);
                if (next_de >= 0x4000 && next_de < 0x4400) mem_write(next_de, 0); // delete upper right part

                target_de = right_one_column(target_de);
                if (target_de >= 0x4000 && target_de < 0x4400) mem_write(target_de, 0); // delete lower left part

                next_de = (target_de & 0xFF00) | ((target_de + 1) & 0xFF);
                if (next_de >= 0x4000 && next_de < 0x4400) mem_write(next_de, 0); // delete lower right part
            }
            break;

        default:
            // Not used
            break;
    }
}

static void execute_bit3_function(uint8_t func_idx, uint16_t bc, uint16_t de, uint16_t hl) {
    (void)hl;
    extern void draw_background_2x2(uint16_t de_reg, uint16_t hl_reg);

    switch (func_idx) {
        case 0: // xxxx_1000 (L076D) Draw 1x1 screen objects
            {
                uint8_t d = mem_read(de + 2);
                uint8_t e = mem_read(de + 3);
                uint16_t target_de = (d << 8) | e;

                uint8_t b_val = mem_read(bc);
                if (target_de >= 0x4000 && target_de < 0x4400) mem_write(target_de, b_val);
            }
            break;

        case 1: // xxxx_1001 (L0788) Draw 2x1 screen objects
            {
                uint8_t d = mem_read(de + 2);
                uint8_t e = mem_read(de + 3);
                uint16_t target_de = (d << 8) | e;

                uint8_t b_val = mem_read(bc);
                uint16_t src_hl = 0x1400 | b_val;

                if (target_de >= 0x4000 && target_de < 0x4400) mem_write(target_de, phoenix_sprite_character_block_shapes[src_hl - 0x1400]);
                src_hl++;

                target_de = right_one_column(target_de);

                if (target_de >= 0x4000 && target_de < 0x4400) mem_write(target_de, phoenix_sprite_character_block_shapes[src_hl - 0x1400]);
            }
            break;

        case 3: // xxxx_1011 (L07AA) Draw 1x2 screen objects
            {
                uint8_t d = mem_read(de + 2);
                uint8_t e = mem_read(de + 3);
                uint16_t target_de = (d << 8) | e;

                uint8_t b_val = mem_read(bc);
                uint16_t src_hl = 0x1400 | b_val;

                if (target_de >= 0x4000 && target_de < 0x4400) mem_write(target_de, phoenix_sprite_character_block_shapes[src_hl - 0x1400]);
                src_hl++;
                target_de = (target_de & 0xFF00) | ((target_de + 1) & 0xFF); // INC E
                if (target_de >= 0x4000 && target_de < 0x4400) mem_write(target_de, phoenix_sprite_character_block_shapes[src_hl - 0x1400]);
            }
            break;

        case 4: // xxxx_1100 (L07D2) Draw 2x2 screen objects
            {
                uint8_t d = mem_read(de + 2);
                uint8_t e = mem_read(de + 3);
                uint16_t target_de = (d << 8) | e;

                uint8_t b_val = mem_read(bc);
                uint16_t src_hl = 0x1400 | b_val;

                if (target_de >= 0x4000 && target_de < 0x4400) draw_background_2x2(target_de, src_hl);
            }
            break;

        default:
            // Not used
            break;
    }
}

/*
 * Translates Bit4Controller
 * [ASM: 0720-073F]
 */
void bit4_controller(uint16_t bc, uint16_t de, uint16_t hl) {
    // 0720: LD A,(BC)
    uint8_t a = mem_read(bc);

    // 0722: AND $10
    if ((a & 0x10) == 0) {
        return; // 0724: RET Z
    }

    // 0726: AND $EF
    a &= 0xEF;

    // 0728: LD (BC),A
    mem_write(bc, a);
    
    // 0729: RLCA 3x
    a = (a << 3) | (a >> 5);
    
    // 072C: AND $07
    a &= 0x07;
    
    // The jump table offset maps directly to a function index
    execute_bit4_function(a, bc, de, hl);
}

/*
 * Translates Bit3Controller
 * [ASM: 0740-07EE]
 */
void bit3_controller(uint16_t bc, uint16_t de, uint16_t hl) {
    // 0740: LD A,(BC)
    uint8_t a = mem_read(bc);

    // 0742: AND $08
    if ((a & 0x08) == 0) {
        return; // 0744: RET Z
    }

    // 0746: AND $07
    uint8_t h_reg = a & 0x07;

    // 0749: RRCA 3x on the value (a & 0x07)
    uint8_t rotated = (h_reg >> 3) | (h_reg << 5);

    // 074C: OR H (top bits)
    a = rotated | h_reg;

    // 074D: OR $18
    a |= 0x18;

    // 074F: LD (BC),A
    mem_write(bc, a);
    
    // 0750: INC BC (go to control state B)
    bc++;
    
    // execute function based on top_bits (which is now in h_reg)
    execute_bit3_function(h_reg, bc, de, hl);
}

/*
 * Translates UpdateScreenObjects
 * [ASM: 0718-071F]
 * Note: original asm uses CALL $0718 which falls through to $0720 and then JP $0740.
 */
void update_screen_objects(uint16_t alien_state_addr, uint16_t screen_ram_addr) {
    uint16_t hl = 0x4400; // 0718: LD HL,$4400
    
    // 071B: CALL $0720 (Bit4Controller)
    bit4_controller(alien_state_addr, screen_ram_addr, hl);
    
    // 071B: JP $0740 (Bit3Controller)
    bit3_controller(alien_state_addr, screen_ram_addr, hl);
}

