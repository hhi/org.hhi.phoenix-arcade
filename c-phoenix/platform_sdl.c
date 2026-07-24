#include <SDL2/SDL.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "phoenix_hw.h"
#include "phoenix_state.h"
#ifndef C2_RENDERER
#include "rom_data.h"
#else
#include "c2_renderer.h"
#endif
#include "sound.h"
#include "z80_core.h"
#include "coverage.h"

// External game state and loops
PhoenixState state = {0};
extern void phoenix_init(void);
extern void phoenix_main_loop(void);

// Hardware State Globals
static volatile uint8_t g_inputs = 0xFF; // All bits 1 (unpressed)
static volatile uint8_t g_dsw = 0x00;    // DIP switches
static volatile uint8_t g_scroll_reg = 0x00; // Vertical scroll offset
static volatile uint8_t g_palette_bank = 0x00; // Palette bank selected via video register
static volatile uint8_t g_vram_page = 0x00; // VRAM page selected via video register
// ADR-001: blocking handshake between the render thread (producer of
// vblank ticks) and the logic thread (consumer), replacing the previous
// SDL_Delay(1) busy-poll pair on a shared counter/ack.
SDL_sem* g_sem_vblank_go = NULL;
SDL_sem* g_sem_frame_done = NULL;
volatile bool g_quit = false;

/* ==========================================================
 * HARDWARE ABSTRACTION IMPLEMENTATIONS
 * ========================================================== */

uint8_t hw_read_inputs(void) {
    return g_inputs;
}

uint8_t hw_read_dsw(void) {
    return g_dsw;
}

bool hw_is_vblank(void) {
    return false; // Deprecated, use call_0080 sync
}

// Two physical VRAM-like banks, mirroring jphoenix's mem[]<->videoRamPages[]
// swap: PhoenixState is a packed, exact 0xC00-byte image of $4000-$4BFF,
// and `state` always holds whichever bank is currently mapped in (matching
// the real hardware's bit 0 of the $5000 video register). bank_storage[1]
// is the "other" bank's content, saved/restored on every real bank switch.
// Zero-initialized like jphoenix's `new int[2][0x1000]`, so a first-ever
// switch to a never-yet-active bank sees a clean slate, matching real RAM.
static uint8_t bank_storage[2][sizeof(PhoenixState)];

static void bank_swap_to(uint8_t new_page) {
    new_page &= 0x01;
    if (new_page == g_vram_page) return;
    memcpy(bank_storage[g_vram_page], &state, sizeof(PhoenixState));
    memcpy(&state, bank_storage[new_page], sizeof(PhoenixState));
    g_vram_page = new_page;
}

void hw_write_video_register(uint8_t val) {
    bank_swap_to(val & 0x01);
    g_palette_bank = (val >> 1) & 1;
}

void hw_toggle_palette_bank(void) {
    g_palette_bank ^= 1;
}

/*
 * Translates CopyMemoryBank
 * Copies specific regions (foreground tiles minus their per-column
 * header bytes, $4380-$43B7 general storage, $4BC0-$4BFF bird storage)
 * from one physical VRAM bank into the other. The real routine toggles
 * the $5000 port per byte (read while 'from' is selected, write while
 * 'to' is selected), so it leaves 'to' as the active bank afterward --
 * that side effect is what actually "changes the visible player" in the
 * attract-mode demo (see L04A0/state_0_new_game_start).
 * [ASM: 0460-049D]
 */
void copy_memory_bank(uint8_t from_bank, uint8_t to_bank) {
    from_bank &= 0x01;
    to_bank &= 0x01;

    uint8_t from_snapshot[sizeof(PhoenixState)];
    if (from_bank == g_vram_page) {
        memcpy(from_snapshot, &state, sizeof(PhoenixState));
    } else {
        memcpy(from_snapshot, bank_storage[from_bank], sizeof(PhoenixState));
    }

    // L0466 writes the source and destination bank numbers (0 or 1) to
    // $5000 for every copied byte. Besides selecting the destination bank,
    // the final write clears palette bit 1. Preserve that video side effect:
    // a plain bank_swap_to() would leave the previous player's palette active.
    hw_write_video_register(to_bank);

    // Region 1: the first 4 bytes of every 32-byte column ($4000, $4020,
    // $4040, ... $4320 and their +1/+2/+3 neighbors) -- the shared
    // scoreboard header (SCORE1/HI-SCORE/SCORE2 labels at row 0, the
    // score digits at row 1, COIN00 at row 2), which must stay in sync
    // across both players' banks. Confirmed against the real ASM (0460-
    // 049D) by simulating its exact byte/column stepping: it walks E
    // through groups of 4 within each column, jumping columns via a
    // "mask off the low nibble, subtract 0x20, borrow -> DEC D" trick,
    // covering exactly rows 0-3 of all 26 columns (104 bytes) before
    // moving on to region 2 -- the opposite range from what this loop
    // used to copy (rows 4-31), which meant the scoreboard header only
    // ever existed in bank 0 and went completely blank on every switch
    // to player 2's bank. Rows 4-31 hold each player's own dynamic
    // in-play foreground (ship/aliens/bullets) and are correctly left
    // alone -- that part of the original comment's intent was right,
    // just applied to the wrong half of the row range.
    for (int col = 0; col < 26; col++) {
        for (int row = 0; row < 4; row++) {
            int off = col * 32 + row;
            mem_write(0x4000 + off, from_snapshot[off]);
        }
    }
    // Region 2: $4380-$43B7 (general game-state storage)
    for (int addr = 0x4380; addr < 0x43B8; addr++) {
        mem_write(addr, from_snapshot[addr - 0x4000]);
    }
    // Region 3: $4BC0-$4BFF (bird extended storage)
    for (int addr = 0x4BC0; addr < 0x4C00; addr++) {
        mem_write(addr, from_snapshot[addr - 0x4000]);
    }
}

