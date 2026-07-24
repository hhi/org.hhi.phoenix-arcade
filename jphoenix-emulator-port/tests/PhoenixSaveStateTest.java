import java.io.ByteArrayOutputStream;
import java.io.File;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

public final class PhoenixSaveStateTest {
    private PhoenixSaveStateTest() {
    }

    public static void main(String[] args) throws Exception {
        testRoundTripAndAudioContinuity();
        testChecksummedAtomicFile();
        testRunningFrameBoundary();
        System.out.println("ok - save state");
    }

    private static void testRoundTripAndAudioContinuity() throws Exception {
        RecordingSink sink = new RecordingSink();
        Phoenix phoenix = loadedPhoenix(sink);
        phoenix.PC(0x2345);
        phoenix.SP(0xcafe);
        phoenix.AF(0x5a93);
        phoenix.BC(0x1234);
        phoenix.DE(0x5678);
        phoenix.HL(0x9abc);
        phoenix.pokeb(0x4000, 0x31);
        phoenix.pokeb(0x4800, 0x62);
        phoenix.pokeb(0x5000, 0x03);
        phoenix.pokeb(0x4000, 0x47);
        phoenix.pokeb(0x4800, 0x73);
        phoenix.pokeb(0x5800, 0x59);
        phoenix.pokeb(0x6000, 0x25);
        phoenix.pokeb(0x6800, 0x4b);
        phoenix.interrupt();

        byte[] snapshot = PhoenixSaveState.encode(phoenix);
        int[] expectedPixels = phoenix.frameBuffer().copyPixels();

        sink.clear();
        renderFrames(phoenix, 4);
        byte[] expectedAudio = sink.bytes();

        phoenix.PC(0);
        phoenix.SP(0);
        phoenix.pokeb(0x4000, 0xff);
        phoenix.pokeb(0x5800, 0);
        phoenix.pokeb(0x6000, 0);
        phoenix.pokeb(0x6800, 0);

        PhoenixSaveState.decode(phoenix, snapshot);
        byte[] restored = PhoenixSaveState.encode(phoenix);
        if (!Arrays.equals(snapshot, restored)) {
            throw new AssertionError("save-state round trip changed serialized machine state");
        }
        if (!Arrays.equals(expectedPixels, phoenix.frameBuffer().copyPixels())) {
            throw new AssertionError("restored framebuffer differs from saved state");
        }

        sink.clear();
        renderFrames(phoenix, 4);
        if (!Arrays.equals(expectedAudio, sink.bytes())) {
            throw new AssertionError("audio continuation differs after save-state load");
        }
    }

    private static void testChecksummedAtomicFile() throws Exception {
        Phoenix phoenix = loadedPhoenix(PcmSink.discarding());
        Path directory = Files.createTempDirectory("jphoenix-state-");
        Path state = directory.resolve("slot.state");
        phoenix.saveState(state);
        byte[] valid = Files.readAllBytes(state);

        phoenix.pokeb(0x4001, 0xaa);
        phoenix.saveState(state);
        if (!Files.isRegularFile(state) || Files.size(state) == 0) {
            throw new AssertionError("atomic save-state replacement failed");
        }

        PhoenixSaveState.decode(phoenix, valid);
        byte[] beforeCorruptLoad = PhoenixSaveState.encode(phoenix);
        valid[valid.length - 1] ^= 0x40;
        Files.write(state, valid);
        try {
            phoenix.loadState(state);
            throw new AssertionError("corrupt save state was accepted");
        } catch (java.io.IOException expected) {
            if (!expected.getMessage().contains("checksum")) {
                throw expected;
            }
        }
        if (!Arrays.equals(beforeCorruptLoad, PhoenixSaveState.encode(phoenix))) {
            throw new AssertionError("rejected save state mutated the machine");
        }
    }

    private static void testRunningFrameBoundary() throws Exception {
        Phoenix phoenix = loadedPhoenix(PcmSink.discarding());
        Thread emulator = new Thread(phoenix::execute, "save-state-test-emulator");
        emulator.start();
        Path state = Files.createTempFile("jphoenix-running-", ".state");
        try {
            long deadline = System.nanoTime() + 3_000_000_000L;
            while (phoenix.frameBuffer().frameNumber() < 2
                    && System.nanoTime() < deadline) {
                Thread.sleep(5);
            }
            if (phoenix.frameBuffer().frameNumber() < 2) {
                throw new AssertionError("emulator did not reach a frame boundary");
            }
            phoenix.saveState(state);
            phoenix.loadState(state);
        } finally {
            phoenix.stop();
            emulator.join(3000);
        }
        if (emulator.isAlive()) {
            throw new AssertionError("emulator did not stop after save-state test");
        }
    }

    private static Phoenix loadedPhoenix(PcmSink sink) throws Exception {
        URL baseUrl = RomLoaderTest.romBaseUrl();
        Phoenix phoenix = new Phoenix(sink);
        phoenix.loadRom(baseUrl);
        phoenix.loadChr(baseUrl);
        phoenix.decodeChars();
        return phoenix;
    }

    private static void renderFrames(Phoenix phoenix, int frames) {
        for (int i = 0; i < frames; i++) {
            phoenix.interrupt();
        }
    }

    private static final class RecordingSink implements PcmSink {
        private final ByteArrayOutputStream output = new ByteArrayOutputStream();

        @Override
        public void write(byte[] pcm, int offset, int length) {
            output.write(pcm, offset, length);
        }

        byte[] bytes() {
            return output.toByteArray();
        }

        void clear() {
            output.reset();
        }
    }
}
