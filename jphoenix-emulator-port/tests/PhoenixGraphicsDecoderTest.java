public final class PhoenixGraphicsDecoderTest {
    private PhoenixGraphicsDecoderTest() {
    }

    public static void main(String[] args) throws Exception {
        testSyntheticPlaneWeights();
        testAllRomPixelsAgainstMameLayout();
        testWrongSizeRejected();
        System.out.println("ok - graphics bitplanes");
    }

    private static void testSyntheticPlaneWeights() {
        byte[] graphics = new byte[PhoenixGraphicsDecoder.GRAPHICS_SIZE];
        int lowPlane = romOffset(0, 0, 0, 0);
        int highPlane = romOffset(0, 0, 1, 0);

        graphics[lowPlane] = 0x01;
        assertEquals("low plane has weight 1", 1, decodedPixel(graphics, 0, 0, 0, 0));

        graphics[lowPlane] = 0;
        graphics[highPlane] = 0x01;
        assertEquals("high plane has weight 2", 2, decodedPixel(graphics, 0, 0, 0, 0));

        graphics[lowPlane] = 0x01;
        assertEquals("combined planes have value 3", 3, decodedPixel(graphics, 0, 0, 0, 0));
        assertEquals("unset neighboring pixel remains zero", 0,
                decodedPixel(graphics, 0, 0, 0, 1));
    }

    private static void testAllRomPixelsAgainstMameLayout() throws Exception {
        byte[] graphics = RomLoader.load(RomLoaderTest.romBaseUrl(), RomLoader.GRAPHICS);
        byte[] actual = PhoenixGraphicsDecoder.decode(graphics);
        int checked = 0;

        for (int charset = 0; charset < 2; charset++) {
            for (int character = 0; character < 256; character++) {
                for (int line = 0; line < 8; line++) {
                    int planeAtOffsetZero =
                            graphics[romOffset(charset, character, 0, line)] & 0xff;
                    int planeAtOffset2048 =
                            graphics[romOffset(charset, character, 1, line)] & 0xff;
                    for (int column = 0; column < 8; column++) {
                        // MAME charlayout uses plane offsets { 256*8*8, 0 }.
                        // Its first listed plane is the most-significant pixel bit.
                        int expected =
                                ((planeAtOffsetZero >> column) & 0x01)
                                        | (((planeAtOffset2048 >> column) & 0x01) << 1);
                        int index = pixelOffset(charset, character, line, column);
                        int found = actual[index] & 0xff;
                        if (expected != found) {
                            throw new AssertionError(
                                    "pixel mismatch at charset " + charset
                                            + ", character " + character
                                            + ", line " + line
                                            + ", column " + column
                                            + ": expected " + expected + ", got " + found);
                        }
                        checked++;
                    }
                }
            }
        }
        assertEquals("checked ROM pixels", 32768, checked);
    }

    private static void testWrongSizeRejected() {
        try {
            PhoenixGraphicsDecoder.decode(
                    new byte[PhoenixGraphicsDecoder.GRAPHICS_SIZE - 1]);
            throw new AssertionError("undersized graphics ROM was accepted");
        } catch (IllegalArgumentException expected) {
            if (!expected.getMessage().contains("8192")) {
                throw new AssertionError("wrong size error lacks expected byte count");
            }
        }
    }

    private static int decodedPixel(
            byte[] graphics, int charset, int character, int line, int column) {
        return PhoenixGraphicsDecoder.decode(graphics)[
                pixelOffset(charset, character, line, column)] & 0xff;
    }

    private static int romOffset(
            int charset, int character, int plane, int line) {
        return charset * 4096 + plane * 2048 + character * 8 + line;
    }

    private static int pixelOffset(
            int charset, int character, int line, int column) {
        return (charset * 256 + character) * 64 + column * 8 + 7 - line;
    }

    private static void assertEquals(String label, int expected, int actual) {
        if (expected != actual) {
            throw new AssertionError(
                    label + ": expected " + expected + ", got " + actual);
        }
    }
}
