import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;

public final class SoundMameNodeTraceReplay {
    private static final int DISCRETE_RATE = 120000;

    private SoundMameNodeTraceReplay() {
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 2 || args.length > 3) {
            throw new IllegalArgumentException(
                    "Usage: java SoundMameNodeTraceReplay"
                            + " <mame-events.csv> <output.csv> [seconds]");
        }
        double seconds = args.length == 3 ? Double.parseDouble(args[2]) : 30.0;
        writeReplay(Path.of(args[0]), new File(args[1]), seconds);
    }

    static void writeReplay(Path tracePath, File output, double seconds) throws Exception {
        File parent = output.getParentFile();
        if (parent != null && !parent.exists() && !parent.mkdirs()) {
            throw new IOException("Could not create " + parent);
        }

        List<SoundMameTraceReplay.Event> events =
                SoundMameTraceReplay.readEvents(tracePath);
        int steppedSamples = (int) Math.round(seconds * DISCRETE_RATE) + 1;
        int eventIndex = 0;
        int latchA = 0;
        int latchB = 0;
        Sound sound = new Sound(PcmSink.discarding());

        try (PrintWriter out = new PrintWriter(output)) {
            out.println("sample,node33,node34,node35,node36,node37,node38,node39,node40");
            // MAME's CSV logger emits one reset row before the first complete
            // netlist step. The autonomous NODE_33/NODE_34 555s have reset,
            // while their downstream nodes have not yet been evaluated.
            out.println("1,4.000000000000,4.000000000000,0.000000000000,"
                    + "0.000000000000,0.000000000000,0.000000000000,"
                    + "0.000000000000,0.000000000000");
            for (int sample = 0; sample < steppedSamples; sample++) {
                while (eventIndex < events.size()
                        && SoundMameRawTraceReplay.eventAppliesBeforeSample(
                                events.get(eventIndex), sample, DISCRETE_RATE)) {
                    SoundMameTraceReplay.Event event = events.get(eventIndex++);
                    if (event.control == 'A') {
                        latchA = event.value;
                    } else {
                        latchB = event.value;
                    }
                }
                Sound.SoundNodes nodes = sound.stepDiscreteNodes(latchA, latchB);
                out.printf(
                        Locale.ROOT,
                        "%d,%.12f,%.12f,%.12f,%.12f,%.12f,%.12f,%.12f,%.12f%n",
                        sample + 2,
                        nodes.node33,
                        nodes.node34,
                        nodes.node35,
                        nodes.node36,
                        nodes.node37,
                        nodes.node38,
                        nodes.node39,
                        nodes.node40);
            }
        }
        System.out.println(output + " samples=" + (steppedSamples + 1));
    }
}
