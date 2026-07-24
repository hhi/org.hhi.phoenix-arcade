/**
 * Decodes Phoenix's two 2 KiB graphics bitplanes into 2-bit pixel indices.
 */
public final class PhoenixGraphicsDecoder {
    static final int CHARSET_COUNT = 2;
    static final int CHARACTERS_PER_SET = 256;
    static final int PIXELS_PER_CHARACTER = 64;
    static final int BYTES_PER_PLANE = 256 * 8;
    static final int BYTES_PER_CHARSET = 2 * BYTES_PER_PLANE;
    static final int GRAPHICS_SIZE = CHARSET_COUNT * BYTES_PER_CHARSET;

    private PhoenixGraphicsDecoder() {
    }

    public static byte[] decode(byte[] graphics) {
        if (graphics.length != GRAPHICS_SIZE) {
            throw new IllegalArgumentException(
                    "Phoenix graphics ROM must be " + GRAPHICS_SIZE + " bytes");
        }

        byte[] pixels =
                new byte[CHARSET_COUNT * CHARACTERS_PER_SET * PIXELS_PER_CHARACTER];
        for (int charset = 0; charset < CHARSET_COUNT; charset++) {
            int charsetOffset = charset * BYTES_PER_CHARSET;
            for (int character = 0; character < CHARACTERS_PER_SET; character++) {
                int characterOffset = charsetOffset + character * 8;
                int pixelOffset =
                        (charset * CHARACTERS_PER_SET + character)
                                * PIXELS_PER_CHARACTER;
                for (int line = 0; line < 8; line++) {
                    int lowPlane = graphics[characterOffset + line] & 0xff;
                    int highPlane =
                            graphics[characterOffset + BYTES_PER_PLANE + line] & 0xff;
                    for (int column = 0; column < 8; column++) {
                        int pixel =
                                ((lowPlane >> column) & 0x01)
                                        | (((highPlane >> column) & 0x01) << 1);
                        pixels[pixelOffset + column * 8 + 7 - line] = (byte) pixel;
                    }
                }
            }
        }
        return pixels;
    }
}