void hw_write_scroll_register(uint8_t val) {
    g_scroll_reg = val;
}

void hw_write_sound_a(uint8_t val) {
    sound_write_control_a(val);
}

void hw_write_sound_b(uint8_t val) {
    sound_write_control_b(val);
}

// SDL audio output (interactive mode only -- see the headless_frames
// guard where this is opened in main()). A dedicated device queue
// rather than a real-time callback: sound_render_frame() is called
// once per game frame from the logic thread (mirroring jphoenix's
// endFrame(), called once per vblank interrupt) and the resulting
// buffer is queued in one shot, matching the existing "produce a
// frame's worth, hand off" pattern already used for video.
static SDL_AudioDeviceID g_audio_device = 0;

void platform_audio_frame_hook(void) {
    int16_t buf[SOUND_MAX_FRAME_SAMPLES];
    int n = sound_render_frame(buf);
    if (g_audio_device != 0 && n > 0) {
        SDL_QueueAudio(g_audio_device, buf, (Uint32)(n * sizeof(int16_t)));
    }
}

/* ==========================================================
 * GAME THREAD & MAIN LOOP
 * ========================================================== */

// The game loop runs infinitely just like the arcade board.
// We run it in a separate thread so it doesn't block the SDL event pump.
static int game_thread_func(void* ptr) {
    (void)ptr;
    phoenix_init();
    phoenix_main_loop();
    return 0;
}

#ifndef C2_RENDERER
// MAME-accurate color-PROM decoding, ported from jphoenix's
// PhoenixPalette.java so both emulators render the same PROM bytes to
// the same RGB values. Two passes:
//   1. computeChannel(): a resistor-network voltage model per R/G/B
//      channel (100 ohm / 270 ohm weighted conductances), not a naive
//      linear 0/85/170/255 scale.
//   2. A global luminance-stretch + YUV resaturation pass across the
//      whole 128-entry palette (matching MAME's driver-level palette
//      normalization for this board).
// prom_idx (0-127) is already the raw hardware PROM address -- it is
// bit-identical to jphoenix's bitswap7(pen) result, so no extra
// permutation step is needed here; only the color math was simplified
// before.
static int compute_channel(int inputs) {
    double conductance = 1.0 / 100.0 + 1.0 / 270.0;
    double current = 5.0 / 100.0;
    if ((inputs & 0x01) == 0) {
        conductance += 1.0 / 270.0;
        current += 0.05 / 270.0;
    }
    if ((inputs & 0x02) == 0) {
        conductance += 1.0;
        current += 0.05;
    }
    double voltage = current / conductance;
    return (int)(voltage * 255.0 / 5.0 + 0.4);
}

static int clamp_byte(int value) {
    if (value < 0) return 0;
    if (value > 255) return 255;
    return value;
}

static uint8_t g_palette_r[128];
static uint8_t g_palette_g[128];
static uint8_t g_palette_b[128];
static bool g_palette_ready = false;

