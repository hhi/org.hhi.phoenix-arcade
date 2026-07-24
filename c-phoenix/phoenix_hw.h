#ifndef PHOENIX_HW_H
#define PHOENIX_HW_H

#include <stdint.h>
#include <stdbool.h>

/* 
 * Hardware I/O Abstraction Layer 
 * 
 * This file decouples the game logic from the specific memory-mapped I/O
 * of the Phoenix arcade hardware. When porting the game, implement these
 * functions for the target platform (e.g. using SDL2, WebAssembly, etc).
 */

/* ==========================================================
 * INPUTS (Mapped to 0x7000 on original hardware)
 * Bit goes from 1 to 0 when pressed.
 * ========================================================== */
#define BTN_LEFT           0x40 // bit 6 (0xBF)
#define BTN_RIGHT          0x20 // bit 5 (0xDF)
#define BTN_FIRE           0x10 // bit 4 (0xEF)
#define BTN_SHIELD         0x80 // bit 7 (0x7F)
#define BTN_START_1P       0x02 // bit 1 (0xFD)
#define BTN_START_2P       0x04 // bit 2 (0xFB)
#define BTN_COIN           0x01 // bit 0 (0xFE)

/* 
 * Returns a byte representing the state of all inputs.
 * Following the original hardware: A bit is 0 if the button is PRESSED, 1 if unpressed.
 * So 0xFF means no buttons are pressed.
 */
uint8_t hw_read_inputs(void);

/* ==========================================================
 * DIP SWITCHES (Mapped to 0x7800 on original hardware)
 * ========================================================== */
/*
 * Reads the DIP switch settings.
 * Bits 0-1: Number of lives (11=3, 01=4, 10=5, 00=6)
 * Bits 2-3: Bonus lives at (11=3K/30K, 01=4K/40K, 10=5K/50K, 00=6K/60K)
 * Bit  4  : Coinage (1=1 coin/1 credit, 0=2 coins/1 credit)
 * Bit  5  : Cabinet mode (1=cocktail, 0=upright)
 * Bit  7  : VBLANK flag (0=in VBLANK, 1=not in VBLANK)
 */
uint8_t hw_read_dsw(void);

/* Helper to check if currently in VBLANK */
bool hw_is_vblank(void);

/* ==========================================================
 * VIDEO (Mapped to 0x5000, 0x5800 on original hardware)
 * ========================================================== */
/* 
 * Video Register (0x5000)
 * Bit 0: Selects RAM bank (and screen flip for cocktail mode)
 * Bit 1: Palette control
 */
void hw_write_video_register(uint8_t val);

void hw_toggle_palette_bank(void);

/*
 * Scroll Register (0x5800)
 * Background vertical scroll offset.
 */
void hw_write_scroll_register(uint8_t val);

/* ==========================================================
 * SOUND (Mapped to 0x6000, 0x6800 on original hardware)
 * ========================================================== */
/* Sound Control A (0x6000) */
void hw_write_sound_a(uint8_t val);

/* Sound Control B (0x6800) */
void hw_write_sound_b(uint8_t val);

#endif // PHOENIX_HW_H
