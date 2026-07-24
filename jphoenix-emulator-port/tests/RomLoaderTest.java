import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.Arrays;

public final class RomLoaderTest {
    private RomLoaderTest() {
    }

    static URL romBaseUrl() throws Exception {
        return new File("../roms/assembled").getCanonicalFile().toURI().toURL();
    }

    public static void main(String[] args) throws Exception {
        URL baseUrl = romBaseUrl();
        byte[] program = RomLoader.load(baseUrl, RomLoader.PROGRAM);
        byte[] graphics = RomLoader.load(baseUrl, RomLoader.GRAPHICS);
        byte[] palette = RomLoader.load(baseUrl, RomLoader.PALETTE);
        assertEquals("program ROM size", 0x4000, program.length);
        assertEquals("graphics ROM size", 0x2000, graphics.length);
        assertEquals("palette PROM size", 0x0200, palette.length);

        byte[] corrupt = program.clone();
        corrupt[0] ^= 0x01;
        assertRejected("SHA-256 mismatch", RomLoader.PROGRAM, corrupt);

        byte[] truncated = Arrays.copyOf(program, program.length - 1);
        assertRejected("wrong size", RomLoader.PROGRAM, truncated);

        byte[] oversized = Arrays.copyOf(graphics, graphics.length + 1);
        assertRejected("wrong size", RomLoader.GRAPHICS, oversized);

        byte[] corruptProm = palette.clone();
        corruptProm[0] ^= 0x01;
        assertRejected("SHA-256 mismatch", RomLoader.PALETTE, corruptProm);

        System.out.println("ok - ROM validation");
    }

    private static void assertRejected(
            String expectedMessage, RomLoader.Spec spec, byte[] bytes) throws Exception {
        try {
            RomLoader.validate(spec, bytes);
            throw new AssertionError("expected ROM rejection containing: " + expectedMessage);
        } catch (IOException e) {
            if (!e.getMessage().contains(expectedMessage)) {
                throw new AssertionError(
                        "expected error containing '" + expectedMessage
                                + "', got: " + e.getMessage());
            }
        }
    }

    private static void assertEquals(String label, int expected, int actual) {
        if (expected != actual) {
            throw new AssertionError(label + " expected " + expected + " but got " + actual);
        }
    }
}