static void init_phoenix_palette(void) {
    int raw_r[128], raw_g[128], raw_b[128], lum[128];
    for (int addr = 0; addr < 128; addr++) {
        uint8_t low = palette_prom_b[addr];  // ic40
        uint8_t high = palette_prom_a[addr]; // ic41
        raw_r[addr] = compute_channel((low & 0x01) | ((high & 0x01) << 1));
        raw_g[addr] = compute_channel(((low >> 2) & 0x01) | (((high >> 2) & 0x01) << 1));
        raw_b[addr] = compute_channel(((low >> 1) & 0x01) | (((high >> 1) & 0x01) << 1));
    }

    int min_lum = 1000 * 255;
    int max_lum = 0;
    for (int i = 0; i < 128; i++) {
        lum[i] = 299 * raw_r[i] + 587 * raw_g[i] + 114 * raw_b[i];
        if (lum[i] < min_lum) min_lum = lum[i];
        if (lum[i] > max_lum) max_lum = lum[i];
    }
    for (int i = 0; i < 128; i++) {
        int u = (raw_b[i] - lum[i] / 1000) * 492 / 1000;
        int v = (raw_r[i] - lum[i] / 1000) * 877 / 1000;
        int target = ((lum[i] - min_lum) * 256) / (max_lum - min_lum);
        g_palette_r[i] = (uint8_t)clamp_byte(target + 1140 * v / 1000);
        g_palette_g[i] = (uint8_t)clamp_byte(target - 395 * u / 1000 - 581 * v / 1000);
        g_palette_b[i] = (uint8_t)clamp_byte(target + 2032 * u / 1000);
    }
    g_palette_ready = true;
}

static void get_phoenix_color(uint8_t prom_idx, uint8_t *r, uint8_t *g, uint8_t *b) {
    if (!g_palette_ready) init_phoenix_palette();
    prom_idx &= 0x7F;
    *r = g_palette_r[prom_idx];
    *g = g_palette_g[prom_idx];
    *b = g_palette_b[prom_idx];
}
#endif

int headless_frames = 0;
const char* screenshot_path = NULL;
const char* dump_vram_path = NULL;
const char* ram_dump_path = NULL; // lockstep verification against jphoenix (-Dphoenix.ramdump)
const char* coverage_dump_path = NULL;
static FILE* ram_dump_file = NULL;
int frame_counter = 0;

// Startup gate, matching jphoenix's --start-delay=/--wait-for-space
// (PhoenixDesktop.java): lets a screen recording be set up before the
// game actually starts. Mutually exclusive; validated in main().
static double g_start_delay_seconds = 0.0;
static bool g_wait_for_space = false;
static bool g_no_render = false;

// F12 in-game screenshot hotkey: set by the event loop, consumed right
// after the frame finishes rendering so the capture matches what's on
// screen this frame.
static bool g_screenshot_requested = false;

// Click-to-pause/resume (interactive mode only -- never in headless test
// runs, which must stay deterministic and can't wait on a mouse).
static bool g_paused = false;

/* Writes the renderer's current contents as a binary PPM (P6). Shared by
 * the F12 hotkey and the one-shot --screenshot= exit capture. */
static void write_screenshot(SDL_Renderer* renderer, const char* path) {
    int width;
    int height;
    if (SDL_GetRendererOutputSize(renderer, &width, &height) != 0 ||
        width <= 0 || height <= 0) {
        SDL_Log("Screenshot size unavailable: %s", SDL_GetError());
        return;
    }

    size_t pixel_count = (size_t)width * (size_t)height;
    uint32_t* pixels = malloc(pixel_count * sizeof(*pixels));
    if (!pixels) return;
    if (SDL_RenderReadPixels(renderer, NULL, SDL_PIXELFORMAT_ARGB8888, pixels,
                             width * (int)sizeof(*pixels)) == 0) {
        FILE* f = fopen(path, "wb");
        if (f) {
            fprintf(f, "P6\n%d %d\n255\n", width, height);
            for (size_t i = 0; i < pixel_count; i++) {
                uint32_t p = pixels[i];
                uint8_t r = (p >> 16) & 0xFF;
                uint8_t g = (p >> 8) & 0xFF;
                uint8_t b = p & 0xFF;
                fwrite(&r, 1, 1, f);
                fwrite(&g, 1, 1, f);
                fwrite(&b, 1, 1, f);
            }
            fclose(f);
            printf("Screenshot saved to %s\n", path);
        }
    }
    free(pixels);
}

/* ==========================================================
 * INPUT SCRIPTING (Front 3): deterministic, replayable input for
 * lockstep verification of real gameplay (coin-in, start, movement,
 * fire) against jphoenix's equivalent -Dphoenix.inputscript= injection.
 * File format, one event per line: "<frame> <button> <press|release>".
 * Blank lines and lines starting with '#' are ignored. Button names:
 * coin, start1, start2, fire, left, right, shield.
 * ========================================================== */
typedef struct {
    int frame;
    uint8_t mask;
    bool press;
} InputScriptEvent;

static InputScriptEvent* g_input_script = NULL;
static int g_input_script_count = 0;
static int g_input_script_next = 0;

