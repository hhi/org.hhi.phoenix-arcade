import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.IOException;
import javax.sound.sampled.AudioFileFormat;
import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;

final class SoundRenderUtil {
	static final int SAMPLE_RATE = 48000;
	static final int FRAME_BYTES = SAMPLE_RATE / 60 * 2;
	static final int CYCLES_PER_FRAME = 12333;

	private SoundRenderUtil() {
	}

	static byte[] renderFrames(Sound sound, int frames) {
		byte[] out = new byte[frames * FRAME_BYTES];
		int offset = 0;
		for (int i = 0; i < frames; i++) {
			byte[] frame = sound.renderFrameForTest();
			System.arraycopy(frame, 0, out, offset, frame.length);
			offset += frame.length;
		}
		return out;
	}

	static PcmStats stats(byte[] pcm) {
		return stats(pcm, 0, pcm.length);
	}

	static PcmStats stats(byte[] pcm, int startByte, int lengthBytes) {
		long sumSquares = 0;
		int peak = 0;
		int clipped = 0;
		int samples = lengthBytes / 2;
		for (int i = startByte; i < startByte + lengthBytes; i += 2) {
			int sample = (short) ((pcm[i] & 0xff) | (pcm[i + 1] << 8));
			int abs = Math.abs(sample);
			if (abs > peak) {
				peak = abs;
			}
			if (sample == 32767 || sample == -32768) {
				clipped++;
			}
			sumSquares += (long) sample * sample;
		}
		return new PcmStats(peak, Math.sqrt(sumSquares / (double) samples), clipped);
	}

	static void writeWav(File file, byte[] pcm) throws IOException {
		AudioFormat format = new AudioFormat(AudioFormat.Encoding.PCM_SIGNED,
				SAMPLE_RATE, 16, 1, 2, SAMPLE_RATE, false);
		try (AudioInputStream stream = new AudioInputStream(
				new ByteArrayInputStream(pcm), format, pcm.length / 2)) {
			AudioSystem.write(stream, AudioFileFormat.Type.WAVE, file);
		}
	}

	static final class PcmStats {
		final int peak;
		final double rms;
		final int clippedSamples;

		PcmStats(int peak, double rms, int clippedSamples) {
			this.peak = peak;
			this.rms = rms;
			this.clippedSamples = clippedSamples;
		}
	}
}
