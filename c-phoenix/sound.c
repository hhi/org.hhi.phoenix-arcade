#include "sound.h"
#include "tms36xx.h"
#include "mame_lofi_resampler.h"
#include "sound_discrete.h"
#include <stdbool.h>
#include <stddef.h>

#define MAME_STREAM_FULL_SCALE 32768.0
#define MAME_DISCRETE_ROUTE 0.6
#define MAME_CUSTOM_ROUTE 0.4
#define MAME_TMS_ROUTE 0.5
#define SOUND_EVENT_CAPACITY 64

typedef struct {
    uint16_t sample_index;
    uint8_t control;
    uint8_t value;
} SoundEvent;

static TMS36XX g_tms;
static MameLofiResampler g_resampler;
static SoundDiscrete g_discrete;
static MameLofiResampler g_discrete_resampler;
static uint8_t g_control_a = 0;
static uint8_t g_control_b = 0;
static uint8_t g_render_latch_a = 0;
static uint8_t g_render_latch_b = 0;
static uint16_t g_frame_sample_index = SOUND_FRAME_END_SAMPLE;
static SoundEvent g_events[SOUND_EVENT_CAPACITY];
static int g_event_count = 0;
static bool g_initialized = false;

/*
 * Adapter used by the MAME-style resampler to pull one native-rate TMS3615
 * music sample from the chip model. The context argument is unused because the
 * current port keeps a single global chip instance.
 */
static double tms_source(void* ctx) {
    (void)ctx;
    return tms36xx_render_internal_sample(&g_tms);
}

/*
 * Adapter used by the discrete-sound resampler. It renders the analog effects
 * domain from the latches that are active at the current output sample.
 */
static double discrete_source(void* ctx) {
    (void)ctx;
    return sound_discrete_step(&g_discrete, g_render_latch_a, g_render_latch_b);
}

/*
 * Initializes all audio generators and clears the frame-local event queue.
 * This mirrors the split hardware model used by jphoenix: TMS music, discrete
 * effects, and custom noise are rendered separately and mixed per output
 * sample in sound_render_frame().
 */
void sound_init(void) {
    tms36xx_init(&g_tms);
    mame_lofi_resampler_init(&g_resampler, g_tms.samplerate, SOUND_SAMPLE_RATE);
    sound_discrete_init(&g_discrete);
    mame_lofi_resampler_init(&g_discrete_resampler, SOUND_DISCRETE_SAMPLE_RATE, SOUND_SAMPLE_RATE);
    g_control_a = 0;
    g_control_b = 0;
    g_render_latch_a = 0;
    g_render_latch_b = 0;
    g_frame_sample_index = SOUND_FRAME_END_SAMPLE;
    g_event_count = 0;
    g_initialized = true;
}

/*
 * Sets the sample position for subsequent sound-control writes in the current
 * video frame. Most translated gameplay writes occur at frame end; callers can
 * move this earlier when a more precise event phase is known.
 */
void sound_set_frame_sample_index(uint16_t sample_index) {
    if (sample_index > SOUND_FRAME_END_SAMPLE) {
        sample_index = SOUND_FRAME_END_SAMPLE;
    }
    g_frame_sample_index = sample_index;
}

/*
 * Queues a sound-control latch update at the current frame sample position.
 * Events are kept ordered so rendering can apply register changes at the same
 * sample offset at which gameplay observed them.
 */
static void queue_event(uint8_t control, uint8_t value) {
    if (g_event_count == SOUND_EVENT_CAPACITY) {
        /* The translated ROM emits at most two writes per frame. Preserve the
         * newest write if a future caller violates that contract. */
        g_events[SOUND_EVENT_CAPACITY - 1].control = control;
        g_events[SOUND_EVENT_CAPACITY - 1].value = value;
        g_events[SOUND_EVENT_CAPACITY - 1].sample_index = g_frame_sample_index;
        return;
    }

    int insert_at = g_event_count;
    while (insert_at > 0 && g_events[insert_at - 1].sample_index > g_frame_sample_index) {
        g_events[insert_at] = g_events[insert_at - 1];
        insert_at--;
    }
    g_events[insert_at].sample_index = g_frame_sample_index;
    g_events[insert_at].control = control;
    g_events[insert_at].value = value;
    g_event_count++;
}

/*
 * Records a write to the $6000 sound-control latch. Repeated writes of the
 * same value are ignored, matching the observable latch state rather than
 * inventing extra audio edges.
 */
void sound_write_control_a(uint8_t val) {
    if (val == g_control_a) return;
    g_control_a = val;
    queue_event('A', val);
}

/*
 * Records a write to the $6800 sound-control latch. The B latch also selects
 * the active TMS tune when the event is applied during rendering.
 */
void sound_write_control_b(uint8_t val) {
    if (val == g_control_b) return;
    g_control_b = val;
    queue_event('B', val);
}

/*
 * Applies one queued latch event to the render-time audio state. Separating
 * queued state from render state lets one frame contain multiple sound writes
 * without collapsing them into a single end-of-frame value.
 */
static void apply_event(const SoundEvent* event) {
    if (event->control == 'A') {
        g_render_latch_a = event->value;
        return;
    }
    g_render_latch_b = event->value;
    tms36xx_mm6221aa_tune_w(&g_tms, (event->value >> 6) & 0x03);
}

/*
 * Saturates the mixed floating-point output after conversion to signed 16-bit
 * PCM. The upstream generators can momentarily sum outside the target range.
 */
static int clamp_pcm16(int sample) {
    if (sample > 32767) return 32767;
    if (sample < -32768) return -32768;
    return sample;
}

/*
 * Renders one video frame worth of audio into the SDL queue buffer. The output
 * sample count distributes 44100 Hz over 60 Hz frames using a remainder so
 * long runs do not drift, then applies queued latch events at their sample
 * positions before mixing TMS music, discrete effects, and custom noise.
 */
int sound_render_frame(int16_t* out) {
    if (!g_initialized) return 0;

    static int remainder = 0;
    remainder += SOUND_SAMPLE_RATE;
    int samples = remainder / 60;
    remainder -= samples * 60;
    if (samples > SOUND_MAX_FRAME_SAMPLES) samples = SOUND_MAX_FRAME_SAMPLES;

    int event_index = 0;
    for (int i = 0; i < samples; i++) {
        while (event_index < g_event_count && g_events[event_index].sample_index <= i) {
            apply_event(&g_events[event_index]);
            event_index++;
        }
        double tms = mame_lofi_resampler_next(&g_resampler, tms_source, NULL);
        double discrete = mame_lofi_resampler_next(&g_discrete_resampler, discrete_source, NULL);
        double custom_noise = (sound_discrete_noise(&g_discrete, SOUND_SAMPLE_RATE, g_render_latch_a) / 2.0) / MAME_STREAM_FULL_SCALE;
        double mixed = discrete * MAME_DISCRETE_ROUTE + custom_noise * MAME_CUSTOM_ROUTE + tms * MAME_TMS_ROUTE;
        int sample = clamp_pcm16((int)(mixed * MAME_STREAM_FULL_SCALE + (mixed >= 0 ? 0.5 : -0.5)));
        out[i] = (int16_t)sample;
    }
    while (event_index < g_event_count) {
        apply_event(&g_events[event_index]);
        event_index++;
    }
    g_event_count = 0;
    g_frame_sample_index = SOUND_FRAME_END_SAMPLE;
    return samples;
}
