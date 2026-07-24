public class SoundWavCompareTest {
	private static final double EPSILON = 0.0000001;

	public static void main(String[] args) {
		short[] actual = { 0, 100, -200, 300, 0, 0 };
		short[] reference = { 0, 0, 50, -100, 150, 0 };
		SoundWavCompare.Comparison comparison = SoundWavCompare.compare(actual, reference, 3);
		if (comparison.lag != 1) {
			throw new AssertionError("Expected lag 1 but got " + comparison.lag);
		}
		assertDouble("correlation", comparison.correlation, 1.0);
		assertDouble("gain", comparison.gain, 0.5);
		assertDouble("gain-adjusted RMS", comparison.gainAdjustedDifferenceRms, 0.0);
	}

	private static void assertDouble(String name, double actual, double expected) {
		if (Math.abs(actual - expected) > EPSILON) {
			throw new AssertionError(name + " expected " + expected + " but got " + actual);
		}
	}
}
