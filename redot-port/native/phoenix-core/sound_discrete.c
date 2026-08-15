#include "sound_discrete.h"
#include <math.h>
#include <string.h>

/*
 * Direct port of jphoenix's Sound.java discrete-circuit section (node20-
 * node90, the c24/c25 noise-envelope shapers, and the 18-bit poly noise
 * generator). Constant names and node numbers match the Java source so
 * the two can be diffed side by side.
 */

#define VMIN 0
#define VMAX 32767

static const double C18a = 0.01e-6;
static const double C20  = 1.0e-6;
static const double C22  = 100.0e-6;
static const double C24  = 6.8e-6;
static const double C25  = 6.8e-6;
static const double C7   = 6.8e-6;
static const double R22 = 470.0;
static const double R23 = 100000.0;
static const double R24 = 33000.0;
static const double R40 = 47000.0;
static const double R41 = 100000.0;
static const double R43 = 510000.0;
static const double R44 = 510000.0;
static const double R49 = 1000.0;
static const double R50 = 1000.0;
static const double R51 = 330.0;
static const double R52 = 20000.0;
static const double R53 = 330.0;
static const double R54 = 47000.0;

#define MAME_TTL_LOGIC_1 3.4
#define MAME_DISCRETE_OUTPUT_GAIN 40000.0
#define MAME_STREAM_FULL_SCALE 32768.0

/* ---- SoundControlMapping ---- */
static int effect2_data(int a) { return a & 0x0f; }
static int effect2_frequency(int a) { return (a & 0x30) >> 4; }
static bool noise_c24_discharge(int a) { return (a & 0x40) != 0; }
static bool noise_c25_charge(int a) { return (a & 0x80) != 0; }
static int effect1_data(int b) { return b & 0x0f; }
static bool effect1_frequency(int b) { return (b & 0x10) != 0; }
static bool effect1_filter_selected(int b) { return (b & 0x20) != 0; }

static double parallel2(double r1, double r2) { return 1.0 / (1.0 / r1 + 1.0 / r2); }

static double rc_exponent(double rc, double dt) {
    if (rc <= 0.0) return 1.0;
    return 1.0 - exp(-dt / rc);
}

static void build_poly18(uint32_t* poly18, int count) {
    uint32_t shiftreg = 0;
    for (int i = 0; i < count; i++) {
        uint32_t bits = 0;
        for (int j = 0; j < 32; j++) {
            bits = (bits >> 1) | (shiftreg << 31);
            if (((shiftreg >> 16) & 1) == ((shiftreg >> 17) & 1)) {
                shiftreg = (shiftreg << 1) | 1;
            } else {
                shiftreg = shiftreg << 1;
            }
        }
        poly18[i] = bits;
    }
}

/* ---- Astable555 ---- */
static void astable_init(Astable555* n, double v_pos, double v_out_high) {
    n->v_pos = v_pos;
    n->v_out_high = v_out_high;
    n->flip_flop = true;
    n->cap_voltage = 0.0;
    n->last_output = 0.0;
}

