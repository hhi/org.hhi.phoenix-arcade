#include "hw_video_audio.h"
#include "phoenix_hw.h"
#include "phoenix_state.h"
#include "phoenix_tables.h"
#include "utilities.h"
#include "z80_core.h"
#include <SDL2/SDL.h>
#include <stdio.h>

extern SDL_sem* g_sem_vblank_go;
extern SDL_sem* g_sem_frame_done;
extern volatile bool g_quit;

extern PhoenixState state;

extern void game_state_machine(void);
extern void update_scores_and_sound(void);
extern uint8_t coin_checking(void);
extern void prompt_for_start_game(void);
extern void splash_and_demo(void);
extern void update_sound_control_ram(uint8_t a);
extern void init_sound_screen(void);
extern void print_text_lines(uint16_t screen_draw_info_addr, uint8_t columns);

/*
 * Translates 0080 WaitVBlankCoin
 * Wait for the vertical blanking and then handle coin counting
 * [ASM: 0080-00B5]
 */
void wait_vblank_coin(void) {
    // Wait for vertical blanking. Signal completion of the *previous*
    // frame's full processing (skipped on the very first call, which has
    // no previous frame to report) before blocking for the next tick --
    // this preserves the original counter-compare handshake's one-frame
    // pipelining without busy-polling.
    static bool first_call = true;
    if (!first_call) {
        SDL_SemPost(g_sem_frame_done);
    }
    first_call = false;
    SDL_SemWait(g_sem_vblank_go);
    if (g_quit) return;

    // Lockstep verification snapshot, same point as jphoenix's interrupt()
    extern void platform_ram_dump_hook(void);
    platform_ram_dump_hook();

    // Render and queue this frame's audio, matching jphoenix's
    // endFrame() (called once per vblank interrupt).
    extern void platform_audio_frame_hook(void);
    platform_audio_frame_hook();

    // 008E-0097: read IN0 from hardware, shift current value to previous
    uint8_t new_in0 = hw_read_inputs();
    state.IN0Previous = state.IN0Current;
    state.IN0Current = new_in0;

    // 0098-009A: AddOneToMem($439B) -> 16-bit counter 439A:439B
    state.Counter9B++;
    if (state.Counter9B == 0) {
        state.Counter9A++;
    }

    if (state.CoinCount == 9) return;

    // 00A6-00AB: CheckInputBits bit 0 -- coin input transitioned 1 -> 0
    if ((state.IN0Current & 0x01) == 0 && (state.IN0Previous & 0x01) != 0) {
        state.CoinCount++;
        mem_write(0x4142, state.CoinCount + 0x20);
    }
}
/*
 * Translates ClearRAMBank
 * [ASM: 006B-0077]
 */
void clear_ram_bank(void) {
    // 006B: LD HL,$4BF8
    // 006E: LD A,$3F
    // 0070: LD (HL),$00
    // 0072: DEC HL
    // 0073: CP H
    // 0074: JP NZ,$0070
    // Note: We just use memset for 0x4000 to 0x4BF8 (inclusive)
    // The ASM clears downwards until H reaches 0x3F (so 0x4000 is included)
    for (uint16_t addr = 0x4000; addr <= 0x4BF8; addr++) {
        mem_write(addr, 0);
    }
}

/*
 * Translates InitSoundScreen
 * [ASM: 0050-006A]
 */
void init_sound_screen(void) {
    // 0050: LD H,$68; 0052: LD (HL),$00
    hw_write_sound_b(0);
    
    // 0054: LD H,$60; 0056: LD (HL),$00
    hw_write_sound_a(0);
    
    // 0058: LD H,$58; 005A: LD (HL),$00
    hw_write_scroll_register(0); // wait, scroll is just written via I/O
    
    // 005C: CALL $006B (ClearRAMBank)
    clear_ram_bank();
    
    // 005F: LD H,$50; 0061: LD (HL),$01
    hw_write_video_register(0x01); // Second memory bank
    
    // 0063: CALL $006B (ClearRAMBank)
    clear_ram_bank(); // We don't emulate double banking properly yet, but we'll call it to stay true to logic
    
    // 0066: LD H,$50; 0068: LD (HL),$00
    hw_write_video_register(0x00); // Back to first memory bank
}


