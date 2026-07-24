import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.Set;

public class SoundVerificationCoverageTest {
	public static void main(String[] args) throws IOException {
		Set<String> runnerTests = new HashSet<String>();
		for (String name : SoundVerificationTest.testClassNames()) {
			runnerTests.add(name);
		}

		try (var paths = Files.list(Path.of("tests"))) {
			for (Path path : paths.filter(p -> p.getFileName().toString().matches("Sound.*Test\\.java")).toList()) {
				String className = path.getFileName().toString().replace(".java", "");
				if ("SoundVerificationTest".equals(className)) {
					continue;
				}
				if (!runnerTests.contains(className)) {
					throw new AssertionError(className + " is not included in SoundVerificationTest");
				}
			}
		}
	}
}
