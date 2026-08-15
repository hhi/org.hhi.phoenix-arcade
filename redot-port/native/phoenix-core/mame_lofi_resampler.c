#include "mame_lofi_resampler.h"
#include <stdbool.h>

#define PHASE_ONE 0x1000000
#define PHASE_MASK (PHASE_ONE - 1)

static float g_interp[2][0x1001];
static bool g_interp_ready = false;

/*
 * Builds the cubic interpolation lookup tables used by MAME's lo-fi stream
 * resampler. The tables are process-global because the coefficients depend
 * only on fractional phase, not on the source stream.
 */
static void build_interpolation(void) {
    if (g_interp_ready) return;
    for (int i = 1; i < 4096; i++) {
        float p = i / 4096.0f;
        g_interp[0][i] = (p - p * p * p) / 6.0f;
    }
    for (int i = 1; i < 2049; i++) {
        float p = i / 4096.0f;
        g_interp[1][i] = p + (p * p - p * p * p) / 2.0f;
    }
    for (int i = 2049; i < 4096; i++) {
        g_interp[1][i] = 1.0f + g_interp[0][i] + g_interp[0][4096 - i] - g_interp[1][4096 - i];
    }
    g_interp[0][0] = 0.0f;
    g_interp[0][0x1000] = 0.0f;
    g_interp[1][0] = 0.0f;
    g_interp[1][0x1000] = 1.0f;
    g_interp_ready = true;
}

/*
 * Initializes one rate converter from a native generator rate to the SDL
 * output rate. source_divide folds very high native rates down before the
 * interpolator so callers can use the same path for TMS and discrete sound.
 */
void mame_lofi_resampler_init(MameLofiResampler* r, int source_rate, int target_rate) {
    build_interpolation();
    r->source_divide = (source_rate <= target_rate) ? 1 : (1 + source_rate / target_rate);
    r->step = (int)((long long)source_rate * PHASE_ONE / target_rate / r->source_divide);
    r->phase = 0;
    r->s0 = r->s1 = r->s2 = r->s3 = 0.0f;
}

/*
 * Reads and averages the required number of native samples for the next source
 * point. Averaging here preserves the original MAME-style downsampling shape
 * without exposing source_divide to individual sound generators.
 */
static float read_source(MameLofiResampler* r, MameLofiSource source, void* ctx) {
    float sum = 0.0f;
    for (int i = 0; i < r->source_divide; i++) {
        sum += (float)source(ctx);
    }
    return sum / r->source_divide;
}

/*
 * Produces one target-rate sample from the four-sample interpolation window.
 * When fixed-point phase crosses a source-sample boundary, the window advances
 * and pulls the next averaged native sample from the callback.
 */
double mame_lofi_resampler_next(MameLofiResampler* r, MameLofiSource source, void* ctx) {
    int current_phase = (unsigned int)r->phase >> 12;
    float output = -r->s0 * g_interp[0][0x1000 - current_phase]
                 +  r->s1 * g_interp[1][0x1000 - current_phase]
                 +  r->s2 * g_interp[1][current_phase]
                 -  r->s3 * g_interp[0][current_phase];

    r->phase += r->step;
    if (r->phase & PHASE_ONE) {
        r->phase &= PHASE_MASK;
        r->s0 = r->s1;
        r->s1 = r->s2;
        r->s2 = r->s3;
        r->s3 = read_source(r, source, ctx);
    }
    return output;
}
