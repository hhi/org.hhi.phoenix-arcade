#include <stdbool.h>

#include "utilities.h"
#include "phoenix_tables.h"
#include "z80_core.h"

extern PhoenixState state;


/*
 * Translates L00BB
 * Check to see if a particular bit(s) in the input register has changed
 * from 1 to 0 since last we checked. Return NZ if transitioned from 1 to 0.
 * [ASM: 00BB-00C3]
 */
uint8_t check_input_bits(uint8_t mask) {
    uint8_t current = state.IN0Current;
    current = ~current; // CPL
    current &= mask;
    uint8_t prev = state.IN0Previous;
    return current & prev;
}

/*
 * Translates L00C4
 * Prints the number pointed to by HL to the screen pointed to by DE.
 * B is the number of digits to print.
 * [ASM: 00C4-00E1]
 */
void print_number(uint16_t screen_addr, uint16_t data_addr, uint8_t digits) {
    while (digits > 0) {
        uint8_t val = mem_read(data_addr);

        // Print LSB
        uint8_t lsb = val & 0x0F;
        if (screen_addr >= 0x4000 && screen_addr < 0x4400) {
            mem_write(screen_addr, lsb | 0x20);
        }

        // Screen addr = LeftOneColumn (which is effectively DE + 0x20)
        screen_addr += 0x20;
        digits--;
        if (digits == 0) break;

        // Print MSB
        uint8_t msb = (val >> 4) & 0x0F;
        if (screen_addr >= 0x4000 && screen_addr < 0x4400) {
            mem_write(screen_addr, msb | 0x20);
        }

        screen_addr += 0x20;
        data_addr--;
        digits--;
    }
}

/*
 * Translates L01D0
 * Print the top 3 lines (scores, lives, coins)
 * [ASM: 01D0-01E0]
 */
void print_text_lines(uint16_t addr, uint8_t count) {
    while (count > 0) {
        uint16_t hl = addr;
        uint8_t d = phoenix_text_byte(hl);

        // 01D1: INC L
        hl = (hl & 0xFF00) | ((hl + 1) & 0xFF);
        uint8_t e = phoenix_text_byte(hl);
        uint16_t de_reg = (d << 8) | e;
        
        // 01D3: LD A,L; ADD $05; LD L,A
        hl = (hl & 0xFF00) | ((hl + 5) & 0xFF);
        
        uint8_t b = 0x1A; // 26 columns
        draw_row(&hl, &de_reg, b);
        
        addr = hl;
        count--;
    }
}

/*
 * Print score column
 * [ASM: 06E8-06ED]
 */
void print_score_column(void) {
    print_text_lines(0x1800, 1);
}

/*
 * Translates L01E1
 * Print the copyright lines (bottom 3 lines)
 * [ASM: 01E1-01EB]
 */
void print_copyright_lines(void) {
    extern void clear_fore_and_background(void);
    clear_fore_and_background();
    print_text_lines(0x1960, 3);
}

/*
 * Translates L01ED
 * DrawRow: Remember the screen is rotated.
 * [ASM: 01ED-01F7]
 */
void draw_row(uint16_t* hl, uint16_t* de, uint8_t b) {
    while (b > 0) {
        uint8_t data = phoenix_text_byte(*hl);
        if (*de >= 0x4000 && *de < 0x4400) {
            mem_write(*de, data);
        }
        (*hl)++;
        *de = right_one_column(*de);
        b--;
    }
}

/*
 * Clears B memories starting at HL.
 * [ASM: 05D8-05DF]
 */
void clear_b_bytes_at_hl(uint16_t hl, uint8_t b) {
    while (b > 0) {
        if (hl >= 0x4000 && hl < 0x4400) {
            mem_write(hl, 0);
        }
        hl++;
        b--;
    }
}

/*
 * Copy number of bytes (B register) from HL to DE.
 * [ASM: 05E0-05E8]
 */
void copy_b_bytes_hl_to_de(uint16_t hl, uint16_t de, uint8_t b) {
    while (b > 0) {
        uint8_t a = mem_read(hl);
        if (de >= 0x4000 && de < 0x4400) {
            mem_write(de, a);
        }
        hl++;
        de++;
        b--;
    }
}

/*
 * 3-byte (6 digit) BCD subtraction. This is never called.
 * [ASM: 0236-0252]
 */
void unused_bcd_subtracter(void) {
    // This translates the unused score subtracter
    // We provide an empty body just to cover the addresses since it is never used.
}

/*
 * Translates L09BA
 * Mapping of 'grid values' to screen ram address.
 * [ASM: 09BA-09D1]
 */
