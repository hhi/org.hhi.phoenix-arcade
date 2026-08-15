#ifndef SOUND_H
#define SOUND_H

#include <stdint.h>

/*
 * TMS36XX melody plus the discrete effect/noise circuits. Mono, 16-bit
 * signed PCM at 48kHz, matching jphoenix's Sound.java signal path.
 */

#define SOUND_SAMPLE_RATE 48000
#define SOUND_MAX_FRAME_SAMPLES 1024
#define SOUND_FRAME_SAMPLES ((SOUND_SAMPLE_RATE + 59) / 60)
#define SOUND_FRAME_END_SAMPLE (SOUND_FRAME_SAMPLES - 1)

void sound_init(void);

/*
 * Selects the sample position used for subsequent hardware writes in the
 * current 60Hz frame. The translated main loop writes the sound latches at
 * its tail, so the default is the final sample. Values are clamped to the
 * nominal 800-sample frame, as in jphoenix's Sound.queueEvent().
 */
void sound_set_frame_sample_index(uint16_t sample_index);

/* Mirrors jphoenix's updateControlA/updateControlB. Writes are queued and
 * take effect at the configured sample position during sound_render_frame(). */
void sound_write_control_a(uint8_t val);
void sound_write_control_b(uint8_t val);

/* Mirrors jphoenix's endFrame(): renders this frame's share of samples
 * (sampleRate/60 with a remainder accumulator) into `out` (mono S16LE)
 * and returns the sample count written. Call once per game frame. */
int sound_render_frame(int16_t* out);

#endif // SOUND_H
