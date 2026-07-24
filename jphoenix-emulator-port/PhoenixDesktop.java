import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Frame;
import java.awt.KeyboardFocusManager;
import java.awt.Panel;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicBoolean;

public class PhoenixDesktop {
    private static final boolean DEBUG = Boolean.getBoolean("phoenix.debug");
    private static final int SCALE = 3;
    private static final String WINDOW_TITLE = "JPhoenix Desktop";

    public static void main(String[] args) throws Exception {
        StartupOptions options;
        try {
            options = StartupOptions.parse(args);
        } catch (IllegalArgumentException e) {
            System.err.println("Error: " + e.getMessage());
            printUsage();
            System.exit(2);
            return;
        }
        if (options.help) {
            printUsage();
            return;
        }

        File romDir = options.romDir != null ? new File(options.romDir) : new File(".");
        if (!romDir.isDirectory()) {
            System.err.println("Error: --rom-dir is not a directory: " + romDir);
            System.exit(2);
            return;
        }
        URL baseURL = romDir.getCanonicalFile().toURI().toURL();
        PcmSink pcmSink;
        try {
            pcmSink = new JavaSoundPcmSink(48000);
        } catch (RuntimeException e) {
            pcmSink = PcmSink.discarding();
            System.out.println("Sound hardware disabled: " + e.getMessage());
        }
        Phoenix phoenix = new Phoenix(pcmSink);
        try {
            phoenix.loadRom(baseURL);
            phoenix.loadChr(baseURL);
        } catch (IOException e) {
            System.err.println();
            System.err.println("ROM error: " + e.getMessage());
            System.exit(1);
            return;
        }
        phoenix.decodeChars();
        phoenix.hiload();

        Frame frame = new Frame(WINDOW_TITLE);
        Panel host = new Panel(new BorderLayout());

        frame.add(host, BorderLayout.CENTER);
        frame.setResizable(false);
        frame.addWindowListener(new WindowAdapter() {
            public void windowClosing(WindowEvent e) {
                phoenix.stop();
                frame.dispose();
                System.exit(0);
            }
        });

        PhoenixCanvas canvas = new PhoenixCanvas(phoenix.frameBuffer());
        host.add(canvas, BorderLayout.CENTER);
        boolean startIsGated = options.waitForSpace || options.delayMillis > 0;
        AtomicBoolean gameInputEnabled = new AtomicBoolean(!startIsGated);
        CountDownLatch spacePressed = new CountDownLatch(options.waitForSpace ? 1 : 0);
        canvas.addMouseListener(new MouseAdapter() {
            public void mousePressed(MouseEvent e) {
                canvas.requestFocus();
                if (gameInputEnabled.get() && e.getButton() == MouseEvent.BUTTON1) {
                    setPausedTitle(frame, phoenix.togglePause());
                }
            }
        });

        KeyboardFocusManager.getCurrentKeyboardFocusManager().addKeyEventDispatcher(e -> {
            if (!gameInputEnabled.get()) {
                if (options.waitForSpace
                        && e.getID() == KeyEvent.KEY_PRESSED
                        && e.getKeyCode() == KeyEvent.VK_SPACE) {
                    spacePressed.countDown();
                }
                return true;
            }
            if (e.getID() == KeyEvent.KEY_PRESSED) {
                if (doSaveStateKey(phoenix, e)) {
                    return true;
                }
                return doDesktopKey(phoenix, 1, e);
            }
            if (e.getID() == KeyEvent.KEY_RELEASED) {
                if (e.getKeyCode() == KeyEvent.VK_F5 || e.getKeyCode() == KeyEvent.VK_F9) {
                    return true;
                }
                return doDesktopKey(phoenix, 0, e);
            }
            return false;
        });
        Dimension gameSize = new Dimension(
                Phoenix.nPixelsWide * SCALE,
                Phoenix.nPixelsHigh * SCALE);
        canvas.setPreferredSize(gameSize);
        canvas.setMinimumSize(gameSize);
        canvas.setMaximumSize(gameSize);
        host.validate();

        frame.pack();
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);

        canvas.requestFocus();
        waitBeforeStart(options, frame, spacePressed);
        gameInputEnabled.set(true);
        setPausedTitle(frame, phoenix.isPaused());
        canvas.requestFocus();