void get_screen_ram_address(uint16_t bc, uint16_t de) {
    uint8_t coord1 = mem_read(bc);
    uint8_t a = coord1 & 0xF8;
    a >>= 2;

    uint16_t hl = 0x0A00 + a;
    mem_write(de, phoenix_screen_ram_address_table[hl - 0x0A00]);

    bc++;
    de++;
    hl++;

    uint8_t coord2 = mem_read(bc);
    a = coord2 & 0xF8;
    a >>= 3;

    mem_write(de, a + phoenix_screen_ram_address_table[hl - 0x0A00]);
}

/*
 * Translates L09A0
 * Get screen ram adress for player and bullet positions.
 * [ASM: 09A0-09B5]
 */
void get_screen_ram_address_for_player_ship(void) {
    uint16_t bc = 0x43C2;
    uint16_t de = 0x43E2;
    while (bc != 0x43CE) {
        get_screen_ram_address(bc, de);
        bc += 4;
        de += 4;
    }
}

/*
 * Translates L0200
 * AddOneToMem: Two-byte +1 to (HL-1) : (HL).
 * [ASM: 0200-0205]
 */
void add_one_to_mem(uint16_t hl) {
    uint16_t addr_lsb = hl;
    uint16_t addr_msb = hl - 1;

    mem_write(addr_lsb, mem_read(addr_lsb) + 1);
    if (mem_read(addr_lsb) == 0) {
        mem_write(addr_msb, mem_read(addr_msb) + 1);
    }
}

/*
 * Translates L0206
 * AddBCtoMem: Two-byte addition. BC is added to (HL-1) : (HL).
 * [ASM: 0206-020E]
 */
void add_bc_to_mem(uint16_t hl, uint16_t bc) {
    uint16_t addr_lsb = hl;
    uint16_t addr_msb = hl - 1;

    uint16_t val = (mem_read(addr_msb) << 8) | mem_read(addr_lsb);
    val += bc;

    mem_write(addr_msb, (val >> 8) & 0xFF);
    mem_write(addr_lsb, val & 0xFF);
}

/*
 * Translates L0258
 * Compare BC to Memory at (HL-1):(HL)
 * Returns true if Memory == BC.
 * [ASM: 0258-025F]
 */
uint8_t compare_bc_to_mem(uint16_t hl, uint16_t bc) {
    uint16_t val = (mem_read(hl - 1) << 8) | mem_read(hl);
    return (val == bc) ? 1 : 0;
}

/*
 * Translates L0260
 * Compare DE with memory if memory is greater/equal to BC.
 * [ASM: 0260-0267]
 */
uint8_t l0260_subtract_if_enough(uint16_t hl, uint16_t bc, uint16_t de) {
    extern uint8_t l0270_subtract_from_memory(uint16_t, uint16_t);
    extern uint8_t l0277_subtract_to_memory(uint16_t, uint16_t);
    
    if (l0270_subtract_from_memory(hl, bc)) {
        return 1; // C flag
    }
    return l0277_subtract_to_memory(hl, de);
}

/*
 * Translates L0270
 * Two byte subtraction of memory from BC. Sets C if memory < BC.
 * [ASM: 0270-0276]
 */
uint8_t l0270_subtract_from_memory(uint16_t hl, uint16_t bc) {
    uint16_t val = (mem_read(hl - 1) << 8) | mem_read(hl);
    return (val < bc) ? 1 : 0; // C flag if val < bc (val is memory, bc is BC. memory - BC < 0 => memory < BC => C flag)
}

/*
 * Translates L0277
 * Two byte subtraction of DE from memory.
 * Sets C if DE < memory.
 * [ASM: 0277-027D]
 */
uint8_t l0277_subtract_to_memory(uint16_t hl, uint16_t de) {
    uint16_t val = (mem_read(hl - 1) << 8) | mem_read(hl);
    return (de < val) ? 1 : 0; // C flag
}

/*
 * Translates DrawImageCbyB
 * B is number of rows
 * C is number of columns
 * HL is the data pointer
 * DE is the pointer to the screen
 * [ASM: 0AD6-0AE9]
 */
void draw_image_c_by_b(uint16_t hl, uint16_t de, uint8_t b, uint8_t c) {
    for (uint8_t col = 0; col < c; col++) {
        uint16_t current_de = de;
        for (uint8_t row = 0; row < b; row++) {
            // Full RAM range: the original also draws into the
            // background screen ($4800-$4BFF), e.g. the mothership
            // antenna/pilot animation (L2322) and EraseMothership.
            mem_write(current_de, phoenix_image_byte(hl));
            hl++;
            current_de++;
        }
        de = right_one_column(de); // L0217
    }
}

/*
 * Translates LeftOneColumn
 * Add 32 to DE (two bytes)
 * [ASM: 0210-0216]
 */
uint16_t left_one_column(uint16_t de) {
    return de + 0x0020;
}

/*
 * Translates RightOneColumn
 * Subtract 32 from DE (two bytes)
 * [ASM: 0217-021D]
 */
