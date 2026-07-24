import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public final class PcCoverageTest {
    private PcCoverageTest() {
    }

    public static void main(String[] args) throws Exception {
        Path output = Files.createTempFile("jphoenix-pc-coverage-", ".csv");
        Files.delete(output);
        String old = System.getProperty("phoenix.pccoverage");
        System.setProperty("phoenix.pccoverage", output.toString());
        try {
            PcCoverage coverage = PcCoverage.fromProperty("phoenix.pccoverage");
            coverage.record(0x0000);
            coverage.record(0x1234);
            coverage.record(0x1234);
            coverage.close();

            List<String> lines = Files.readAllLines(output);
            assertContains(lines, "pc,count,frequency");
            assertContains(lines, "0x0000,1,0.333333333333");
            assertContains(lines, "0x1234,2,0.666666666667");
        } finally {
            restoreProperty("phoenix.pccoverage", old);
            Files.deleteIfExists(output);
        }
        System.out.println("ok - PC coverage CSV");
    }

    private static void restoreProperty(String key, String value) {
        if (value == null) {
            System.clearProperty(key);
        } else {
            System.setProperty(key, value);
        }
    }

    private static void assertContains(List<String> lines, String expected) {
        if (!lines.contains(expected)) {
            throw new AssertionError("missing line: " + expected + " in " + lines);
        }
    }
}