static double astable_step(Astable555* n, double r1, double r2, double c,
                            double control_voltage, int sample_rate, bool count_f_output) {
    bool use_cv = control_voltage >= 0.0;
    double threshold = use_cv ? control_voltage : n->v_pos * 2.0 / 3.0;
    if (threshold < 0.25) {
        return n->last_output;
    }
    double trigger = threshold / 2.0;
    double charge_voltage = n->v_pos;
    double dt = 1.0 / sample_rate;
    double x_time = 0.0;
    int count_f = 0, count_r = 0;

    if (use_cv) {
        if (n->cap_voltage >= threshold) {
            n->flip_flop = false;
            count_f++;
        } else if (n->cap_voltage <= trigger) {
            n->flip_flop = true;
            count_r++;
        }
    }

    while (dt > 0.0) {
        if (c == 0.0) {
            n->flip_flop = true;
            n->cap_voltage = charge_voltage;
            break;
        }
        if (n->flip_flop) {
            if (r1 == 0.0) {
                n->cap_voltage -= n->cap_voltage * rc_exponent(10000000.0 * c, dt);
                break;
            }
            double rc = (r1 + r2) * c;
            double next = n->cap_voltage + (charge_voltage - n->cap_voltage) * rc_exponent(rc, dt);
            if (next >= threshold) {
                double overshoot_ratio = (next - threshold) / (charge_voltage - n->cap_voltage);
                dt = rc * log(1.0 / (1.0 - overshoot_ratio));
                x_time = dt;
                n->cap_voltage = threshold;
                n->flip_flop = false;
                count_f++;
            } else {
                n->cap_voltage = next;
                dt = 0.0;
            }
        } else {
            if (r2 == 0.0) {
                n->cap_voltage = trigger;
            } else {
                double rc = r2 * c;
                double next = n->cap_voltage - n->cap_voltage * rc_exponent(rc, dt);
                if (next <= trigger) {
                    if (next < trigger && n->cap_voltage > 0.0) {
                        double overshoot_ratio = (trigger - next) / n->cap_voltage;
                        dt = rc * log(1.0 / (1.0 - overshoot_ratio));
                    }
                    x_time = dt;
                    n->cap_voltage = trigger;
                    n->flip_flop = true;
                    count_r++;
                } else {
                    n->cap_voltage = next;
                    dt = 0.0;
                }
            }
        }
    }
    (void)count_r;

    double x_ratio = x_time * sample_rate;
    double output;
    if (count_f_output) {
        output = count_f != 0 ? count_f + x_ratio : 0.0;
    } else {
        if (x_ratio == 0.0) x_ratio = 1.0;
        output = n->v_out_high * (n->flip_flop ? x_ratio : (1.0 - x_ratio));
    }
    n->last_output = output;
    return output;
}

static double astable_step_count_f(Astable555* n, double r1, double r2, double c, double cv, int sr) {
    return astable_step(n, r1, r2, c, cv, sr, true);
}
static double astable_step_energy(Astable555* n, double r1, double r2, double c, double cv, int sr) {
    return astable_step(n, r1, r2, c, cv, sr, false);
}

/* ---- RcDisc4Type1 ---- */
static void rcdisc4_init(RcDisc4Type1* n, double r1, double r2, double r3, double c, double supply_voltage) {
    double diode_supply = supply_voltage - 0.5;

    double input_high_r = parallel2(r1, r3);
    double input_high_current = diode_supply / (r2 + input_high_r);
    n->target[1] = input_high_current * input_high_r + 0.5;
    n->rc[1] = parallel2(r2, input_high_r) * c;

    double input_low_current = diode_supply / (r2 + r3);
    n->target[0] = input_low_current * r3 + 0.5;
    n->rc[0] = parallel2(r2, r3) * c;

    n->max_output = supply_voltage - 1.5;
    n->cap_voltage = 0.0;
}

static double rcdisc4_step(RcDisc4Type1* n, bool input, int sample_rate) {
    int index = input ? 1 : 0;
    double exponent = rc_exponent(n->rc[index], 1.0 / sample_rate);
    n->cap_voltage += (n->target[index] - n->cap_voltage) * exponent;
    if (n->cap_voltage < 0.0) return 0.0;
    if (n->cap_voltage > n->max_output) return n->max_output;
    return n->cap_voltage;
}

/* ---- effect2 support ---- */
static double effect2_capacitance(int frequency_select) {
    switch (frequency_select) {
        case 1: return C18a + 0.47e-6;
        case 2: return C18a + 1.0e-6;
        case 3: return C18a + 0.47e-6 + 1.0e-6;
        default: return C18a;
    }
}

typedef struct { double node35, node36; } Effect2MixerNodes;

static double resistor_mixer(const double* values, const double* resistors, int n, double feedback) {
    double current = 0.0;
    double conductance = feedback != 0.0 ? 1.0 / feedback : 0.0;
    for (int i = 0; i < n; i++) {
        current += values[i] / resistors[i];
        conductance += 1.0 / resistors[i];
    }
    return current / conductance;
}