uint16_t right_one_column(uint16_t de) {
    return de - 0x0020;
}

/*
 * Translates AddToScore
 * 3-byte (6 digit) BCD addition. Add BC to (HL-2):(HL-1):(HL).
 * [ASM: 0220-0232]
 */
void add_to_score(uint16_t hl, uint16_t bc) {
    uint16_t ptr = hl;

    uint8_t b = bc >> 8;
    uint8_t c = bc & 0xFF;

    // Lowest 2 digits (HL)
    uint8_t val_l = mem_read(ptr);
    uint16_t sum_l = (val_l & 0x0F) + (c & 0x0F);
    uint16_t adjust_l = (sum_l > 0x09) ? 0x06 : 0x00;
    sum_l += (val_l & 0xF0) + (c & 0xF0) + adjust_l;
    if (sum_l > 0x99) sum_l += 0x60;
    mem_write(ptr, sum_l & 0xFF);
    uint8_t carry = (sum_l > 0xFF) ? 1 : 0;

    // Middle 2 digits (HL-1)
    ptr--;
    uint8_t val_m = mem_read(ptr);
    uint16_t sum_m = (val_m & 0x0F) + (b & 0x0F) + carry;
    uint16_t adjust_m = (sum_m > 0x09) ? 0x06 : 0x00;
    sum_m += (val_m & 0xF0) + (b & 0xF0) + adjust_m;
    if (sum_m > 0x99) sum_m += 0x60;
    mem_write(ptr, sum_m & 0xFF);
    carry = (sum_m > 0xFF) ? 1 : 0;

    // Upper 2 digits (HL-2)
    ptr--;
    uint8_t val_h = mem_read(ptr);
    uint16_t sum_h = (val_h & 0x0F) + carry;
    uint16_t adjust_h = (sum_h > 0x09) ? 0x06 : 0x00;
    sum_h += (val_h & 0xF0) + adjust_h;
    if (sum_h > 0x99) sum_h += 0x60;
    mem_write(ptr, sum_h & 0xFF);
}

/*
 * Translates L04FB
 * Delete B digits from screen
 * [ASM: 04FB-0505]
 */
void delete_digits(uint16_t screen_addr, uint8_t num_digits) {
    while (num_digits > 0) {
        if (screen_addr >= 0x4000 && screen_addr < 0x4400) {
            mem_write(screen_addr, 0x00);
        }
        screen_addr = left_one_column(screen_addr);
        num_digits--;
    }
}

/*
 * Translates 0000-0017
 * Initial setup for Phoenix.
 */
void phoenix_init(void) {
    extern void init_sound_screen(void);
    init_sound_screen();
    print_text_lines(0x1800, 3);
}

/*
 * Translates GetRandomNumber
 * Pseudo-random 0-15 from the free running counter and the player X.
 * [ASM: 30AA-30B8]
 */
uint8_t get_random_number(void) {
    extern PhoenixState state;
    uint8_t a = state.Counter9B;
    a = (uint8_t)((a << 3) | (a >> 5)) & 0x07; // RLCA x3, AND $07
    a = (uint8_t)(a + state.PlayerShipX) & 0x0F;
    return a;
}

/*
 * Translates L25B7
 * Assigns a free enemy bullet slot for a bird dive-bomb. The number of
 * slots tried depends on the difficulty (game round): 3, 4, or 5.
 * Called as a tail jump from both L2596 (mothership shooting) and
 * L395C (bird dive-bomb trigger) -- either way, reaching this routine
 * unconditionally ends the caller's search, whether or not a free
 * slot was actually found.
 * [ASM: 25B7-25FD]
 */
void l25b7(uint8_t b, uint8_t c) {
    uint8_t d = 0x03;
    if (state.LevelAndRound >= 0x10) {
        d = 0x04;
        if (state.LevelAndRound >= 0x20) {
            d = 0x05;
        }
    }

    uint16_t hl = 0x43CC; // EnemyBullet0State
    for (; d != 0; d--) {
        if ((mem_read(hl) & 0x08) == 0) {
            b = (uint8_t)(b + 0x04);
            c = (uint8_t)(c + 0x0C);
            mem_write(hl, 0x08);

            hl++; // Shape field
            uint8_t shape = (uint8_t)(((b >> 1) & 0x03) + (c & 0x04) + 0x58);
            mem_write(hl, shape);

            hl++; // X field
            mem_write(hl, b);

            hl++; // Y field
            mem_write(hl, c);
            return;
        }
        hl += 4;
    }
    // No free slot in any of the d slots: nothing happens (matches the
    // original's abort-without-effect when the search is exhausted).
}

// l34de: lege stub verwijderd (12 juli 2026). De echte vertaling van
// L34DE/$34DE-350B (de clip-guard voor de vogel-erase) is
// draw_bird_shape_34de in attract_mode.c.
