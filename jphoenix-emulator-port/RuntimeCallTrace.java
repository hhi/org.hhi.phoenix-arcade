import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.TreeMap;

/** Aggregates executed 8080 CALL edges for an opt-in runtime graph. */
public final class RuntimeCallTrace {
    private final Map<Long, Integer> counts = new TreeMap<>();

    public void record(int caller, int callee) {
        long key = ((long) (caller & 0xffff) << 16) | (callee & 0xffff);
        counts.merge(key, 1, Integer::sum);
    }

    public void write(Path output) throws IOException {
        try (BufferedWriter writer = Files.newBufferedWriter(output)) {
            writer.write("caller,callee,count\n");
            for (Map.Entry<Long, Integer> entry : counts.entrySet()) {
                int caller = (int) (entry.getKey() >>> 16);
                int callee = (int) (entry.getKey() & 0xffffL);
                writer.write(String.format("%04X,%04X,%d%n", caller, callee, entry.getValue()));
            }
        }
    }
}
