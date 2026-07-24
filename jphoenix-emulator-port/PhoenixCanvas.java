import java.awt.Canvas;
import java.awt.Graphics;
import java.awt.image.BufferedImage;

/**
 * AWT display adapter for the framework-neutral Phoenix framebuffer.
 */
public final class PhoenixCanvas extends Canvas {
    private static final long serialVersionUID = 1L;

    private final transient PhoenixFrameBuffer frameBuffer;
    private final transient BufferedImage image = new BufferedImage(
            PhoenixFrameBuffer.WIDTH,
            PhoenixFrameBuffer.HEIGHT,
            BufferedImage.TYPE_INT_ARGB);
    private final transient int[] paintPixels =
            new int[PhoenixFrameBuffer.WIDTH * PhoenixFrameBuffer.HEIGHT];

    public PhoenixCanvas(PhoenixFrameBuffer frameBuffer) {
        this.frameBuffer = frameBuffer;
        setFocusable(true);
        frameBuffer.addFrameListener(this::repaint);
    }

    @Override
    public void update(Graphics graphics) {
        paint(graphics);
    }

    @Override
    public void paint(Graphics graphics) {
        frameBuffer.copyPixels(paintPixels);
        image.setRGB(
                0,
                0,
                PhoenixFrameBuffer.WIDTH,
                PhoenixFrameBuffer.HEIGHT,
                paintPixels,
                0,
                PhoenixFrameBuffer.WIDTH);
        graphics.drawImage(image, 0, 0, getWidth(), getHeight(), null);
    }
}
