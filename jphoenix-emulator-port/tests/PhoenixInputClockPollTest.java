import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public final class PhoenixInputClockPollTest {
    private PhoenixInputClockPollTest() {
    }

    public static void main(String[] args) throws Exception {
        if (!"poll".equals(System.getProperty("phoenix.inputclock"))) {
            throw new AssertionError("run with -Dphoenix.inputclock=poll");
        }
        Path script = Files.createTempFile("jphoenix-input-poll-", ".txt");
        Files.write(script, List.of("1 coin press"));
        String oldScript = System.getProperty("phoenix.inputscript");
        System.setProperty("phoenix.inputscript", script.toString());
        try {
            Phoenix phoenix = new Phoenix();
            phoenix.interrupt();
            assertEquals("coin not applied on raw interrupt", 0x01, phoenix.gameControlStateForTest() & 0x01);

            phoenix.peekb(0x7800);
            phoenix.peekb(0x7800);
            phoenix.PC(0x0161);
            assertEquals("mid-frame DIP read", 0x00, phoenix.peekb(0x7800));
            assertEquals("coin not applied on mid-frame DIP read", 0x01, phoenix.gameControlStateForTest() & 0x01);

            phoenix.PC(0x0082);
            assertEquals("wait-vblank clear read", 0x00, phoenix.peekb(0x7800));
            assertEquals("coin applied on poll tick", 0x00, phoenix.gameControlStateForTest() & 0x01);
        } finally {
            restoreProperty("phoenix.inputscript", oldScript);
            Files.deleteIfExists(script);
        }
        System.out.println("ok - input poll clock");
    }

    private static void restoreProperty(String key, String value) {
        if (value == null) {
            System.clearProperty(key);
        } else {
            System.setProperty(key, value);
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
