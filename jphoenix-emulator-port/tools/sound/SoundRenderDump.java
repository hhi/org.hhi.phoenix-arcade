import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Locale;

public class SoundRenderDump {
	private static final RenderCase[] CASES = {
			new RenderCase("effect2_bird_hit.wav", (byte) 0x28, (byte) 0x0f, 120),
			new RenderCase("effect1_shield_explosion.wav", (byte) 0x0f, (byte) 0x18, 120),
			new RenderCase("effect1_filtered.wav", (byte) 0x0f, (byte) 0x38, 120),
			new RenderCase("noise_control.wav", (byte) 0xcf, (byte) 0x0f, 120),
			new RenderCase("music_tune.wav", (byte) 0x0f, (byte) 0x8f, 240)
	};

	public static void main(String[] args) throws Exception {
		File outDir = new File(args.length == 0 ? "sound-renders" : args[0]);
		writeDumps(outDir, true);
	}

	static void writeDumps(File outDir, boolean verbose) throws IOException {
		if (!outDir.exists() && !outDir.mkdirs()) {
			throw new IOException("Could not create " + outDir);
		}

		try (PrintWriter metrics = new PrintWriter(new File(outDir, "metrics.csv"))) {
			metrics.println("file,duration_seconds,peak,rms,clipped_samples");
			for (RenderCase renderCase : CASES) {
				writeCase(outDir, renderCase, metrics, verbose);
			}
		}
	}

	private static void writeCase(File outDir, RenderCase renderCase, PrintWriter metrics)
			throws IOException {
		writeCase(outDir, renderCase, metrics, true);
	}

	private static void writeCase(File outDir, RenderCase renderCase, PrintWriter metrics, boolean verbose)
			throws IOException {
		Sound sound = new Sound(PcmSink.discarding());
		sound.updateControlA((byte) 0x0f, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		sound.updateControlB((byte) 0x0f, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		SoundRenderUtil.renderFrames(sound, 6);

		sound.updateControlA(renderCase.controlA, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		sound.updateControlB(renderCase.controlB, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		byte[] pcm = SoundRenderUtil.renderFrames(sound, renderCase.frames);
		File file = new File(outDir, renderCase.fileName);
		SoundRenderUtil.writeWav(file, pcm);
		SoundRenderUtil.PcmStats stats = SoundRenderUtil.stats(pcm);
		double duration = pcm.length / (double) (SoundRenderUtil.SAMPLE_RATE * 2);
		if (verbose) {
			System.out.println(file.getPath()
					+ " duration=" + String.format(Locale.ROOT, "%.3fs", duration)
					+ " peak=" + stats.peak
					+ " rms=" + String.format(Locale.ROOT, "%.2f", stats.rms)
					+ " clipped=" + stats.clippedSamples);
		}
		metrics.println(renderCase.fileName
				+ "," + String.format(Locale.ROOT, "%.6f", duration)
				+ "," + stats.peak
				+ "," + String.format(Locale.ROOT, "%.6f", stats.rms)
				+ "," + stats.clippedSamples);
	}

	private static final class RenderCase {
		final String fileName;
		final byte controlA;
		final byte controlB;
		final int frames;

		RenderCase(String fileName, byte controlA, byte controlB, int frames) {
			this.fileName = fileName;
			this.controlA = controlA;
			this.controlB = controlB;
			this.frames = frames;
		}
	}
}
