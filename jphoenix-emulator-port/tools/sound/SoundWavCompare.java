import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.file.Path;
import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;

public class SoundWavCompare {
	public static void main(String[] args) throws Exception {
		if (args.length < 2 || args.length > 3) {
			throw new IllegalArgumentException(
					"Usage: java SoundWavCompare <java.wav> <reference.wav> [max_lag_samples]");
		}
		int maxLag = args.length == 3 ? Integer.parseInt(args[2]) : 256;
		short[] actual = readMonoPcm16(Path.of(args[0]));
		short[] reference = readMonoPcm16(Path.of(args[1]));
		Comparison comparison = compare(actual, reference, maxLag);
		System.out.println("actual_samples=" + actual.length);
		System.out.println("reference_samples=" + reference.length);
		System.out.println("actual_peak=" + peak(actual));
		System.out.println("reference_peak=" + peak(reference));
		System.out.printf(java.util.Locale.ROOT, "actual_rms=%.6f%n", rms(actual));
		System.out.printf(java.util.Locale.ROOT, "reference_rms=%.6f%n", rms(reference));
		System.out.println("best_lag_samples=" + comparison.lag);
		System.out.printf(java.util.Locale.ROOT, "correlation=%.9f%n", comparison.correlation);
		System.out.printf(java.util.Locale.ROOT, "reference_gain_from_actual=%.9f%n", comparison.gain);
		System.out.printf(java.util.Locale.ROOT, "raw_difference_rms=%.6f%n", comparison.rawDifferenceRms);
		System.out.printf(java.util.Locale.ROOT, "gain_adjusted_difference_rms=%.6f%n",
				comparison.gainAdjustedDifferenceRms);
	}

	static Comparison compare(short[] actual, short[] reference, int maxLag) {
		Comparison best = null;
		for (int lag = -maxLag; lag <= maxLag; lag++) {
			Comparison candidate = compareAtLag(actual, reference, lag);
			if (best == null || candidate.correlation > best.correlation) {
				best = candidate;
			}
		}
		return best;
	}

	private static Comparison compareAtLag(short[] actual, short[] reference, int lag) {
		int actualStart = Math.max(0, -lag);
		int referenceStart = Math.max(0, lag);
		int samples = Math.min(actual.length - actualStart, reference.length - referenceStart);
		double dot = 0.0;
		double actualSquares = 0.0;
		double referenceSquares = 0.0;
		double differenceSquares = 0.0;
		for (int i = 0; i < samples; i++) {
			double a = actual[actualStart + i];
			double r = reference[referenceStart + i];
			dot += a * r;
			actualSquares += a * a;
			referenceSquares += r * r;
			double difference = a - r;
			differenceSquares += difference * difference;
		}
		double correlation = actualSquares == 0.0 || referenceSquares == 0.0
				? 0.0 : dot / Math.sqrt(actualSquares * referenceSquares);
		double gain = actualSquares == 0.0 ? 0.0 : dot / actualSquares;
		double adjustedSquares = 0.0;
		for (int i = 0; i < samples; i++) {
			double difference = actual[actualStart + i] * gain - reference[referenceStart + i];
			adjustedSquares += difference * difference;
		}
		return new Comparison(lag, samples, correlation, gain,
				Math.sqrt(differenceSquares / samples),
				Math.sqrt(adjustedSquares / samples));
	}

	private static short[] readMonoPcm16(Path path) throws Exception {
		try (AudioInputStream source = AudioSystem.getAudioInputStream(path.toFile())) {
			AudioFormat sourceFormat = source.getFormat();
			AudioFormat targetFormat = new AudioFormat(AudioFormat.Encoding.PCM_SIGNED,
					sourceFormat.getSampleRate(), 16, 1, 2, sourceFormat.getSampleRate(), false);
			try (AudioInputStream pcm = AudioSystem.getAudioInputStream(targetFormat, source)) {
				byte[] bytes = readAll(pcm);
				short[] samples = new short[bytes.length / 2];
				for (int i = 0; i < samples.length; i++) {
					samples[i] = (short) ((bytes[i * 2] & 0xff) | (bytes[i * 2 + 1] << 8));
				}
				return samples;
			}
		}
	}

	private static byte[] readAll(AudioInputStream stream) throws IOException {
		ByteArrayOutputStream bytes = new ByteArrayOutputStream();
		byte[] buffer = new byte[16384];
		int read;
		while ((read = stream.read(buffer)) >= 0) {
			bytes.write(buffer, 0, read);
		}
		return bytes.toByteArray();
	}

	private static int peak(short[] samples) {
		int peak = 0;
		for (short sample : samples) {
			peak = Math.max(peak, Math.abs((int) sample));
		}
		return peak;
	}

	private static double rms(short[] samples) {
		double squares = 0.0;
		for (short sample : samples) {
			squares += (double) sample * sample;
		}
		return Math.sqrt(squares / samples.length);
	}

	static final class Comparison {
		final int lag;
		final int samples;
		final double correlation;
		final double gain;
		final double rawDifferenceRms;
		final double gainAdjustedDifferenceRms;

		Comparison(int lag, int samples, double correlation, double gain,
				double rawDifferenceRms, double gainAdjustedDifferenceRms) {
			this.lag = lag;
			this.samples = samples;
			this.correlation = correlation;
			this.gain = gain;
			this.rawDifferenceRms = rawDifferenceRms;
			this.gainAdjustedDifferenceRms = gainAdjustedDifferenceRms;
		}
	}
}
