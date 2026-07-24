public final class PhoenixPaletteTest {
    private static final int[] MAME_PALETTE = {
        0xff000000, 0xff0a07bd, 0xff9f1114, 0xffc8c8c8,
        0xff000000, 0xff2db8e0, 0xffd11eaa, 0xffedc63a,
        0xff000000, 0xffcdf040, 0xffa71bce, 0xffedc63a,
        0xff000000, 0xffa71bce, 0xff2ab5b6, 0xffd11eaa,
        0xff000000, 0xfff6f644, 0xff0a07bd, 0xffd5fbf9,
        0xff000000, 0xff2db8e0, 0xffd11eaa, 0xffcdf040,
        0xff000000, 0xff2db8e0, 0xffd11eaa, 0xffcdf040,
        0xff000000, 0xff2db8e0, 0xffd11eaa, 0xffcdf040,
        0xff000000, 0xff35e7bf, 0xff2db8e0, 0xff36e8e9,
        0xff000000, 0xffca1618, 0xfff6f644, 0xffffffff,
        0xff000000, 0xffca1618, 0xfff6f644, 0xffffffff,
        0xff000000, 0xffd31fd2, 0xfff4cdcf, 0xfff6f644,
        0xff000000, 0xffd31fd2, 0xfff4cdcf, 0xfff6f644,
        0xff000000, 0xffd31fd2, 0xfff4cdcf, 0xfff6f644,
        0xff000000, 0xffca1618, 0xffffffff, 0xffd31fd2,
        0xff000000, 0xff23ad24, 0xffa518a5, 0xffffffff,
        0xff000000, 0xff0a07bd, 0xff9f1114, 0xffc0c136,
        0xff000000, 0xff0a07bd, 0xffd11eaa, 0xffedc63a,
        0xff000000, 0xffcdf040, 0xffa71bce, 0xffedc63a,
        0xff000000, 0xffa71bce, 0xff2ab5b6, 0xffd11eaa,
        0xff000000, 0xffd11eaa, 0xff2db8e0, 0xffcdf040,
        0xff000000, 0xffd11eaa, 0xff2db8e0, 0xffcdf040,
        0xff000000, 0xffd11eaa, 0xff2db8e0, 0xffcdf040,
        0xff000000, 0xffd11eaa, 0xff2db8e0, 0xffcdf040,
        0xff000000, 0xff35e7bf, 0xff2db8e0, 0xfff6f644,
        0xff000000, 0xffca1618, 0xfff6f644, 0xffffffff,
        0xff000000, 0xffca1618, 0xfff6f644, 0xffffffff,
        0xff000000, 0xff2edf2d, 0xfff6f644, 0xfff5d0f5,
        0xff000000, 0xff2edf2d, 0xfff6f644, 0xfff5d0f5,
        0xff000000, 0xff2edf2d, 0xfff6f644, 0xfff5d0f5,
        0xff000000, 0xffd31fd2, 0xffffffff, 0xfff6f644,
        0xff000000, 0xff2edf2d, 0xffa518a5, 0xffffffff
    };

    private PhoenixPaletteTest() {
    }

    public static void main(String[] args) throws Exception {
        byte[] proms = RomLoader.load(RomLoaderTest.romBaseUrl(), RomLoader.PALETTE);
        int[] actual = PhoenixPalette.decode(proms);
        if (actual.length != MAME_PALETTE.length) {
            throw new AssertionError("wrong palette length: " + actual.length);
        }
        for (int i = 0; i < actual.length; i++) {
            if (actual[i] != MAME_PALETTE[i]) {
                throw new AssertionError(
                        "MAME palette pen " + i
                                + ": expected 0x" + Integer.toHexString(MAME_PALETTE[i])
                                + ", got 0x" + Integer.toHexString(actual[i]));
            }
        }
        System.out.println("ok - palette PROM");
    }
}
