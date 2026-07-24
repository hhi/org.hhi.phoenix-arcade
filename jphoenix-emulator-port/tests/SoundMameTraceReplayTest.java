import java.nio.file.Files;
import java.nio.file.Path;

public class SoundMameTraceReplayTest {
	public static void main(String[] args) throws Exception {
		Path trace = Files.createTempFile("phoenix-mame-sound-events-", ".csv");
		Files.writeString(trace,
				"time_seconds,control,value\n"
				+ "0.000000000000,A,0x28\n"
				+ "0.000000000000,B,0x18\n"
				+ "0.100000000000,A,0x0f\n"
				+ "0.100000000000,B,0x0f\n");

		byte[] mixed = SoundMameTraceReplay.replay(trace, 0.2);
		if (mixed.length != 48000 / 5 * 2) {
			throw new AssertionError("Unexpected mixed replay byte count " + mixed.length);
		}
		if (SoundRenderUtil.stats(mixed).peak == 0) {
			throw new AssertionError("MAME trace replay produced silence");
		}

		Path rawDir = Files.createTempDirectory("phoenix-mame-raw-replay-");
		SoundMameRawTraceReplay.writeReplay(trace, rawDir.toFile(), 0.2, false);
		assertSize(rawDir.resolve("discrete.f32"), 24000L * 4);
		assertSize(rawDir.resolve("custom.f32"), 9600L * 4);
		assertSize(rawDir.resolve("tms.f32"), 4762L * 4);
		if (!Files.exists(rawDir.resolve("manifest.csv"))) {
			throw new AssertionError("Raw replay did not write manifest.csv");
		}
		Path nodeReplay = Files.createTempFile("phoenix-mame-node-replay-", ".csv");
		SoundMameNodeTraceReplay.writeReplay(trace, nodeReplay.toFile(), 0.001);
		java.util.List<String> nodeLines = Files.readAllLines(nodeReplay);
		if (!"sample,node33,node34,node35,node36,node37,node38,node39,node40"
				.equals(nodeLines.get(0))) {
			throw new AssertionError("Unexpected node replay header");
		}
		if (nodeLines.size() != 123) {
			throw new AssertionError(
					"Node replay expected 123 lines but got " + nodeLines.size());
		}
		assertRawWriteBoundary();
	}

	private static void assertRawWriteBoundary() {
		SoundMameTraceReplay.Event event =
				new SoundMameTraceReplay.Event(1.0 / 120000.0, 'A', 0x28);
		if (SoundMameRawTraceReplay.eventAppliesBeforeSample(event, 1, 120000)) {
			throw new AssertionError("MAME write changed the sample rendered up to its timestamp");
		}
		if (!SoundMameRawTraceReplay.eventAppliesBeforeSample(event, 2, 120000)) {
			throw new AssertionError("MAME write was not active on the following sample");
		}
	}

	private static void assertSize(Path path, long expected) throws Exception {
		long actual = Files.size(path);
		if (actual != expected) {
			throw new AssertionError(path.getFileName() + " expected " + expected
					+ " bytes but got " + actual);
		}
	}
}
