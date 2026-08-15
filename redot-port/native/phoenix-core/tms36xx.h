#ifndef TMS36XX_H
#define TMS36XX_H

#include <stdint.h>

/*
 * MM6221AA/TMS3615/TMS3617-style 6-voice/12-harmonic square-wave organ
 * chip, direct port of jphoenix's TMS36XX.java (itself MAME's canonical
 * software model of this chip -- not a real recording). Drives Phoenix's
 * melodies: the attract tune, "Fur Elise", and the game's sad theme.
 *
 * Scope note: only the mm6221aa_tune_w() entry point is ported, since
 * that's the only one jphoenix's Sound.java actually calls from the
 * game -- note_w()/tms3617_enable_w() (dynamic per-note play, used by
 * some OTHER TMS3615-based games, not Phoenix) are not wired up here.
 */

#define TMS36XX_VOICES 12

typedef struct {
    int basefreq;
    int samplerate; /* basefreq * 64, matching MAME */

    int speed;
    int tune_counter;
    int note_counter;

    int voices;
    int shift;
    int vol[TMS36XX_VOICES];
    int vol_counter[TMS36XX_VOICES];
    int decay[TMS36XX_VOICES];

    int counter[TMS36XX_VOICES];
    int frequency[TMS36XX_VOICES];
    int output;
    int enable;

    int tune_num; /* 0=silence, 1..3 = tune1..tune3 */
    int tune_ofs;
    int tune_max;
} TMS36XX;

void tms36xx_init(TMS36XX* tms);
void tms36xx_mm6221aa_tune_w(TMS36XX* tms, int tune);
/* Renders one sample at the chip's native samplerate (basefreq*64). */
double tms36xx_render_internal_sample(TMS36XX* tms);

#endif // TMS36XX_H
