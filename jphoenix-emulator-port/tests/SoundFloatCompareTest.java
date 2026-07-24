public class SoundFloatCompareTest {
	private static final double EPSILON = 0.0000001;

	public static void main(String[] args) {
		float[] actual = { 0.0f, 0.25f, -0.5f, 0.75f, 0.0f, 0.0f };
		float[] reference = { 0.0f, 0.0f, 0.5f, -1.0f, 1.5f, 0.0f };
		SoundFloatCompare.Comparison comparison = SoundFloatCompare.compare(actual, reference, 3);
		if (comparison.lag != 1) {
			throw new AssertionError("Expected lag 1 but got " + comparison.lag);
		}
		assertDouble("correlation", comparison.correlation, 1.0);
		assertDouble("gain", comparison.gain, 2.0);
		assertDouble("gain-adjusted RMS", comparison.gainAdjustedDifferenceRms, 0.0);
	}

	private static void assertDouble(String name, double actual, double expected) {
		if (Math.abs(actual - expected) > EPSILON) {
			throw new AssertionError(name + " expected " + expected + " but got " + actual);
		}
	}
}
