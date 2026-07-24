import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.util.zip.CRC32;

public class SoundArtifactDump {
	private static final int NODE_SAMPLES = 1200;
	private static final NodeCase[] NODE_CASES = {
			new NodeCase("nodes_effect2_bird_hit.csv", 0x28, 0x0f),
			new NodeCase("nodes_effect1_shield_explosion.csv", 0x0f, 0x18),
			new NodeCase("nodes_effect1_filtered.csv", 0x0f, 0x38),
			new NodeCase("nodes_mixed_effects.csv", 0x28, 0x18)
	};

	public static void main(String[] args) throws Exception {
		File outDir = new File(args.length == 0 ? "sound-renders" : args[0]);
		writeArtifacts(outDir, true);
	}

	static void writeArtifacts(File outDir, boolean verbose) throws Exception {
		if (!outDir.exists() && !outDir.mkdirs()) {
			throw new IOException("Could not create " + outDir);
		}

		SoundRenderDump.writeDumps(outDir, verbose);
		for (NodeCase nodeCase : NODE_CASES) {
			File file = new File(outDir, nodeCase.fileName);
			SoundNodeDump.writeDump(file, nodeCase.controlA, nodeCase.controlB, NODE_SAMPLES);
			if (verbose) {
				System.out.println(file.getPath()
						+ " controlA=0x" + Integer.toHexString(nodeCase.controlA)
						+ " controlB=0x" + Integer.toHexString(nodeCase.controlB)
						+ " samples=" + NODE_SAMPLES);
			}
		}
		writeManifest(outDir);
		if (verbose) {
			System.out.println(new File(outDir, "manifest.csv").getPath());
		}
	}

	private static void writeManifest(File outDir) throws IOException {
		String[] files = {
				"metrics.csv",
				"effect2_bird_hit.wav",
				"effect1_shield_explosion.wav",
				"effect1_filtered.wav",
				"noise_control.wav",
				"music_tune.wav",
				"nodes_effect2_bird_hit.csv",
				"nodes_effect1_shield_explosion.csv",
				"nodes_effect1_filtered.csv",
				"nodes_mixed_effects.csv"
		};
		try (PrintWriter out = new PrintWriter(new File(outDir, "manifest.csv"))) {
			out.println("file,size_bytes,crc32");
			for (String fileName : files) {
				File file = new File(outDir, fileName);
				byte[] bytes = Files.readAllBytes(file.toPath());
				CRC32 crc = new CRC32();
				crc.update(bytes, 0, bytes.length);
				out.println(fileName + "," + bytes.length + "," + crc.getValue());
			}
		}
	}

	private static final class NodeCase {
		final String fileName;
		final int controlA;
		final int controlB;

		NodeCase(String fileName, int controlA, int controlB) {
			this.fileName = fileName;
			this.controlA = controlA;
			this.controlB = controlB;
		}
	}
}
