public class SoundMetricsRegressionTest {
	private static final double RMS_TOLERANCE = 0.01;

	private static final MetricCase[] CASES = {
			new MetricCase("effect2 bird/hit", (byte) 0x28, (byte) 0x0f, 120, 5736, 2641.621837, 0),
			new MetricCase("effect1 shield/explosion", (byte) 0x0f, (byte) 0x18, 120, 5988, 2786.267601, 0),
			new MetricCase("effect1 filtered", (byte) 0x0f, (byte) 0x38, 120, 3415, 638.382486, 0),
			new MetricCase("noise control", (byte) 0xcf, (byte) 0x0f, 120, 13107, 7633.154206, 0),
			new MetricCase("music tune", (byte) 0x0f, (byte) 0x8f, 240, 6855, 2995.459099, 0)
	};

	public static void main(String[] args) {
		for (MetricCase metricCase : CASES) {
			assertMetrics(metricCase);
		}
	}

	private static void assertMetrics(MetricCase metricCase) {
		Sound sound = new Sound(PcmSink.discarding());
		sound.updateControlA((byte) 0x0f, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		sound.updateControlB((byte) 0x0f, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		SoundRenderUtil.renderFrames(sound, 6);

		sound.updateControlA(metricCase.controlA, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		sound.updateControlB(metricCase.controlB, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		byte[] pcm = SoundRenderUtil.renderFrames(sound, metricCase.frames);
		SoundRenderUtil.PcmStats stats = SoundRenderUtil.stats(pcm);

		if (stats.peak != metricCase.peak) {
			throw new AssertionError(metricCase.name + " peak expected "
					+ metricCase.peak + " but got " + stats.peak);
		}
		if (Math.abs(stats.rms - metricCase.rms) > RMS_TOLERANCE) {
			throw new AssertionError(metricCase.name + " RMS expected "
					+ metricCase.rms + " but got " + stats.rms);
		}
		if (stats.clippedSamples != metricCase.clippedSamples) {
			throw new AssertionError(metricCase.name + " clipped samples expected "
					+ metricCase.clippedSamples + " but got " + stats.clippedSamples);
		}
	}

	private static final class MetricCase {
		final String name;
		final byte controlA;
		final byte controlB;
		final int frames;
		final int peak;
		final double rms;
		final int clippedSamples;

		MetricCase(String name, byte controlA, byte controlB, int frames,
				int peak, double rms, int clippedSamples) {
			this.name = name;
			this.controlA = controlA;
			this.controlB = controlB;
			this.frames = frames;
			this.peak = peak;
			this.rms = rms;
			this.clippedSamples = clippedSamples;
		}
	}
}
