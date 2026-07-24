import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class SoundSourceAuditTest {
	private static final List<String> FORBIDDEN_RUNTIME_TOKENS = List.of(
			"DesktopAudioClip",
			"AudioClip",
			"newAudioClip",
			"javax.sound.sampled.Clip",
			".au\"",
			"phoenix.effects",
			"effects.gain",
			"effects.pitch",
			"effects.balance",
			"discreteStepAccumulator",
			"tone1_vco",
			"tone2_vco");

	public static void main(String[] args) throws IOException {
		try (var paths = Files.list(Path.of("."))) {
			for (Path path : paths.filter(p -> p.toString().endsWith(".java")).toList()) {
				if (path.getFileName().toString().equals("SoundSourceAuditTest.java")) {
					continue;
				}
				String source = Files.readString(path);
				for (String token : FORBIDDEN_RUNTIME_TOKENS) {
					if (source.contains(token)) {
						throw new AssertionError(path + " still references legacy sample token: " + token);
					}
				}
			}
		}
		String soundCore = Files.readString(Path.of("Sound.java"));
		if (soundCore.contains("javax.sound") || soundCore.contains("JavaSoundPcmSink")) {
			throw new AssertionError("Sound.java must remain independent of Java Sound");
		}
	}
}
