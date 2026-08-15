#include "tms36xx.h"
#include <stddef.h>
#include <stdbool.h>

#define VMIN 0x0000
#define VMAX 0x7fff
#define FSCALE 1024

/*
 * Tune data, direct port of TMS36XX.java's tune1[]/tune2[]/tune3[] (the
 * chip's built-in note tables: the alarm, "Fur Elise", and Phoenix's sad
 * theme). Values are pre-evaluated note-frequency constants -- generated
 * programmatically from the Java source (via each note-name helper,
 * e.g. C(n) = (FSCALE<<(n-1)) * 1.18921 truncated to int) rather than
 * hand-transcribed, to guarantee an exact match; hand-retyping ~500
 * note values invites a silent slip that would only surface as "the
 * tune sounds subtly wrong". tune4 (single-note play via note_w, not
 * used by Phoenix's own sound driver -- see tms36xx_mm6221aa_tune_w)
 * is not included.
 */
#define TUNE1_LEN 192
#define TUNE2_LEN 288
#define TUNE3_LEN 576

static const int g_tune1[TUNE1_LEN] = {
    4871, 0, 0, 2435, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 0, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 0, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 0, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 9742, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 0, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 0, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 0, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 2435, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 0, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 0, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 0, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 9742, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 0, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 0, 0, 0, 7298, 0, 0, 0, 0, 0,
    4871, 0, 0, 0, 0, 0, 7298, 0, 0, 0, 0, 0,
};

static const int g_tune2[TUNE2_LEN] = {
    5467, 10935, 21870, 0, 0, 0, 5160, 10321, 20642, 0, 0, 0,
    5467, 10935, 21870, 0, 0, 0, 5160, 10321, 20642, 0, 0, 0,
    5467, 10935, 21870, 0, 0, 0, 4096, 8192, 16384, 0, 0, 0,
    4871, 9742, 19484, 0, 0, 0, 4339, 8679, 17358, 0, 0, 0,
    3649, 7298, 14596, 0, 0, 0, 1366, 2733, 5467, 0, 0, 0,
    1824, 3649, 7298, 0, 0, 0, 2169, 4339, 8679, 0, 0, 0,
    2733, 5467, 10935, 0, 0, 0, 3649, 7298, 14596, 0, 0, 0,
    4096, 8192, 16384, 0, 0, 0, 1366, 2733, 5467, 0, 0, 0,
    2048, 4096, 8192, 0, 0, 0, 2733, 5467, 10935, 0, 0, 0,
    3444, 6888, 13777, 0, 0, 0, 4096, 8192, 16384, 0, 0, 0,
    4339, 8679, 17358, 0, 0, 0, 1366, 2733, 5467, 0, 0, 0,
    1824, 3649, 7298, 0, 0, 0, 2169, 4339, 8679, 0, 0, 0,
    5467, 10935, 21870, 0, 0, 0, 5160, 10321, 20642, 0, 0, 0,
    5467, 10935, 21870, 0, 0, 0, 5160, 10321, 20642, 0, 0, 0,
    5467, 10935, 21870, 0, 0, 0, 4096, 8192, 16384, 0, 0, 0,
    4871, 9742, 19484, 0, 0, 0, 4339, 8679, 17358, 0, 0, 0,
    3649, 7298, 14596, 0, 0, 0, 1366, 2733, 5467, 0, 0, 0,
    1824, 3649, 7298, 0, 0, 0, 2169, 4339, 8679, 0, 0, 0,
    2733, 5467, 10935, 0, 0, 0, 3649, 7298, 14596, 0, 0, 0,
    4096, 8192, 16384, 0, 0, 0, 1366, 2733, 5467, 0, 0, 0,
    2048, 4096, 8192, 0, 0, 0, 2733, 5467, 10935, 0, 0, 0,
    4339, 8679, 17358, 0, 0, 0, 4096, 8192, 16384, 0, 0, 0,
    0, 0, 0, 3649, 7298, 14596, 1366, 2733, 5467, 0, 0, 0,
    1824, 3649, 7298, 0, 0, 0, 0, 0, 0, 0, 0, 0,
};