/*
 * Translates 0x0000
 * Reset vector, the main entry point of the game.
 * [ASM: 0000-004F]
 */
void phoenix_main_loop(void) {
    init_sound_screen();
    print_text_lines(0x1800, 3);
    
    while (1) {
        wait_vblank_coin();
        if (g_quit) break;

        if (state.GameOrAttract == 0) {
            // 002D-0035: mute the TMS36XX and mirror it in RAM
            hw_write_sound_a(0x0F);
            hw_write_sound_b(0x0F);
            update_sound_control_ram(0x0F);

            extern uint8_t coin_checking(void);
            if (coin_checking() > 0) {
                prompt_for_start_game();
            } else {
                splash_and_demo();
            }
        } else {
            game_state_machine();
            update_scores_and_sound();
        }
    }
}

/*
 * Translates L03A0
 * Clear the background.
 * [ASM: 03A0-03AF]
 */
void clear_background(void) {
    // ASM 03A0: Clears from 0x4B3F down to 0x4800 with 0x00
    // 0x4800 to 0x4B3F is exactly 832 bytes (26 columns).
    for (int i = 0x0800; i < 0x0800 + 832; i++) {
        mem_write(i + 0x4000, 0x00);
    }
}

/*
 * Render sprites - abstracted loop over sprite structures
 */
void render_sprites(void) {
    // Translates the high level sprite looping and rendering (L0718)
    // Here we iterate over the alien and bird active slots and push to the frame buffer
    uint16_t sprite_base = 0x4B70;
    for (int i = 0; i < 16; i++) {
        uint8_t ctrl = mem_read(sprite_base + (i*4));
        if (ctrl & 0x18) {
            // Draw active sprite to framebuffer (emulator core responsibility)
        }
    }
}

extern void update_scores_and_sound(void);

void update_audio_registers(void) {
    // Translates L2700 Sound Control
    update_scores_and_sound();
}

/*
 * Translates PrintScore
 * Used only to skip the printing when both players are dead.
 * Actually 0280-0285 is L0280 (Compare HL/BC) but here 0280-02A4 includes it?
 * Wait, I will just implement clear_and_print_scores etc.
 */

/*
 * Translates ClearAndPrintScores
 * [ASM: 032E-034E]
 */
void clear_and_print_scores(void) {
    // 032E: LD HL,$4380 ... to $4387 (Clear scores)
    for (int i = 0x4380; i <= 0x4387; i++) {
        mem_write(i, 0);
    }
    
    // print player 1 score
    // 033A: LD L,$83
    // 033C: LD DE,$4261
    // 033F: LD B,$06
    print_number(0x4261, 0x4383, 6);
    
    // print player 2 score
    print_number(0x4021, 0x4387, 6);
}

/*
 * Translates UpdateLivesScreen
 * [ASM: 0367-0376]
 */
void update_lives_screen(void) {
    uint8_t p1 = state.Player1Lives;
    mem_write(0x42A2, p1 | 0x20);

    uint8_t p2 = state.Player2Lives;
    mem_write(0x4062, p2 | 0x20);
}

/*
 * Translates UpdateSoundControlRAM
 * [ASM: 0377-037D]
 */
void update_sound_control_ram(uint8_t a) {
    state.SoundControlA = a;
    state.SoundControlB = a;
}

/*
 * Translates ClearForeground
 * [ASM: 0380-039D]
 */
void clear_foreground(void) {
    // ASM 0380: Clears from 0x433F down to 0x4000, skipping L & 0x1F < 4
    // 0x433F means 832 bytes (26 columns of 32 bytes)
    for (int col = 0; col < 26; col++) {
        for (int row = 4; row < 32; row++) {
            uint16_t addr = 0x4000 + (col * 32) + row;
            mem_write(addr, 0x00);
        }
    }
}

/*
 * Translates SetBitsVideoRegister
 * [ASM: 041E-042E]
 */
void set_bits_video_register(void) {
    extern void hw_write_video_register(uint8_t);
    uint8_t bank = state.GameAndDemoOrSplash & 0x01;
    uint8_t palette = state.LevelAndRound & 0x02;
    hw_write_video_register(bank | palette);
}

