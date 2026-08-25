#include "hw_video_audio.h"
#include "phoenix_hw.h"
#include "phoenix_render_assets.h"
#include "phoenix_state.h"
#include "sound.h"
#include <stdint.h>
#include <string.h>

extern void phoenix_init(void);

#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define PHOENIX_WEB_EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define PHOENIX_WEB_EXPORT
#endif

enum {
    PHOENIX_WEB_LAYER_WIDTH = 208,
    PHOENIX_WEB_LAYER_HEIGHT = 256,
    PHOENIX_WEB_LAYER_BYTES = PHOENIX_WEB_LAYER_WIDTH * PHOENIX_WEB_LAYER_HEIGHT * 4,
};

PhoenixState state = {0};
static uint8_t inputs = 0xff;
static uint8_t vram_page;
static uint8_t palette_bank;
static uint8_t scroll_register;
static uint8_t bank_storage[2][sizeof(PhoenixState)];
static uint8_t background_layer[PHOENIX_WEB_LAYER_BYTES];
static uint8_t foreground_layer[PHOENIX_WEB_LAYER_BYTES];
static int16_t audio_buffer[SOUND_MAX_FRAME_SAMPLES];
static uint32_t audio_sample_count;

uint8_t hw_read_inputs(void) { return inputs; }
uint8_t hw_read_dsw(void) { return 0x0f; }
bool hw_is_vblank(void) { return true; }
bool platform_wait_vblank(void) { return true; }
void platform_ram_dump_hook(void) { }

void platform_audio_frame_hook(void) {
    audio_sample_count = (uint32_t)sound_render_frame(audio_buffer);
}

static void bank_swap_to(uint8_t page) {
    page &= 1;
    if (page == vram_page) return;
    memcpy(bank_storage[vram_page], &state, sizeof(state));
    memcpy(&state, bank_storage[page], sizeof(state));
    vram_page = page;
}

void hw_write_video_register(uint8_t value) {
    bank_swap_to(value & 1);
    palette_bank = (value >> 1) & 1;
}
void hw_toggle_palette_bank(void) { palette_bank ^= 1; }
void hw_write_scroll_register(uint8_t value) { scroll_register = value; }
void hw_write_sound_a(uint8_t value) { sound_write_control_a(value); }
void hw_write_sound_b(uint8_t value) { sound_write_control_b(value); }

void copy_memory_bank(uint8_t from_bank, uint8_t to_bank) {
    uint8_t snapshot[sizeof(PhoenixState)];
    from_bank &= 1;
    to_bank &= 1;
    if (from_bank == vram_page) memcpy(snapshot, &state, sizeof(state));
    else memcpy(snapshot, bank_storage[from_bank], sizeof(snapshot));
    hw_write_video_register(to_bank);
    for (int column = 0; column < 26; column++) {
        for (int row = 0; row < 4; row++) {
            state.ForegroundScreen[column * 32 + row] = snapshot[column * 32 + row];
        }
    }
    memcpy((uint8_t *)&state + 0x380, snapshot + 0x380, 0x38);
    memcpy((uint8_t *)&state + 0xbc0, snapshot + 0xbc0, 0x40);
}

static void render_layer(uint8_t *out, uint8_t foreground) {
    const uint8_t *screen = foreground ? state.ForegroundScreen : state.BackgroundScreen;
    const uint8_t (*tiles)[64] = foreground ? phoenix_foreground_tiles : phoenix_background_tiles;
    uint8_t scroll = foreground ? 0 : scroll_register;
    memset(out, 0, PHOENIX_WEB_LAYER_BYTES);
    for (int column = 0; column < 26; column++) for (int row = 0; row < 32; row++) {
        uint8_t tile = screen[column * 32 + row];
        if (!tile) continue;
        for (int ty = 0; ty < 8; ty++) for (int tx = 0; tx < 8; tx++) {
            uint8_t colour_index = tiles[tile][ty * 8 + tx];
            if (!colour_index) continue;
            uint8_t prom = (uint8_t)((palette_bank << 6) | (foreground ? 0x20 : 0)
                | (colour_index << 3) | ((tile >> 5) & 7));
            PhoenixRgb colour = phoenix_palette_rgb[prom & 0x7f];
            int x = (25 - column) * 8 + (7 - ty);
            int y = (row * 8 + (foreground ? 0 : 256 - scroll) + (7 - tx)) & 255;
            uint32_t pixel = (uint32_t)(y * 208 + x) * 4u;
            out[pixel] = colour.red;
            out[pixel + 1] = colour.green;
            out[pixel + 2] = colour.blue;
            out[pixel + 3] = 255;
        }
    }
}

static void render_layers(void) {
    render_layer(background_layer, 0);
    render_layer(foreground_layer, 1);
}

PHOENIX_WEB_EXPORT void phoenix_web_create(void) {
    memset(&state, 0, sizeof(state));
    memset(bank_storage, 0, sizeof(bank_storage));
    inputs = 0xff;
    vram_page = palette_bank = scroll_register = 0;
    audio_sample_count = 0;
    sound_init();
    phoenix_init();
    state.IN0Current = state.IN0Previous = 0xff;
    render_layers();
}

PHOENIX_WEB_EXPORT void phoenix_web_set_input(uint8_t active_low_inputs) {
    inputs = active_low_inputs;
}

PHOENIX_WEB_EXPORT void phoenix_web_step(void) {
    if (wait_vblank_coin()) phoenix_run_game_frame();
    render_layers();
}

PHOENIX_WEB_EXPORT uintptr_t phoenix_web_background_layer(void) {
    return (uintptr_t)background_layer;
}
PHOENIX_WEB_EXPORT uintptr_t phoenix_web_foreground_layer(void) {
    return (uintptr_t)foreground_layer;
}
PHOENIX_WEB_EXPORT uint32_t phoenix_web_layer_length(void) { return PHOENIX_WEB_LAYER_BYTES; }
PHOENIX_WEB_EXPORT uintptr_t phoenix_web_audio_buffer(void) { return (uintptr_t)audio_buffer; }
PHOENIX_WEB_EXPORT uint32_t phoenix_web_audio_sample_count(void) {
    uint32_t count = audio_sample_count;
    audio_sample_count = 0;
    return count;
}
