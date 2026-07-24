import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Path;
import java.util.List;

public class SoundMameRawTraceReplay {
	private static final int DISCRETE_RATE = 120000;
	private static final int CUSTOM_RATE = 48000;
	private static final int TMS_RATE = 372 * 64;

	public static void main(String[] args) throws Exception {
		if (args.length < 2 || args.length > 3) {
			throw new IllegalArgumentException(
					"Usage: java SoundMameRawTraceReplay <mame-events.csv> <output-dir> [seconds]");
		}
		double seconds = args.length == 3 ? Double.parseDouble(args[2]) : 30.0;
		File outputDir = new File(args[1]);
		writeReplay(Path.of(args[0]), outputDir, seconds, true);
	}

	static void writeReplay(Path tracePath, File outputDir, double seconds, boolean verbose)
			throws Exception {
		if (!outputDir.exists() && !outputDir.mkdirs()) {
			throw new IOException("Could not create " + outputDir);
		}
		List<SoundMameTraceReplay.Event> events = SoundMameTraceReplay.readEvents(tracePath);
		int discreteSamples = writeDiscrete(events, new File(outputDir, "discrete.f32"), seconds);
		int customSamples = writeCustom(events, new File(outputDir, "custom.f32"), seconds);
		int tmsSamples = writeTms(events, new File(outputDir, "tms.f32"), seconds);
		try (PrintWriter manifest = new PrintWriter(new File(outputDir, "manifest.csv"))) {
			manifest.println("tag,file,sample_rate,samples");
			manifest.println(":discrete,discrete.f32," + DISCRETE_RATE + "," + discreteSamples);
			manifest.println(":cust,custom.f32," + CUSTOM_RATE + "," + customSamples);
			manifest.println(":tms,tms.f32," + TMS_RATE + "," + tmsSamples);
		}
		if (verbose) {
			System.out.println(new File(outputDir, "manifest.csv"));
		}
	}

	private static int writeDiscrete(List<SoundMameTraceReplay.Event> events, File output,
			double seconds) throws IOException {
		Sound sound = new Sound(PcmSink.discarding());
		int[] latches = { 0, 0 };
		return writeSource(events, output, seconds, DISCRETE_RATE, latches,
				() -> (float) sound.stepDiscreteNodes(latches[0], latches[1]).node90);
	}

	private static int writeCustom(List<SoundMameTraceReplay.Event> events, File output,
			double seconds) throws IOException {
		Sound sound = new Sound(PcmSink.discarding());
		int[] latches = { 0, 0 };
		return writeSource(events, output, seconds, CUSTOM_RATE, latches,
				() -> (float) ((sound.noise(CUSTOM_RATE, latches[0]) / 2.0) / 32768.0));
	}

	private static int writeTms(List<SoundMameTraceReplay.Event> events, File output,
			double seconds) throws IOException {
		TMS36XX tms = new TMS36XX();
		int[] latches = { 0, 0 };
		return writeSource(events, output, seconds, TMS_RATE, latches, () -> {
			tms.mm6221aa_tune_w(SoundControlMapping.mm6221aaTune(latches[1]));
			return (float) tms.nextInternalSampleForTest();
		});
	}

	private static int writeSource(List<SoundMameTraceReplay.Event> events, File output,
			double seconds, int sampleRate, int[] latches, FloatSource source) throws IOException {
		int samples = (int) Math.round(seconds * sampleRate);
		int eventIndex = 0;
		try (Float32Writer writer = new Float32Writer(output)) {
			for (int sample = 0; sample < samples; sample++) {
				while (eventIndex < events.size()
						&& eventAppliesBeforeSample(events.get(eventIndex), sample, sampleRate)) {
					SoundMameTraceReplay.Event event = events.get(eventIndex++);
					latches[event.control == 'A' ? 0 : 1] = event.value;
				}
				writer.write(source.nextSample());
			}
		}
		return samples;
	}

	static boolean eventAppliesBeforeSample(
			SoundMameTraceReplay.Event event, int sample, int sampleRate) {
		return SoundMameTraceReplay.sampleIndex(event.timeSeconds, sampleRate) < sample;
	}

	private interface FloatSource {
		float nextSample();
	}

	private static final class Float32Writer implements AutoCloseable {
		private final BufferedOutputStream output;

		Float32Writer(File file) throws IOException {
			output = new BufferedOutputStream(new FileOutputStream(file), 65536);
		}

		void write(float value) throws IOException {
			int bits = Float.floatToRawIntBits(value);
			output.write(bits & 0xff);
			output.write((bits >>> 8) & 0xff);
			output.write((bits >>> 16) & 0xff);
			output.write((bits >>> 24) & 0xff);
		}

		@Override
		public void close() throws IOException {
			output.close();
		}
	}
}