static uint8_t input_script_button_mask(const char* name) {
    if (strcmp(name, "coin") == 0) return BTN_COIN;
    if (strcmp(name, "start1") == 0) return BTN_START_1P;
    if (strcmp(name, "start2") == 0) return BTN_START_2P;
    if (strcmp(name, "fire") == 0) return BTN_FIRE;
    if (strcmp(name, "left") == 0) return BTN_LEFT;
    if (strcmp(name, "right") == 0) return BTN_RIGHT;
    if (strcmp(name, "shield") == 0) return BTN_SHIELD;
    return 0;
}

static void load_input_script(const char* path) {
    FILE* f = fopen(path, "r");
    if (!f) {
        printf("Input script failed to open %s, disabling\n", path);
        return;
    }
    int capacity = 64;
    g_input_script = malloc(sizeof(InputScriptEvent) * capacity);
    char line[256];
    while (fgets(line, sizeof(line), f)) {
        if (line[0] == '#' || line[0] == '\n' || line[0] == '\r') continue;
        int frame;
        char button[32];
        char action[16];
        if (sscanf(line, "%d %31s %15s", &frame, button, action) != 3) continue;
        uint8_t mask = input_script_button_mask(button);
        if (mask == 0) {
            printf("Input script: unknown button '%s', skipping\n", button);
            continue;
        }
        bool press = (strcmp(action, "press") == 0);
        if (g_input_script_count >= capacity) {
            capacity *= 2;
            g_input_script = realloc(g_input_script, sizeof(InputScriptEvent) * capacity);
        }
        g_input_script[g_input_script_count].frame = frame;
        g_input_script[g_input_script_count].mask = mask;
        g_input_script[g_input_script_count].press = press;
        g_input_script_count++;
    }
    fclose(f);
    // Stable insertion sort by frame -- scripts are small, O(n^2) is fine.
    for (int i = 1; i < g_input_script_count; i++) {
        InputScriptEvent key = g_input_script[i];
        int j = i - 1;
        while (j >= 0 && g_input_script[j].frame > key.frame) {
            g_input_script[j + 1] = g_input_script[j];
            j--;
        }
        g_input_script[j + 1] = key;
    }
    printf("Loaded %d input-script events from %s\n", g_input_script_count, path);
}

static void apply_input_script(int frame) {
    while (g_input_script_next < g_input_script_count &&
           g_input_script[g_input_script_next].frame <= frame) {
        InputScriptEvent* ev = &g_input_script[g_input_script_next];
        if (ev->press) {
            g_inputs &= ~ev->mask; // bit clears to 0 when pressed
        } else {
            g_inputs |= ev->mask;
        }
        g_input_script_next++;
    }
}

/* ==========================================================
 * INPUT RECORDING: the flip side of input scripting. A bug that only
 * shows up during real, undirected play (aim, timing, which levels get
 * reached) can't always be captured by a hand-written script -- this
 * writes every real key press/release straight to a file in the exact
 * same "<frame> <button> <press|release>" format load_input_script()
 * reads, using the same frame numbering apply_input_script() expects.
 * Hit the bug once while recording, hand over the resulting file, and
 * it replays headlessly with --ram-dump=/--screenshot= for byte-exact,
 * frame-by-frame inspection instead of a guessed reproduction attempt.
 * ========================================================== */
static FILE* g_record_input_file = NULL;
static int g_record_input_events = 0;

static const char* input_script_button_name(uint8_t mask) {
    switch (mask) {
        case BTN_COIN: return "coin";
        case BTN_START_1P: return "start1";
        case BTN_START_2P: return "start2";
        case BTN_FIRE: return "fire";
        case BTN_LEFT: return "left";
        case BTN_RIGHT: return "right";
        case BTN_SHIELD: return "shield";
        default: return NULL;
    }
}

static void start_input_recording(const char* path) {
    g_record_input_file = fopen(path, "w");
    if (!g_record_input_file) {
        printf("Input recording failed to open %s, disabling\n", path);
        return;
    }
    time_t now = time(NULL);
    fprintf(g_record_input_file, "# Recorded session, %s", ctime(&now));
    fprintf(g_record_input_file, "# Replay with: ./c-phoenix --input-script=%s\n", path);
    fflush(g_record_input_file);
    printf("Recording input to %s\n", path);
}

/* frame is the upcoming frame (frame_counter as it will be once
 * incremented later this iteration), matching what apply_input_script()
 * compares against on replay -- events are polled before the increment. */
static void record_input_event(int frame, uint8_t mask, bool press) {
    if (!g_record_input_file) return;
    const char* name = input_script_button_name(mask);
    if (!name) return;
    fprintf(g_record_input_file, "%d %s %s\n", frame, name, press ? "press" : "release");
    fflush(g_record_input_file); // survive a force-quit mid-session
    g_record_input_events++;
}

