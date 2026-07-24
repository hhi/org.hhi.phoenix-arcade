public class SoundRenderSmokeTest {
	public static void main(String[] args) {
		Sound sound = new Sound(PcmSink.discarding());

		byte[] silentFrame = sound.renderFrameForTest();
		if (silentFrame.length != SoundRenderUtil.FRAME_BYTES) {
			throw new AssertionError("Expected one 48 kHz / 60 Hz frame");
		}

		sound.updateControlA((byte) 0x0f, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		sound.updateControlB((byte) 0x18, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		byte[] activeFrame = sound.renderFrameForTest();
		if (activeFrame.length != SoundRenderUtil.FRAME_BYTES) {
			throw new AssertionError("Expected stable frame length after sound events");
		}

		boolean hasSignal = false;
		for (int i = 0; i < activeFrame.length; i += 2) {
			int sample = (activeFrame[i] & 0xff) | (activeFrame[i + 1] << 8);
			if (sample != 0) {
				hasSignal = true;
				break;
			}
		}
		if (!hasSignal) {
			throw new AssertionError("Expected non-zero rendered sound after latch events");
		}

		assertEffectSignal("effect2 bird/hit path", (byte) 0x28, (byte) 0x0f);
		assertEffectSignal("effect1 shield/explosion path", (byte) 0x0f, (byte) 0x18);
		assertEffectSignal("effect1 filtered path", (byte) 0x0f, (byte) 0x38);
		assertEffectSignal("noise control path", (byte) 0xcf, (byte) 0x0f);
		assertEffectSignal("music tune path", (byte) 0x0f, (byte) 0x8f);
		assertMidFrameEventTiming();
		assertLateFrameEventTiming();
		assertSameFrameEventOrdering();
		assertSameSampleLastWriteWins();
		assertOutOfOrderEventsRenderChronologically();
	}

	private static void assertEffectSignal(String name, byte controlA, byte controlB) {
		Sound sound = new Sound(PcmSink.discarding());
		sound.updateControlA(controlA, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		sound.updateControlB(controlB, 0, SoundRenderUtil.CYCLES_PER_FRAME);
		byte[] frames = SoundRenderUtil.renderFrames(sound, 12);

		SoundRenderUtil.PcmStats stats = SoundRenderUtil.stats(frames);
		if (stats.peak == 0 || stats.rms < 1.0) {
			throw new AssertionError(name + " produced silence");
		}
		if (stats.clippedSamples != 0) {
			throw new AssertionError(name + " clipped " + stats.clippedSamples + " samples");
		}
	}

	private static void assertMidFrameEventTiming() {
		Sound sound = new Sound(PcmSink.discarding());
		int cyclesPerFrame = SoundRenderUtil.CYCLES_PER_FRAME;
		sound.updateControlA((byte) 0x0f, 0, cyclesPerFrame);
		sound.updateControlB((byte) 0x0f, 0, cyclesPerFrame);
		SoundRenderUtil.renderFrames(sound, 6);

		sound.updateControlB((byte) 0x8f, cyclesPerFrame * 3 / 4, cyclesPerFrame);
		byte[] frame = sound.renderFrameForTest();

		SoundRenderUtil.PcmStats firstHalf = SoundRenderUtil.stats(frame, 0, frame.length / 2);
		SoundRenderUtil.PcmStats secondHalf = SoundRenderUtil.stats(frame, frame.length / 2, frame.length / 2);
		if (firstHalf.peak != 0) {
			throw new AssertionError("Mid-frame event leaked into first half of frame");
		}
		if (secondHalf.peak == 0 || secondHalf.rms < 1.0) {
			throw new AssertionError("Mid-frame event did not render in second half of frame");
		}
	}

	private static void assertLateFrameEventTiming() {
		Sound sound = new Sound(PcmSink.discarding());
		int cyclesPerFrame = SoundRenderUtil.CYCLES_PER_FRAME;
		sound.updateControlA((byte) 0x0f, 0, cyclesPerFrame);
		sound.updateControlB((byte) 0x0f, 0, cyclesPerFrame);
		SoundRenderUtil.renderFrames(sound, 6);

		sound.updateControlB((byte) 0x8f, cyclesPerFrame * 7 / 8, cyclesPerFrame);
		byte[] frame = sound.renderFrameForTest();

		SoundRenderUtil.PcmStats firstThreeQuarters = SoundRenderUtil.stats(frame, 0, frame.length * 3 / 4);
		SoundRenderUtil.PcmStats finalQuarter = SoundRenderUtil.stats(frame, frame.length * 3 / 4, frame.length / 4);
		if (firstThreeQuarters.peak != 0) {
			throw new AssertionError("Late-frame event leaked before final quarter");
		}
		if (finalQuarter.peak == 0 || finalQuarter.rms < 1.0) {
			throw new AssertionError("Late-frame event did not render in final quarter");
		}
	}

	private static void assertSameFrameEventOrdering() {
		Sound sound = new Sound(PcmSink.discarding());
		int cyclesPerFrame = SoundRenderUtil.CYCLES_PER_FRAME;
		sound.updateControlA((byte) 0x0f, 0, cyclesPerFrame);
		sound.updateControlB((byte) 0x0f, 0, cyclesPerFrame);
		SoundRenderUtil.renderFrames(sound, 6);

		sound.updateControlB((byte) 0x8f, cyclesPerFrame / 4, cyclesPerFrame);
		sound.updateControlB((byte) 0x0f, cyclesPerFrame * 3 / 4, cyclesPerFrame);
		byte[] frame = sound.renderFrameForTest();

		SoundRenderUtil.PcmStats firstQuarter = SoundRenderUtil.stats(frame, 0, frame.length / 4);
		SoundRenderUtil.PcmStats middleHalf = SoundRenderUtil.stats(frame, frame.length / 4, frame.length / 2);
		int resamplerTailBytes = 16 * 2;
		int settledOffset = frame.length * 3 / 4 + resamplerTailBytes;
		SoundRenderUtil.PcmStats settledFinalQuarter = SoundRenderUtil.stats(
				frame, settledOffset, frame.length - settledOffset);
		if (firstQuarter.peak != 0) {
			throw new AssertionError("Same-frame on event leaked before its sample position");
		}
		if (middleHalf.peak == 0 || middleHalf.rms < 1.0) {
			throw new AssertionError("Same-frame on event did not render between writes");
		}
		if (settledFinalQuarter.peak != 0) {
			throw new AssertionError("Same-frame off event did not stop after MAME resampler tail");
		}
	}

	private static void assertSameSampleLastWriteWins() {
		Sound sound = new Sound(PcmSink.discarding());
		int cyclesPerFrame = SoundRenderUtil.CYCLES_PER_FRAME;
		sound.updateControlA((byte) 0x0f, 0, cyclesPerFrame);
		sound.updateControlB((byte) 0x0f, 0, cyclesPerFrame);
		SoundRenderUtil.renderFrames(sound, 6);

		int eventCycle = cyclesPerFrame / 2;
		sound.updateControlB((byte) 0x8f, eventCycle, cyclesPerFrame);
		sound.updateControlB((byte) 0x0f, eventCycle, cyclesPerFrame);
		byte[] frame = sound.renderFrameForTest();
		SoundRenderUtil.PcmStats stats = SoundRenderUtil.stats(frame);
		if (stats.peak != 0) {
			throw new AssertionError("Same-sample last write did not win");
		}
	}

	private static void assertOutOfOrderEventsRenderChronologically() {
		Sound sound = new Sound(PcmSink.discarding());
		int cyclesPerFrame = SoundRenderUtil.CYCLES_PER_FRAME;
		sound.updateControlA((byte) 0x0f, 0, cyclesPerFrame);
		sound.updateControlB((byte) 0x0f, 0, cyclesPerFrame);
		SoundRenderUtil.renderFrames(sound, 6);

		sound.updateControlB((byte) 0x8f, cyclesPerFrame * 7 / 8, cyclesPerFrame);
		sound.updateControlB((byte) 0x0f, cyclesPerFrame / 4, cyclesPerFrame);
		byte[] frame = sound.renderFrameForTest();

		SoundRenderUtil.PcmStats firstThreeQuarters = SoundRenderUtil.stats(frame, 0, frame.length * 3 / 4);
		SoundRenderUtil.PcmStats finalQuarter = SoundRenderUtil.stats(frame, frame.length * 3 / 4, frame.length / 4);
		if (firstThreeQuarters.peak != 0) {
			throw new AssertionError("Out-of-order earlier off event was not applied first");
		}
		if (finalQuarter.peak == 0 || finalQuarter.rms < 1.0) {
			throw new AssertionError("Out-of-order later on event did not render last");
		}
	}
}
