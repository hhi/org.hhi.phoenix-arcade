import java.util.Arrays;

public final class PhoenixVideoRegisterTest {
    private PhoenixVideoRegisterTest() {
    }

    public static void main(String[] args) throws Exception {
        Phoenix phoenix = new Phoenix();

        phoenix.pokeb(0x4000, 0x11);
        assertEquals("initial video page", 0, phoenix.videoRamPage());
        assertEquals("initial palette", 0, phoenix.paletteBank());

        phoenix.pokeb(0x5000, 0x01);
        assertEquals("selected video page", 1, phoenix.videoRamPage());
        assertEquals("palette remains zero", 0, phoenix.paletteBank());
        assertEquals("page 1 starts clear", 0, phoenix.peekb(0x4000));
        phoenix.pokeb(0x4000, 0x22);

        phoenix.pokeb(0x5000, 0x02);
        assertEquals("bit zero selects page 0", 0, phoenix.videoRamPage());
        assertEquals("bit one selects palette 1", 1, phoenix.paletteBank());
        assertEquals("page 0 retained", 0x11, phoenix.peekb(0x4000));

        phoenix.pokeb(0x5000, 0x03);
        assertEquals("page 1 restored", 1, phoenix.videoRamPage());
        assertEquals("palette 1 retained", 1, phoenix.paletteBank());
        assertEquals("page 1 retained", 0x22, phoenix.peekb(0x4000));

        phoenix.pokew(0x4001, 0x4433);
        assertEquals("word low byte stored in selected page", 0x33, phoenix.peekb(0x4001));
        assertEquals("word high byte stored in selected page", 0x44, phoenix.peekb(0x4002));

        testRegisterChangesRenderedFrame();
        testMamePromBirdColors();
        System.out.println("ok - video register");
    }

    private static void testRegisterChangesRenderedFrame() throws Exception {
        Phoenix phoenix = new Phoenix();
        phoenix.loadChr(RomLoaderTest.romBaseUrl());
        phoenix.decodeChars();

        int topLeftForegroundAddress = 0x4000 + 32 * 25;
        phoenix.pokeb(topLeftForegroundAddress, 0x60);
        phoenix.pokeb(0x5000, 0x00);
        phoenix.screenRefresh();
        int[] palette0 = phoenix.frameBuffer().copyPixels();

        phoenix.pokeb(0x5000, 0x02);
        phoenix.screenRefresh();
        int[] palette1 = phoenix.frameBuffer().copyPixels();
        assertDifferent("palette bank changes rendered colors", palette0, palette1);

        phoenix.pokeb(0x5000, 0x01);
        phoenix.screenRefresh();
        int[] emptyPage1 = phoenix.frameBuffer().copyPixels();
        assertDifferent("video page changes rendered contents", palette0, emptyPage1);
    }

    private static void testMamePromBirdColors() throws Exception {
        Phoenix phoenix = new Phoenix();
        phoenix.loadChr(RomLoaderTest.romBaseUrl());
        phoenix.decodeChars();

        int tile = 0;
        for (int character = 0x60; character <= 0xbf; character++, tile++) {
            int x = tile % 26;
            int y = tile / 26;
            phoenix.pokeb(videoAddress(0x4000, x, y), character);
        }
        phoenix.pokeb(0x5000, 0x02);
        phoenix.screenRefresh();
        int[] pixels = phoenix.frameBuffer().copyPixels();
        assertContains("palette-B bird green", pixels, 0xff2edf2d);
        assertContains("palette-B bird yellow", pixels, 0xfff6f644);
        assertContains("palette-B bird light purple", pixels, 0xfff5d0f5);
    }

    private static void assertDifferent(String label, int[] first, int[] second) {
        if (Arrays.equals(first, second)) {
            throw new AssertionError(label);
        }
    }

    private static void assertContains(String label, int[] pixels, int expected) {
        for (int pixel : pixels) {
            if (pixel == expected) {
                return;
            }
        }
        throw new AssertionError(
                label + " missing color 0x" + Integer.toHexString(expected));
    }

    private static int videoAddress(int base, int x, int y) {
        return base + 32 * (25 - x) + y;
    }

    private static void assertEquals(String label, int expected, int actual) {
        if (expected != actual) {
            throw new AssertionError(
                    label + " expected 0x" + Integer.toHexString(expected)
                            + " but got 0x" + Integer.toHexString(actual));
        }
    }
}