static void stop_input_recording(void) {
    if (!g_record_input_file) return;
    fclose(g_record_input_file);
    printf("Input recording complete (%d events)\n", g_record_input_events);
    g_record_input_file = NULL;
}

/* Record format per frame: 4-byte big-endian frame number + 3072 bytes RAM (0x4000-0x4BFF).
 * Must stay identical to Phoenix.java dumpRamFrame().
 * Called from the game logic thread (wait_vblank_coin) so the snapshot is
 * race-free and taken at the same point as jphoenix's interrupt(). */
void platform_ram_dump_hook(void) {
    static int dump_frame = 0;
    static int coverage_frame = 0;
    coverage_frame++;
    coverage_observe_frame(coverage_frame, &state);
    if (ram_dump_path == NULL || g_quit) return;
    if (ram_dump_file == NULL) {
        ram_dump_file = fopen(ram_dump_path, "wb");
        if (ram_dump_file == NULL) {
            printf("RAM dump failed to open %s, disabling\n", ram_dump_path);
            ram_dump_path = NULL;
            return;
        }
    }
    dump_frame++;
    uint8_t hdr[4] = {
        (uint8_t)(dump_frame >> 24), (uint8_t)(dump_frame >> 16),
        (uint8_t)(dump_frame >> 8), (uint8_t)dump_frame
    };
    fwrite(hdr, 1, 4, ram_dump_file);
    fwrite(&state, 1, sizeof(PhoenixState), ram_dump_file);
    fflush(ram_dump_file);
}

int main(int argc, char* argv[]) {
    const char* record_input_path = NULL;
    const char* runtime_call_trace_path = NULL;
    for (int i = 1; i < argc; i++) {
        if (strncmp(argv[i], "--run-frames=", 13) == 0) {
            headless_frames = atoi(argv[i] + 13);
        } else if (strncmp(argv[i], "--screenshot=", 13) == 0) {
            screenshot_path = argv[i] + 13;
        } else if (strncmp(argv[i], "--dump-vram=", 12) == 0) {
            dump_vram_path = argv[i] + 12;
        } else if (strncmp(argv[i], "--ram-dump=", 11) == 0) {
            ram_dump_path = argv[i] + 11;
        } else if (strncmp(argv[i], "--coverage-dump=", 16) == 0) {
            coverage_dump_path = argv[i] + 16;
            coverage_set_output_path(coverage_dump_path);
        } else if (strncmp(argv[i], "--runtime-call-trace=", 21) == 0) {
            runtime_call_trace_path = argv[i] + 21;
        } else if (strncmp(argv[i], "--input-script=", 15) == 0) {
            load_input_script(argv[i] + 15);
        } else if (strncmp(argv[i], "--record-input=", 15) == 0) {
            record_input_path = argv[i] + 15;
        } else if (strncmp(argv[i], "--start-delay=", 14) == 0) {
            g_start_delay_seconds = atof(argv[i] + 14);
        } else if (strcmp(argv[i], "--wait-for-space") == 0) {
            g_wait_for_space = true;
        } else if (strcmp(argv[i], "--no-render") == 0) {
            g_no_render = true;
        }
    }

    if (g_wait_for_space && g_start_delay_seconds > 0.0) {
        SDL_Log("--wait-for-space and --start-delay cannot be combined");
        return 2;
    }

    // Interactive-only, same rule as audio/pause: headless test runs must
    // stay deterministic and shouldn't depend on -- or produce -- a
    // recording.
    if (record_input_path != NULL && headless_frames == 0) {
        start_input_recording(record_input_path);
    }

    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_EVENTS) < 0) {
        SDL_Log("SDL_Init failed: %s", SDL_GetError());
        return 1;
    }
    
    // Original resolution is 208x256 (rotated). We'll do 224x256 or similar.
    // Let's create a generic 600x800 window for now.
    uint32_t window_flags = SDL_WINDOW_SHOWN;
    if (headless_frames > 0) {
        window_flags |= SDL_WINDOW_HIDDEN;
    }
    
    SDL_Window* window = SDL_CreateWindow(
#ifdef C2_RENDERER
        "C2-Phoenix",
#else
        "Phoenix C Port",
#endif
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 
        208 *
#ifdef C2_RENDERER
        4,
#else
        3,
#endif
        256 *
#ifdef C2_RENDERER
        4,
#else
        3,
#endif
        window_flags
    );
    
    if (!window) {
        SDL_Log("SDL_CreateWindow failed: %s", SDL_GetError());
        SDL_Quit();
        return 1;
    }
        
    uint32_t renderer_flags = headless_frames > 0
        ? SDL_RENDERER_SOFTWARE
        : (SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, renderer_flags);
    if (!renderer) {
        SDL_Log("SDL_CreateRenderer failed: %s", SDL_GetError());
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }
    
    // C2 renders native 4x coordinates; the reference renderer preserves
    // the original 3x pixel-scale presentation.
