import java.io.IOException;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Shared asynchronous F5/F9 actions for desktop frontends.
 */
public final class PhoenixStateHotkeys {
    private static final AtomicBoolean OPERATION_RUNNING = new AtomicBoolean();

    private PhoenixStateHotkeys() {
    }

    public static void save(Phoenix phoenix) {
        runAsync(phoenix, false);
    }

    public static void load(Phoenix phoenix) {
        runAsync(phoenix, true);
    }

    private static void runAsync(Phoenix phoenix, boolean load) {
        if (!OPERATION_RUNNING.compareAndSet(false, true)) {
            return;
        }
        Thread operation = new Thread(() -> {
            try {
                if (load) {
                    phoenix.loadState(PhoenixSaveState.DEFAULT_PATH);
                    System.out.println(
                            "Save state loaded: " + PhoenixSaveState.DEFAULT_PATH);
                } else {
                    phoenix.saveState(PhoenixSaveState.DEFAULT_PATH);
                    System.out.println(
                            "Save state saved: " + PhoenixSaveState.DEFAULT_PATH);
                }
            } catch (IOException e) {
                System.err.println(
                        (load ? "Save-state load failed: " : "Save-state save failed: ")
                                + e.getMessage());
            } finally {
                OPERATION_RUNNING.set(false);
            }
        }, load ? "Phoenix Load State" : "Phoenix Save State");
        operation.setDaemon(true);
        operation.start();
    }
}