static Effect2MixerNodes effect2_mixer_nodes(double node33, double node34) {
    double v1[3] = { node33, node34, 5.0 };
    double r1[3] = { 10000.0, 5100.0 + 5100.0, 5000.0 };
    double node35 = resistor_mixer(v1, r1, 3, 10000.0);

    double v2[2] = { node34, node35 };
    double r2[2] = { 5100.0, 5100.0 };
    double node36 = resistor_mixer(v2, r2, 2, 0.0);

    Effect2MixerNodes result;
    result.node35 = node35;
    result.node36 = node36;
    return result;
}

static double effect2_control_voltage(double node33, double c22_voltage) {
    double v[3] = { node33, c22_voltage, 5.0 };
    double r[3] = { 10000.0, 5100.0, 5000.0 };
    return resistor_mixer(v, r, 3, 10000.0);
}

static double effect2_charge_resistance(void) {
    double internal = 1.0 / (1.0 / 10000.0 + 1.0 / 5000.0 + 1.0 / 10000.0);
    return 1.0 / (1.0 / 5100.0 + 1.0 / (5100.0 + internal));
}

static double effect2_c22_exponent(int rate) {
    return 1.0 - exp(-1.0 / (rate * effect2_charge_resistance() * C22));
}

/* ---- shared effect1/effect2 note counter ---- */
static double note_energy(SoundDiscrete* sd, int data, double clock_input, bool is_effect2) {
    int count1 = is_effect2 ? sd->effect2_note_count1 : sd->effect1_note_count1;
    int count2 = is_effect2 ? sd->effect2_note_count2 : sd->effect1_note_count2;
    int last_count2 = count2;
    int increments = (int)clock_input;
    double x_time = clock_input - increments;

    if (data != 0x0f) {
        for (int i = 0; i < increments; i++) {
            count1++;
            if (count1 > 0x0f) {
                count1 = data;
                count2++;
                if (count2 > 1) count2 = 0;
            }
        }
    }

    double output = count2;
    if (count2 != last_count2) {
        if (x_time == 0.0) x_time = 1.0;
        output = last_count2;
        if (count2 > last_count2) {
            output += (count2 - last_count2) * x_time;
        } else {
            output -= (last_count2 - count2) * x_time;
        }
    }

    if (is_effect2) {
        sd->effect2_note_count1 = count1;
        sd->effect2_note_count2 = count2;
    } else {
        sd->effect1_note_count1 = count1;
        sd->effect1_note_count2 = count2;
    }
    return output;
}

/* ---- effect1 output filter ---- */
static double effect1_filter_step(SoundDiscrete* sd, double input, int latch_b) {
    double resistance = parallel2(10000.0, 100000.0);
    double capacitor = 0.047e-6;
    double exponent = 1.0 - exp(-1.0 / (SOUND_DISCRETE_SAMPLE_RATE * resistance * capacitor));
    sd->effect1_filter_state += (input - sd->effect1_filter_state) * exponent;
    return effect1_filter_selected(latch_b) ? sd->effect1_filter_state : input;
}

/* ---- final discrete mixer (node90) ---- */
static double high_pass_mixer_input(SoundDiscrete* sd, int index, double input,
                                     double resistor, double feedback, double capacitor) {
    double rc_resistance = parallel2(resistor, feedback);
    double exponent = 1.0 - exp(-1.0 / (SOUND_DISCRETE_SAMPLE_RATE * rc_resistance * capacitor));
    sd->mixer_input_caps[index] += (input - sd->mixer_input_caps[index]) * exponent;
    return input - sd->mixer_input_caps[index];
}

static double high_pass_mixer_output(SoundDiscrete* sd, double input) {
    double exponent = 1.0 - exp(-1.0 / (SOUND_DISCRETE_SAMPLE_RATE * 100000.0 * 10.0e-6));
    sd->mixer_amp_cap += (input - sd->mixer_amp_cap) * exponent;
    return input - sd->mixer_amp_cap;
}

