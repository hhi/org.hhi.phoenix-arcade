import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Random;
import java.util.concurrent.atomic.AtomicInteger;

public class PhoenixVideoRendererTest {
    private static final int BLACK = 0xff000000;
    private static final int RED = 0xffff0000;
    private static final int GREEN = 0xff00ff00;
    private static final int BLUE = 0xff0000ff;

    public static void main(String[] args) throws IOException {
        testCoreHasNoAwtDependency();
        testFrameBufferPublication();
        testLayerCompositionAndScroll();
        testPaletteBankSelection();
        testPixelParityWithOriginalRenderer();
        System.out.println("ok - video renderer");
    }

    private static void testCoreHasNoAwtDependency() throws IOException {
        assertNoAwtImport("Phoenix.java");
        assertNoAwtImport("PhoenixFrameBuffer.java");
        assertNoAwtImport("PhoenixVideoRenderer.java");
    }

    private static void assertNoAwtImport(String fileName) throws IOException {
        String source = Files.readString(Path.of(fileName));
        if (source.contains("import java.awt")) {
            throw new AssertionError(fileName + " must remain framework-neutral");
        }
    }

    private static void testFrameBufferPublication() {
        PhoenixFrameBuffer frameBuffer = new PhoenixFrameBuffer();
        int[] source = new int[PhoenixFrameBuffer.WIDTH * PhoenixFrameBuffer.HEIGHT];
        Arrays.fill(source, BLACK);
        source[0] = RED;
        AtomicInteger notifications = new AtomicInteger();
        frameBuffer.addFrameListener(notifications::incrementAndGet);

        frameBuffer.publish(source);
        source[0] = BLUE;

        int[] snapshot = frameBuffer.copyPixels();
        assertEquals("published pixel", RED, snapshot[0]);
        assertEquals("frame number", 1L, frameBuffer.frameNumber());
        assertEquals("listener notification", 1, notifications.get());
    }

    private static void testLayerCompositionAndScroll() {
        int[] memory = new int[0x10000];
        int[] characters = new int[2 * 512 * 64];
        int[] destination =
                new int[PhoenixVideoRenderer.WIDTH * PhoenixVideoRenderer.HEIGHT];

        fillCharacter(characters, 1, RED);
        fillCharacter(characters, 2, BLUE);
        setBackgroundRow(memory, 0, 1);
        for (int row = 1; row < 32; row++) {
            setBackgroundRow(memory, row, 2);
        }

        int foregroundCharacter = 3;
        memory[videoAddress(0x4000, 0, 0)] = foregroundCharacter;
        characters[256 * 64 + foregroundCharacter * 64] = GREEN;

        PhoenixVideoRenderer renderer = new PhoenixVideoRenderer();
        renderer.render(memory, characters, 0, 0, destination);
        assertEquals("foreground overlays background", GREEN, destination[0]);
        assertEquals("top background row", RED, destination[1]);
        assertEquals(
                "second background row",
                BLUE,
                destination[8 * PhoenixVideoRenderer.WIDTH + 1]);

        renderer.render(memory, characters, 0, 8, destination);
        assertEquals("scrolled background", BLUE, destination[1]);
        assertEquals(
                "wrapped background",
                RED,
                destination[248 * PhoenixVideoRenderer.WIDTH + 1]);
        assertEquals("foreground does not scroll", GREEN, destination[0]);
    }

    private static void testPaletteBankSelection() {
        int[] memory = new int[0x10000];
        int[] characters = new int[2 * 512 * 64];
        int[] destination =
                new int[PhoenixVideoRenderer.WIDTH * PhoenixVideoRenderer.HEIGHT];
        int character = 1;
        setBackgroundRow(memory, 0, character);
        fillCharacter(characters, character, RED);
        fillCharacter(characters, 512 + character, BLUE);

        PhoenixVideoRenderer renderer = new PhoenixVideoRenderer();
        renderer.render(memory, characters, 0, 0, destination);
        assertEquals("palette 0", RED, destination[0]);
        renderer.render(memory, characters, 1, 0, destination);
        assertEquals("palette 1", BLUE, destination[0]);
    }

