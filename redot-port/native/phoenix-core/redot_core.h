#ifndef PHOENIX_REDOT_CORE_H
#define PHOENIX_REDOT_CORE_H

#include <stdint.h>

typedef struct {
    uint8_t active;
    uint8_t shape;
    uint8_t x;
    uint8_t y;
    uint16_t screen_addr;
} PhoenixRedotObject;

typedef struct {
    uint8_t game_or_attract;
    uint8_t game_state;
    uint8_t level_and_round;
    uint8_t player_x;
    uint8_t player_y;
    uint8_t player_bullet_x;
    uint8_t player_bullet_y;
    uint8_t player_bullet_state;
    uint8_t player_lives;
    uint8_t aliens_left;
    uint8_t birds_left;
    uint8_t coin_count;
    uint32_t score;
    PhoenixRedotObject aliens[16];
    PhoenixRedotObject birds[8];
    PhoenixRedotObject enemy_bullets[5];
} PhoenixRedotSnapshot;

/* A narrow ABI for the future GDExtension. Input uses the active-low masks
 * defined in phoenix_hw.h; 0xFF means no cabinet button is pressed. */
void phoenix_redot_create(void);
void phoenix_redot_set_input(uint8_t active_low_inputs);
void phoenix_redot_step(void);
void phoenix_redot_snapshot(PhoenixRedotSnapshot* out);
/* Writes the C2 hires 416x512 framebuffer as RGBA8888 (851,968 bytes). */
void phoenix_redot_frame_rgba(uint8_t* out, uint32_t length);
/* Writes one unscaled 208x256 Phoenix video layer as RGBA8888. */
void phoenix_redot_layer_rgba(uint8_t* out, uint32_t length, uint8_t foreground);
/* Copies the latest 48 kHz mono PCM frame and consumes it. */
uint32_t phoenix_redot_audio_pcm(int16_t* out, uint32_t capacity);

#endif
