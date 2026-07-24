"""Regression test for sample-positioned audio latch events."""

import pathlib
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SoundEventQueueTest(unittest.TestCase):
    def test_tune_event_applies_at_its_sample_index(self):
        source = r'''
            #include <stdint.h>
            #include "sound.h"

            static long energy(const int16_t *pcm, int start, int end) {
                long total = 0;
                for (int i = start; i < end; i++) {
                    total += pcm[i] < 0 ? -pcm[i] : pcm[i];
                }
                return total;
            }

            int main(void) {
                int16_t pcm[SOUND_MAX_FRAME_SAMPLES];
                long baseline_before;
                long baseline_after;
                long tune_before;
                long tune_after;
                int samples;

                sound_init();
                sound_set_frame_sample_index(0);
                sound_write_control_b(0x0F);
                samples = sound_render_frame(pcm);
                if (samples != SOUND_FRAME_SAMPLES) return 1;
                baseline_before = energy(pcm, 32, 400);
                baseline_after = energy(pcm, 416, samples);

                sound_init();
                sound_set_frame_sample_index(0);
                sound_write_control_b(0xCF);
                sound_set_frame_sample_index(400);
                sound_write_control_b(0x0F);
                samples = sound_render_frame(pcm);
                if (samples != SOUND_FRAME_SAMPLES) return 1;
                tune_before = energy(pcm, 32, 400);
                tune_after = energy(pcm, 416, samples);
                if (tune_before <= baseline_before * 4 / 3) return 2;
                if (tune_after > baseline_after * 101 / 100) return 3;
                return 0;
            }
        '''
        with tempfile.TemporaryDirectory() as directory:
            directory = pathlib.Path(directory)
            program = directory / "sound_event_queue.c"
            binary = directory / "sound_event_queue"
            program.write_text(source)
            subprocess.run(
                [
                    "cc", "-std=c99", "-I", str(ROOT), str(program),
                    str(ROOT / "sound.c"),
                    str(ROOT / "sound_discrete.c"),
                    str(ROOT / "tms36xx.c"),
                    str(ROOT / "mame_lofi_resampler.c"),
                    "-lm", "-o", str(binary),
                ],
                check=True,
                cwd=ROOT,
            )
            subprocess.run([str(binary)], check=True, cwd=ROOT)


if __name__ == "__main__":
    unittest.main()
