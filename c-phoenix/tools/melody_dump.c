/*
 * Standalone melody-capture harness for c-phoenix's sound module.
 *
 * Drives sound.c exactly the way the real ROM does at the start of a level
 * (l3a10 in sound_dispatcher.c: SoundControlB = 0xCF when LevelAndRound==0),
 * which selects TMS36XX tune 3 -- "ESTUDIO", Phoenix's own theme -- with
 * SoundControlA held at 0x0f (effects silent) so the recording isolates the
 * melody. Renders SOUND_SAMPLE_RATE/60 samples per frame via
 * sound_render_frame(), exactly as platform_sdl.c's main loop does, and
 * writes the accumulated PCM to a standard 16-bit mono WAV file.
 *
 * This mirrors jphoenix-emulator-port's tools/sound/SoundMameTraceReplay.java
 * recipe (controlA=0x0f, controlB=0xCF) so the two recordings are directly
 * comparable.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "sound.h"

static void write_u32le(FILE* f, uint32_t v) {
    uint8_t b[4] = { (uint8_t)v, (uint8_t)(v >> 8), (uint8_t)(v >> 16), (uint8_t)(v >> 24) };
    fwrite(b, 1, 4, f);
}
static void write_u16le(FILE* f, uint16_t v) {
    uint8_t b[2] = { (uint8_t)v, (uint8_t)(v >> 8) };
    fwrite(b, 1, 2, f);
}

static void write_wav(const char* path, const int16_t* samples, uint32_t count, int sample_rate) {
    FILE* f = fopen(path, "wb");
    if (!f) { perror("fopen"); return; }
    uint32_t data_bytes = count * 2;
    uint32_t byte_rate = sample_rate * 2;

    fwrite("RIFF", 1, 4, f);
    write_u32le(f, 36 + data_bytes);
    fwrite("WAVE", 1, 4, f);

    fwrite("fmt ", 1, 4, f);
    write_u32le(f, 16);
    write_u16le(f, 1);              /* PCM */
    write_u16le(f, 1);              /* mono */
    write_u32le(f, sample_rate);
    write_u32le(f, byte_rate);
    write_u16le(f, 2);              /* block align */
    write_u16le(f, 16);             /* bits per sample */

    fwrite("data", 1, 4, f);
    write_u32le(f, data_bytes);
    fwrite(samples, 2, count, f);

    fclose(f);
}

int main(int argc, char** argv) {
    const char* out_path = argc > 1 ? argv[1] : "c-phoenix_tune3.wav";
    double seconds = argc > 2 ? atof(argv[2]) : 15.0;

    sound_init();
    sound_write_control_a(0x0f);
    sound_write_control_b(0xCF);

    int total_samples = (int)(seconds * SOUND_SAMPLE_RATE);
    static int16_t buf[48000 * 20];
    int written = 0;
    int16_t frame[SOUND_MAX_FRAME_SAMPLES];

    while (written < total_samples) {
        int n = sound_render_frame(frame);
        if (n <= 0) break;
        int remaining = total_samples - written;
        int copy = n < remaining ? n : remaining;
        memcpy(&buf[written], frame, copy * sizeof(int16_t));
        written += copy;
    }

    write_wav(out_path, buf, written, SOUND_SAMPLE_RATE);

    /* quick stats, mirrors jphoenix's SoundRenderUtil.stats() */
    long long sumsq = 0;
    int peak = 0;
    for (int i = 0; i < written; i++) {
        int s = buf[i];
        int a = s < 0 ? -s : s;
        if (a > peak) peak = a;
        sumsq += (long long)s * s;
    }
    double rms = written ? __builtin_sqrt((double)sumsq / written) : 0.0;
    printf("%s samples=%d duration=%.3fs peak=%d rms=%.2f\n", out_path, written, written / (double)SOUND_SAMPLE_RATE, peak, rms);
    return 0;
}