static double mix_discrete_sources(SoundDiscrete* sd, double effect1, double effect2) {
    double inputs[4] = { effect1, effect2, 0.0, 0.0 };
    double resistors[4] = { 57000.0, 30000.0, 20000.0, 20000.0 };
    double capacitors[4] = { 10.0e-6, 10.0e-6, 0.1e-6, 10.0e-6 };
    double feedback = 10000.0;
    double total_conductance = 1.0 / feedback;
    double current = 0.0;

    for (int i = 0; i < 4; i++) {
        double filtered = high_pass_mixer_input(sd, i, inputs[i], resistors[i], feedback, capacitors[i]);
        current += filtered / resistors[i];
        total_conductance += 1.0 / resistors[i];
    }

    double mixed_voltage = current / total_conductance;
    double output = high_pass_mixer_output(sd, mixed_voltage);
    return output * MAME_DISCRETE_OUTPUT_GAIN / MAME_STREAM_FULL_SCALE;
}

/* ---- c24/c25 noise envelope + poly18 noise ---- */
static int update_c24(SoundDiscrete* sd, int samplerate, int latch_a) {
    if (noise_c24_discharge(latch_a)) {
        if (sd->c24_level > VMIN) {
            sd->c24_counter -= (int)((sd->c24_level - VMIN) / (R52 * C24));
            if (sd->c24_counter <= 0) {
                int n = -sd->c24_counter / samplerate + 1;
                sd->c24_counter += n * samplerate;
                sd->c24_level -= n;
                if (sd->c24_level < VMIN) sd->c24_level = VMIN;
            }
        }
    } else {
        if (sd->c24_level < VMAX) {
            sd->c24_counter -= (int)((VMAX - sd->c24_level) / ((R51 + R49) * C24));
            if (sd->c24_counter <= 0) {
                int n = -sd->c24_counter / samplerate + 1;
                sd->c24_counter += n * samplerate;
                sd->c24_level += n;
                if (sd->c24_level > VMAX) sd->c24_level = VMAX;
            }
        }
    }
    return VMAX - sd->c24_level;
}

static int update_c25(SoundDiscrete* sd, int samplerate, int latch_a) {
    if (noise_c25_charge(latch_a)) {
        if (sd->c25_level < VMAX) {
            sd->c25_counter -= (int)((VMAX - sd->c25_level) / ((R50 + R53) * C25));
            if (sd->c25_counter <= 0) {
                int n = -sd->c25_counter / samplerate + 1;
                sd->c25_counter += n * samplerate;
                sd->c25_level += n;
                if (sd->c25_level > VMAX) sd->c25_level = VMAX;
            }
        }
    } else {
        if (sd->c25_level > VMIN) {
            sd->c25_counter -= (int)((sd->c25_level - VMIN) / (R54 * C25));
            if (sd->c25_counter <= 0) {
                int n = -sd->c25_counter / samplerate + 1;
                sd->c25_counter += n * samplerate;
                sd->c25_level -= n;
                if (sd->c25_level < VMIN) sd->c25_level = VMIN;
            }
        }
    }
    return sd->c25_level;
}

int sound_discrete_noise(SoundDiscrete* sd, int samplerate, uint8_t latch_a) {
    int vc24 = update_c24(sd, samplerate, latch_a);
    int vc25 = update_c25(sd, samplerate, latch_a);
    int sum = 0, level, frequency;

    if (vc24 < vc25) level = vc24 + (vc25 - vc24) / 2;
    else level = vc25 + (vc24 - vc25) / 2;

    frequency = 588 + 6325 * level / 32768;

    sd->n_counter -= frequency;
    if (sd->n_counter <= 0) {
        int n = (-sd->n_counter / samplerate) + 1;
        sd->n_counter += n * samplerate;
        sd->n_polyoffs = (sd->n_polyoffs + n) & 0x3ffff;
        sd->n_polybit = (sd->poly18[sd->n_polyoffs >> 5] >> (sd->n_polyoffs & 31)) & 1;
    }
    if (sd->n_polybit == 0) sum += vc24;

    sd->n_lowpass_counter -= 400;
    if (sd->n_lowpass_counter <= 0) {
        sd->n_lowpass_counter += samplerate;
        sd->n_lowpass_polybit = sd->n_polybit;
    }
    if (sd->n_lowpass_polybit == 0) sum += vc25;

    return sum;
}

