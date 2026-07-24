public final class PhoenixPauseTest {
    private PhoenixPauseTest() {
    }

    public static void main(String[] args) {
        Phoenix phoenix = new Phoenix();
        assertPaused("initial pause state", phoenix, false);
        if (!phoenix.togglePause()) {
            throw new AssertionError("togglePause did not enter pause");
        }
        assertPaused("after toggle on", phoenix, true);
        phoenix.setPaused(false);
        assertPaused("after setPaused false", phoenix, false);
        phoenix.setPaused(true);
        assertPaused("after setPaused true", phoenix, true);
        phoenix.stop();
        assertPaused("after stop", phoenix, false);
        System.out.println("ok - pause toggle");
    }

    private static void assertPaused(String label, Phoenix phoenix, boolean expected) {
        if (phoenix.isPaused() != expected) {
            throw new AssertionError(label + " expected " + expected);
        }
    }
}
