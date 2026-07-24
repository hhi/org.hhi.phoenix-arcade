public class SoundControlMappingTest {
	public static void main(String[] args) {
		for (int value = 0; value < 256; value++) {
			assertEquals("effect2 data", SoundControlMapping.effect2Data(value), value & 0x0f);
			assertEquals("effect2 frequency", SoundControlMapping.effect2Frequency(value), (value & 0x30) >> 4);
			assertEquals("noise C24 discharge", SoundControlMapping.noiseC24Discharge(value), (value & 0x40) != 0);
			assertEquals("noise C25 charge", SoundControlMapping.noiseC25Charge(value), (value & 0x80) != 0);

			assertEquals("effect1 data", SoundControlMapping.effect1Data(value), value & 0x0f);
			assertEquals("effect1 frequency", SoundControlMapping.effect1Frequency(value), (value & 0x10) != 0);
			assertEquals("effect1 filter", SoundControlMapping.effect1Filter(value), (value & 0x20) != 0);
			assertEquals("MM6221AA tune", SoundControlMapping.mm6221aaTune(value), (value >> 6) & 0x03);
		}

		assertEquals("effect2 level select follows original control A bit 5",
				SoundControlMapping.effect2Frequency(0x20) & 0x02, 0x02);
		assertEquals("effect1 filter follows original control B bit 5",
				SoundControlMapping.effect1Filter(0x20), true);
		assertEquals("MM6221AA tune follows original control B bits 6-7",
				SoundControlMapping.mm6221aaTune(0xc0), 0x03);
	}

	private static void assertEquals(String name, int actual, int expected) {
		if (actual != expected) {
			throw new AssertionError(name + " expected " + expected + " but got " + actual);
		}
	}

	private static void assertEquals(String name, boolean actual, boolean expected) {
		if (actual != expected) {
			throw new AssertionError(name + " expected " + expected + " but got " + actual);
		}
	}
}
