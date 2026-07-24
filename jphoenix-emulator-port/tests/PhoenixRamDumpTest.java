import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;

public final class PhoenixRamDumpTest {
    private static final int RAM_START = 0x4000;
    private static final int RAM_LENGTH = 0x0c00;
    private static final int RECORD_LENGTH = Integer.BYTES + RAM_LENGTH;

    private PhoenixRamDumpTest() {
    }

    public static void main(String[] args) throws Exception {
        Path dump = Files.createTempFile("jphoenix-ram-", ".bin");
        Files.delete(dump);
        String oldDump = System.getProperty("phoenix.ramdump");
        String oldFrames = System.getProperty("phoenix.ramdump.frames");
        setDumpProperties(dump);

        try {
            testDumpWaitsForWaitVblankClear(dump);
            testMidFrameDipReadDoesNotConsumeDumpArm(dump);
            System.out.println("ok - RAM dump timing");
        } finally {
            restoreProperty("phoenix.ramdump", oldDump);
            restoreProperty("phoenix.ramdump.frames", oldFrames);
            Files.deleteIfExists(dump);
        }
    }

    private static void testDumpWaitsForWaitVblankClear(Path dump) throws Exception {
        Files.deleteIfExists(dump);
        Phoenix phoenix = new Phoenix();
        phoenix.pokeb(RAM_START, 0x5a);
        phoenix.pokeb(RAM_START + RAM_LENGTH - 1, 0xa5);
        phoenix.interrupt();

        assertFalse("dump before vblank reads", Files.exists(dump));
        assertEquals("first vblank read", 0x80, phoenix.peekb(0x7800));
        assertFalse("dump after first vblank read", Files.exists(dump));
        assertEquals("second vblank read", 0x80, phoenix.peekb(0x7800));
        assertFalse("dump after second vblank read", Files.exists(dump));
        assertEquals("vblank-clear read", 0x00, phoenix.peekb(0x7800));

        byte[] record = Files.readAllBytes(dump);
        assertEquals("record length", RECORD_LENGTH, record.length);
        ByteBuffer bytes = ByteBuffer.wrap(record);
        assertEquals("frame number", 1, bytes.getInt());
        assertEquals("first RAM byte", 0x5a, bytes.get() & 0xff);
        assertEquals(
                "last RAM byte",
                0xa5,
                record[record.length - 1] & 0xff);
    }

    private static void testMidFrameDipReadDoesNotConsumeDumpArm(Path dump) throws Exception {
        Files.deleteIfExists(dump);
        Phoenix phoenix = new Phoenix();
        phoenix.interrupt();
        phoenix.peekb(0x7800);
        phoenix.peekb(0x7800);

        phoenix.PC(0x0161);
        assertEquals("mid-frame DIP read", 0x00, phoenix.peekb(0x7800));
        assertFalse("dump not consumed by mid-frame DIP read", Files.exists(dump));

        phoenix.PC(0x0082);
        assertEquals("wait-vblank clear read", 0x00, phoenix.peekb(0x7800));
        assertEquals("record length after gated read", RECORD_LENGTH, Files.readAllBytes(dump).length);
    }

    private static void setDumpProperties(Path dump) {
        System.setProperty("phoenix.ramdump", dump.toString());
        System.setProperty("phoenix.ramdump.frames", "1");
    }

    private static void restoreProperty(String key, String value) {
        if (value == null) {
            System.clearProperty(key);
        } else {
            System.setProperty(key, value);
        }
    }

    private static void assertFalse(String label, boolean value) {
        if (value) {
            throw new AssertionError(label);
        }
    }

    private static void assertEquals(String label, int expected, int actual) {
        if (expected != actual) {
            throw new AssertionError(
                    label + " expected 0x" + Integer.toHexString(expected)
                            + " but got 0x" + Integer.toHexString(actual));
        }
    }
}
