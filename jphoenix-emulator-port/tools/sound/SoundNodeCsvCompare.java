import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class SoundNodeCsvCompare {
	public static void main(String[] args) throws IOException {
		if (args.length != 2 && args.length != 4) {
			throw new IllegalArgumentException("Usage: java SoundNodeCsvCompare <java-node.csv> <reference-node.csv> [max_abs_tolerance rms_tolerance]");
		}
		List<ColumnDiff> diffs = compare(Path.of(args[0]), Path.of(args[1]));
		System.out.println("column,samples,max_abs_diff,rms_diff");
		for (ColumnDiff diff : diffs) {
			System.out.printf(Locale.ROOT, "%s,%d,%.12f,%.12f%n",
					diff.column, diff.samples, diff.maxAbsDiff, diff.rmsDiff);
		}
		if (args.length == 4) {
			assertWithinTolerance(diffs, Double.parseDouble(args[2]), Double.parseDouble(args[3]));
		}
	}

	static List<ColumnDiff> compare(Path actualPath, Path referencePath) throws IOException {
		CsvData actual = CsvData.read(actualPath);
		CsvData reference = CsvData.read(referencePath);
		if (actual.rows.size() != reference.rows.size()) {
			throw new IllegalArgumentException("CSV row count differs: "
					+ actual.rows.size() + " vs " + reference.rows.size());
		}

		List<ColumnDiff> diffs = new ArrayList<ColumnDiff>();
		List<String> missingReferenceColumns = new ArrayList<String>();
		for (String column : actual.columns) {
			if (!reference.columnIndex.containsKey(column)) {
				if (!isCoordinateColumn(column)) {
					missingReferenceColumns.add(column);
				}
				continue;
			}
			if (isCoordinateColumn(column)) {
				continue;
			}
			int actualIndex = actual.columnIndex.get(column);
			int referenceIndex = reference.columnIndex.get(column);
			double maxAbsDiff = 0.0;
			double sumSquares = 0.0;
			for (int row = 0; row < actual.rows.size(); row++) {
				double delta = actual.rows.get(row)[actualIndex] - reference.rows.get(row)[referenceIndex];
				double abs = Math.abs(delta);
				if (abs > maxAbsDiff) {
					maxAbsDiff = abs;
				}
				sumSquares += delta * delta;
			}
			diffs.add(new ColumnDiff(column, actual.rows.size(), maxAbsDiff,
					Math.sqrt(sumSquares / actual.rows.size())));
		}
		if (!missingReferenceColumns.isEmpty()) {
			throw new IllegalArgumentException("Reference CSV is missing comparable columns: "
					+ String.join(",", missingReferenceColumns));
		}
		if (diffs.isEmpty()) {
			throw new IllegalArgumentException("CSV files have no comparable node columns");
		}
		return diffs;
	}

	private static boolean isCoordinateColumn(String column) {
		return "sample".equals(column) || "timeseconds".equals(column);
	}

	static void assertWithinTolerance(List<ColumnDiff> diffs, double maxAbsTolerance, double rmsTolerance) {
		for (ColumnDiff diff : diffs) {
			if (diff.maxAbsDiff > maxAbsTolerance || diff.rmsDiff > rmsTolerance) {
				throw new AssertionError(diff.column + " exceeds tolerance: max_abs_diff="
						+ diff.maxAbsDiff + " rms_diff=" + diff.rmsDiff
						+ " tolerances=" + maxAbsTolerance + "/" + rmsTolerance);
			}
		}
	}

	static final class ColumnDiff {
		final String column;
		final int samples;
		final double maxAbsDiff;
		final double rmsDiff;

		ColumnDiff(String column, int samples, double maxAbsDiff, double rmsDiff) {
			this.column = column;
			this.samples = samples;
			this.maxAbsDiff = maxAbsDiff;
			this.rmsDiff = rmsDiff;
		}
	}

	private static final class CsvData {
		final List<String> columns;
		final Map<String, Integer> columnIndex;
		final List<double[]> rows;

		CsvData(List<String> columns, Map<String, Integer> columnIndex, List<double[]> rows) {
			this.columns = columns;
			this.columnIndex = columnIndex;
			this.rows = rows;
		}

		static CsvData read(Path path) throws IOException {
			List<String> lines = Files.readAllLines(path);
			if (lines.isEmpty()) {
				throw new IllegalArgumentException("Empty CSV: " + path);
			}
			int headerLine = findHeaderLine(lines, path);
			String[] header = parseLine(lines.get(headerLine));
			for (int i = 0; i < header.length; i++) {
				header[i] = normalizeColumn(header[i]);
			}
			List<String> columns = List.of(header);
			Map<String, Integer> columnIndex = new LinkedHashMap<String, Integer>();
			for (int i = 0; i < header.length; i++) {
				columnIndex.put(header[i], i);
			}

			List<double[]> rows = new ArrayList<double[]>();
			for (int line = headerLine + 1; line < lines.size(); line++) {
				if (lines.get(line).isBlank()) {
					continue;
				}
				String[] values = parseLine(lines.get(line));
				if (values.length != header.length) {
					throw new IllegalArgumentException(path + " line " + (line + 1)
							+ " has " + values.length + " columns, expected " + header.length);
				}
				double[] row = new double[values.length];
				for (int i = 0; i < values.length; i++) {
					row[i] = Double.parseDouble(values[i]);
				}
				rows.add(row);
			}
			return new CsvData(columns, columnIndex, rows);
		}

		private static int findHeaderLine(List<String> lines, Path path) {
			for (int line = 0; line < lines.size(); line++) {
				String[] fields = parseLine(lines.get(line));
				if (fields.length > 1 && "sample".equals(normalizeColumn(fields[0]))) {
					return line;
				}
			}
			throw new IllegalArgumentException("CSV header not found: " + path);
		}

		private static String[] parseLine(String line) {
			String[] fields = line.split(",");
			for (int i = 0; i < fields.length; i++) {
				fields[i] = fields[i].trim().replace("\"", "");
			}
			return fields;
		}

		private static String normalizeColumn(String column) {
			return column.trim().toLowerCase(Locale.ROOT).replace("_", "");
		}
	}
}
