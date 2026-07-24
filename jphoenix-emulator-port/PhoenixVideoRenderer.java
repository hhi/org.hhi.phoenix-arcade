/**
 * Framework-neutral Phoenix tile renderer.
 *
 * The renderer consumes emulated memory and decoded character pixels and
 * produces one fixed-size ARGB frame. It has no dependency on AWT, Swing or a
 * specific game framework.
 */
public final class PhoenixVideoRenderer {
    public static final int WIDTH = 208;
    public static final int HEIGHT = 256;
    private static final int OPAQUE_BLACK = 0xff000000;

    private static final int TILE_SIZE = 8;
    private static final int TILE_ROWS = 32;
    private static final int TILE_COLUMNS = 26;
    private static final int CHARACTER_PIXELS = TILE_SIZE * TILE_SIZE;
    private static final int FOREGROUND_CHARACTER_OFFSET = 256 * CHARACTER_PIXELS;
    private static final int PALETTE_CHARACTER_OFFSET = 512 * CHARACTER_PIXELS;

    private final int[] background = new int[WIDTH * HEIGHT];
    private final int[] foreground = new int[WIDTH * HEIGHT];

    public void render(
            int[] memory,
            int[] characters,
            int paletteBank,
            int scroll,
            int[] destination) {
        if (memory.length < 0x4c00) {
            throw new IllegalArgumentException("memory is too small");
        }
        if (characters.length < 2 * PALETTE_CHARACTER_OFFSET) {
            throw new IllegalArgumentException("decoded character table is too small");
        }
        if (destination.length != WIDTH * HEIGHT) {
            throw new IllegalArgumentException(
                    "expected " + (WIDTH * HEIGHT) + " pixels, got " + destination.length);
        }

        int paletteOffset = (paletteBank & 0x01) * PALETTE_CHARACTER_OFFSET;
        renderLayer(memory, 0x4800, characters, paletteOffset, background);
        renderLayer(
                memory,
                0x4000,
                characters,
                paletteOffset + FOREGROUND_CHARACTER_OFFSET,
                foreground);

        int normalizedScroll = scroll & 0xff;
        for (int y = 0; y < HEIGHT; y++) {
            int backgroundY = (y + normalizedScroll) & 0xff;
            int destinationRow = y * WIDTH;
            int backgroundRow = backgroundY * WIDTH;
            for (int x = 0; x < WIDTH; x++) {
                int foregroundPixel = foreground[destinationRow + x];
                int backgroundPixel = background[backgroundRow + x];
                destination[destinationRow + x] = foregroundPixel != 0
                        ? foregroundPixel
                        : backgroundPixel != 0 ? backgroundPixel : OPAQUE_BLACK;
            }
        }
    }

    private static void renderLayer(
            int[] memory,
            int videoRamStart,
            int[] characters,
            int characterOffset,
            int[] destination) {
        for (int tileY = 0; tileY < TILE_ROWS; tileY++) {
            int videoAddress = videoRamStart + 32 * (TILE_COLUMNS - 1) + tileY;
            for (int tileX = 0; tileX < TILE_COLUMNS; tileX++) {
                int character = memory[videoAddress] & 0xff;
                int characterBase = characterOffset + character * CHARACTER_PIXELS;
                for (int pixelY = 0; pixelY < TILE_SIZE; pixelY++) {
                    int destinationBase =
                            (tileY * TILE_SIZE + pixelY) * WIDTH + tileX * TILE_SIZE;
                    int characterRow = characterBase + pixelY * TILE_SIZE;
                    System.arraycopy(
                            characters,
                            characterRow,
                            destination,
                            destinationBase,
                            TILE_SIZE);
                }
                videoAddress -= 32;
            }
        }
    }
}
