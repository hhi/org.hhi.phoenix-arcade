import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class SoundArtifactManifestTest {
	private static final List<String> EXPECTED_LINES = List.of(
			"file,size_bytes,crc32",
			"metrics.csv,291,1146406951",
			"effect2_bird_hit.wav,192044,4226295044",
			"effect1_shield_explosion.wav,192044,3174689833",
			"effect1_filtered.wav,192044,2504423522",
			"noise_control.wav,192044,668477744",
			"music_tune.wav,384044,1869629502",
			"nodes_effect2_bird_hit.csv,311599,3283733182",
			"nodes_effect1_shield_explosion.csv,311484,1286413018",
			"nodes_effect1_filtered.csv,311052,4026353117",
			"nodes_mixed_effects.csv,311367,2359521915");

	public static void main(String[] args) throws Exception {
		Path outDir = Files.createTempDirectory("phoenix-artifacts-");
		SoundArtifactDump.writeArtifacts(outDir.toFile(), false);
		List<String> lines = Files.readAllLines(outDir.resolve("manifest.csv"));
		if (!EXPECTED_LINES.equals(lines)) {
			throw new AssertionError("Unexpected artifact manifest:\n" + String.join("\n", lines));
		}
	}
}
