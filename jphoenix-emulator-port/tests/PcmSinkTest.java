import java.util.Arrays;

public final class PcmSinkTest {
    private PcmSinkTest() {
    }

    public static void main(String[] args) {
        RecordingSink sink = new RecordingSink();
        Sound sound = new Sound(sink);
        sound.endFrame();

        if (sink.writeCalls != 1) {
            throw new AssertionError("expected one PCM write, got " + sink.writeCalls);
        }
        if (sink.pcm.length != 48000 / 60 * 2) {
            throw new AssertionError(
                    "expected one 48 kHz mono frame, got " + sink.pcm.length + " bytes");
        }

        sound.stop();
        if (!sink.closed) {
            throw new AssertionError("Sound.stop() did not close the PCM sink");
        }

        PcmSink.discarding().write(new byte[2], 0, 2);
    }

    private static final class RecordingSink implements PcmSink {
        byte[] pcm = new byte[0];
        int writeCalls;
        boolean closed;

        @Override
        public void write(byte[] source, int offset, int length) {
            pcm = Arrays.copyOfRange(source, offset, offset + length);
            writeCalls++;
        }

        @Override
        public void close() {
            closed = true;
        }
    }
}