// Translates CopyMemoryBank [ASM: 0460-049D] -- real implementation now
// lives in platform_sdl.c, where the two physical VRAM banks live.

/*
 * Translates StarsScrollDown
 * [ASM: 067A-06AF]
 */
void stars_scroll_down(void) {
    extern void hw_write_scroll_register(uint8_t);

    uint8_t a = state.CounterB9;
    state.CounterB9--;
    hw_write_scroll_register(a);
    
    if ((a & 0x07) != 0) {
        return; // continue after 8 pixels
    }
    
    // Fill the background with stars or mothership
    uint8_t b = 0x20;
    uint8_t c = 0x47;
    uint16_t de = 0x4B21; // BackgroundScreen + 321
    
    a = state.CounterB9;
    a = (a >> 3) | (a << 5); // RRCA 3 times
    a &= 0x1F;
    
    uint8_t e = (de & 0xFF) + a;
    de = (de & 0xFF00) | e;
    
    uint16_t hl = (state.M43B2 << 8) | state.M43B3;

    while (1) {
        mem_write(de, phoenix_starfield_or_mothership_byte(hl));
        hl = (hl & 0xFF00) | ((hl + 1) & 0xFF); // INC L
        
        uint16_t sub_result = (de & 0xFF) - b;
        de = (de & 0xFF00) | (sub_result & 0xFF);
        
        if (!(sub_result > 0xFF)) { // JP NC (No carry/borrow)
            continue;
        }
        
        uint8_t d = (de >> 8) - 1; // DEC D
        de = (d << 8) | (de & 0xFF);
        
        if (d != c) { // CP C; JP NZ
            continue;
        }
        
        break;
    }
    
    state.M43B3 = hl & 0xFF;
}

/*
 * Translates L07DC
 * Draws a 2x2 character block to the background.
 * [ASM: 07DC-07EF]
 */
void draw_background_2x2(uint16_t de, uint16_t hl) {
    // 07DC: LD A,(HL); 07DD: LD (DE),A
    mem_write(de, phoenix_background_2x2_byte(hl));

    // 07DE: INC HL; 07DF: INC DE
    hl++;
    de++;

    // 07E0: LD A,(HL); 07E1: LD (DE),A
    mem_write(de, phoenix_background_2x2_byte(hl));

    // 07E2: INC HL; 07E3: DEC DE
    hl++;
    de--;

    // 07E4: CALL $0217 (RightOneColumn)
    de = right_one_column(de);

    // 07E7: LD A,(HL); 07E8: LD (DE),A
    mem_write(de, phoenix_background_2x2_byte(hl));

    // 07E9: INC HL; 07EA: INC DE
    hl++;
    de++;

    // 07EB: LD A,(HL); 07EC: LD (DE),A
    mem_write(de, phoenix_background_2x2_byte(hl));

    // 07ED: DEC BC (we don't strictly need to do this as BC is only used by caller if they loop, but 06E4 doesn't loop)
    // 07EE: RET
}

/*
 * Translates AddPlanetsToBackground
 * [ASM: 06B0-06E7]
 */
