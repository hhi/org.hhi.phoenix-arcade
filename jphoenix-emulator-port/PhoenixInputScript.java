import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.Closeable;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

final class PhoenixInputScript {
    private final List<Event> events;
    private int nextEvent;

    private PhoenixInputScript(List<Event> events) {
        this.events = events;
    }

    static PhoenixInputScript load(Path path) throws IOException {
        List<Event> events = new ArrayList<Event>();
        try (BufferedReader reader = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
            String line;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) {
                    continue;
                }
                String[] parts = line.split("\\s+");
                if (parts.length < 3) {
                    continue;
                }
                int frame;
                try {
                    frame = Integer.parseInt(parts[0]);
                } catch (NumberFormatException e) {
                    continue;
                }
                int mask = maskForButton(parts[1]);
                if (mask == 0) {
                    System.out.println("Input script: unknown button '" + parts[1] + "', skipping");
                    continue;
                }
                events.add(new Event(frame, mask, "press".equals(parts[2])));
            }
        }
        events.sort(Comparator.comparingInt(event -> event.frame));
        System.out.println("Loaded " + events.size() + " input-script events from " + path);
        return new PhoenixInputScript(events);
    }

    void applyDueEvents(int frame, Phoenix phoenix) {
        while (nextEvent < events.size() && events.get(nextEvent).frame <= frame) {
            Event event = events.get(nextEvent);
            phoenix.applyInputEvent(event.mask, event.press);
            nextEvent++;
        }
    }

    static int maskForButton(String name) {
        if ("coin".equals(name)) return 0x01;
        if ("start1".equals(name)) return 0x02;
        if ("start2".equals(name)) return 0x04;
        if ("fire".equals(name)) return 0x10;
        if ("right".equals(name)) return 0x20;
        if ("left".equals(name)) return 0x40;
        if ("shield".equals(name)) return 0x80;
        return 0;
    }

    static String buttonNameForMask(int mask) {
        switch (mask) {
        case 0x01:
            return "coin";
        case 0x02:
            return "start1";
        case 0x04:
            return "start2";
        case 0x10:
            return "fire";
        case 0x20:
            return "right";
        case 0x40:
            return "left";
        case 0x80:
            return "shield";
        default:
            return null;
        }
    }

    static final class Recorder implements Closeable {
        private final BufferedWriter writer;
        private int eventsWritten;
        private boolean disabled;

        Recorder(Path path) throws IOException {
            writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8);
            writer.write("# Recorded session, " + ZonedDateTime.now());
            writer.newLine();
            writer.write("# Replay with: java -Dphoenix.inputscript=" + path + " -cp build/classes PhoenixDesktop");
            writer.newLine();
            writer.flush();
            System.out.println("Recording input to " + path);
        }

        void record(int frame, int mask, boolean press) {
            if (disabled) {
                return;
            }
            String name = buttonNameForMask(mask);
            if (name == null) {
                return;
            }
            try {
                writer.write(Integer.toString(frame));
                writer.write(' ');
                writer.write(name);
                writer.write(' ');
                writer.write(press ? "press" : "release");
                writer.newLine();
                writer.flush();
                eventsWritten++;
            } catch (IOException e) {
                System.out.println("Input recording failed, disabling: " + e.getMessage());
                disabled = true;
                closeQuietly();
            }
        }

        @Override
        public void close() throws IOException {
            writer.close();
            System.out.println("Input recording complete (" + eventsWritten + " events)");
        }

        private void closeQuietly() {
            try {
                writer.close();
            } catch (IOException ignored) {
            }
        }
    }

    private static final class Event {
        final int frame;
        final int mask;
        final boolean press;

        Event(int frame, int mask, boolean press) {
            this.frame = frame;
            this.mask = mask;
            this.press = press;
        }
    }
}
