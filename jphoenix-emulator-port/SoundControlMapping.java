final class SoundControlMapping {
	private SoundControlMapping() {
	}

	static int effect2Data(int controlA) {
		return controlA & 0x0f;
	}

	static int effect2Frequency(int controlA) {
		return (controlA & 0x30) >> 4;
	}

	static boolean noiseC24Discharge(int controlA) {
		return (controlA & 0x40) != 0;
	}

	static boolean noiseC25Charge(int controlA) {
		return (controlA & 0x80) != 0;
	}

	static int effect1Data(int controlB) {
		return controlB & 0x0f;
	}

	static boolean effect1Frequency(int controlB) {
		return (controlB & 0x10) != 0;
	}

	static boolean effect1Filter(int controlB) {
		return (controlB & 0x20) != 0;
	}

	static int mm6221aaTune(int controlB) {
		return (controlB >> 6) & 0x03;
	}
}
