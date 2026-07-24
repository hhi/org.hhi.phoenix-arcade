import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public final class PhoenixInputScriptTest {
    private PhoenixInputScriptTest() {
    }

    public static void main(String[] args) throws Exception {
        testReplayAppliesSortedEvents();
        testRecordingUsesNextFrameAndSkipsRepeats();
        System.out.println("ok - input script replay/recording");
    }

    private static void testReplayAppliesSortedEvents() throws Exception {
        Path script = Files.createTempFile("jphoenix-input-", ".txt");
        Files.write(script, List.of(
                "# comment",
                "2 fire release",
                "1 coin press",
                "1 fire press",
                "1 unknown press"));
        String old = System.getProperty("phoenix.inputscript");
        System.setProperty("phoenix.inputscript", script.toString());
        try {
            Phoenix phoenix = new Phoenix();
            phoenix.interrupt();
            assertEquals("coin pressed on frame 1", 0x00, phoenix.gameControlStateForTest() & 0x01);
            assertEquals("fire pressed on frame 1", 0x00, phoenix.gameControlStateForTest() & 0x10);
            phoenix.interrupt();
            assertEquals("fire released on frame 2", 0x10, phoenix.gameControlStateForTest() & 0x10);
        } finally {
            restoreProperty("phoenix.inputscript", old);
            Files.deleteIfExists(script);
        }
    }

    private static void testRecordingUsesNextFrameAndSkipsRepeats() throws Exception {
        Path recording = Files.createTempFile("jphoenix-recording-", ".txt");
        Files.delete(recording);
        String old = System.getProperty("phoenix.recordinput");
        System.setProperty("phoenix.recordinput", recording.toString());
        try {
            Phoenix phoenix = new Phoenix();
            phoenix.doKey(1, '3');
            phoenix.doKey(1, '3');
            phoenix.interrupt();
            phoenix.doKey(0, '3');
            phoenix.stop();

            List<String> lines = Files.readAllLines(recording);
            assertContains("first press", lines, "1 coin press");
            assertContains("release after one interrupt", lines, "2 coin release");
            int eventLines = 0;
            for (String line : lines) {
                if (!line.startsWith("#")) {
                    eventLines++;
                }
            }
            assertEquals("repeat keydown skipped", 2, eventLines);
        } finally {
            restoreProperty("phoenix.recordinput", old);
            Files.deleteIfExists(recording);
        }
    }

    private static void restoreProperty(String key, String value) {
        if (value == null) {
            System.clearProperty(key);
        } else {
            System.setProperty(key, value);
        }
    }

    private static void assertContains(String label, List<String> lines, String expected) {
        if (!lines.contains(expected)) {
            throw new AssertionError(label + " missing line: " + expected + " in " + lines);
        }
    }

    private static void assertEquals(String label, int expected, int actual) {
        if (expected != actual) {
            throw new AssertionError(
                    label + " expected 0x" + Integer.toHexString(expected)
                            + " but got 0x" + Integer.toHexString(actual));
        }
    }
}