/* ---- public entry points ---- */
void sound_discrete_init(SoundDiscrete* sd) {
    memset(sd, 0, sizeof(*sd));
    build_poly18(sd->poly18, SOUND_DISCRETE_POLY18_COUNT);

    astable_init(&sd->effect2_node33, 5.0, 4.0);
    astable_init(&sd->effect2_node34, 5.0, 4.0);
    astable_init(&sd->effect2_node39, 5.0, 3.8);
    astable_init(&sd->effect1_node21, 5.0, 3.8);
    rcdisc4_init(&sd->effect1_node20, R22, R23, R24, C7, 12.0);

    /* resetDiscreteNodes(): settle the two 555s with one discrete-rate
     * step at construction time, matching Sound.java's constructor. */
    astable_step_energy(&sd->effect2_node33, R40, R41, effect2_capacitance(0), -1.0, SOUND_DISCRETE_SAMPLE_RATE);
    astable_step_energy(&sd->effect2_node34, R43, R44, C20, -1.0, SOUND_DISCRETE_SAMPLE_RATE);
}

double sound_discrete_step(SoundDiscrete* sd, uint8_t latch_a, uint8_t latch_b) {
    double effect2_node30 = effect2_capacitance(effect2_frequency(latch_a));
    double effect2_node31 = (effect2_frequency(latch_a) & 0x02) != 0 ? 1.0 : 0.0;
    double effect2_node32 = effect2_node31 != 0.0 ? MAME_TTL_LOGIC_1 / 2.0 : MAME_TTL_LOGIC_1;
    double effect2_node33 = astable_step_energy(&sd->effect2_node33, R40, R41, effect2_node30, -1.0, SOUND_DISCRETE_SAMPLE_RATE);
    double effect2_node34 = astable_step_energy(&sd->effect2_node34, R43, R44, C20, -1.0, SOUND_DISCRETE_SAMPLE_RATE);
    Effect2MixerNodes mix_nodes = effect2_mixer_nodes(effect2_node33, effect2_node34);
    double effect2_node36 = mix_nodes.node36;
    sd->effect2_c22_voltage += (effect2_node36 - sd->effect2_c22_voltage) * effect2_c22_exponent(SOUND_DISCRETE_SAMPLE_RATE);
    double effect2_node37 = sd->effect2_c22_voltage;
    double effect2_node38 = effect2_control_voltage(effect2_node33, effect2_node37);
    double effect2_node39 = astable_step_count_f(&sd->effect2_node39, 20000.0, 20000.0, 0.001e-6,
                                                  effect2_node38, SOUND_DISCRETE_SAMPLE_RATE);
    double effect2_node40 = note_energy(sd, effect2_data(latch_a), effect2_node39, true);
    double effect2_sound = effect2_node40 * effect2_node32;

    double effect1_node20 = rcdisc4_step(&sd->effect1_node20, effect1_frequency(latch_b), SOUND_DISCRETE_SAMPLE_RATE);
    double effect1_node21 = astable_step_count_f(&sd->effect1_node21, 47000.0, 47000.0, 0.001e-6,
                                                  effect1_node20, SOUND_DISCRETE_SAMPLE_RATE);
    double effect1_node22 = note_energy(sd, effect1_data(latch_b), effect1_node21, false);
    double effect1_node23 = effect1_filter_selected(latch_b)
        ? MAME_TTL_LOGIC_1 * 100000.0 / 110000.0 : MAME_TTL_LOGIC_1;
    double effect1_node24 = effect1_node22 * effect1_node23;
    double effect1_node25 = effect1_filter_step(sd, effect1_node24, latch_b);
    double effect1_sound = effect1_filter_selected(latch_b) ? effect1_node25 : effect1_node24;

    return mix_discrete_sources(sd, effect1_sound, effect2_sound);
}
