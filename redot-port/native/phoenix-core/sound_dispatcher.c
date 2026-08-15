#include <stdint.h>
#include "phoenix_state.h"
#include "z80_core.h"
#include "game_constants.h"

extern PhoenixState state;

/* Translation of the L3A10-L3B5B per-frame sound-effect dispatcher. */

static uint8_t rrca(uint8_t v) { return (uint8_t)((v >> 1) | ((v & 1) << 7)); }

static void l3a98_scan(void);
static void l3ad0(void);
static void l3b02(void);
static void l3b43(void);

/*
 * [ASM: 23D6-23FB] Level-type dispatcher: routes into the alien-hit scan
 * or the bird/mothership sound trigger depending on the sub-level.
 */
static void l23d6(void) {
    uint8_t lvl = state.LevelAndRound & 0x0F;
    if (lvl == 0x01 || lvl == 0x03) { l3a98_scan(); return; }
    if (lvl == 0x05 || lvl == 0x07) { l3ad0(); return; }
    if (lvl < 0x09) return;
    if (lvl < 0x0B) { l3b02(); return; }
    l3b02();
    l3a98_scan();
}

/*
 * [ASM: 27BD-27EE] Player-hit / bullet-fired sound effect trigger.
 * Proposed C name: update_player_hit_and_bullet_sound
 */
static void l27bd(void) {
    if (state.ParticleExplosion != 0) {
        if (state.ParticleExplosion >= 0x40) {
            state.ParticleExplosion = 0x40;
        }
        state.ParticleExplosion--;
        state.SoundControlA = 0x8F;
        return;
    }

    if (state.BulletTriggered == 0) return;
    if (state.BulletTriggered >= 0x19) {
        state.BulletTriggered = 0x18;
        state.SoundControlA &= 0xBF;
        return;
    }
    state.BulletTriggered--;
    state.SoundControlA |= 0x40;
}

/*
 * L3A1D-L3A3F fades SoundControlB's alien-hit chime nibble down over
 * ~32 frames whenever M4369 (set by add_score on a hit) is nonzero.
 */
static void l3a40(void);

/* [ASM: 3A2C-3A3F] */
static void l3a2c(void) {
    state.M4369--;
    uint8_t a = (uint8_t)(state.M4369 << 2); /* RLCA x2, safe: M4369 <= 0x1F here */
    a = (uint8_t)(~a) & 0x0E;
    state.SoundControlB = a;
    state.M4368 = 0;
    state.M4366 = 0;
}

/* [ASM: 3A1D-3A2B] */
static void l3a1d(void) {
    if (state.M4369 == 0) {
        l3a40();
        return;
    }
    if (state.M4369 >= 0x20) {
        state.M4369 = 0x20;
    }
    l3a2c();
}

/*
 * L3A40-L3A5F uses the same fade pattern, driving SoundControlA instead.
 */
static void l3a62(void);

/* [ASM: 3A4E-3A5F] */
static void l3a4e(void) {
    state.M4364--;
    uint8_t a = rrca(state.M4364);
    a = (uint8_t)(~a) & 0x07;
    a |= 0x10;
    state.SoundControlA = a;
    state.M4366 = 0;
}

/* [ASM: 3A40-3A4D] */
static void l3a40(void) {
    if (state.M4364 == 0) {
        l3a62();
        return;
    }
    if (state.M4364 >= 0x10) {
        state.M4364 = 0x10;
    }
    l3a4e();
}

/*
 * L3A62-L3A81 is a third fade-down stage feeding SoundControlA.
 */
/* [ASM: 3A78-3A81] */
static void l3a78(void) {
    state.M4366--;
    state.SoundControlA = (uint8_t)((state.SoundControlA & 0x08) | 0x04);
}

/* [ASM: 3A62-3A77] */
static void l3a62(void) {
    if (state.M4366 == 0) return;
    if (state.M4366 >= 0x10) {
        state.M4366 = 0x10;
        if (state.LevelAndRound & 0x08) {
            state.M4366 = 0x05;
        }
    }
    l3a78();
}

/*
 * [ASM: 3A82-3A8F] Mutes the tune-select bits once Counter9A reaches 3.
 */
static void l3a82(void) {
    if (state.Counter9A < 0x03) return;
    state.SoundControlB &= 0x3F;
}

/*
 * [ASM: 3A90-3A95, 3923-392D] Mothership score-display tick sound.
 */
