import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.zip.CRC32;

public class SoundNodeDumpRegressionTest {
	private static final String EXPECTED_HEADER = "sample,time_seconds,node20,node21,node22,node23,node24,node25,effect1,"
			+ "node30,node31,node32,node33,node34,node35,node36,node37,node38,node39,node40,effect2,node90";
	private static final int SAMPLES = 1200;
	private static final DumpCase[] CASES = {
			new DumpCase("effect2 bird/hit", "0x28", "0x0f", 3283733182L),
			new DumpCase("effect1 shield/explosion", "0x0f", "0x18", 1286413018L),
			new DumpCase("effect1 filtered", "0x0f", "0x38", 4026353117L),
			new DumpCase("mixed effect1/effect2", "0x28", "0x18", 2359521915L)
	};

	public static void main(String[] args) throws Exception {
		for (DumpCase dumpCase : CASES) {
			assertDump(dumpCase);
		}
	}

	private static void assertDump(DumpCase dumpCase) throws Exception {
		Path out = Files.createTempFile("phoenix-node-dump-", ".csv");
		SoundNodeDump.writeDump(out.toFile(), Integer.decode(dumpCase.controlA) & 0xff,
				Integer.decode(dumpCase.controlB) & 0xff, SAMPLES);

		List<String> lines = Files.readAllLines(out);
		if (lines.size() != SAMPLES + 1) {
			throw new AssertionError(dumpCase.name + " expected " + (SAMPLES + 1)
					+ " CSV lines but got " + lines.size());
		}
		if (!EXPECTED_HEADER.equals(lines.get(0))) {
			throw new AssertionError(dumpCase.name + " unexpected node dump header: " + lines.get(0));
		}

		CRC32 crc = new CRC32();
		byte[] bytes = Files.readAllBytes(out);
		crc.update(bytes, 0, bytes.length);
		long actual = crc.getValue();
		if (actual != dumpCase.expectedCrc) {
			throw new AssertionError(dumpCase.name + " node dump CRC expected "
					+ dumpCase.expectedCrc + " but got " + actual);
		}
	}

	private static final class DumpCase {
		final String name;
		final String controlA;
		final String controlB;
		final long expectedCrc;

		DumpCase(String name, String controlA, String controlB, long expectedCrc) {
			this.name = name;
			this.controlA = controlA;
			this.controlB = controlB;
			this.expectedCrc = expectedCrc;
		}
	}
}
