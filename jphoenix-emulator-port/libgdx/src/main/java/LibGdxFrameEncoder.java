import java.nio.ByteBuffer;

/**
 * Converts core ARGB pixels to the RGBA8888 byte order expected by a LibGDX Pixmap.
 */
final class LibGdxFrameEncoder {
    private LibGdxFrameEncoder() {
    }

    static void writeRgba8888(int[] argbPixels, ByteBuffer destination) {
        int requiredBytes = argbPixels.length * 4;
        if (destination.capacity() < requiredBytes) {
            throw new IllegalArgumentException(
                    "destination needs " + requiredBytes + " bytes");
        }
        destination.clear();
        for (int argb : argbPixels) {
            destination.put((byte) (argb >>> 16));
            destination.put((byte) (argb >>> 8));
            destination.put((byte) argb);
            destination.put((byte) (argb >>> 24));
        }
        destination.flip();
    }
}
