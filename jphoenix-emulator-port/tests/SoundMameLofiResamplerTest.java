import java.lang.reflect.Field;

public class SoundMameLofiResamplerTest {
	private static final double EPSILON = 0.0000001;

	public static void main(String[] args) throws Exception {
		MameLofiResampler tmsResampler = new MameLofiResampler(372 * 64, 48000);
		assertInt("TMS source divide", tmsResampler.sourceDivide(), 1);
		assertInt("TMS phase step", tmsResampler.step(), 8321499);

		MameLofiResampler discreteResampler = new MameLofiResampler(120000, 48000);
		assertInt("discrete source divide", discreteResampler.sourceDivide(), 3);
		assertInt("discrete phase step", discreteResampler.step(), 13981013);
		assertDiscreteMovingAverage(discreteResampler);

		assertInt("phase one", MameLofiResampler.PHASE_ONE, 0x1000000);
		assertInt("phase mask", MameLofiResampler.PHASE_MASK, 0x00ffffff);
		assertDouble("f0[0]", MameLofiResampler.interpolation(0, 0), 0.0);
		assertDouble("f0[2048]", MameLofiResampler.interpolation(0, 2048), 0.0625);
		assertDouble("f0[4096]", MameLofiResampler.interpolation(0, 4096), 0.0);
		assertDouble("f1[0]", MameLofiResampler.interpolation(1, 0), 0.0);
		assertDouble("f1[2048]", MameLofiResampler.interpolation(1, 2048), 0.5625);
		assertDouble("f1[4096]", MameLofiResampler.interpolation(1, 4096), 1.0);

		TMS36XX tms = new TMS36XX();
		tms.nextSample(48000);
		assertIntegratedResampler("TMS36XX", tms, "resampler", 1, 8321499);
		tms.nextSample(22050);

		Sound sound = new Sound(PcmSink.discarding());
		assertIntegratedResampler("Sound", sound, "discreteResampler", 3, 13981013);
	}

	private static void assertDiscreteMovingAverage(MameLofiResampler resampler) throws Exception {
		SequenceSource source = new SequenceSource();
		resampler.nextSample(source);
		assertInt("source calls before first wrap", source.calls, 0);
		resampler.nextSample(source);
		assertInt("source calls at first wrap", source.calls, 3);

		Field s3Field = MameLofiResampler.class.getDeclaredField("s3");
		s3Field.setAccessible(true);
		assertDouble("first moving-average source sample", s3Field.getFloat(resampler), 2.0);
	}

	private static void assertIntegratedResampler(String name, Object target, String fieldName,
			int expectedSourceDivide, int expectedStep) throws Exception {
		Field field = target.getClass().getDeclaredField(fieldName);
		field.setAccessible(true);
		MameLofiResampler resampler = (MameLofiResampler) field.get(target);
		if (resampler == null) {
			throw new AssertionError(name + " did not initialize " + fieldName);
		}
		assertInt(name + " source divide", resampler.sourceDivide(), expectedSourceDivide);
		assertInt(name + " phase step", resampler.step(), expectedStep);
	}

	private static void assertInt(String name, int actual, int expected) {
		if (actual != expected) {
			throw new AssertionError(name + " expected " + expected + " but got " + actual);
		}
	}

	private static void assertDouble(String name, double actual, double expected) {
		if (Math.abs(actual - expected) > EPSILON) {
			throw new AssertionError(name + " expected " + expected + " but got " + actual);
		}
	}

	private static final class SequenceSource implements MameLofiResampler.Source {
		int calls;

		@Override
		public double nextSample() {
			calls++;
			return calls;
		}
	}
}
