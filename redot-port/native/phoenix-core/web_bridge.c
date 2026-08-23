#include "redot_core.h"
#include "sound.h"
#include <stdint.h>

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
    PHOENIX_WEB_FRAME_WIDTH = 416,
    PHOENIX_WEB_FRAME_HEIGHT = 512,
    PHOENIX_WEB_FRAME_BYTES = PHOENIX_WEB_FRAME_WIDTH * PHOENIX_WEB_FRAME_HEIGHT * 4,
};

static uint8_t web_frame_buffer[PHOENIX_WEB_FRAME_BYTES];
static uint8_t web_background_layer[PHOENIX_WEB_LAYER_BYTES];
static uint8_t web_foreground_layer[PHOENIX_WEB_LAYER_BYTES];
static int16_t web_audio_buffer[SOUND_MAX_FRAME_SAMPLES];
static uint32_t web_audio_sample_count;

PHOENIX_WEB_EXPORT void phoenix_web_create(void) {
    phoenix_redot_create();
    web_audio_sample_count = 0;
    phoenix_redot_frame_rgba(web_frame_buffer, sizeof(web_frame_buffer));
    phoenix_redot_layer_rgba(web_background_layer, sizeof(web_background_layer), 0);
    phoenix_redot_layer_rgba(web_foreground_layer, sizeof(web_foreground_layer), 1);
}

PHOENIX_WEB_EXPORT void phoenix_web_set_input(uint8_t active_low_inputs) {
    phoenix_redot_set_input(active_low_inputs);
}

PHOENIX_WEB_EXPORT void phoenix_web_step(void) {
    phoenix_redot_step();
    phoenix_redot_frame_rgba(web_frame_buffer, sizeof(web_frame_buffer));
    phoenix_redot_layer_rgba(web_background_layer, sizeof(web_background_layer), 0);
    phoenix_redot_layer_rgba(web_foreground_layer, sizeof(web_foreground_layer), 1);
    web_audio_sample_count = phoenix_redot_audio_pcm(web_audio_buffer, SOUND_MAX_FRAME_SAMPLES);
}

PHOENIX_WEB_EXPORT uintptr_t phoenix_web_frame_buffer(void) {
    return (uintptr_t)web_frame_buffer;
}

PHOENIX_WEB_EXPORT uint32_t phoenix_web_frame_buffer_length(void) {
    return sizeof(web_frame_buffer);
}

PHOENIX_WEB_EXPORT uintptr_t phoenix_web_background_layer(void) {
    return (uintptr_t)web_background_layer;
}

PHOENIX_WEB_EXPORT uintptr_t phoenix_web_foreground_layer(void) {
    return (uintptr_t)web_foreground_layer;
}

PHOENIX_WEB_EXPORT uint32_t phoenix_web_layer_length(void) {
    return sizeof(web_background_layer);
}

PHOENIX_WEB_EXPORT uintptr_t phoenix_web_audio_buffer(void) {
    return (uintptr_t)web_audio_buffer;
}

PHOENIX_WEB_EXPORT uint32_t phoenix_web_audio_sample_count(void) {
    return web_audio_sample_count;
}
