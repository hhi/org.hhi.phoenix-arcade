#include "phoenix_hw.h"
#include "redot_core.h"
#include "sound.h"
#include <stdio.h>

static int write_frame_ppm(void) {
    static unsigned char rgba[416 * 512 * 4];
    FILE *file = fopen("build/phoenix_redot_frame.ppm", "wb");
    if (!file) return 1;
    phoenix_redot_frame_rgba(rgba, sizeof(rgba));
    fprintf(file, "P6\n416 512\n255\n");
    for (int pixel = 0; pixel < 416 * 512; pixel++) {
        fwrite(&rgba[pixel * 4], 1, 3, file);
    }
    return fclose(file) != 0;
}

int main(void) {
    PhoenixRedotSnapshot snapshot = {0};
    int16_t audio[SOUND_MAX_FRAME_SAMPLES];
    uint32_t audio_samples;
    uint32_t non_silent_samples = 0;
    phoenix_redot_create();

    /* Coin and Start are active-low, like the original cabinet's IN0 port. */
    phoenix_redot_set_input(0xFF & ~BTN_COIN);
    phoenix_redot_step();
    phoenix_redot_set_input(0xFF);
    phoenix_redot_step();
    phoenix_redot_set_input(0xFF & ~BTN_START_1P);
    phoenix_redot_step();
    phoenix_redot_set_input(0xFF);

    for (int frame = 0; frame < 1000; frame++) {
        phoenix_redot_step();
    }
    phoenix_redot_snapshot(&snapshot);
    audio_samples = phoenix_redot_audio_pcm(audio, SOUND_MAX_FRAME_SAMPLES);

    if (snapshot.game_state > 7) {
        fprintf(stderr, "invalid game state: %u\n", snapshot.game_state);
        return 1;
    }
    if (audio_samples == 0 || audio_samples > SOUND_MAX_FRAME_SAMPLES) {
        fprintf(stderr, "invalid audio frame size: %u\n", audio_samples);
        return 1;
    }
    for (uint32_t sample = 0; sample < audio_samples; sample++) {
        if (audio[sample] != 0) non_silent_samples++;
    }
    if (non_silent_samples == 0) {
        fprintf(stderr, "audio frame unexpectedly contains silence only\n");
        return 1;
    }
    printf("Phoenix Redot core smoke test passed (mode=%u, state=%u, coins=%u, score=%u).\n",
           snapshot.game_or_attract, snapshot.game_state, snapshot.coin_count, snapshot.score);
    printf("player=(%u,%u), bullet=(%u,%u) state=%u\n", snapshot.player_x,
           snapshot.player_y, snapshot.player_bullet_x, snapshot.player_bullet_y,
           snapshot.player_bullet_state);
    for (int slot = 0; slot < 16; slot++) {
        if (snapshot.aliens[slot].active) {
            printf("alien[%d]=(%u,%u), shape=%u\n", slot, snapshot.aliens[slot].x,
                   snapshot.aliens[slot].y, snapshot.aliens[slot].shape);
        }
    }
    if (write_frame_ppm()) {
        fprintf(stderr, "could not write rendered Phoenix frame\n");
        return 1;
    }
    return 0;
}
