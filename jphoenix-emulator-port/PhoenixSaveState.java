import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.EOFException;
import java.io.IOException;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.zip.CRC32;

/**
 * Versioned, checksummed save-state container for the validated Phoenix ROM set.
 */
public final class PhoenixSaveState {
    public static final Path DEFAULT_PATH = Path.of("jphoenix.state");

    private static final long MAGIC = 0x4a50484f454e4958L; // "JPHOENIX"
    private static final int VERSION = 2;
    private static final int MAX_FILE_SIZE = 2 * 1024 * 1024;

    private PhoenixSaveState() {
    }

    static void save(Phoenix phoenix, Path path) throws IOException {
        byte[] encoded = encode(phoenix);
        Path target = path.toAbsolutePath().normalize();
        Path parent = target.getParent();
        if (parent == null) {
            throw new IOException("save-state path has no parent: " + path);
        }
        Files.createDirectories(parent);
        String prefix = target.getFileName().toString();
        while (prefix.length() < 3) {
            prefix += "_";
        }
        Path temporary = Files.createTempFile(parent, prefix, ".tmp");
        try {
            Files.write(temporary, encoded);
            try {
                Files.move(
                        temporary,
                        target,
                        StandardCopyOption.ATOMIC_MOVE,
                        StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException e) {
                Files.move(temporary, target, StandardCopyOption.REPLACE_EXISTING);
            }
        } finally {
            Files.deleteIfExists(temporary);
        }
    }

    static void load(Phoenix phoenix, Path path) throws IOException {
        Path source = path.toAbsolutePath().normalize();
        long size = Files.size(source);
        if (size <= 0 || size > MAX_FILE_SIZE) {
            throw new IOException("invalid save-state size: " + size + " bytes");
        }
        decode(phoenix, Files.readAllBytes(source));
    }

    static byte[] encode(Phoenix phoenix) throws IOException {
        ByteArrayOutputStream payloadBytes = new ByteArrayOutputStream();
        try (DataOutputStream payload = new DataOutputStream(payloadBytes)) {
            phoenix.writeState(payload);
        }
        byte[] body = payloadBytes.toByteArray();
        CRC32 crc = new CRC32();
        crc.update(body);

        ByteArrayOutputStream fileBytes = new ByteArrayOutputStream(body.length + 256);
        try (DataOutputStream output = new DataOutputStream(fileBytes)) {
            output.writeLong(MAGIC);
            output.writeInt(VERSION);
            output.writeUTF(RomLoader.PROGRAM.sha256);
            output.writeUTF(RomLoader.GRAPHICS.sha256);
            // Keep the two original IC hashes in version 2 save states so
            // existing states remain compatible with the combined proms.rom.
            output.writeUTF(RomLoader.PALETTE_LOW_SHA256);
            output.writeUTF(RomLoader.PALETTE_HIGH_SHA256);
            output.writeInt(body.length);
            output.writeLong(crc.getValue());
            output.write(body);
        }
        return fileBytes.toByteArray();
    }

    static void decode(Phoenix phoenix, byte[] encoded) throws IOException {
        if (encoded.length <= 0 || encoded.length > MAX_FILE_SIZE) {
            throw new IOException("invalid save-state size: " + encoded.length + " bytes");
        }
        try (DataInputStream input =
                new DataInputStream(new ByteArrayInputStream(encoded))) {
            if (input.readLong() != MAGIC) {
                throw new IOException("not a JPhoenix save state");
            }
            int version = input.readInt();
            if (version != VERSION) {
                throw new IOException(
                        "unsupported save-state version " + version
                                + " (expected " + VERSION + ")");
            }
            requireHash("program ROM", RomLoader.PROGRAM.sha256, input.readUTF());
            requireHash("graphics ROM", RomLoader.GRAPHICS.sha256, input.readUTF());
            requireHash("palette PROM IC40", RomLoader.PALETTE_LOW_SHA256, input.readUTF());
            requireHash("palette PROM IC41", RomLoader.PALETTE_HIGH_SHA256, input.readUTF());
            int payloadLength = input.readInt();
            long expectedCrc = input.readLong();
            if (payloadLength < 0 || payloadLength != input.available()) {
                throw new IOException("invalid save-state payload length");
            }
            byte[] payload = input.readNBytes(payloadLength);
            if (payload.length != payloadLength) {
                throw new EOFException("truncated save-state payload");
            }
            CRC32 crc = new CRC32();
            crc.update(payload);
            if (crc.getValue() != expectedCrc) {
                throw new IOException("save-state checksum mismatch");
            }

            try (DataInputStream state =
                    new DataInputStream(new ByteArrayInputStream(payload))) {
                phoenix.readState(state);
                if (state.available() != 0) {
                    throw new IOException("unexpected trailing save-state data");
                }
            }
        } catch (EOFException e) {
            throw new IOException("truncated save state", e);
        }
    }

    private static void requireHash(String label, String expected, String actual)
            throws IOException {
        if (!expected.equals(actual)) {
            throw new IOException(label + " does not match this save state");
        }
    }
}