void add_planets_to_background(void) {
    if (state.CounterB9 != state.M43AB) {
        return;
    }

    uint8_t c = state.CounterB9;
    
    // 06B9: LD A,(HL) -> HL is 43AB
    // 06BA: INC L -> HL is 43AC
    // 06BB: ADD A,(HL) -> A = 43AB + 43AC
    // 06BC: DEC L -> HL is 43AB
    // 06BD: LD (HL),A -> 43AB = A
    state.M43AB += state.M43AC;
    
    // 06BE: INC L, 06BF: INC L -> HL is 43AD
    // 06C0: INC (HL) -> 43AD++
    state.M43AD++;
    
    // 06C1: LD B,(HL)
    uint8_t b = state.M43AD;
    
    // 06C2: INC L -> HL is 43AE
    // 06C3: INC (HL) -> 43AE++
    state.M43AE++;
    
    // 06C4: LD A,(HL)
    uint8_t a = state.M43AE;
    
    // 06C5: LD HL,$1E20
    uint16_t hl = 0x1E20;
    
    // 06C8: AND $1F; 06CA: ADD A,L; 06CB: LD L,A
    a &= 0x1F;
    hl = (hl & 0xFF00) | ((hl + a) & 0xFF);
    
    // 06CC: LD D,(HL)
    uint8_t d = phoenix_planet_galaxy_page[hl - 0x1E20];
    
    // 06CD: ADD $20; 06CF: LD L,A -- Z80's A was already updated by the
    // 06CA "ADD A,L" folded into hl above (A==L after 06CB), so hl.L (not
    // the stale pre-06CA `a`) holds the correct value to add $20 to.
    a = (hl + 0x20) & 0xFF;
    hl = (hl & 0xFF00) | a;
    
    // 06D0: LD E,(HL)
    uint8_t e = phoenix_planet_galaxy_page[hl - 0x1E20];
    
    // 06D1: LD A,C; 06D2-06D4: RRCA x3; 06D5: AND $1E
    a = c;
    a = (a >> 3) | (a << 5);
    a &= 0x1E;
    
    // 06D7: ADD A,E; 06D8: ADD $02; 06DA: LD E,A
    a = (a + e + 0x02) & 0xFF;
    e = a;
    
    uint16_t de = (d << 8) | e;
    
    // 06DB: LD HL,$1E60
    hl = 0x1E60;
    
    // 06DE: LD A,B; 06DF: AND $1F; 06E1: ADD A,L; 06E2: LD L,A
    a = b;
    a &= 0x1F;
    hl = (hl & 0xFF00) | ((hl + a) & 0xFF);
    
    // 06E3: LD L,(HL)
    hl = (hl & 0xFF00) | phoenix_planet_galaxy_page[hl - 0x1E20];
    
    // 06E4: CALL $07DC
    draw_background_2x2(de, hl);
}

/*
 * Translates AddGalaxiesToBackground
 * [ASM: 2040-208A]
 */
void add_galaxies_to_background(void) {
    // 2040-2048: only act when CounterB9 reaches the galaxy schedule value
    if (state.CounterB9 != state.M43AF) {
        return;
    }
    uint8_t c = state.CounterB9;

    // 2049-204D: 43AF -= 43B0 (schedule next galaxy event)
    state.M43AF -= state.M43B0;

    // 204E-2051: 43B1++ selects the next of the 16 small galaxies
    state.M43B1++;
    uint8_t a = state.M43B1;

    // 2052-2061: T1E80 lookup: character, screen MSB, screen LSB
    uint16_t hl = 0x1E80;
    a &= 0x1F;
    hl = (hl & 0xFF00) | ((hl + a) & 0xFF);
    uint8_t chr = phoenix_planet_galaxy_page[hl - 0x1E20];           // 2059: LD B,(HL)
    hl = (hl & 0xFF00) | ((hl + 0x20) & 0xFF);
    uint8_t d = phoenix_planet_galaxy_page[hl - 0x1E20];             // 205D: LD D,(HL)
    hl = (hl & 0xFF00) | ((hl + 0x20) & 0xFF);
    uint8_t e = phoenix_planet_galaxy_page[hl - 0x1E20];             // 2061: LD E,(HL)

    // 2062-206A: vary the row with CounterB9 bits
    a = c;
    a = (uint8_t)((a >> 3) | (a << 5));  // RRCA x3
    a &= 0x1F;
    a = (uint8_t)(a + e + 1);            // ADD A,E; INC A
    e = a;

    // 206B-206C: write the single galaxy character to the background
    uint16_t de = (d << 8) | e;
    mem_write(de, chr);
}

/*
 * Translates L06F0
 * [ASM: 06F0-06F8]
 */
void update_scroll_register_and_fill_background(void) {
    stars_scroll_down();
    add_galaxies_to_background();
    add_planets_to_background();
}

// IN0 ($7000) and DSW0 ($7800) port reads.
uint8_t read_in0(void) { extern uint8_t hw_read_inputs(void); return hw_read_inputs(); }
uint8_t read_dsw0(void) { extern uint8_t hw_read_dsw(void); return hw_read_dsw(); }