#ifdef C2_RENDERER
    SDL_RenderSetScale(renderer, 1.0f, 1.0f);
#else
    SDL_RenderSetScale(renderer, 3.0f, 3.0f);
#endif

    // Audio: skipped in headless mode (--run-frames), matching every
    // other interactive-only feature -- automated/lockstep test runs
    // must stay deterministic and not depend on audio hardware being
    // present in whatever environment they run in.
    sound_init();
    if (headless_frames == 0) {
        SDL_AudioSpec want, have;
        SDL_zero(want);
        want.freq = SOUND_SAMPLE_RATE;
        want.format = AUDIO_S16LSB;
        want.channels = 1;
        want.samples = 1024;
        g_audio_device = SDL_OpenAudioDevice(NULL, 0, &want, &have, 0);
        if (g_audio_device == 0) {
            SDL_Log("SDL_OpenAudioDevice failed: %s", SDL_GetError());
        } else {
            SDL_PauseAudioDevice(g_audio_device, 0);
        }
    }

    // DIP switches all 0 to match the jphoenix reference emulator
    // (its $7800 read models only the vblank bit, so DSW bits read as 0)
    g_dsw = 0x00;

    g_sem_vblank_go = SDL_CreateSemaphore(0);
    g_sem_frame_done = SDL_CreateSemaphore(0);
    if (!g_sem_vblank_go || !g_sem_frame_done) {
        SDL_Log("SDL_CreateSemaphore failed: %s", SDL_GetError());
        return 1;
    }

    SDL_Thread* game_thread = SDL_CreateThread(game_thread_func, "PhoenixLogicThread", NULL);
    if (!game_thread) {
        SDL_Log("SDL_CreateThread failed: %s", SDL_GetError());
    }

    // Startup gate (skipped in headless mode: --run-frames drives automated
    // tests/lockstep dumps, which must not block on a human). The logic
    // thread stays safely parked on its first SDL_SemWait(g_sem_vblank_go)
    // the whole time, since nothing posts to that semaphore until the main
    // loop below starts.
    if (headless_frames == 0 && (g_wait_for_space || g_start_delay_seconds > 0.0)) {
        char title[128];
        if (g_wait_for_space) {
            SDL_SetWindowTitle(window, "Phoenix C Port - druk op spatie om te starten");
            bool space_pressed = false;
            while (!space_pressed && !g_quit) {
                SDL_Event e;
                while (SDL_PollEvent(&e)) {
                    if (e.type == SDL_QUIT) {
                        g_quit = true;
                    } else if (e.type == SDL_KEYDOWN && e.key.keysym.sym == SDLK_SPACE) {
                        space_pressed = true;
                    }
                }
                SDL_Delay(10);
            }
        } else {
            snprintf(title, sizeof(title), "Phoenix C Port - start over %g seconden", g_start_delay_seconds);
            SDL_SetWindowTitle(window, title);
            Uint64 wait_start = SDL_GetPerformanceCounter();
            double elapsed = 0.0;
            while (elapsed < g_start_delay_seconds && !g_quit) {
                SDL_Event e;
                while (SDL_PollEvent(&e)) {
                    if (e.type == SDL_QUIT) g_quit = true;
                }
                SDL_Delay(10);
                elapsed = (double)(SDL_GetPerformanceCounter() - wait_start) / (double)SDL_GetPerformanceFrequency();
            }
        }
        SDL_SetWindowTitle(window,
#ifdef C2_RENDERER
                           "C2-Phoenix");
#else
                           "Phoenix C Port");
