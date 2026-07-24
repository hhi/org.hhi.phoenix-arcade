import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;

final class PcCoverage implements AutoCloseable {
    private final long[] hits = new long[0x10000];
    private final Path path;
    private long totalInstructions;
    private boolean closed;

    private PcCoverage(Path path) {
        this.path = path;
    }

    static PcCoverage fromProperty(String propertyName) {
        String value = System.getProperty(propertyName);
        if (value == null || value.isEmpty()) {
            return null;
        }
        return new PcCoverage(Path.of(value));
    }

    void record(int pc) {
        hits[pc & 0xffff]++;
        totalInstructions++;
    }

    long hitCount(int pc) {
        return hits[pc & 0xffff];
    }

    long totalInstructions() {
        return totalInstructions;
    }

    @Override
    public void close() throws IOException {
        if (closed) {
            return;
        }
        closed = true;
        Path parent = path.getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }
        try (BufferedWriter writer = Files.newBufferedWriter(path)) {
            writer.write("pc,count,frequency\n");
            for (int pc = 0; pc < hits.length; pc++) {
                long count = hits[pc];
                if (count == 0) {
                    continue;
                }
                double frequency = totalInstructions == 0
                        ? 0.0
                        : (double) count / (double) totalInstructions;
                writer.write(String.format(Locale.ROOT, "0x%04x,%d,%.12f%n", pc, count, frequency));
            }
        }
    }
}
