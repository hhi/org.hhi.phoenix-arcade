#include "phoenix_hw.h"
#include "phoenix_state.h"
#include "redot_core.h"
#include "redot_c2_renderer.h"
#include "sound.h"
#include "utilities.h"
#include "../../../c-phoenix/phoenix_render_assets.h"
#include <string.h>

PhoenixState state = {0};

static uint8_t g_inputs = 0xFF;
/* The translated coin checker treats a cleared bit 4 as one coin per play. */
static uint8_t g_dsw = 0x0F;
static uint8_t g_vram_page = 0;
static uint8_t g_palette_bank = 0;
static uint8_t g_scroll_reg = 0;
static uint8_t bank_storage[2][sizeof(PhoenixState)];
static int16_t g_audio_frame[SOUND_MAX_FRAME_SAMPLES];
static uint32_t g_audio_samples = 0;

uint8_t hw_read_inputs(void) { return g_inputs; }
uint8_t hw_read_dsw(void) { return g_dsw; }
bool hw_is_vblank(void) { return true; }

static void bank_swap_to(uint8_t new_page) {
    new_page &= 1;
    if (new_page == g_vram_page) return;
    memcpy(bank_storage[g_vram_page], &state, sizeof(state));
    memcpy(&state, bank_storage[new_page], sizeof(state));
    g_vram_page = new_page;
}

void hw_write_video_register(uint8_t value) {
    bank_swap_to(value & 1);
    g_palette_bank = (value >> 1) & 1;
}
void hw_toggle_palette_bank(void) { g_palette_bank ^= 1; }
void hw_write_scroll_register(uint8_t value) { g_scroll_reg = value; }
void hw_write_sound_a(uint8_t value) { sound_write_control_a(value); }
void hw_write_sound_b(uint8_t value) { sound_write_control_b(value); }

uint8_t phoenix_redot_palette_bank(void) { return g_palette_bank; }
uint8_t phoenix_redot_scroll_register(void) { return g_scroll_reg; }

void copy_memory_bank(uint8_t from_bank, uint8_t to_bank) {
    from_bank &= 1;
    to_bank &= 1;
    uint8_t snapshot[sizeof(PhoenixState)];
    if (from_bank == g_vram_page) memcpy(snapshot, &state, sizeof(state));
    else memcpy(snapshot, bank_storage[from_bank], sizeof(snapshot));
    hw_write_video_register(to_bank);
    for (int column = 0; column < 26; column++) {
        for (int row = 0; row < 4; row++) {
            state.ForegroundScreen[column * 32 + row] = snapshot[column * 32 + row];
        }
    }
    memcpy((uint8_t*)&state + (0x4380 - 0x4000), snapshot + (0x4380 - 0x4000), 0x38);
    memcpy((uint8_t*)&state + (0x4BC0 - 0x4000), snapshot + (0x4BC0 - 0x4000), 0x40);
}

void platform_ram_dump_hook(void) { }
void platform_audio_frame_hook(void) {
    g_audio_samples = (uint32_t)sound_render_frame(g_audio_frame);
}

static uint32_t packed_bcd_score(uint8_t high, uint8_t mid, uint8_t low) {
    return ((high >> 4) * 100000 + (high & 0x0F) * 10000 +
            (mid >> 4) * 1000 + (mid & 0x0F) * 100 +
            (low >> 4) * 10 + (low & 0x0F));
}

void phoenix_redot_create(void) {
    memset(&state, 0, sizeof(state));
    memset(bank_storage, 0, sizeof(bank_storage));
    g_inputs = 0xFF;
    g_vram_page = 0;
    g_palette_bank = 0;
    g_scroll_reg = 0;
    g_audio_samples = 0;
    sound_init();
    phoenix_init();
    /* Cabinet inputs idle high. Seed both latches so the first coin press is
     * observed as the hardware's required 1 -> 0 transition. */
    state.IN0Current = 0xFF;
    state.IN0Previous = 0xFF;
}

void phoenix_redot_set_input(uint8_t active_low_inputs) {
    g_inputs = active_low_inputs;
}

void phoenix_redot_snapshot(PhoenixRedotSnapshot* out) {
    if (!out) return;
    out->game_or_attract = state.GameOrAttract;
    out->game_state = state.GameState;
    out->level_and_round = state.LevelAndRound;
    out->player_x = state.PlayerShipX;
    out->player_y = state.PlayerShipY;
    out->player_bullet_x = state.PlayerBulletX;
    out->player_bullet_y = state.PlayerBulletY;
    out->player_bullet_state = state.PlayerBulletState;
    out->player_lives = state.Player1Lives;
    out->aliens_left = state.AliensLeft;
    out->birds_left = state.BirdsLeft;
    out->coin_count = state.CoinCount;
    out->score = packed_bcd_score(state.Score1high, state.Score1mid, state.Score1low);
    const uint8_t* ram = (const uint8_t*)&state;
    for (int slot = 0; slot < 16; slot++) {
        const uint8_t* object = ram + (0x4B70 - 0x4000) + slot * 4;
        out->aliens[slot] = (PhoenixRedotObject){
            .active = (uint8_t)((object[0] & 0x08) != 0),
            .shape = object[1], .x = object[2], .y = object[3],
            .screen_addr = (uint16_t)((ram[0xBB0 + slot * 4 + 2] << 8) | ram[0xBB0 + slot * 4 + 3]),
        };
    }
    for (int slot = 0; slot < 8; slot++) {
        const uint8_t* object = ram + (0x4B70 - 0x4000) + slot * 8;
        out->birds[slot] = (PhoenixRedotObject){
            .active = (uint8_t)(object[0] != 0), .shape = object[0],
            .x = object[5], .y = object[7],
            .screen_addr = (uint16_t)((object[1] << 8) | object[2]),
        };
    }
    for (int slot = 0; slot < 5; slot++) {
        const uint8_t* object = ram + (0x43CC - 0x4000) + slot * 4;
        out->enemy_bullets[slot] = (PhoenixRedotObject){
            .active = (uint8_t)((object[0] & 0x08) != 0),
            .shape = object[1], .x = object[2], .y = object[3], .screen_addr = 0,
        };
    }
}

void phoenix_redot_frame_rgba(uint8_t* out, uint32_t length) {
    phoenix_redot_c2_frame_rgba(out, length);
}

void phoenix_redot_layer_rgba(uint8_t* out, uint32_t length, uint8_t foreground) {
    const uint8_t* screen;
    const uint8_t (*tiles)[64];
    uint8_t scroll;
    if (!out || length < 208u * 256u * 4u) return;
    memset(out, 0, 208u * 256u * 4u);
    screen = foreground ? state.ForegroundScreen : state.BackgroundScreen;
    tiles = foreground ? phoenix_foreground_tiles : phoenix_background_tiles;
    scroll = foreground ? 0 : g_scroll_reg;
    for (int column = 0; column < 26; column++) for (int row = 0; row < 32; row++) {
        uint8_t tile = screen[column * 32 + row];
        if (!tile) continue;
        for (int ty = 0; ty < 8; ty++) for (int tx = 0; tx < 8; tx++) {
            uint8_t colour_index = tiles[tile][ty * 8 + tx];
            if (!colour_index) continue;
            uint8_t prom = (uint8_t)((g_palette_bank << 6) | (foreground ? 0x20 : 0)
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

uint32_t phoenix_redot_audio_pcm(int16_t* out, uint32_t capacity) {
    uint32_t samples = g_audio_samples;
    if (!out || capacity < samples) return 0;
    memcpy(out, g_audio_frame, samples * sizeof(*out));
    g_audio_samples = 0;
    return samples;
}
