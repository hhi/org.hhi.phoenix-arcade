import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.DataLine;
import javax.sound.sampled.LineUnavailableException;
import javax.sound.sampled.SourceDataLine;

/**
 * Desktop PCM adapter backed by Java Sound.
 */
public final class JavaSoundPcmSink implements PcmSink {
    private final SourceDataLine line;

    public JavaSoundPcmSink(int sampleRate) {
        AudioFormat format = new AudioFormat(
                AudioFormat.Encoding.PCM_SIGNED,
                sampleRate,
                16,
                1,
                2,
                sampleRate,
                false);
        DataLine.Info info = new DataLine.Info(SourceDataLine.class, format);
        if (!AudioSystem.isLineSupported(info)) {
            throw new IllegalStateException("Line unsupported: " + info);
        }

        try {
            line = (SourceDataLine) AudioSystem.getLine(info);
            line.open(format, sampleRate / 10 * 2);
            line.start();
        } catch (LineUnavailableException e) {
            throw new IllegalStateException("DataLine not available", e);
        }
    }

    @Override
    public void write(byte[] pcm, int offset, int length) {
        line.write(pcm, offset, length);
    }

    @Override
    public void close() {
        line.drain();
        line.stop();
        line.close();
    }
}
