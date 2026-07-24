import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Locale;

public class SoundNodeDump {
	private static final int DISCRETE_RATE = 120000;
	private static final int DEFAULT_SAMPLES = DISCRETE_RATE / 2;

	public static void main(String[] args) throws IOException {
		File outFile = new File(args.length == 0 ? "sound-renders/nodes_effect2_bird_hit.csv" : args[0]);
		int controlA = args.length > 1 ? Integer.decode(args[1]) & 0xff : 0x28;
		int controlB = args.length > 2 ? Integer.decode(args[2]) & 0xff : 0x0f;
		int samples = args.length > 3 ? Integer.parseInt(args[3]) : DEFAULT_SAMPLES;
		writeDump(outFile, controlA, controlB, samples);
		System.out.println(summary(outFile, controlA, controlB, samples));
	}

	static void writeDump(File outFile, int controlA, int controlB, int samples) throws IOException {
		File parent = outFile.getParentFile();
		if (parent != null && !parent.exists() && !parent.mkdirs()) {
			throw new IOException("Could not create " + parent);
		}

		try (PrintWriter out = new PrintWriter(outFile)) {
			out.println("sample,time_seconds,node20,node21,node22,node23,node24,node25,effect1,"
					+ "node30,node31,node32,node33,node34,node35,node36,node37,node38,node39,node40,effect2,node90");
			Sound sound = new Sound(PcmSink.discarding());
			for (int i = 0; i < samples; i++) {
				Sound.SoundNodes nodes = sound.stepDiscreteNodes(controlA, controlB);
				out.printf(Locale.ROOT,
						"%d,%.9f,%.9f,%.9f,%.9f,%.9f,%.9f,%.9f,%.9f,%.12f,%.9f,%.9f,%.9f,%.9f,%.9f,%.9f,%.9f,%.9f,%.9f,%.9f,%.9f,%.9f%n",
						i,
						i / (double) DISCRETE_RATE,
						nodes.node20,
						nodes.node21,
						nodes.node22,
						nodes.node23,
						nodes.node24,
						nodes.node25,
						nodes.effect1Sound,
						nodes.node30,
						nodes.node31,
						nodes.node32,
						nodes.node33,
						nodes.node34,
						nodes.node35,
						nodes.node36,
						nodes.node37,
						nodes.node38,
						nodes.node39,
						nodes.node40,
						nodes.effect2Sound,
						nodes.node90);
			}
		}
	}

	private static String summary(File outFile, int controlA, int controlB, int samples) {
		return outFile.getPath()
				+ " controlA=0x" + Integer.toHexString(controlA)
				+ " controlB=0x" + Integer.toHexString(controlB)
				+ " samples=" + samples;
	}
}