/* [ASM: 3A90-3A95] */
static void l3a90(void) {
    if (state.M436B == 0) return;
    state.M436B--;
    state.SoundControlB = (uint8_t)((state.SoundControlB & 0x3F) | 0x80);
}

/*
 * [ASM: 3A98-3ACA] Scans the alien slot table at $4B70 (stepping 4 bytes
 * at a time, 16 slots) counting active/damaged aliens, then folds the
 * count into SoundControlA's low 6 bits.
 */
static void l3a98_scan(void) {
    uint8_t lo = 0x70;
    uint8_t c = 0;
    do {
        uint8_t a = mem_read((uint16_t)(0x4B00 | lo));
        lo++;
        if (a & 0x08) {
            a = mem_read((uint16_t)(0x4B00 | lo));
            if (a >= 0x28) c++;
        }
        lo = (uint8_t)(lo + 3);
    } while (lo != 0xB0);

    if (c == 0) return;
    if (c >= 8) c = 8;
    state.SoundControlA = (uint8_t)((state.SoundControlA & 0xC0) | (uint8_t)(c + 0x25));
}

/*
 * [ASM: 3AF8-3B00] Bumps the bird-wave sound stage counter.
 */
static void l3af8(void) {
    state.M438E++;
    state.SoundControlB |= 0x10;
}

/*
 * [ASM: 3AD0-3AF6] Bird-wave sound trigger: mixes M438E's low bit into
 * SoundControlB, then advances M4396 against a decay table (T3DE0) that
 * resets it once the count runs past the table's threshold for the
 * current bird-layer scroll position (B4BD6).
 */
static void l3ad0(void) {
    uint8_t b = (uint8_t)(((state.M438E & 0x01) << 2) | 0x20);
    state.SoundControlB = (uint8_t)((state.SoundControlB & 0xC0) | b);

    uint8_t old_m4396 = state.M4396;
    state.M4396++;
    if (old_m4396 == 0) {
        l3af8();
        return;
    }
    extern const uint8_t phoenix_bird_sound_cadence[0x20];
    uint8_t table_val = phoenix_bird_sound_cadence[state.B4BD6];
    if (table_val < state.M4396) {
        state.M4396 = 0;
    }
}

/*
 * [ASM: 3B02-3B19] Mothership sound trigger, gated on Counter9A/Counter9B.
 */
static void l3b02(void) {
    if (state.Counter9A >= 0x02) return;
    uint8_t b = state.Counter9B;
    state.SoundControlB = 0x0A;
    if (b & 0x60) return;
    state.SoundControlB = (uint8_t)((b & 0x02) + 0x1C);
}

/*
 * L3B1B-L3B31 is the M4362 fade-down stage feeding SoundControlB.
 */
/* [ASM: 3B28-3B31] */
static void l3b28(void) {
    state.M4362--;
    state.SoundControlB = (uint8_t)((state.M4362 & 0x06) << 1);
}

/* [ASM: 3B1B-3B27] */
static void l3b1b(void) {
    if (state.M4362 == 0) return;
    if (state.M4362 >= 0x40) {
        state.M4362 = 0x40;
    }
    l3b28();
}

/*
 * [ASM: 3B33-3B41] M436A fade-down stage feeding SoundControlB.
 */
static void l3b33(void) {
    if (state.M436A == 0) return;
    uint8_t old = state.M436A;
    state.M436A--;
    state.SoundControlB = (uint8_t)((old & 0x08) | 0x07);
}

/*
 * [ASM: 3B43-3B5B] Master per-frame sound dispatcher: runs the level-type
 * dispatcher (only during normal gameplay), then every fade/trigger stage
 * in turn.
 */
static void l3b43(void) {
    if (state.GameState == GAME_STATE_PLAYING) {
        l23d6();
    }
    l3b33();
    l3b1b();
    l3a1d();
    l27bd();
    l3a82();
    l3a90();
}

/*
 * [ASM: 3A10-3A1C] Entry point, reached via a tail-jump from
 * UpdateSoundControlHW (scoring.c's update_scores_and_sound). At the
 * start of a level (LevelAndRound==0) it kicks off Tune3 (ESTUDIO, the
 * Phoenix theme); otherwise it runs the master dispatcher every frame.
 */
void l3a10(void) {
    if (state.LevelAndRound != 0) {
        l3b43();
        return;
    }
    state.SoundControlB = 0xCF;
}
