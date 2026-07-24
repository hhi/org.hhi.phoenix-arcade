/**
 * Destination for signed 16-bit, mono, little-endian PCM at 48 kHz.
 */
public interface PcmSink extends AutoCloseable {
    void write(byte[] pcm, int offset, int length);

    @Override
    default void close() {
    }

    static PcmSink discarding() {
        return (pcm, offset, length) -> {
        };
    }
}
