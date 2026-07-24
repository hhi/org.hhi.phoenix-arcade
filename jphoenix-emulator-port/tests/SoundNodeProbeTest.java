public class SoundNodeProbeTest {
	public static void main(String[] args) {
		assertCase("effect2", (byte) 0x28, (byte) 0x0f, true, false);
		assertCase("effect1", (byte) 0x0f, (byte) 0x18, false, true);
		assertCase("mixed", (byte) 0x28, (byte) 0x18, true, true);
	}

	private static void assertCase(String name, byte controlA, byte controlB,
			boolean expectEffect2, boolean expectEffect1) {
		Sound sound = new Sound(PcmSink.discarding());
		Sound.SoundNodes nodes = null;
		for (int i = 0; i < 120000 / 10; i++) {
			nodes = sound.stepDiscreteNodes(controlA & 0xff, controlB & 0xff);
		}
		if (nodes == null) {
			throw new AssertionError(name + " did not render nodes");
		}
		assertFinite(name + " node20", nodes.node20);
		assertFinite(name + " node21", nodes.node21);
		assertFinite(name + " node22", nodes.node22);
		assertFinite(name + " node25", nodes.node25);
		assertFinite(name + " node30", nodes.node30);
		assertFinite(name + " node31", nodes.node31);
		assertFinite(name + " node32", nodes.node32);
		assertFinite(name + " node33", nodes.node33);
		assertFinite(name + " node34", nodes.node34);
		assertFinite(name + " node35", nodes.node35);
		assertFinite(name + " node37", nodes.node37);
		assertFinite(name + " node38", nodes.node38);
		assertFinite(name + " node39", nodes.node39);
		assertFinite(name + " node40", nodes.node40);
		assertFinite(name + " node90", nodes.node90);
		if (expectEffect2 && Math.abs(nodes.effect2Sound) < 0.0001) {
			throw new AssertionError(name + " expected effect2 node activity");
		}
		if (expectEffect1 && Math.abs(nodes.effect1Sound) < 0.0001) {
			throw new AssertionError(name + " expected effect1 node activity");
		}
		if (Math.abs(nodes.node90) > 1.0) {
			throw new AssertionError(name + " node90 unexpectedly large: " + nodes.node90);
		}
	}

	private static void assertFinite(String name, double value) {
		if (Double.isNaN(value) || Double.isInfinite(value)) {
			throw new AssertionError(name + " is not finite: " + value);
		}
	}
}
