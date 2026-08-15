#ifndef SOUND_DISCRETE_H
#define SOUND_DISCRETE_H

#include <stdint.h>
#include <stdbool.h>

/*
 * Phase B: the discrete analog effect1/effect2/noise circuitry from
 * jphoenix's Sound.java (itself a port of MAME's phoenix.cpp discrete
 * netlist) -- 555-timer astables, RC filters, resistor mixer networks,
 * and an 18-bit polynomial noise generator. Ported node-for-node so the
 * exact same voltage-domain math runs here; only Java's object identity
 * (each node a field) becomes explicit struct members.
 */

#define SOUND_DISCRETE_SAMPLE_RATE 120000
#define SOUND_DISCRETE_POLY18_COUNT (1 << 13) /* 1 << (18 - 5) */

typedef struct {
    bool flip_flop;
    double cap_voltage;
    double last_output;
    double v_pos;
    double v_out_high;
} Astable555;

typedef struct {
    double target[2];
    double rc[2];
    double max_output;
    double cap_voltage;
} RcDisc4Type1;

typedef struct {
    uint32_t poly18[SOUND_DISCRETE_POLY18_COUNT];

    double effect2_c22_voltage;
    Astable555 effect2_node33;
    Astable555 effect2_node34;
    Astable555 effect2_node39;
    Astable555 effect1_node21;
    RcDisc4Type1 effect1_node20;

    int effect2_note_count1, effect2_note_count2;
    int effect1_note_count1, effect1_note_count2;

    int c24_counter, c24_level;
    int c25_counter, c25_level;

    int n_counter, n_polyoffs, n_polybit;
    int n_lowpass_counter, n_lowpass_polybit;

    double mixer_input_caps[4];
    double mixer_amp_cap;
    double effect1_filter_state;
} SoundDiscrete;

void sound_discrete_init(SoundDiscrete* sd);

/* Renders one discrete-domain sample (SOUND_DISCRETE_SAMPLE_RATE) of the
 * effect1+effect2 mix (Sound.java's stepDiscreteNodes(...).node90). Feed
 * through a MameLofiResampler (120kHz -> output rate) before mixing. */
double sound_discrete_step(SoundDiscrete* sd, uint8_t latch_a, uint8_t latch_b);

/* Renders one custom-noise sample directly at the OUTPUT sample rate (no
 * resampling in the original -- Sound.java's noise() runs at sampleRate,
 * not discreteSampleRate). Caller divides by 2.0 * 32768.0 to match
 * Sound.java's process(): (noise(...) / 2.0) / MAME_STREAM_FULL_SCALE. */
int sound_discrete_noise(SoundDiscrete* sd, int samplerate, uint8_t latch_a);

#endif // SOUND_DISCRETE_H
