import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.stream.Stream;

public final class PhoenixCoverageRunner {
    private static final int DEFAULT_PASSIVE_FRAMES = 3600;
    private static final int DEFAULT_TAIL_FRAMES = 600;

    private PhoenixCoverageRunner() {
    }

    public static void main(String[] args) throws Exception {
        Path scriptRoot = args.length > 0
                ? Path.of(args[0])
                : Path.of("../c-phoenix/context/input-scripts");
        Path outputDir = args.length > 1
                ? Path.of(args[1])
                : Path.of("build/pc-coverage");
        int fixedFrames = args.length > 2 ? Integer.parseInt(args[2]) : 0;

        Path relativeRoot = Files.isRegularFile(scriptRoot) ? scriptRoot.getParent() : scriptRoot;
        if (relativeRoot == null) {
            relativeRoot = Path.of("");
        }
        List<Path> scripts = findScripts(scriptRoot, relativeRoot);
        if (scripts.isEmpty()) {
            throw new IOException("No input scripts found in " + scriptRoot);
        }

        System.setProperty("phoenix.fast", "true");
        String romDirProperty = System.getProperty("phoenix.romdir");
        File romDir = romDirProperty != null ? new File(romDirProperty) : new File(".");
        URL baseURL = romDir.getCanonicalFile().toURI().toURL();
        for (Path script : scripts) {
            int frames = fixedFrames > 0
                    ? fixedFrames
                    : framesForScript(script);
            Path relativeOutput = coverageOutputPath(relativeRoot.relativize(script));
            Path output = outputDir.resolve(relativeOutput);
            runScript(baseURL, script, output, frames);
        }
    }

    private static List<Path> findScripts(Path scriptRoot, Path relativeRoot) throws IOException {
        if (Files.isRegularFile(scriptRoot)) {
            if (!scriptRoot.getFileName().toString().endsWith(".txt")) {
                return List.of();
            }
            return List.of(scriptRoot);
        }
        try (Stream<Path> stream = Files.walk(scriptRoot)) {
            return stream
                    .filter(Files::isRegularFile)
                    .filter(path -> path.getFileName().toString().endsWith(".txt"))
                    .sorted(Comparator.comparing(path -> relativeRoot.relativize(path).toString()))
                    .toList();
        }
    }

    private static void runScript(URL baseURL, Path script, Path output, int frames) throws IOException {
        System.setProperty("phoenix.inputscript", script.toString());
        System.setProperty("phoenix.pccoverage", output.toString());
        System.setProperty("phoenix.stopframes", Integer.toString(frames));

        Phoenix phoenix = new Phoenix(PcmSink.discarding());
        try {
            phoenix.loadRom(baseURL);
            phoenix.execute();
        } finally {
            phoenix.stop();
            System.clearProperty("phoenix.inputscript");
            System.clearProperty("phoenix.pccoverage");
            System.clearProperty("phoenix.stopframes");
        }
        System.out.println(script.getFileName() + " -> " + output + " (" + frames + " frames)");
    }

    private static int framesForScript(Path script) throws IOException {
        int maxFrame = 0;
        for (String line : Files.readAllLines(script)) {
            String trimmed = line.trim();
            if (trimmed.isEmpty() || trimmed.startsWith("#")) {
                continue;
            }
            String[] parts = trimmed.split("\\s+");
            try {
                maxFrame = Math.max(maxFrame, Integer.parseInt(parts[0]));
            } catch (NumberFormatException ignored) {
            }
        }
        if (maxFrame == 0) {
            return DEFAULT_PASSIVE_FRAMES;
        }
        return maxFrame + DEFAULT_TAIL_FRAMES;
    }

    private static Path coverageOutputPath(Path relativeScript) {
        Path parent = relativeScript.getParent();
        String outputName = stripExtension(relativeScript.getFileName().toString()) + ".pc-coverage.csv";
        return parent == null ? Path.of(outputName) : parent.resolve(outputName);
    }

    private static String stripExtension(String fileName) {
        int dot = fileName.lastIndexOf('.');
        String base = dot < 0 ? fileName : fileName.substring(0, dot);
        return base.toLowerCase(Locale.ROOT);
    }
}
