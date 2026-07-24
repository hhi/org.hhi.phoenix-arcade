import java.lang.reflect.Field;

public class SoundNoisePolynomialTest {
	public static void main(String[] args) throws Exception {
		Sound sound = new Sound(PcmSink.discarding());
		Field field = Sound.class.getDeclaredField("poly18");
		field.setAccessible(true);
		int[] actual = (int[]) field.get(sound);
		int[] expected = generateMamePoly18();
		if (actual.length != expected.length) {
			throw new AssertionError("poly18 length expected " + expected.length
					+ " but got " + actual.length);
		}
		for (int i = 0; i < expected.length; i++) {
			if (actual[i] != expected[i]) {
				throw new AssertionError("poly18 word " + i + " expected 0x"
						+ Integer.toHexString(expected[i]) + " but got 0x"
						+ Integer.toHexString(actual[i]));
			}
		}
	}

	private static int[] generateMamePoly18() {
		int[] poly = new int[1 << (18 - 5)];
		int shiftRegister = 0;
		for (int i = 0; i < poly.length; i++) {
			int bits = 0;
			for (int bit = 0; bit < 32; bit++) {
				bits = (bits >>> 1) | (shiftRegister << 31);
				if (((shiftRegister >>> 16) & 1) == ((shiftRegister >>> 17) & 1)) {
					shiftRegister = (shiftRegister << 1) | 1;
				} else {
					shiftRegister <<= 1;
				}
			}
			poly[i] = bits;
		}
		return poly;
	}
}
