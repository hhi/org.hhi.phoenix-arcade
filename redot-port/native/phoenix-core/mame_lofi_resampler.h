#ifndef MAME_LOFI_RESAMPLER_H
#define MAME_LOFI_RESAMPLER_H

/*
 * MAME's fixed-point lofi resampler (4-tap cubic-Hermite-style
 * interpolation over a phase accumulator), direct port of jphoenix's
 * MameLofiResampler.java. Used to resample the TMS36XX chip's native
 * ~23.8kHz output up to the SDL audio device's output rate.
 */

typedef double (*MameLofiSource)(void* ctx);

typedef struct {
    int source_divide;
    int step;
    int phase;
    float s0, s1, s2, s3;
} MameLofiResampler;

void mame_lofi_resampler_init(MameLofiResampler* r, int source_rate, int target_rate);
double mame_lofi_resampler_next(MameLofiResampler* r, MameLofiSource source, void* ctx);

#endif // MAME_LOFI_RESAMPLER_H