        Thread emulatorThread = new Thread(() -> {
            try {
                phoenix.execute();
            } catch (Throwable t) {
                System.err.println("Emulator thread stopped:");
                t.printStackTrace();
            }
        }, "Phoenix Emulator");
        emulatorThread.start();
    }

    private static boolean doSaveStateKey(Phoenix phoenix, KeyEvent event) {
        if (event.getKeyCode() == KeyEvent.VK_F5) {
            PhoenixStateHotkeys.save(phoenix);
            return true;
        }
        if (event.getKeyCode() == KeyEvent.VK_F9) {
            PhoenixStateHotkeys.load(phoenix);
            return true;
        }
        return false;
    }

    private static boolean doDesktopKey(Phoenix phoenix, int down, KeyEvent event) {
        int mappedKey;
        String label = null;
        switch (event.getKeyCode()) {
        case KeyEvent.VK_1:
            mappedKey = '1';
            label = "start 1";
            break;
        case KeyEvent.VK_2:
            mappedKey = '2';
            label = "start 2";
            break;
        case KeyEvent.VK_3:
            mappedKey = '3';
            label = "coin";
            break;
        case KeyEvent.VK_SPACE:
            mappedKey = 32;
            label = "fire";
            break;
        case KeyEvent.VK_B:
            mappedKey = 'b';
            label = "barrier";
            break;
        case KeyEvent.VK_LEFT:
            mappedKey = 1006;
            break;
        case KeyEvent.VK_RIGHT:
            mappedKey = 1007;
            break;
        case KeyEvent.VK_DOWN:
            mappedKey = 1005;
            break;
        default:
            return false;
        }
        phoenix.doKey(down, mappedKey);
        if (DEBUG && down == 1 && label != null) {
            System.out.println("Input: " + label);
        }
        return true;
    }

    private static void waitBeforeStart(
            StartupOptions options, Frame frame, CountDownLatch spacePressed)
            throws InterruptedException {
        if (options.waitForSpace) {
            frame.setTitle(WINDOW_TITLE + " - druk op spatie om te starten");
            spacePressed.await();
        } else if (options.delayMillis > 0) {
            frame.setTitle(WINDOW_TITLE + " - start over "
                    + formatDelay(options.delayMillis) + " seconden");
            Thread.sleep(options.delayMillis);
        }
    }

    private static String formatDelay(long delayMillis) {
        if (delayMillis % 1000 == 0) {
            return Long.toString(delayMillis / 1000);
        }
        return Double.toString(delayMillis / 1000.0);
    }

    private static void setPausedTitle(Frame frame, boolean paused) {
        frame.setTitle(paused
                ? WINDOW_TITLE + " - PAUZE (klik om verder te gaan)"
                : WINDOW_TITLE);
    }

    private static void printUsage() {
        System.out.println("Usage: java PhoenixDesktop [options]");
        System.out.println();
        System.out.println("Options:");
        System.out.println("  --start-delay=<seconds>  Start after the specified delay");
        System.out.println("  --start-delay <seconds>  Same as --start-delay=<seconds>");
        System.out.println("  --wait-for-space         Start when Space is pressed");
        System.out.println("  --rom-dir=<path>         Load program.rom/graphics.rom/proms.rom from <path>");
        System.out.println("  --rom-dir <path>         Same as --rom-dir=<path>");
        System.out.println("  -h, --help               Show this help");
        System.out.println();
        System.out.println("Notes:");
        System.out.println("  --start-delay and --wait-for-space cannot be combined.");
        System.out.println("  <seconds> may be fractional, for example 2.5.");
        System.out.println("  --rom-dir defaults to the current working directory.");
        System.out.println();
        System.out.println("Examples:");
        System.out.println("  java -cp build/classes PhoenixDesktop");
        System.out.println("  java -cp build/classes PhoenixDesktop --start-delay=5");
        System.out.println("  java -cp build/classes PhoenixDesktop --start-delay 2.5");
        System.out.println("  java -cp build/classes PhoenixDesktop --wait-for-space");
        System.out.println("  java -cp build/classes PhoenixDesktop --rom-dir=../roms/assembled");
    }

    static final class StartupOptions {
        final long delayMillis;
        final boolean waitForSpace;
        final boolean help;
        final String romDir;

        StartupOptions(long delayMillis, boolean waitForSpace, boolean help, String romDir) {
            this.delayMillis = delayMillis;
            this.waitForSpace = waitForSpace;
            this.help = help;
            this.romDir = romDir;
        }

        static StartupOptions parse(String[] args) {
            long delayMillis = 0;
            boolean waitForSpace = false;
            boolean help = false;
            String romDir = null;

            for (int i = 0; i < args.length; i++) {
                String arg = args[i];
                if ("--wait-for-space".equals(arg)) {
                    waitForSpace = true;
                } else if ("--help".equals(arg) || "-h".equals(arg)) {
                    help = true;
                } else if (arg.startsWith("--start-delay=")) {
                    delayMillis = parseDelay(arg.substring("--start-delay=".length()));
                } else if ("--start-delay".equals(arg)) {
                    if (++i >= args.length) {
                        throw new IllegalArgumentException(
                                "--start-delay requires a number of seconds");
                    }
                    delayMillis = parseDelay(args[i]);
                } else if (arg.startsWith("--rom-dir=")) {
                    romDir = arg.substring("--rom-dir=".length());
                } else if ("--rom-dir".equals(arg)) {
                    if (++i >= args.length) {
                        throw new IllegalArgumentException("--rom-dir requires a path");
                    }
                    romDir = args[i];
                } else {
                    throw new IllegalArgumentException("unknown option: " + arg);
                }
            }

            if (waitForSpace && delayMillis > 0) {
                throw new IllegalArgumentException(
                        "--wait-for-space and --start-delay cannot be combined");
            }
            return new StartupOptions(delayMillis, waitForSpace, help, romDir);
        }

        private static long parseDelay(String value) {
            final double seconds;
            try {
                seconds = Double.parseDouble(value);
            } catch (NumberFormatException e) {
                throw new IllegalArgumentException(
                        "invalid start delay: " + value);
            }
            if (!Double.isFinite(seconds) || seconds < 0.0) {
                throw new IllegalArgumentException(
                        "start delay must be a finite, non-negative number");
            }
            if (seconds > Long.MAX_VALUE / 1000.0) {
                throw new IllegalArgumentException("start delay is too large");
            }
            return Math.round(seconds * 1000.0);
        }
    }
}
