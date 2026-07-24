import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class SoundNodeCsvCompareTest {
	public static void main(String[] args) throws Exception {
		Path first = Files.createTempFile("phoenix-node-a-", ".csv");
		Path second = Files.createTempFile("phoenix-node-b-", ".csv");
		Files.writeString(first,
				"sample,time_seconds,node20,node90\n"
						+ "0,0.000000000,1.000000000,2.000000000\n"
						+ "1,0.000008333,3.000000000,4.000000000\n");
		Files.writeString(second,
				"sample,time_seconds,node20,node90\n"
						+ "0,0.000000000,1.000000000,2.500000000\n"
						+ "1,0.000008333,4.000000000,4.500000000\n");

		List<SoundNodeCsvCompare.ColumnDiff> diffs = SoundNodeCsvCompare.compare(first, second);
		if (diffs.size() != 2) {
			throw new AssertionError("Expected two comparable columns, got " + diffs.size());
		}
		assertDiff(diffs.get(0), "node20", 2, 1.0, Math.sqrt(0.5));
		assertDiff(diffs.get(1), "node90", 2, 0.5, 0.5);
		SoundNodeCsvCompare.assertWithinTolerance(diffs, 1.0, Math.sqrt(0.5));
		assertToleranceFailure(diffs);
		assertMameCsvFormat(first);
		assertMissingColumnFailure();
		assertNoComparableColumnFailure();
	}

	private static void assertMameCsvFormat(Path javaCsv) throws Exception {
		Path mame = Files.createTempFile("phoenix-node-mame-", ".csv");
		Files.writeString(mame,
				"\"MAME Discrete System Node Log\"\n"
						+ "\"Log Version\", 1.0\n"
						+ "\"Sample Rate\", 120000\n\n"
						+ "\"Sample\", \"NODE_20\", \"NODE_90\"\n"
						+ "1, 1.000000000, 2.000000000\n"
						+ "2, 3.000000000, 4.000000000\n");
		List<SoundNodeCsvCompare.ColumnDiff> diffs =
				SoundNodeCsvCompare.compare(javaCsv, mame);
		assertDiff(diffs.get(0), "node20", 2, 0.0, 0.0);
		assertDiff(diffs.get(1), "node90", 2, 0.0, 0.0);
	}

	private static void assertToleranceFailure(List<SoundNodeCsvCompare.ColumnDiff> diffs) {
		try {
			SoundNodeCsvCompare.assertWithinTolerance(diffs, 0.25, 0.25);
		} catch (AssertionError expected) {
			return;
		}
		throw new AssertionError("Expected node CSV comparison to fail strict tolerance");
	}

	private static void assertMissingColumnFailure() throws Exception {
		Path first = Files.createTempFile("phoenix-node-missing-a-", ".csv");
		Path second = Files.createTempFile("phoenix-node-missing-b-", ".csv");
		Files.writeString(first, "sample,time_seconds,node20,node90\n0,0.000000000,1.0,2.0\n");
		Files.writeString(second, "sample,time_seconds,node20\n0,0.000000000,1.0\n");
		try {
			SoundNodeCsvCompare.compare(first, second);
		} catch (IllegalArgumentException expected) {
			if (!expected.getMessage().contains("node90")) {
				throw new AssertionError("Missing-column failure did not mention node90: "
						+ expected.getMessage());
			}
			return;
		}
		throw new AssertionError("Expected missing reference column failure");
	}

	private static void assertNoComparableColumnFailure() throws Exception {
		Path first = Files.createTempFile("phoenix-node-empty-a-", ".csv");
		Path second = Files.createTempFile("phoenix-node-empty-b-", ".csv");
		Files.writeString(first, "sample,time_seconds\n0,0.000000000\n");
		Files.writeString(second, "sample,time_seconds\n0,0.000000000\n");
		try {
			SoundNodeCsvCompare.compare(first, second);
		} catch (IllegalArgumentException expected) {
			if (!expected.getMessage().contains("no comparable")) {
				throw new AssertionError("No-comparable-column failure was unclear: "
						+ expected.getMessage());
			}
			return;
		}
		throw new AssertionError("Expected no comparable node column failure");
	}

	private static void assertDiff(SoundNodeCsvCompare.ColumnDiff diff, String column,
			int samples, double maxAbsDiff, double rmsDiff) {
		if (!column.equals(diff.column)) {
			throw new AssertionError("Expected column " + column + " but got " + diff.column);
		}
		if (diff.samples != samples) {
			throw new AssertionError(column + " expected " + samples + " samples but got " + diff.samples);
		}
		if (Math.abs(diff.maxAbsDiff - maxAbsDiff) > 0.000000001) {
			throw new AssertionError(column + " expected max diff " + maxAbsDiff + " but got " + diff.maxAbsDiff);
		}
		if (Math.abs(diff.rmsDiff - rmsDiff) > 0.000000001) {
			throw new AssertionError(column + " expected RMS diff " + rmsDiff + " but got " + diff.rmsDiff);
		}
	}
}
