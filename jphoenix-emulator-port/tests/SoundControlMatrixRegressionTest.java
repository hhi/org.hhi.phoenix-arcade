import java.util.zip.CRC32;

public class SoundControlMatrixRegressionTest {
	private static final int FRAMES_PER_CASE = 60;
	private static final long EXPECTED_EFFECT2_CRC = 3640533991L;
	private static final long EXPECTED_EFFECT1_CRC = 202944505L;
	private static final long EXPECTED_NOISE_CRC = 3395184943L;
	private static final long EXPECTED_TMS_CRC = 4270631993L;

	public static void main(String[] args) {
		assertCrc("effect2 data/frequency matrix", effect2Crc(), EXPECTED_EFFECT2_CRC);
		assertCrc("effect1 data/frequency/filter matrix", effect1Crc(), EXPECTED_EFFECT1_CRC);
		assertCrc("noise enable matrix", noiseCrc(), EXPECTED_NOISE_CRC);
		assertCrc("MM6221AA tune matrix", tmsCrc(), EXPECTED_TMS_CRC);
	}

	private static long effect2Crc() {
		CRC32 crc = new CRC32();
		for (int frequency = 0; frequency < 4; frequency++) {
			for (int data = 0; data < 16; data++) {
				renderCase(crc, (byte) ((frequency << 4) | data), (byte) 0x0f);
			}
		}
		return crc.getValue();
	}

	private static long effect1Crc() {
		CRC32 crc = new CRC32();
		for (int filter = 0; filter < 2; filter++) {
			for (int frequency = 0; frequency < 2; frequency++) {
				for (int data = 0; data < 16; data++) {
					int controlB = data | (frequency << 4) | (filter << 5);
					renderCase(crc, (byte) 0x0f, (byte) controlB);
				}
			}
		}
		return crc.getValue();
	}

	private static long noiseCrc() {
		CRC32 crc = new CRC32();
		for (int noise = 0; noise < 4; noise++) {
			renderCase(crc, (byte) (0x0f | (noise << 6)), (byte) 0x0f);
		}
		return crc.getValue();
	}

	private static long tmsCrc() {
		CRC32 crc = new CRC32();
		for (int tune = 0; tune < 4; tune++) {
			renderCase(crc, (byte) 0x0f, (byte) (0x0f | (tune << 6)));
		}
		return crc.getValue();
	}

	private static void renderCase(CRC32 crc, byte controlA, byte controlB) {
		Sound sound = new Sound(PcmSink.discarding());
		sound.updateControlA((byte) 0x0f, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		sound.updateControlB((byte) 0x0f, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		SoundRenderUtil.renderFrames(sound, 6);

		sound.updateControlA(controlA, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		sound.updateControlB(controlB, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		byte[] pcm = SoundRenderUtil.renderFrames(sound, FRAMES_PER_CASE);
		crc.update(controlA & 0xff);
		crc.update(controlB & 0xff);
		crc.update(pcm, 0, pcm.length);
	}

	private static void assertCrc(String name, long actual, long expected) {
		if (actual != expected) {
			throw new AssertionError(name + " CRC expected " + expected + " but got " + actual);
		}
	}
}
