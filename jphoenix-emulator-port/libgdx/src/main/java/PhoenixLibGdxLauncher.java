import com.badlogic.gdx.backends.lwjgl3.Lwjgl3Application;
import com.badlogic.gdx.backends.lwjgl3.Lwjgl3ApplicationConfiguration;

public final class PhoenixLibGdxLauncher {
    private static final int SCALE = 3;

    private PhoenixLibGdxLauncher() {
    }

    public static void main(String[] args) {
        Lwjgl3ApplicationConfiguration configuration =
                new Lwjgl3ApplicationConfiguration();
        configuration.setTitle("JPhoenix LibGDX");
        configuration.setWindowedMode(
                PhoenixFrameBuffer.WIDTH * SCALE,
                PhoenixFrameBuffer.HEIGHT * SCALE);
        configuration.setResizable(false);
        configuration.setForegroundFPS(60);
        configuration.setIdleFPS(15);
        configuration.useVsync(true);
        new Lwjgl3Application(new LibGdxPhoenixApplication(), configuration);
    }
}