static const int g_tune3[TUNE3_LEN] = {
    4096, 8192, 16384, 1366, 2733, 5467, 0, 0, 0, 0, 0, 0,
    4096, 8192, 16384, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    4096, 8192, 16384, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    4096, 8192, 16384, 2048, 4096, 8192, 0, 0, 0, 0, 0, 0,
    3649, 7298, 14596, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    3250, 6501, 13003, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    3250, 6501, 13003, 1625, 3250, 6501, 0, 0, 0, 0, 0, 0,
    3068, 6137, 12274, 1625, 3250, 6501, 0, 0, 0, 0, 0, 0,
    2733, 5467, 10935, 1625, 3250, 6501, 0, 0, 0, 0, 0, 0,
    2733, 5467, 10935, 2048, 4096, 8192, 0, 0, 0, 0, 0, 0,
    3250, 6501, 13003, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    4096, 8192, 16384, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    5467, 10935, 21870, 1366, 2733, 5467, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1366, 2733, 5467, 0, 0, 0, 1625, 3250, 6501,
    0, 0, 0, 2048, 4096, 8192, 0, 0, 0, 2733, 2733, 2733,
    5467, 10935, 21870, 1366, 2733, 5467, 0, 0, 0, 0, 0, 0,
    4871, 9742, 19484, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    4339, 8679, 17358, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    4339, 8679, 17358, 2169, 4339, 8679, 0, 0, 0, 0, 0, 0,
    4096, 8192, 16384, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    3649, 7298, 14596, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    3649, 7298, 14596, 1824, 3649, 7298, 0, 0, 0, 0, 0, 0,
    4096, 8192, 16384, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    4339, 8679, 17358, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    4096, 8192, 16384, 2048, 4096, 8192, 0, 0, 0, 0, 0, 0,
    4339, 8679, 17358, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    4096, 8192, 16384, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    5160, 10321, 20642, 2048, 4096, 8192, 0, 0, 0, 0, 0, 0,
    4339, 8679, 17358, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    4096, 8192, 16384, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    4096, 8192, 16384, 1625, 3250, 6501, 0, 0, 0, 0, 0, 0,
    3649, 7298, 14596, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    3250, 6501, 13003, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    3250, 6501, 13003, 1366, 2733, 5467, 0, 0, 0, 0, 0, 0,
    3068, 6137, 12274, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    2733, 5467, 10935, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    3068, 6137, 12274, 1534, 3068, 6137, 0, 0, 0, 0, 0, 0,
    3068, 6137, 12274, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    3068, 6137, 12274, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    3068, 6137, 12274, 2169, 4339, 8679, 0, 0, 0, 0, 0, 0,
    3250, 6501, 13003, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    3068, 6137, 12274, 1625, 3250, 6501, 0, 0, 0, 0, 0, 0,
    2733, 5467, 10935, 1366, 2733, 5467, 0, 0, 0, 0, 0, 0,
    3250, 6501, 13003, 2048, 4096, 8192, 0, 0, 0, 0, 0, 0,
    4096, 8192, 16384, 1625, 3250, 6501, 0, 0, 0, 0, 0, 0,
    5467, 10935, 21870, 1366, 2733, 5467, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
};

/*
 * Selects the currently requested built-in tune table. Tune 0 is silence; the
 * other values match the MM6221AA/TMS36XX tune select bits driven from the
 * sound-control B latch.
 */
static const int* tune_table(int tune_num, int* out_len) {
    switch (tune_num) {
        case 1: *out_len = TUNE1_LEN; return g_tune1;
        case 2: *out_len = TUNE2_LEN; return g_tune2;
        case 3: *out_len = TUNE3_LEN; return g_tune3;
        default: *out_len = 0; return NULL;
    }
}

/*
 * Applies one native-sample worth of envelope decay to a voice. When the
 * volume reaches zero the corresponding frequency is cleared so silent voices
 * stop toggling.
 */
static void tms36xx_decay(TMS36XX* tms, int voice) {
    if (tms->vol[voice] > VMIN) {
        tms->vol_counter[voice] -= tms->decay[voice];
        while (tms->vol_counter[voice] <= 0) {
            tms->vol_counter[voice] += tms->samplerate;
            if (tms->vol[voice]-- <= VMIN) {
                tms->frequency[voice] = 0;
                tms->vol[voice] = VMIN;
                break;
            }
        }
    }
}

/*
 * Starts one of the six note slots for the current tune step. The chip model
 * alternates between the lower and upper six voices through tms->shift, so a
 * restart writes into the active half of the twelve-voice state.
 */
static void tms36xx_restart(TMS36XX* tms, int voice) {
    int len;
    const int* tune = tune_table(tms->tune_num, &len);
    if (!tune) return;
    int idx = tms->tune_ofs * 6 + voice;
    // Defensive bound (tune_max is hardcoded to 96 regardless of the
    // selected tune's actual length in the original chip model; real
    // gameplay always switches tunes well before running past the end,
    // but nothing structurally prevents it, so this guards the read
    // rather than relying on that assumption holding forever).
    if (idx < 0 || idx >= len) return;
    if (tune[idx] != 0) {
        tms->frequency[tms->shift + voice] = tune[idx] * tms->basefreq / FSCALE;
        tms->vol[tms->shift + voice] = VMAX;
    }
}

