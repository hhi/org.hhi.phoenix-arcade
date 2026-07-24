import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.nio.ByteBuffer;
import java.util.concurrent.atomic.AtomicReference;

import com.badlogic.gdx.ApplicationAdapter;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Input;
import com.badlogic.gdx.InputAdapter;
import com.badlogic.gdx.audio.AudioDevice;
import com.badlogic.gdx.graphics.GL20;
import com.badlogic.gdx.graphics.OrthographicCamera;
import com.badlogic.gdx.graphics.Pixmap;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.utils.GdxRuntimeException;
import com.badlogic.gdx.utils.viewport.FitViewport;

/**
 * LibGDX frontend for the framework-neutral Phoenix emulation core.
 */
final class LibGdxPhoenixApplication extends ApplicationAdapter {
    private static final int SAMPLE_RATE = 48000;
    private static final String WINDOW_TITLE = "JPhoenix LibGDX";

    private final AtomicReference<Throwable> emulatorFailure = new AtomicReference<Throwable>();
    private final int[] framePixels =
            new int[PhoenixFrameBuffer.WIDTH * PhoenixFrameBuffer.HEIGHT];

    private Phoenix phoenix;
    private Thread emulatorThread;
    private SpriteBatch batch;
    private Pixmap pixmap;
    private Texture texture;
    private FitViewport viewport;
    private long uploadedFrame = -1;
    private InputAdapter inputAdapter;

    @Override
    public void create() {
        batch = new SpriteBatch();
        pixmap = new Pixmap(
                PhoenixFrameBuffer.WIDTH,
                PhoenixFrameBuffer.HEIGHT,
                Pixmap.Format.RGBA8888);
        texture = new Texture(pixmap);
        texture.setFilter(Texture.TextureFilter.Nearest, Texture.TextureFilter.Nearest);
        viewport = new FitViewport(
                PhoenixFrameBuffer.WIDTH,
                PhoenixFrameBuffer.HEIGHT,
                new OrthographicCamera());

        PcmSink pcmSink = createPcmSink();
        phoenix = new Phoenix(pcmSink);
        try {
            URL baseUrl = new File("../roms/assembled").getCanonicalFile().toURI().toURL();
            phoenix.loadRom(baseUrl);
            phoenix.loadChr(baseUrl);
        } catch (IOException e) {
            phoenix.stop();
            throw new GdxRuntimeException("ROM error: " + e.getMessage(), e);
        }
        phoenix.decodeChars();
        phoenix.hiload();

        inputAdapter = new InputAdapter() {
            @Override
            public boolean keyDown(int keycode) {
                if (keycode == Input.Keys.F5) {
                    PhoenixStateHotkeys.save(phoenix);
                    return true;
                }
                if (keycode == Input.Keys.F9) {
                    PhoenixStateHotkeys.load(phoenix);
                    return true;
                }
                if (keycode == Input.Keys.ESCAPE) {
                    Gdx.app.exit();
                    return true;
                }
                return updateInput(1, keycode);
            }

            @Override
            public boolean keyUp(int keycode) {
                if (keycode == Input.Keys.F5 || keycode == Input.Keys.F9) {
                    return true;
                }
                return updateInput(0, keycode);
            }

            @Override
            public boolean touchDown(int screenX, int screenY, int pointer, int button) {
                if (button != Input.Buttons.LEFT) {
                    return false;
                }
                setPausedTitle(phoenix.togglePause());
                return true;
            }
        };
        Gdx.input.setInputProcessor(inputAdapter);

        emulatorThread = new Thread(() -> {
            try {
                phoenix.execute();
            } catch (Throwable failure) {
                emulatorFailure.compareAndSet(null, failure);
            }
        }, "Phoenix Emulator");
        emulatorThread.start();
    }

    private static PcmSink createPcmSink() {
        try {
            AudioDevice device = Gdx.audio.newAudioDevice(SAMPLE_RATE, true);
            return new LibGdxPcmSink(device);
        } catch (RuntimeException e) {
            System.out.println("Sound hardware disabled: " + e.getMessage());
            return PcmSink.discarding();
        }
    }

    private boolean updateInput(int down, int keycode) {
        int mappedKey = mapKey(keycode);
        if (mappedKey == -1) {
            return false;
        }
        phoenix.doKey(down, mappedKey);
        return true;
    }

    private static void setPausedTitle(boolean paused) {
        Gdx.graphics.setTitle(paused
                ? WINDOW_TITLE + " - PAUZE (klik om verder te gaan)"
                : WINDOW_TITLE);
    }

    static int mapKey(int keycode) {
        switch (keycode) {
        case Input.Keys.NUM_1:
        case Input.Keys.NUMPAD_1:
            return '1';
        case Input.Keys.NUM_2:
        case Input.Keys.NUMPAD_2:
            return '2';
        case Input.Keys.NUM_3:
        case Input.Keys.NUMPAD_3:
            return '3';
        case Input.Keys.SPACE:
            return 32;
        case Input.Keys.B:
            return 'b';
        case Input.Keys.DOWN:
            return 1005;
        case Input.Keys.LEFT:
            return 1006;
        case Input.Keys.RIGHT:
            return 1007;
        default:
            return -1;
        }
    }

    @Override
    public void render() {
        Throwable failure = emulatorFailure.get();
        if (failure != null) {
            throw new GdxRuntimeException("Emulator thread stopped", failure);
        }

        uploadLatestFrame();
        Gdx.gl.glClearColor(0f, 0f, 0f, 1f);
        Gdx.gl.glClear(GL20.GL_COLOR_BUFFER_BIT);
        viewport.apply();
        batch.setProjectionMatrix(viewport.getCamera().combined);
        batch.begin();
        batch.draw(
                texture,
                0,
                0,
                PhoenixFrameBuffer.WIDTH,
                PhoenixFrameBuffer.HEIGHT);
        batch.end();
    }

    private void uploadLatestFrame() {
        PhoenixFrameBuffer frameBuffer = phoenix.frameBuffer();
        long frameNumber = frameBuffer.frameNumber();
        if (frameNumber == uploadedFrame) {
            return;
        }
        frameBuffer.copyPixels(framePixels);
        ByteBuffer pixels = pixmap.getPixels();
        LibGdxFrameEncoder.writeRgba8888(framePixels, pixels);
        texture.draw(pixmap, 0, 0);
        uploadedFrame = frameNumber;
    }

    @Override
    public void resize(int width, int height) {
        viewport.update(width, height, true);
    }

    @Override
    public void dispose() {
        if (Gdx.input.getInputProcessor() == inputAdapter) {
            Gdx.input.setInputProcessor(null);
        }
        if (phoenix != null) {
            phoenix.stop();
        }
        if (emulatorThread != null && emulatorThread != Thread.currentThread()) {
            try {
                emulatorThread.join(2000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        if (texture != null) {
            texture.dispose();
        }
        if (pixmap != null) {
            pixmap.dispose();
        }
        if (batch != null) {
            batch.dispose();
        }
    }
}
