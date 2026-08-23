#include "sprite_rendering.h"
#include "phoenix_state.h"
#include "phoenix_tables.h"
#include "z80_core.h"
#include <stdbool.h>

extern PhoenixState state;
extern uint16_t right_one_column(uint16_t screen_address);

/*
 * Helper to jump into the Bit4 / Bit3 jump table logic.
 */
static void erase_object_shape(uint8_t shape_index, uint16_t object_state_address,
                               uint16_t object_screen_address, uint16_t scratch_address) {
    (void)object_state_address;
    (void)scratch_address;

    switch (shape_index) {
        case 0: // 0001_xxxx (L0763) Delete 1x1 screen objects
            {
                uint8_t screen_high_byte = mem_read(object_screen_address);
                uint8_t screen_low_byte = mem_read(object_screen_address + 1);
                uint16_t tile_address = (screen_high_byte << 8) | screen_low_byte;
                if (tile_address >= 0x4000 && tile_address < 0x4400) {
                    mem_write(tile_address, 0);
                }
            }
            break;

        case 1: // 0011_xxxx (L0779) Delete 2x1 screen objects
            {
                uint8_t screen_high_byte = mem_read(object_screen_address);
                uint8_t screen_low_byte = mem_read(object_screen_address + 1);
                uint16_t tile_address = (screen_high_byte << 8) | screen_low_byte;

                if (tile_address >= 0x4000 && tile_address < 0x4400) mem_write(tile_address, 0); // delete left part
                tile_address = right_one_column(tile_address);
                if (tile_address >= 0x4000 && tile_address < 0x4400) mem_write(tile_address, 0); // delete right part
            }
            break;

        case 3: // 0111_xxxx (L079E) Delete 1x2 screen objects
            {
                uint8_t screen_high_byte = mem_read(object_screen_address);
                uint8_t screen_low_byte = mem_read(object_screen_address + 1);
                uint16_t tile_address = (screen_high_byte << 8) | screen_low_byte;

                if (tile_address >= 0x4000 && tile_address < 0x4400) mem_write(tile_address, 0); // delete upper part
                tile_address = (tile_address & 0xFF00) | ((tile_address + 1) & 0xFF); // INC E actually.
                if (tile_address >= 0x4000 && tile_address < 0x4400) mem_write(tile_address, 0); // delete lower part
            }
            break;

        case 4: // 1001_xxxx (L07BE) Delete 2x2 screen objects
            {
                uint8_t screen_high_byte = mem_read(object_screen_address);
                uint8_t screen_low_byte = mem_read(object_screen_address + 1);
                uint16_t tile_address = (screen_high_byte << 8) | screen_low_byte;

                if (tile_address >= 0x4000 && tile_address < 0x4400) mem_write(tile_address, 0); // delete upper left part
                uint16_t adjacent_tile_address = (tile_address & 0xFF00) | ((tile_address + 1) & 0xFF);
                if (adjacent_tile_address >= 0x4000 && adjacent_tile_address < 0x4400) mem_write(adjacent_tile_address, 0); // delete upper right part

                tile_address = right_one_column(tile_address);
                if (tile_address >= 0x4000 && tile_address < 0x4400) mem_write(tile_address, 0); // delete lower left part

                adjacent_tile_address = (tile_address & 0xFF00) | ((tile_address + 1) & 0xFF);
                if (adjacent_tile_address >= 0x4000 && adjacent_tile_address < 0x4400) mem_write(adjacent_tile_address, 0); // delete lower right part
            }
            break;

        default:
            // Not used
            break;
    }
}