/*
 * Advances the square-wave phase for one voice and adds its current envelope
 * volume to the mixed sum when the voice is enabled and its output bit is high.
 */
static int tms36xx_tone(TMS36XX* tms, int voice, int sum) {
    if ((tms->enable & (1 << voice)) != 0 && tms->frequency[voice] != 0) {
        tms->counter[voice] -= tms->frequency[voice];
        while (tms->counter[voice] <= 0) {
            tms->counter[voice] += tms->samplerate;
            tms->output ^= 1 << voice;
        }
        if ((tms->output & tms->enable & (1 << voice)) != 0) {
            sum += tms->vol[voice];
        }
    }
    return sum;
}

/*
 * Initializes the TMS36XX/MM6221AA model with Phoenix's clocking and decay
 * constants. The initial enable mask is derived from the voices with non-zero
 * decay, matching the jphoenix constructor path.
 */
void tms36xx_init(TMS36XX* tms) {
    for (int i = 0; i < TMS36XX_VOICES; i++) {
        tms->vol[i] = 0;
        tms->vol_counter[i] = 0;
        tms->counter[i] = 0;
        tms->frequency[i] = 0;
        tms->decay[i] = 0;
    }
    tms->decay[0] = (int)(VMAX / 0.50);
    tms->decay[3] = (int)(VMAX / 1.05);
    tms->decay[6] = (int)(VMAX / 0.50);
    tms->decay[9] = (int)(VMAX / 1.05);

    tms->basefreq = 372;
    tms->samplerate = tms->basefreq * 64;
    tms->speed = (int)(VMAX / 0.21);
    tms->tune_counter = 0;
    tms->note_counter = 0;
    tms->voices = 0;
    tms->shift = 0;
    tms->output = 0;
    tms->enable = 0;
    tms->tune_num = 0;
    tms->tune_ofs = 0;
    tms->tune_max = 0;

    // Constructor logic: duplicate the 6 voice-enable bits for whichever
    // decay slots are active (matches TMS36XX() computing initialEnable
    // from the decay array, then calling tms3617_enable).
    int initial_enable = 0;
    for (int j = 0; j < 6; j++) {
        if (tms->decay[j] > 0) initial_enable |= 0x41 << j;
    }
    int enable = (initial_enable & 0x3f) | ((initial_enable & 0x3f) << 6);
    int bits = 0;
    for (int i = 0; i < 6; i++) {
        if (enable & (1 << i)) bits += 2;
    }
    tms->enable = enable;
    tms->voices = bits;
}

/*
 * Handles the tune-select write coming from sound-control B bits 6-7. A tune
 * change restarts playback at note offset zero; re-writing the same tune leaves
 * the current melody position untouched.
 */
void tms36xx_mm6221aa_tune_w(TMS36XX* tms, int tune) {
    tune &= 3;
    if (tune == tms->tune_num) return;
    tms->tune_num = tune;
    tms->tune_ofs = 0;
    tms->tune_max = 96;
}

/*
 * Renders one sample at the chip's native rate. This advances envelopes,
 * schedules tune steps, restarts notes as needed, mixes active square waves,
 * and returns a normalized value for the outer audio mixer/resampler.
 */
double tms36xx_render_internal_sample(TMS36XX* tms) {
    int len;
    const int* tune = tune_table(tms->tune_num, &len);
    if (!tune || tms->voices == 0) return 0.0;

    int sum = 0;
    for (int v = 0; v < TMS36XX_VOICES; v++) tms36xx_decay(tms, v);

    tms->tune_counter -= tms->speed;
    if (tms->tune_counter <= 0) {
        int n = (-tms->tune_counter / tms->samplerate) + 1;
        tms->tune_counter += n * tms->samplerate;

        tms->note_counter -= n;
        if (tms->note_counter <= 0) {
            tms->note_counter += VMAX;
            if (tms->tune_ofs < tms->tune_max) {
                tms->shift ^= 6;
                for (int v = 0; v < 6; v++) tms36xx_restart(tms, v);
                tms->tune_ofs++;
            }
        }
    }

    for (int v = 0; v < TMS36XX_VOICES; v++) sum = tms36xx_tone(tms, v, sum);

    return sum / (double)(32768 * tms->voices);
}
