import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.net.URISyntaxException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public final class RomLoader {
    public static final Spec PROGRAM = new Spec(
            "program.rom",
            0x4000,
            "261cddb2f0ef45248f976d56f810e3b6a5e71284ba57dbeade31aae562728e2e");
    public static final Spec GRAPHICS = new Spec(
            "graphics.rom",
            0x2000,
            "e11168866950870074e7a5f9bcb749dedd2c89f8c8643c174710b73d21a96545");
    public static final Spec PALETTE = new Spec(
            "proms.rom",
            0x0200,
            "4dc21d169eb6f344e1af22ecb2cfe6423fd5e14b4a5f2df2e2e188d26a062b37");
    static final String PALETTE_LOW_SHA256 =
            "a562286665950882048a03994f78ab5b6f472e9405a8302f1833f3655877ea1e";
    static final String PALETTE_HIGH_SHA256 =
            "88e0c79c0c59e1724d8de46833422938ee630a34150418f02f28e15482bc4c3d";

    private RomLoader() {
    }

    public static byte[] load(URL baseUrl, Spec spec) throws IOException {
        try (InputStream input = open(baseUrl, spec.fileName)) {
            byte[] bytes = input.readAllBytes();
            validate(spec, bytes);
            return bytes;
        }
    }

    static void validate(Spec spec, byte[] bytes) throws IOException {
        if (bytes.length != spec.size) {
            throw new IOException(
                    spec.fileName + " has wrong size: expected " + spec.size
                            + " bytes, got " + bytes.length);
        }

        String actualHash = sha256(bytes);
        if (!spec.sha256.equals(actualHash)) {
            throw new IOException(
                    spec.fileName + " SHA-256 mismatch: expected " + spec.sha256
                            + ", got " + actualHash);
        }
    }

    private static InputStream open(URL baseUrl, String fileName) throws IOException {
        if (baseUrl != null) {
            try {
                return baseUrl.toURI().resolve(fileName).toURL().openStream();
            } catch (URISyntaxException e) {
                throw new IOException("Invalid ROM base URL: " + baseUrl, e);
            }
        }
        return new FileInputStream(new File(fileName));
    }

    private static String sha256(byte[] bytes) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(bytes);
            StringBuilder result = new StringBuilder(hash.length * 2);
            for (byte value : hash) {
                result.append(String.format("%02x", value & 0xff));
            }
            return result.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 is unavailable", e);
        }
    }

    public static final class Spec {
        final String fileName;
        final int size;
        final String sha256;

        Spec(String fileName, int size, String sha256) {
            this.fileName = fileName;
            this.size = size;
            this.sha256 = sha256;
        }
    }
}
