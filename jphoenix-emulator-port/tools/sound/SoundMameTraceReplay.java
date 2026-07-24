import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class SoundMameTraceReplay {
	private static final int FRAME_SAMPLES = SoundRenderUtil.SAMPLE_RATE / 60;

	public static void main(String[] args) throws Exception {
		if (args.length < 2 || args.length > 3) {
			throw new IllegalArgumentException(
					"Usage: java SoundMameTraceReplay <mame-events.csv> <output.wav> [seconds]");
		}
		double seconds = args.length == 3 ? Double.parseDouble(args[2]) : 30.0;
		byte[] pcm = replay(Path.of(args[0]), seconds);
		File output = new File(args[1]);
		File parent = output.getParentFile();
		if (parent != null && !parent.exists() && !parent.mkdirs()) {
			throw new IOException("Could not create " + parent);
		}
		SoundRenderUtil.writeWav(output, pcm);
		SoundRenderUtil.PcmStats stats = SoundRenderUtil.stats(pcm);
		System.out.printf(Locale.ROOT, "%s samples=%d peak=%d rms=%.6f clipped=%d%n",
				output, pcm.length / 2, stats.peak, stats.rms, stats.clippedSamples);
	}

	static byte[] replay(Path tracePath, double seconds) throws IOException {
		List<Event> events = readEvents(tracePath);
		int totalSamples = (int) Math.round(seconds * SoundRenderUtil.SAMPLE_RATE);
		int totalFrames = (totalSamples + FRAME_SAMPLES - 1) / FRAME_SAMPLES;
		ByteArrayOutputStream pcm = new ByteArrayOutputStream(totalFrames * SoundRenderUtil.FRAME_BYTES);
		Sound sound = new Sound(PcmSink.discarding());
		int eventIndex = 0;

		for (int frame = 0; frame < totalFrames; frame++) {
			int frameStart = frame * FRAME_SAMPLES;
			int frameEnd = frameStart + FRAME_SAMPLES;
			while (eventIndex < events.size()
					&& sampleIndex(events.get(eventIndex).timeSeconds, SoundRenderUtil.SAMPLE_RATE) < frameEnd) {
				Event event = events.get(eventIndex++);
				int eventSampleIndex = sampleIndex(event.timeSeconds, SoundRenderUtil.SAMPLE_RATE);
				if (eventSampleIndex >= frameStart && eventSampleIndex < totalSamples) {
					int sampleInFrame = eventSampleIndex - frameStart;
					if (event.control == 'A') {
						sound.updateControlA((byte) event.value, sampleInFrame, FRAME_SAMPLES);
					} else {
						sound.updateControlB((byte) event.value, sampleInFrame, FRAME_SAMPLES);
					}
				}
			}
			byte[] rendered = sound.renderFrameForTest();
			int remainingBytes = totalSamples * 2 - pcm.size();
			pcm.write(rendered, 0, Math.min(rendered.length, remainingBytes));
		}
		return pcm.toByteArray();
	}

	static List<Event> readEvents(Path tracePath) throws IOException {
		List<String> lines = Files.readAllLines(tracePath);
		if (lines.isEmpty() || !"time_seconds,control,value".equals(lines.get(0))) {
			throw new IllegalArgumentException("Unexpected MAME sound trace header: " + tracePath);
		}
		List<Event> events = new ArrayList<Event>();
		for (int line = 1; line < lines.size(); line++) {
			String[] fields = lines.get(line).split(",");
			if (fields.length != 3) {
				throw new IllegalArgumentException(tracePath + " line " + (line + 1)
						+ " must have three columns");
			}
			double time = Double.parseDouble(fields[0]);
			char control = fields[1].charAt(0);
			if (control != 'A' && control != 'B') {
				throw new IllegalArgumentException(tracePath + " line " + (line + 1)
						+ " has invalid control " + fields[1]);
			}
			int value = Integer.decode(fields[2]) & 0xff;
			events.add(new Event(time, control, value));
		}
		return events;
	}

	static int sampleIndex(double timeSeconds, int sampleRate) {
		return (int) Math.floor(timeSeconds * sampleRate);
	}

	static final class Event {
		final double timeSeconds;
		final char control;
		final int value;

		Event(double timeSeconds, char control, int value) {
			this.timeSeconds = timeSeconds;
			this.control = control;
			this.value = value;
		}
	}
}
