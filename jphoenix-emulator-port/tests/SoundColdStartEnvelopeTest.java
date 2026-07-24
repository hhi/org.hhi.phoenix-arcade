/*
 * Measures the RMS envelope of the first few seconds of audio starting
 * from a cold (all-zero-latch) Sound instance -- no updateControlA/B
 * calls at all, matching how the chip powers on before the game ever
 * writes to $6000/$6800. Prints one RMS value per 100ms window so it can
 * be diffed against the equivalent measurement from the C port.
 */
public class SoundColdStartEnvelopeTest {
    public static void main(String[] args) throws Exception {
        Sound sound = new Sound(PcmSink.discarding());

        int windowMs = 100;
        int windowFrames = windowMs * 60 / 1000; // frames per window at 60fps
        int totalWindows = 30; // 3 seconds

        for (int w = 0; w < totalWindows; w++) {
            long sumSquares = 0;
            long count = 0;
            for (int f = 0; f < windowFrames; f++) {
                byte[] frame = sound.renderFrameForTest();
                for (int i = 0; i + 1 < frame.length; i += 2) {
                    int sample = (short) ((frame[i] & 0xff) | (frame[i + 1] << 8));
                    sumSquares += (long) sample * sample;
                    count++;
                }
            }
            double rms = count > 0 ? Math.sqrt((double) sumSquares / count) : 0.0;
            System.out.printf("window=%2d t=%.1fs rms=%.1f%n", w, w * windowMs / 1000.0, rms);
        }
    }
}
