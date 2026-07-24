import com.badlogic.gdx.audio.AudioDevice;

/**
 * LibGDX PCM adapter for the emulator's 48 kHz mono little-endian byte stream.
 */
final class LibGdxPcmSink implements PcmSink {
    private final AudioDevice device;
    private short[] samples = new short[0];
    private boolean closed;

    LibGdxPcmSink(AudioDevice device) {
        if (device == null) {
            throw new NullPointerException("device");
        }
        this.device = device;
    }

    @Override
    public synchronized void write(byte[] pcm, int offset, int length) {
        if (closed) {
            return;
        }
        if (offset < 0 || length < 0 || offset + length > pcm.length || (length & 1) != 0) {
            throw new IllegalArgumentException("invalid 16-bit PCM range");
        }
        int sampleCount = length / 2;
        if (samples.length < sampleCount) {
            samples = new short[sampleCount];
        }
        for (int i = 0; i < sampleCount; i++) {
            int byteIndex = offset + i * 2;
            samples[i] = (short) ((pcm[byteIndex] & 0xff) | (pcm[byteIndex + 1] << 8));
        }
        device.writeSamples(samples, 0, sampleCount);
    }

    @Override
    public synchronized void close() {
        if (!closed) {
            closed = true;
            device.dispose();
        }
    }
}