    private static void testPixelParityWithOriginalRenderer() {
        Random random = new Random(0x1981);
        int[] memory = new int[0x10000];
        int[] characters = new int[2 * 512 * 64];
        int[] palette = {0, BLACK, RED, GREEN, BLUE};
        for (int i = 0; i < 512 * 64; i++) {
            characters[i] = palette[random.nextInt(palette.length)];
        }
        for (int address = 0x4000; address < 0x4c00; address++) {
            memory[address] = random.nextInt(256);
        }

        PhoenixVideoRenderer renderer = new PhoenixVideoRenderer();
        int[] actual = new int[PhoenixVideoRenderer.WIDTH * PhoenixVideoRenderer.HEIGHT];
        int[] expected = new int[actual.length];
        int[] scrollValues = {0, 1, 7, 8, 127, 255};
        for (int scroll : scrollValues) {
            renderer.render(memory, characters, 0, scroll, actual);
            renderLikeOriginMain(memory, characters, scroll, expected);
            if (!Arrays.equals(expected, actual)) {
                for (int i = 0; i < expected.length; i++) {
                    if (expected[i] != actual[i]) {
                        throw new AssertionError(
                                "origin/main parity at scroll " + scroll + ", pixel " + i
                                        + ": expected 0x" + Integer.toHexString(expected[i])
                                        + " but got 0x" + Integer.toHexString(actual[i]));
                    }
                }
            }
        }
    }

    /**
     * Reference implementation copied structurally from Phoenix.screenRefresh
     * on origin/main. Keep this independent of PhoenixVideoRenderer.
     */
    private static void renderLikeOriginMain(
            int[] memory, int[] characters, int scroll, int[] destination) {
        int[] backgroundPixels =
                new int[PhoenixVideoRenderer.WIDTH * PhoenixVideoRenderer.HEIGHT];
        int[] foregroundPixels = new int[backgroundPixels.length];
        renderLegacyLayer(memory, 0x4800, characters, 0, backgroundPixels);
        renderLegacyLayer(memory, 0x4000, characters, 256 * 64, foregroundPixels);

        BufferedImage background = new BufferedImage(
                PhoenixVideoRenderer.WIDTH,
                PhoenixVideoRenderer.HEIGHT,
                BufferedImage.TYPE_INT_ARGB);
        BufferedImage foreground = new BufferedImage(
                PhoenixVideoRenderer.WIDTH,
                PhoenixVideoRenderer.HEIGHT,
                BufferedImage.TYPE_INT_ARGB);
        BufferedImage composed = new BufferedImage(
                PhoenixVideoRenderer.WIDTH,
                PhoenixVideoRenderer.HEIGHT,
                BufferedImage.TYPE_INT_ARGB);
        background.setRGB(
                0, 0, PhoenixVideoRenderer.WIDTH, PhoenixVideoRenderer.HEIGHT,
                backgroundPixels, 0, PhoenixVideoRenderer.WIDTH);
        foreground.setRGB(
                0, 0, PhoenixVideoRenderer.WIDTH, PhoenixVideoRenderer.HEIGHT,
                foregroundPixels, 0, PhoenixVideoRenderer.WIDTH);

        Graphics graphics = composed.getGraphics();
        graphics.setColor(java.awt.Color.BLACK);
        graphics.fillRect(0, 0, PhoenixVideoRenderer.WIDTH, PhoenixVideoRenderer.HEIGHT);
        graphics.drawImage(background, 0, PhoenixVideoRenderer.HEIGHT - scroll, null);
        graphics.drawImage(background, 0, -scroll, null);
        graphics.drawImage(foreground, 0, 0, null);
        graphics.dispose();
        composed.getRGB(
                0, 0, PhoenixVideoRenderer.WIDTH, PhoenixVideoRenderer.HEIGHT,
                destination, 0, PhoenixVideoRenderer.WIDTH);
    }

    private static void renderLegacyLayer(
            int[] memory,
            int videoRamStart,
            int[] characters,
            int characterOffset,
            int[] destination) {
        for (int y = 0; y < 32; y++) {
            int videoAddress = videoRamStart + 32 * 25 + y;
            for (int x = 0; x < 26; x++) {
                int character = memory[videoAddress] & 0xff;
                for (int pixelY = 0; pixelY < 8; pixelY++) {
                    for (int pixelX = 0; pixelX < 8; pixelX++) {
                        destination[y * 8 * 26 * 8 + x * 8 + pixelX
                                + pixelY * PhoenixVideoRenderer.WIDTH] =
                                characters[characterOffset + character * 64
                                        + pixelX + pixelY * 8];
                    }
                }
                videoAddress -= 32;
            }
        }
    }

    private static void fillCharacter(int[] characters, int character, int color) {
        Arrays.fill(characters, character * 64, character * 64 + 64, color);
    }

    private static void setBackgroundRow(int[] memory, int row, int character) {
        for (int column = 0; column < 26; column++) {
            memory[videoAddress(0x4800, column, row)] = character;
        }
    }

    private static int videoAddress(int start, int column, int row) {
        return start + 32 * (25 - column) + row;
    }

    private static void assertEquals(String label, long expected, long actual) {
        if (expected != actual) {
            throw new AssertionError(
                    label + " expected 0x" + Long.toHexString(expected)
                            + " but got 0x" + Long.toHexString(actual));
        }
    }
}
