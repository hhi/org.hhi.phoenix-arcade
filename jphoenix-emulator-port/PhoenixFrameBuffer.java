import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Thread-safe publication point for complete Phoenix video frames.
 *
 * The emulator thread publishes ARGB pixels while frontends copy the latest
 * frame at their own pace. Frontends never receive a mutable core-owned array.
 */
public final class PhoenixFrameBuffer {
    public static final int WIDTH = PhoenixVideoRenderer.WIDTH;
    public static final int HEIGHT = PhoenixVideoRenderer.HEIGHT;

    private final int[] pixels = new int[WIDTH * HEIGHT];
    private final List<Runnable> frameListeners = new CopyOnWriteArrayList<Runnable>();
    private long frameNumber;

    public PhoenixFrameBuffer() {
        for (int i = 0; i < pixels.length; i++) {
            pixels[i] = 0xff000000;
        }
    }

    public void publish(int[] source) {
        if (source.length != pixels.length) {
            throw new IllegalArgumentException(
                    "expected " + pixels.length + " pixels, got " + source.length);
        }
        synchronized (this) {
            System.arraycopy(source, 0, pixels, 0, pixels.length);
            frameNumber++;
        }
        for (Runnable listener : frameListeners) {
            listener.run();
        }
    }

    public synchronized void copyPixels(int[] destination) {
        if (destination.length != pixels.length) {
            throw new IllegalArgumentException(
                    "expected " + pixels.length + " pixels, got " + destination.length);
        }
        System.arraycopy(pixels, 0, destination, 0, pixels.length);
    }

    public synchronized int[] copyPixels() {
        return pixels.clone();
    }

    public synchronized long frameNumber() {
        return frameNumber;
    }

    public void addFrameListener(Runnable listener) {
        if (listener == null) {
            throw new NullPointerException("listener");
        }
        frameListeners.add(listener);
    }

    public void removeFrameListener(Runnable listener) {
        frameListeners.remove(listener);
    }
}
