import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

public class SoundFloatCompare {
	public static void main(String[] args) throws Exception {
		if (args.length < 2 || args.length > 5) {
			throw new IllegalArgumentException(
					"Usage: java SoundFloatCompare <java.f32> <reference.f32> "
					+ "[max_lag_samples [start_sample [sample_count]]]");
		}
		int maxLag = args.length == 3 ? Integer.parseInt(args[2]) : 32;
		if (args.length > 3) {
			maxLag = Integer.parseInt(args[2]);
		}
		float[] actual = readFloat32(Path.of(args[0]));
		float[] reference = readFloat32(Path.of(args[1]));
		if (args.length >= 4) {
			int start = Integer.parseInt(args[3]);
			int available = Math.min(actual.length, reference.length) - start;
			int count = args.length == 5 ? Integer.parseInt(args[4]) : available;
			if (start < 0 || count <= 0 || count > available) {
				throw new IllegalArgumentException("Invalid comparison range start="
						+ start + " count=" + count + " available=" + available);
			}
			actual = Arrays.copyOfRange(actual, start, start + count);
			reference = Arrays.copyOfRange(reference, start, start + count);
		}
		Comparison comparison = compare(actual, reference, maxLag);
		System.out.println("actual_samples=" + actual.length);
		System.out.println("reference_samples=" + reference.length);
		System.out.printf(java.util.Locale.ROOT, "actual_peak=%.9f%n", peak(actual));
		System.out.printf(java.util.Locale.ROOT, "reference_peak=%.9f%n", peak(reference));
		System.out.printf(java.util.Locale.ROOT, "actual_rms=%.9f%n", rms(actual));
		System.out.printf(java.util.Locale.ROOT, "reference_rms=%.9f%n", rms(reference));
		System.out.println("best_lag_samples=" + comparison.lag);
		System.out.printf(java.util.Locale.ROOT, "correlation=%.9f%n", comparison.correlation);
		System.out.printf(java.util.Locale.ROOT, "reference_gain_from_actual=%.9f%n", comparison.gain);
		System.out.printf(java.util.Locale.ROOT, "raw_difference_rms=%.9f%n", comparison.rawDifferenceRms);
		System.out.printf(java.util.Locale.ROOT, "gain_adjusted_difference_rms=%.9f%n",
				comparison.gainAdjustedDifferenceRms);
	}

	static Comparison compare(float[] actual, float[] reference, int maxLag) {
		Comparison best = null;
		for (int lag = -maxLag; lag <= maxLag; lag++) {
			Comparison candidate = compareAtLag(actual, reference, lag);
			if (best == null || candidate.correlation > best.correlation) {
				best = candidate;
			}
		}
		return best;
	}

	private static Comparison compareAtLag(float[] actual, float[] reference, int lag) {
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
		return new Comparison(lag, correlation, gain,
				Math.sqrt(differenceSquares / samples),
				Math.sqrt(adjustedSquares / samples));
	}

	private static float[] readFloat32(Path path) throws Exception {
		byte[] bytes = Files.readAllBytes(path);
		if ((bytes.length & 3) != 0) {
			throw new IllegalArgumentException(path + " size is not a multiple of four");
		}
		float[] samples = new float[bytes.length / 4];
		ByteBuffer buffer = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);
		for (int i = 0; i < samples.length; i++) {
			samples[i] = buffer.getFloat();
		}
		return samples;
	}

	private static double peak(float[] samples) {
		double peak = 0.0;
		for (float sample : samples) {
			peak = Math.max(peak, Math.abs(sample));
		}
		return peak;
	}

	private static double rms(float[] samples) {
		double squares = 0.0;
		for (float sample : samples) {
			squares += (double) sample * sample;
		}
		return Math.sqrt(squares / samples.length);
	}

	static final class Comparison {
		final int lag;
		final double correlation;
		final double gain;
		final double rawDifferenceRms;
		final double gainAdjustedDifferenceRms;

		Comparison(int lag, double correlation, double gain,
				double rawDifferenceRms, double gainAdjustedDifferenceRms) {
			this.lag = lag;
			this.correlation = correlation;
			this.gain = gain;
			this.rawDifferenceRms = rawDifferenceRms;
			this.gainAdjustedDifferenceRms = gainAdjustedDifferenceRms;
		}
	}
}
