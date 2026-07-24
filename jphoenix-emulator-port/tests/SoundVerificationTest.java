public class SoundVerificationTest {
	private static final TestCase[] TESTS = {
			new TestCase("source audit", "SoundSourceAuditTest", () -> SoundSourceAuditTest.main(new String[0])),
			new TestCase("MAME alignment", "SoundMameAlignmentTest", () -> SoundMameAlignmentTest.main(new String[0])),
			new TestCase("MAME traceability", "SoundMameTraceabilityTest", () -> SoundMameTraceabilityTest.main(new String[0])),
			new TestCase("MAME LoFi resampler", "SoundMameLofiResamplerTest", () -> SoundMameLofiResamplerTest.main(new String[0])),
			new TestCase("MAME noise polynomial", "SoundNoisePolynomialTest", () -> SoundNoisePolynomialTest.main(new String[0])),
			new TestCase("control mapping", "SoundControlMappingTest", () -> SoundControlMappingTest.main(new String[0])),
			new TestCase("PCM sink", "PcmSinkTest", () -> PcmSinkTest.main(new String[0])),
			new TestCase("render smoke", "SoundRenderSmokeTest", () -> SoundRenderSmokeTest.main(new String[0])),
			new TestCase("node probe", "SoundNodeProbeTest", () -> SoundNodeProbeTest.main(new String[0])),
			new TestCase("node CSV compare", "SoundNodeCsvCompareTest", () -> SoundNodeCsvCompareTest.main(new String[0])),
			new TestCase("WAV compare", "SoundWavCompareTest", () -> SoundWavCompareTest.main(new String[0])),
			new TestCase("float compare", "SoundFloatCompareTest", () -> SoundFloatCompareTest.main(new String[0])),
			new TestCase("MAME trace replay", "SoundMameTraceReplayTest", () -> SoundMameTraceReplayTest.main(new String[0])),
			new TestCase("node dump regression", "SoundNodeDumpRegressionTest", () -> SoundNodeDumpRegressionTest.main(new String[0])),
			new TestCase("artifact manifest", "SoundArtifactManifestTest", () -> SoundArtifactManifestTest.main(new String[0])),
			new TestCase("metrics regression", "SoundMetricsRegressionTest", () -> SoundMetricsRegressionTest.main(new String[0])),
			new TestCase("control matrix regression", "SoundControlMatrixRegressionTest", () -> SoundControlMatrixRegressionTest.main(new String[0])),
			new TestCase("cold-start envelope", "SoundColdStartEnvelopeTest", () -> SoundColdStartEnvelopeTest.main(new String[0])),
			new TestCase("verification coverage", "SoundVerificationCoverageTest", () -> SoundVerificationCoverageTest.main(new String[0]))
	};

	public static void main(String[] args) throws Exception {
		for (TestCase test : TESTS) {
			test.runnable.run();
			System.out.println("ok - " + test.name);
		}
	}

	private interface ThrowingRunnable {
		void run() throws Exception;
	}

	static String[] testClassNames() {
		String[] names = new String[TESTS.length];
		for (int i = 0; i < TESTS.length; i++) {
			names[i] = TESTS[i].className;
		}
		return names;
	}

	private static final class TestCase {
		final String name;
		final String className;
		final ThrowingRunnable runnable;

		TestCase(String name, String className, ThrowingRunnable runnable) {
			this.name = name;
			this.className = className;
			this.runnable = runnable;
		}
	}
}
