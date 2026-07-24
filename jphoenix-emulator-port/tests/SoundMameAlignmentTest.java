import java.lang.reflect.Field;

public class SoundMameAlignmentTest {
	private static final double EPSILON = 0.0000001;

	public static void main(String[] args) throws Exception {
		Sound sound = new Sound(PcmSink.discarding());
		assertIntField(sound, "sampleRate", 48000);
		assertIntField(sound, "discreteSampleRate", 120000);

		assertDoubleStatic(Sound.class, "MAME_DISCRETE_OUTPUT_GAIN", 40000.0);
		assertDoubleStatic(Sound.class, "MAME_STREAM_FULL_SCALE", 32768.0);
		assertDoubleStatic(Sound.class, "MAME_TTL_LOGIC_1", 3.4);
		assertDoubleStatic(Sound.class, "MAME_DISCRETE_ROUTE", 0.6);
		assertDoubleStatic(Sound.class, "MAME_CUSTOM_ROUTE", 0.4);
		assertDoubleStatic(Sound.class, "MAME_TMS_ROUTE", 0.5);

		assertIntField(sound, "R22", 470);
		assertIntField(sound, "R23", 100000);
		assertIntField(sound, "R24", 33000);
		assertIntField(sound, "R40", 47000);
		assertIntField(sound, "R41", 100000);
		assertIntField(sound, "R43", 510000);
		assertIntField(sound, "R44", 510000);
		assertIntField(sound, "R45", 5100);
		assertIntField(sound, "R46", 5100);
		assertIntField(sound, "R49", 1000);
		assertIntField(sound, "R50", 1000);
		assertIntField(sound, "R51", 330);
		assertIntField(sound, "R52", 20000);
		assertIntField(sound, "R53", 330);
		assertIntField(sound, "R54", 47000);

		assertDoubleField(sound, "C18a", 0.01e-6);
		assertDoubleField(sound, "C20", 1.0e-6);
		assertDoubleField(sound, "C22", 100.0e-6);
		assertDoubleField(sound, "C24", 6.8e-6);
		assertDoubleField(sound, "C25", 6.8e-6);
		assertDoubleField(sound, "C7", 6.8e-6);
		assert555ResetState(sound);

		TMS36XX tms = new TMS36XX();
		assertIntField(tms, "basefreq", 372);
		assertIntField(tms, "samplerate", 372 * 64);
		assertIntField(tms, "speed", (int) (TMS36XX.VMAX / 0.21));
		assertIntField(tms, "voices", 4);

		int[] decay = (int[]) readField(tms, "decay");
		assertInt("decay[0]", decay[0], (int) (TMS36XX.VMAX / 0.50));
		assertInt("decay[3]", decay[3], (int) (TMS36XX.VMAX / 1.05));
		assertInt("decay[6]", decay[6], (int) (TMS36XX.VMAX / 0.50));
		assertInt("decay[9]", decay[9], (int) (TMS36XX.VMAX / 1.05));
	}

	private static void assert555ResetState(Sound sound) throws Exception {
		Object node33 = readField(sound, "effect2Node33");
		Object node34 = readField(sound, "effect2Node34");
		Object node39 = readField(sound, "effect2Node39");
		Object node21 = readField(sound, "effect1Node21");
		double sampleTime = 1.0 / 120000.0;
		double expected33 = 5.0 * (1.0 - Math.exp(-sampleTime / ((47000.0 + 100000.0) * 0.01e-6)));
		double expected34 = 5.0 * (1.0 - Math.exp(-sampleTime / ((510000.0 + 510000.0) * 1.0e-6)));
		assertClose("NODE_33 reset capacitor", readDouble(node33, "capVoltage"), expected33, 1.0e-15);
		assertClose("NODE_34 reset capacitor", readDouble(node34, "capVoltage"), expected34, 1.0e-15);
		assertClose("NODE_39 reset capacitor", readDouble(node39, "capVoltage"), 0.0, 0.0);
		assertClose("NODE_21 reset capacitor", readDouble(node21, "capVoltage"), 0.0, 0.0);
	}

	private static void assertIntField(Object target, String name, int expected) throws Exception {
		assertInt(name, ((Integer) readField(target, name)).intValue(), expected);
	}

	private static void assertDoubleField(Object target, String name, double expected) throws Exception {
		double actual = ((Double) readField(target, name)).doubleValue();
		if (Math.abs(actual - expected) > EPSILON) {
			throw new AssertionError(name + " expected " + expected + " but got " + actual);
		}
	}

	private static void assertDoubleStatic(Class<?> type, String name, double expected) throws Exception {
		Field field = type.getDeclaredField(name);
		field.setAccessible(true);
		double actual = field.getDouble(null);
		if (Math.abs(actual - expected) > EPSILON) {
			throw new AssertionError(name + " expected " + expected + " but got " + actual);
		}
	}

	private static Object readField(Object target, String name) throws Exception {
		Field field = target.getClass().getDeclaredField(name);
		field.setAccessible(true);
		return field.get(target);
	}

	private static double readDouble(Object target, String name) throws Exception {
		return ((Double) readField(target, name)).doubleValue();
	}

	private static void assertClose(String name, double actual, double expected, double tolerance) {
		if (Math.abs(actual - expected) > tolerance) {
			throw new AssertionError(name + " expected " + expected + " but got " + actual);
		}
	}

	private static void assertInt(String name, int actual, int expected) {
		if (actual != expected) {
			throw new AssertionError(name + " expected " + expected + " but got " + actual);
		}
	}
}
