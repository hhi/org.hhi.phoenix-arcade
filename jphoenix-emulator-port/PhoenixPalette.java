/**
 * Phoenix color-PROM decoder matching MAME's resistor network and normalization.
 */
public final class PhoenixPalette {
    public static final int COLOR_COUNT = 128;
    public static final int PROM_SEGMENT_SIZE = 256;
    public static final int PROM_SIZE = 2 * PROM_SEGMENT_SIZE;

    private PhoenixPalette() {
    }

    public static int[] decode(byte[] proms) {
        if (proms.length != PROM_SIZE) {
            throw new IllegalArgumentException(
                    "Phoenix palette PROM must be " + PROM_SIZE + " bytes");
        }
        byte[] lowBits = new byte[PROM_SEGMENT_SIZE];
        byte[] highBits = new byte[PROM_SEGMENT_SIZE];
        System.arraycopy(proms, 0, lowBits, 0, PROM_SEGMENT_SIZE);
        System.arraycopy(
                proms, PROM_SEGMENT_SIZE, highBits, 0, PROM_SEGMENT_SIZE);
        return decode(lowBits, highBits);
    }

    public static int[] decode(byte[] lowBits, byte[] highBits) {
        if (lowBits.length != PROM_SEGMENT_SIZE
                || highBits.length != PROM_SEGMENT_SIZE) {
            throw new IllegalArgumentException("Phoenix palette PROMs must be 256 bytes each");
        }

        int[] raw = new int[256];
        for (int address = 0; address < raw.length; address++) {
            int low = lowBits[address] & 0xff;
            int high = highBits[address] & 0xff;
            int red = computeChannel((low & 0x01) | ((high & 0x01) << 1));
            int green = computeChannel(((low >> 2) & 0x01) | (((high >> 2) & 0x01) << 1));
            int blue = computeChannel(((low >> 1) & 0x01) | (((high >> 1) & 0x01) << 1));
            raw[address] = 0xff000000 | (red << 16) | (green << 8) | blue;
        }

        int[] nativeOrder = new int[COLOR_COUNT];
        for (int pen = 0; pen < nativeOrder.length; pen++) {
            nativeOrder[pen] = raw[bitswap7(pen)];
        }
        normalize(nativeOrder);
        return nativeOrder;
    }

    private static int computeChannel(int inputs) {
        double conductance = 1.0 / 100.0 + 1.0 / 270.0;
        double current = 5.0 / 100.0;
        if ((inputs & 0x01) == 0) {
            conductance += 1.0 / 270.0;
            current += 0.05 / 270.0;
        }
        if ((inputs & 0x02) == 0) {
            conductance += 1.0;
            current += 0.05;
        }
        double voltage = current / conductance;
        return (int) (voltage * 255.0 / 5.0 + 0.4);
    }

    private static int bitswap7(int value) {
        return ((value >> 6) & 1) << 6
                | ((value >> 5) & 1) << 5
                | ((value >> 1) & 1) << 4
                | (value & 1) << 3
                | ((value >> 4) & 1) << 2
                | ((value >> 3) & 1) << 1
                | ((value >> 2) & 1);
    }

    private static void normalize(int[] colors) {
        int minimumLuminance = 1000 * 255;
        int maximumLuminance = 0;
        for (int color : colors) {
            int luminance = luminance(color);
            minimumLuminance = Math.min(minimumLuminance, luminance);
            maximumLuminance = Math.max(maximumLuminance, luminance);
        }

        for (int i = 0; i < colors.length; i++) {
            int color = colors[i];
            int red = (color >> 16) & 0xff;
            int green = (color >> 8) & 0xff;
            int blue = color & 0xff;
            int luminance = luminance(color);
            int u = (blue - luminance / 1000) * 492 / 1000;
            int v = (red - luminance / 1000) * 877 / 1000;
            int target =
                    ((luminance - minimumLuminance) * 256)
                            / (maximumLuminance - minimumLuminance);
            red = clamp(target + 1140 * v / 1000);
            green = clamp(target - 395 * u / 1000 - 581 * v / 1000);
            blue = clamp(target + 2032 * u / 1000);
            colors[i] = 0xff000000 | (red << 16) | (green << 8) | blue;
        }
    }

    private static int luminance(int color) {
        return 299 * ((color >> 16) & 0xff)
                + 587 * ((color >> 8) & 0xff)
                + 114 * (color & 0xff);
    }

    private static int clamp(int value) {
        return Math.max(0, Math.min(255, value));
    }
}