#endif
    }

    // Clock-based frame pacing (ADR-001): an accumulator ticking at the
    // exact target period avoids drift over long runs, unlike a fixed
    // SDL_Delay per frame. Target matches jphoenix's paceFrame() (flat
    // 60 Hz), not the real arcade hardware's 61.035156 Hz (11 MHz XTAL /
    // 2 / (352*256), per MAME's phoenix.h) -- chosen for a consistent
    // side-by-side feel between the two emulators over hardware purism.
    const double target_period_s = 1.0 / 60.0;
    Uint64 perf_freq = SDL_GetPerformanceFrequency();
    Uint64 next_frame_time = SDL_GetPerformanceCounter();
    extern void runtime_call_trace_start(const char *path);
    if (runtime_call_trace_path != NULL) runtime_call_trace_start(runtime_call_trace_path);

    // Platform Main Loop (Video/Events)
    while (!g_quit) {
        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_QUIT) {
                g_quit = true;
            } else if (e.type == SDL_KEYDOWN && e.key.keysym.sym == SDLK_F12 && !e.key.repeat) {
                g_screenshot_requested = true;
            } else if (e.type == SDL_MOUSEBUTTONDOWN && e.button.button == SDL_BUTTON_LEFT
                       && headless_frames == 0) {
                g_paused = !g_paused;
                SDL_SetWindowTitle(window, g_paused
                    ? "Phoenix C Port - PAUZE (klik om verder te gaan)"
                    : "Phoenix C Port");
            } else if (e.type == SDL_KEYDOWN || e.type == SDL_KEYUP) {
                bool pressed = (e.type == SDL_KEYDOWN);
                uint8_t mask = 0;

                switch (e.key.keysym.sym) {
                    case SDLK_LEFT: case SDLK_a: case SDLK_j: mask = BTN_LEFT; break;
                    case SDLK_RIGHT: case SDLK_d: case SDLK_l: mask = BTN_RIGHT; break;
                    case SDLK_SPACE: case SDLK_w: case SDLK_i: mask = BTN_FIRE; break;
                    case SDLK_DOWN: case SDLK_s: case SDLK_k: mask = BTN_SHIELD; break;
                    case SDLK_1: mask = BTN_START_1P; break;
                    case SDLK_2: mask = BTN_START_2P; break;
                    case SDLK_c: case SDLK_3: case SDLK_5: mask = BTN_COIN; break;
                }
                
                if (mask != 0) {
                    if (pressed) {
                        g_inputs &= ~mask; // Bit 0 means pressed
                    } else {
                        g_inputs |= mask;  // Bit 1 means released
                    }
                    // Skip key-repeat autofire (held key -> repeated
                    // SDL_KEYDOWN) so the recording gets one press event
                    // per actual press, not one per repeat tick.
                    if (!e.key.repeat) {
                        record_input_event(frame_counter + 1, mask, pressed);
                    }
                }
            }
        }
        
        if (!g_paused) {
            // Advance frame counter and exit if needed
            frame_counter++;
            if (headless_frames > 0 && frame_counter >= headless_frames) {
                g_quit = true;
            }

            // Apply any scripted input events due by this frame, before the
            // logic thread reads hw_read_inputs() for it.
            apply_input_script(frame_counter);

            // Emulate VBLANK hardware signal lockstep: tell the logic thread
            // to go, then block (no polling) until it signals this frame's
            // full processing is complete.
            SDL_SemPost(g_sem_vblank_go);
            if (!g_quit) SDL_SemWait(g_sem_frame_done);
        }

        // Clock-based pacing (skipped in headless mode, which runs flat out
        // for dump/test speed): sleep for the remainder of the target
        // ~60.6096 Hz period. The accumulator (not "now + period") avoids
        // drift over long runs; if we fall behind, resync instead of
        // trying to catch up in a burst.
        if (headless_frames == 0) {
            if (g_paused) {
                // Idle without busy-spinning; keep resyncing the pacing
                // accumulator so resuming doesn't trigger a catch-up burst.
                SDL_Delay(16);
                next_frame_time = SDL_GetPerformanceCounter();
            } else {
                next_frame_time += (Uint64)(target_period_s * (double)perf_freq);
                Uint64 now = SDL_GetPerformanceCounter();
                if (now < next_frame_time) {
                    Uint32 delay_ms = (Uint32)(((next_frame_time - now) * 1000) / perf_freq);
                    if (delay_ms > 0) SDL_Delay(delay_ms);
                } else {
                    next_frame_time = now;
                }
            }
        }

        if (g_no_render) {
            continue;
        }

#ifdef C2_RENDERER
        c2_render_frame(renderer, &state, g_scroll_reg, g_palette_bank);