static void draw_object_shape(uint8_t shape_index, uint16_t shape_state_address,
                              uint16_t object_screen_address, uint16_t scratch_address) {
    (void)scratch_address;
    extern void draw_background_2x2(uint16_t de_reg, uint16_t hl_reg);

    switch (shape_index) {
        case 0: // xxxx_1000 (L076D) Draw 1x1 screen objects
            {
                uint8_t screen_high_byte = mem_read(object_screen_address + 2);
                uint8_t screen_low_byte = mem_read(object_screen_address + 3);
                uint16_t tile_address = (screen_high_byte << 8) | screen_low_byte;

                uint8_t tile = mem_read(shape_state_address);
                if (tile_address >= 0x4000 && tile_address < 0x4400) mem_write(tile_address, tile);
            }
            break;

        case 1: // xxxx_1001 (L0788) Draw 2x1 screen objects
            {
                uint8_t screen_high_byte = mem_read(object_screen_address + 2);
                uint8_t screen_low_byte = mem_read(object_screen_address + 3);
                uint16_t tile_address = (screen_high_byte << 8) | screen_low_byte;

                uint8_t tile = mem_read(shape_state_address);
                uint16_t shape_address = 0x1400 | tile;

                if (tile_address >= 0x4000 && tile_address < 0x4400) mem_write(tile_address, phoenix_sprite_character_block_shapes[shape_address - 0x1400]);
                shape_address++;

                tile_address = right_one_column(tile_address);

                if (tile_address >= 0x4000 && tile_address < 0x4400) mem_write(tile_address, phoenix_sprite_character_block_shapes[shape_address - 0x1400]);
            }
            break;

        case 3: // xxxx_1011 (L07AA) Draw 1x2 screen objects
            {
                uint8_t screen_high_byte = mem_read(object_screen_address + 2);
                uint8_t screen_low_byte = mem_read(object_screen_address + 3);
                uint16_t tile_address = (screen_high_byte << 8) | screen_low_byte;

                uint8_t tile = mem_read(shape_state_address);
                uint16_t shape_address = 0x1400 | tile;

                if (tile_address >= 0x4000 && tile_address < 0x4400) mem_write(tile_address, phoenix_sprite_character_block_shapes[shape_address - 0x1400]);
                shape_address++;
                tile_address = (tile_address & 0xFF00) | ((tile_address + 1) & 0xFF); // INC E
                if (tile_address >= 0x4000 && tile_address < 0x4400) mem_write(tile_address, phoenix_sprite_character_block_shapes[shape_address - 0x1400]);
            }
            break;

        case 4: // xxxx_1100 (L07D2) Draw 2x2 screen objects
            {
                uint8_t screen_high_byte = mem_read(object_screen_address + 2);
                uint8_t screen_low_byte = mem_read(object_screen_address + 3);
                uint16_t tile_address = (screen_high_byte << 8) | screen_low_byte;

                uint8_t tile = mem_read(shape_state_address);
                uint16_t shape_address = 0x1400 | tile;

                if (tile_address >= 0x4000 && tile_address < 0x4400) draw_background_2x2(tile_address, shape_address);
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
void bit4_controller(uint16_t object_state_address, uint16_t object_screen_address, uint16_t scratch_address) {
    // 0720: LD A,(BC)
    uint8_t object_control = mem_read(object_state_address);

    // 0722: AND $10
    if ((object_control & 0x10) == 0) {
        return; // 0724: RET Z
    }

    // 0726: AND $EF
    object_control &= 0xEF;

    // 0728: LD (BC),A
    mem_write(object_state_address, object_control);
    
    // 0729: RLCA 3x
    uint8_t erase_shape_index = (object_control << 3) | (object_control >> 5);
    
    // 072C: AND $07
    erase_shape_index &= 0x07;
    
    // The jump table offset maps directly to a function index
    erase_object_shape(erase_shape_index, object_state_address, object_screen_address, scratch_address);
}

/*
 * Translates Bit3Controller
 * [ASM: 0740-07EE]
 */
void bit3_controller(uint16_t object_state_address, uint16_t object_screen_address, uint16_t scratch_address) {
    // 0740: LD A,(BC)
    uint8_t object_control = mem_read(object_state_address);

    // 0742: AND $08
    if ((object_control & 0x08) == 0) {
        return; // 0744: RET Z
    }

    // 0746: AND $07
    uint8_t shape_index = object_control & 0x07;

    // 0749: RRCA 3x on the value (a & 0x07)
    uint8_t rotated_shape_index = (shape_index >> 3) | (shape_index << 5);

    // 074C: OR H (top bits)
    object_control = rotated_shape_index | shape_index;

    // 074D: OR $18
    object_control |= 0x18;

    // 074F: LD (BC),A
    mem_write(object_state_address, object_control);
    
    // 0750: INC BC (go to control state B)
    object_state_address++;
    
    // execute function based on top_bits (which is now in h_reg)
    draw_object_shape(shape_index, object_state_address, object_screen_address, scratch_address);
}

/*
 * Translates UpdateScreenObjects
 * [ASM: 0718-071F]
 * Note: original asm uses CALL $0718 which falls through to $0720 and then JP $0740.
 */
void update_screen_objects(uint16_t object_state_address, uint16_t object_screen_address) {
    uint16_t scratch_address = 0x4400; // 0718: LD HL,$4400
    
    // 071B: CALL $0720 (Bit4Controller)
    bit4_controller(object_state_address, object_screen_address, scratch_address);
    
    // 071B: JP $0740 (Bit3Controller)
    bit3_controller(object_state_address, object_screen_address, scratch_address);
}
