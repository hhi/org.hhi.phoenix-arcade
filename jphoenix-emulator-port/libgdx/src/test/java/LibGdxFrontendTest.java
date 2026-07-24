import java.lang.reflect.Proxy;
import java.nio.ByteBuffer;
import java.util.Arrays;

import com.badlogic.gdx.Input;
import com.badlogic.gdx.audio.AudioDevice;

public final class LibGdxFrontendTest {
    private LibGdxFrontendTest() {
    }

    public static void main(String[] args) {
        testFrameEncoding();
        testInputMapping();
        testPcmSink();
        System.out.println("ok - LibGDX frontend");
    }

    private static void testFrameEncoding() {
        ByteBuffer output = ByteBuffer.allocate(8);
        LibGdxFrameEncoder.writeRgba8888(
                new int[] {0xff123456, 0x807f00ff},
                output);
        byte[] actual = new byte[8];
        output.get(actual);
        byte[] expected = {
            0x12, 0x34, 0x56, (byte) 0xff,
            0x7f, 0x00, (byte) 0xff, (byte) 0x80
        };
        if (!Arrays.equals(actual, expected)) {
            throw new AssertionError("wrong RGBA8888 encoding: " + Arrays.toString(actual));
        }
    }

    private static void testInputMapping() {
        assertMapping(Input.Keys.NUM_1, '1');
        assertMapping(Input.Keys.NUMPAD_2, '2');
        assertMapping(Input.Keys.NUM_3, '3');
        assertMapping(Input.Keys.SPACE, 32);
        assertMapping(Input.Keys.B, 'b');
        assertMapping(Input.Keys.DOWN, 1005);
        assertMapping(Input.Keys.LEFT, 1006);
        assertMapping(Input.Keys.RIGHT, 1007);
        assertMapping(Input.Keys.A, -1);
    }

    private static void assertMapping(int keycode, int expected) {
        int actual = LibGdxPhoenixApplication.mapKey(keycode);
        if (actual != expected) {
            throw new AssertionError(
                    "key " + keycode + ": expected " + expected + ", got " + actual);
        }
    }

    private static void testPcmSink() {
        AudioCapture capture = new AudioCapture();
        AudioDevice device = (AudioDevice) Proxy.newProxyInstance(
                AudioDevice.class.getClassLoader(),
                new Class<?>[] {AudioDevice.class},
                (proxy, method, arguments) -> {
                    if ("writeSamples".equals(method.getName())
                            && arguments[0] instanceof short[]) {
                        short[] source = (short[]) arguments[0];
                        int offset = (Integer) arguments[1];
                        int length = (Integer) arguments[2];
                        capture.samples = Arrays.copyOfRange(source, offset, offset + length);
                        capture.writeCalls++;
                    } else if ("dispose".equals(method.getName())) {
                        capture.disposed = true;
                    }
                    return defaultValue(method.getReturnType());
                });

        LibGdxPcmSink sink = new LibGdxPcmSink(device);
        sink.write(new byte[] {0x34, 0x12, 0x00, (byte) 0x80}, 0, 4);
        if (capture.writeCalls != 1
                || !Arrays.equals(capture.samples, new short[] {0x1234, (short) 0x8000})) {
            throw new AssertionError("wrong LibGDX PCM conversion");
        }
        sink.close();
        sink.close();
        if (!capture.disposed) {
            throw new AssertionError("LibGDX AudioDevice was not disposed");
        }
    }

    private static Object defaultValue(Class<?> type) {
        if (!type.isPrimitive() || type == void.class) {
            return null;
        }
        if (type == boolean.class) {
            return false;
        }
        if (type == float.class) {
            return 0f;
        }
        if (type == double.class) {
            return 0d;
        }
        if (type == long.class) {
            return 0L;
        }
        return 0;
    }

    private static final class AudioCapture {
        short[] samples = new short[0];
        int writeCalls;
        boolean disposed;
    }
}