#else
        // Clear screen
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderClear(renderer);
        
        // RENDER LOOP (TATE Mode)
        // Arcade resolution is 208x256. 26 columns of 32 tiles (8x8).
        // Since the monitor is rotated 90 degrees clockwise, X and Y are swapped.
        // Screen memory: 0x4000 to 0x433F (Foreground), 0x4800 to 0x4B3F (Background)
        // Memory is laid out such that each 32 bytes is a column.
        uint8_t* state_mem = (uint8_t*)&state;
        
        // Render Background (0x4800 - 0x4BFF)
        for (int addr = 0x4800; addr < 0x4C00; addr++) {
            uint8_t tile_idx = state_mem[addr - 0x4000];
            
            int mem_offset = addr - 0x4800;
            int grid_y = mem_offset % 32; // row
            int grid_x = mem_offset / 32; // col
            
            if (grid_x >= 26) continue; // Columns 26-31 are off-screen (RAM variables)
            
            int screen_x = (25 - grid_x) * 8;
            int screen_y = grid_y * 8;
            
            uint16_t tile_base = 0x0000 + (tile_idx * 8); 
            for (int ty = 0; ty < 8; ty++) {
                uint8_t b0 = gfx_mem[tile_base + ty + 0x800]; 
                uint8_t b1 = gfx_mem[tile_base + ty];         
                
                for (int tx = 0; tx < 8; tx++) {
                    int bit = 7 - tx;
                    int color_idx = (((b0 >> bit) & 1) << 1) | ((b1 >> bit) & 1);
                    
                    // Background uses is_fg = 0
                    uint8_t prom_idx = ((g_palette_bank & 1) << 6) | (0x00) | (color_idx << 3) | ((tile_idx >> 5) & 0x07);
                    uint8_t r, g, b;

                    if (color_idx == 0) {
                        r = 0; g = 0; b = 0; // Transparent/Black space
                    } else {
                        get_phoenix_color(prom_idx, &r, &g, &b);
                    }
                    
                    SDL_SetRenderDrawColor(renderer, r, g, b, 255);
                    
                    int px = screen_x + (7 - ty); 
                    int py = (screen_y + (256 - g_scroll_reg) + (7 - tx)) % 256;
                    
                    SDL_RenderDrawPoint(renderer, px, py);
                }
            }
        }
        
        // Render Foreground (0x4000 - 0x43FF)
        int fg_chars = 0;
        for (int addr = 0x4000; addr < 0x4400; addr++) {
            uint8_t tile_idx = state_mem[addr - 0x4000];
            if (tile_idx == 0) continue; // optimization: 0 is blank space usually
            
            int mem_offset = addr - 0x4000;
            int grid_y = mem_offset % 32; // row
            int grid_x = mem_offset / 32; // col
            
            if (grid_x >= 26) continue; // Columns 26-31 are off-screen
            fg_chars++;
            
            int screen_x = (25 - grid_x) * 8;
            int screen_y = grid_y * 8;
            
            uint16_t tile_base = 0x1000 + (tile_idx * 8); 
            for (int ty = 0; ty < 8; ty++) {
                uint8_t b0 = gfx_mem[tile_base + ty + 0x800]; 
                uint8_t b1 = gfx_mem[tile_base + ty];         
                
                for (int tx = 0; tx < 8; tx++) {
                    int bit = 7 - tx;
                    int color_idx = (((b0 >> bit) & 1) << 1) | ((b1 >> bit) & 1);
                    
                    if (color_idx > 0) { 
                        // Foreground uses is_fg = 1 (0x20)
                        uint8_t prom_idx = ((g_palette_bank & 1) << 6) | (0x20) | (color_idx << 3) | ((tile_idx >> 5) & 0x07);

                        // Transparency is strictly color_idx == 0. If color_idx > 0, we draw it (even if black).
                        uint8_t r, g, b;
                        get_phoenix_color(prom_idx, &r, &g, &b);

                        SDL_SetRenderDrawColor(renderer, r, g, b, 255);

                        int px = screen_x + (7 - ty);
                        int py = (screen_y + (7 - tx)) % 256;

                        SDL_RenderDrawPoint(renderer, px, py);
                    }
                }
            }
        }
        if (frame_counter == headless_frames - 1) printf("Foreground chars drawn: %d\n", fg_chars);

        SDL_RenderPresent(renderer);
#endif

        if (g_screenshot_requested) {
            g_screenshot_requested = false;
            char path[64];
            snprintf(path, sizeof(path), "screenshot_%06d.ppm", frame_counter);
            write_screenshot(renderer, path);
        }
    }

    if (screenshot_path != NULL) {
        write_screenshot(renderer, screenshot_path);
    }

    if (dump_vram_path != NULL) {
        FILE *f = fopen(dump_vram_path, "wb");
        if (f) {
            // Header
            fwrite("VRAMDUMP", 1, 8, f);
            
            // Registers
            uint8_t regs[8] = {0};
            regs[0] = g_vram_page;
            regs[1] = g_palette_bank;
            regs[2] = g_scroll_reg;
            fwrite(regs, 1, 8, f);
            
            // State
            fwrite(&state, 1, sizeof(PhoenixState), f);
            fclose(f);
            printf("DEBUG: Dumped VRAM to %s\n", dump_vram_path);
        }
    }
    
    if (ram_dump_file != NULL) {
        fclose(ram_dump_file);
        printf("RAM dump complete (%d frames)\n", frame_counter);
    }
    coverage_write_dump();
    extern void runtime_call_trace_stop(void);
    runtime_call_trace_stop();
    stop_input_recording();

    SDL_DetachThread(game_thread);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    
    return 0;
}
