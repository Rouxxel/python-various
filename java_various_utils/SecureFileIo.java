// NOTE: These helper files are intended to be copied into other projects.
// Change the package `java_various_utils` below to match your project's package
// before integrating.
//
// Secure file I/O utility
//
// General-purpose, hardened helpers for reading and writing files by path.
//
// Why not just use Files.read/Files.write directly everywhere?
//   * No path safety  -> a path built from user input ("../../etc/passwd") or a
//     malicious symlink can read/clobber files outside your project.
//   * No crash safety  -> a plain truncating write that fails mid-way leaves the
//     file half-written / corrupt.
//   * No size guard    -> reading a huge/malicious file can exhaust memory.
//   * No concurrency    -> two threads writing the same file race.
//
// This module addresses all four:
//   * Optional allowed-root confinement (see setAllowedRoot). When set, every
//     resolved path must live inside that root; ".." traversal and symlinks
//     escaping the root are rejected.
//   * Atomic writes: data is written to a temp file in the same directory, then
//     moved over the target (ATOMIC_MOVE when the platform supports it). Readers
//     never see a partial file.
//   * A configurable max-read-size guard (maxReadBytes).
//   * A per-path lock so reads/writes of the same file are serialized; the
//     record helpers hold the lock for the whole read-modify-write transaction.
//
// Layers:
//   Primitives : readBytes / writeBytes / readText / writeText   (pure JDK)
//   CSV        : readCsv / writeCsv                                (pure JDK)
//   JSON       : readJson / writeJson                             (needs Jackson)
//   YAML       : readYaml / writeYaml                             (needs Jackson YAML)
//   Records    : readAll / saveAll / findById / findByField /
//                createRecord / updateRecord / deleteRecord       (needs Jackson)
//
// Optional dependencies (only for the JSON/YAML/record helpers):
// - Jackson databind   (Maven: com.fasterxml.jackson.core:jackson-databind)
// - Jackson YAML       (Maven: com.fasterxml.jackson.dataformat:jackson-dataformat-yaml)
//   The primitives and CSV helpers work with zero external dependencies.
//
// HOW TO TEST (standalone, primitives/CSV only - no Jackson needed)
//   javac SecureFileIo.java   # JSON/YAML/record methods need Jackson on the classpath
//   java java_various_utils.SecureFileIo

// Change package based on whatever project is implemented
package java_various_utils;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLMapper;

public final class SecureFileIo {

    // --- EXCEPTIONS ---
    public static class FileStoreError extends RuntimeException {
        public FileStoreError(String message) { super(message); }
    }

    public static class PathSecurityError extends FileStoreError {
        public PathSecurityError(String message) { super(message); }
    }

    public static class FileTooLargeError extends FileStoreError {
        public FileTooLargeError(String message) { super(message); }
    }

    // --- CONFIGURATION ---
    /** Maximum bytes any read helper will load into memory (50 MiB default). */
    public static long maxReadBytes = 50L * 1024 * 1024;

    // When not null, every path is resolved and required to live inside this root.
    private static Path allowedRoot;

    // Per-path locks - created on first access, keyed by the resolved path string.
    private static final ConcurrentHashMap<String, Lock> LOCKS = new ConcurrentHashMap<>();

    // Lazily created JSON/YAML mappers (only touched by the JSON/YAML helpers).
    private static volatile ObjectMapper jsonMapper;
    private static volatile YAMLMapper yamlMapper;

    private SecureFileIo() { }

    // --- CONFIG HELPERS ---
    public static void setAllowedRoot(String root) {
        allowedRoot = (root == null) ? null : Paths.get(root).toAbsolutePath().normalize();
    }

    public static Path getAllowedRoot() {
        return allowedRoot;
    }

    // --- INTERNAL HELPERS ---
    private static Path resolvePath(String path) {
        Path resolved;
        try {
            // toRealPath resolves symlinks when the file exists; fall back to normalize otherwise.
            Path candidate = Paths.get(path).toAbsolutePath();
            resolved = Files.exists(candidate) ? candidate.toRealPath() : candidate.normalize();
        } catch (IOException e) {
            resolved = Paths.get(path).toAbsolutePath().normalize();
        }

        if (allowedRoot != null && !resolved.startsWith(allowedRoot)) {
            throw new PathSecurityError(
                    "Path '" + resolved + "' is outside the allowed root '" + allowedRoot + "'.");
        }
        return resolved;
    }

    private static Lock getLock(Path path) {
        return LOCKS.computeIfAbsent(path.toString(), k -> new ReentrantLock());
    }

    private static byte[] readBytesUnlocked(Path path, Long maxBytes) throws IOException {
        if (!Files.isRegularFile(path)) {
            throw new FileStoreError("No such file: '" + path + "'");
        }
        if (maxBytes != null) {
            long size = Files.size(path);
            if (size > maxBytes) {
                throw new FileTooLargeError(
                        "File '" + path + "' is " + size + " bytes, exceeds limit of " + maxBytes + ".");
            }
        }
        byte[] data = Files.readAllBytes(path);
        if (maxBytes != null && data.length > maxBytes) {
            throw new FileTooLargeError(
                    "File '" + path + "' exceeds the read limit of " + maxBytes + " bytes.");
        }
        return data;
    }

    private static void atomicWriteUnlocked(Path path, byte[] data) throws IOException {
        Path parent = path.getParent();
        if (parent != null) Files.createDirectories(parent);

        Path tmp = (parent != null ? parent : Paths.get("."))
                .resolve("." + path.getFileName() + "." + UUID.randomUUID().toString().replace("-", "") + ".tmp");
        try {
            Files.write(tmp, data);
            try {
                Files.move(tmp, path, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
            } catch (java.nio.file.AtomicMoveNotSupportedException e) {
                Files.move(tmp, path, StandardCopyOption.REPLACE_EXISTING);
            }
        } finally {
            Files.deleteIfExists(tmp);
        }
    }

    // ---------------------------------------------------------------------------
    // Primitives: bytes & text
    // ---------------------------------------------------------------------------
    public static byte[] readBytes(String path) {
        return readBytes(path, maxReadBytes);
    }

    public static byte[] readBytes(String path, Long maxBytes) {
        Path resolved = resolvePath(path);
        Lock lock = getLock(resolved);
        lock.lock();
        try {
            return readBytesUnlocked(resolved, maxBytes);
        } catch (IOException e) {
            throw new FileStoreError("Failed to read '" + resolved + "': " + e.getMessage());
        } finally {
            lock.unlock();
        }
    }

    public static void writeBytes(String path, byte[] data) {
        Path resolved = resolvePath(path);
        Lock lock = getLock(resolved);
        lock.lock();
        try {
            atomicWriteUnlocked(resolved, data);
        } catch (IOException e) {
            throw new FileStoreError("Failed to write '" + resolved + "': " + e.getMessage());
        } finally {
            lock.unlock();
        }
    }

    public static String readText(String path) {
        return readText(path, StandardCharsets.UTF_8, maxReadBytes);
    }

    public static String readText(String path, Charset encoding, Long maxBytes) {
        return new String(readBytes(path, maxBytes), encoding);
    }

    public static void writeText(String path, String text) {
        writeText(path, text, StandardCharsets.UTF_8);
    }

    public static void writeText(String path, String text, Charset encoding) {
        writeBytes(path, text.getBytes(encoding));
    }

    // ---------------------------------------------------------------------------
    // JSON  (requires Jackson databind)
    // ---------------------------------------------------------------------------
    private static ObjectMapper json() {
        if (jsonMapper == null) {
            synchronized (SecureFileIo.class) {
                if (jsonMapper == null) jsonMapper = new ObjectMapper();
            }
        }
        return jsonMapper;
    }

    /**
     * Read and parse a JSON file into a generic structure (Map/List/primitives).
     *
     * @param throwIfMissing when true, a missing file throws; when false, returns defaultValue.
     */
    public static Object readJson(String path, Object defaultValue, boolean throwIfMissing) {
        Path resolved = resolvePath(path);
        Lock lock = getLock(resolved);
        lock.lock();
        try {
            if (!Files.isRegularFile(resolved)) {
                if (throwIfMissing) throw new FileStoreError("No such file: '" + resolved + "'");
                return defaultValue;
            }
            byte[] raw = readBytesUnlocked(resolved, maxReadBytes);
            return json().readValue(raw, Object.class);
        } catch (IOException e) {
            throw new FileStoreError("Failed to read JSON '" + resolved + "': " + e.getMessage());
        } finally {
            lock.unlock();
        }
    }

    public static void writeJson(String path, Object data) {
        try {
            String text = json().writerWithDefaultPrettyPrinter().writeValueAsString(data);
            writeText(path, text);
        } catch (IOException e) {
            throw new FileStoreError("Failed to serialize JSON: " + e.getMessage());
        }
    }

    // ---------------------------------------------------------------------------
    // CSV  (returns / accepts list of row maps; pure JDK)
    // ---------------------------------------------------------------------------
    public static List<Map<String, String>> readCsv(String path) {
        return readCsv(path, ',');
    }

    public static List<Map<String, String>> readCsv(String path, char delimiter) {
        String text = readText(path);
        List<Map<String, String>> rows = new ArrayList<>();
        List<List<String>> records = parseCsv(text, delimiter);
        if (records.isEmpty()) return rows;

        List<String> headers = records.get(0);
        for (int r = 1; r < records.size(); r++) {
            List<String> values = records.get(r);
            Map<String, String> row = new LinkedHashMap<>();
            for (int i = 0; i < headers.size(); i++) {
                row.put(headers.get(i), i < values.size() ? values.get(i) : "");
            }
            rows.add(row);
        }
        return rows;
    }

    public static void writeCsv(String path, List<Map<String, String>> rows) {
        writeCsv(path, rows, null, ',');
    }

    public static void writeCsv(String path, List<Map<String, String>> rows,
                                List<String> fieldnames, char delimiter) {
        List<String> columns = (fieldnames != null) ? fieldnames : deriveFieldnames(rows);
        StringBuilder sb = new StringBuilder();
        sb.append(joinCsv(columns, delimiter)).append("\n");
        for (Map<String, String> row : rows) {
            List<String> values = new ArrayList<>();
            for (String col : columns) {
                values.add(row.getOrDefault(col, ""));
            }
            sb.append(joinCsv(values, delimiter)).append("\n");
        }
        writeText(path, sb.toString());
    }

    private static List<String> deriveFieldnames(List<Map<String, String>> rows) {
        Set<String> seen = new LinkedHashSet<>();
        for (Map<String, String> row : rows) {
            seen.addAll(row.keySet());
        }
        return new ArrayList<>(seen);
    }

    private static String joinCsv(List<String> fields, char delimiter) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < fields.size(); i++) {
            if (i > 0) sb.append(delimiter);
            sb.append(escapeCsvField(fields.get(i), delimiter));
        }
        return sb.toString();
    }

    private static String escapeCsvField(String field, char delimiter) {
        if (field == null) field = "";
        if (field.indexOf('"') >= 0 || field.indexOf(delimiter) >= 0
                || field.indexOf('\n') >= 0 || field.indexOf('\r') >= 0) {
            return "\"" + field.replace("\"", "\"\"") + "\"";
        }
        return field;
    }

    // Minimal RFC-4180-ish CSV parser supporting quoted fields and embedded newlines.
    private static List<List<String>> parseCsv(String text, char delimiter) {
        List<List<String>> records = new ArrayList<>();
        List<String> current = new ArrayList<>();
        StringBuilder field = new StringBuilder();
        boolean inQuotes = false;

        for (int i = 0; i < text.length(); i++) {
            char ch = text.charAt(i);
            if (inQuotes) {
                if (ch == '"') {
                    if (i + 1 < text.length() && text.charAt(i + 1) == '"') {
                        field.append('"');
                        i++;
                    } else {
                        inQuotes = false;
                    }
                } else {
                    field.append(ch);
                }
            } else if (ch == '"') {
                inQuotes = true;
            } else if (ch == delimiter) {
                current.add(field.toString());
                field.setLength(0);
            } else if (ch == '\n' || ch == '\r') {
                if (ch == '\r' && i + 1 < text.length() && text.charAt(i + 1) == '\n') {
                    i++; // swallow CRLF
                }
                current.add(field.toString());
                field.setLength(0);
                records.add(current);
                current = new ArrayList<>();
            } else {
                field.append(ch);
            }
        }
        // flush trailing field/record if any content remains
        if (field.length() > 0 || !current.isEmpty()) {
            current.add(field.toString());
            records.add(current);
        }
        return records;
    }

    // ---------------------------------------------------------------------------
    // YAML  (requires Jackson YAML; safe by default)
    // ---------------------------------------------------------------------------
    private static YAMLMapper yaml() {
        if (yamlMapper == null) {
            synchronized (SecureFileIo.class) {
                if (yamlMapper == null) yamlMapper = new YAMLMapper();
            }
        }
        return yamlMapper;
    }

    public static Object readYaml(String path, Object defaultValue, boolean throwIfMissing) {
        Path resolved = resolvePath(path);
        Lock lock = getLock(resolved);
        lock.lock();
        try {
            if (!Files.isRegularFile(resolved)) {
                if (throwIfMissing) throw new FileStoreError("No such file: '" + resolved + "'");
                return defaultValue;
            }
            byte[] raw = readBytesUnlocked(resolved, maxReadBytes);
            return yaml().readValue(raw, Object.class);
        } catch (IOException e) {
            throw new FileStoreError("Failed to read YAML '" + resolved + "': " + e.getMessage());
        } finally {
            lock.unlock();
        }
    }

    public static void writeYaml(String path, Object data) {
        try {
            String text = yaml().writeValueAsString(data);
            writeText(path, text);
        } catch (IOException e) {
            throw new FileStoreError("Failed to serialize YAML: " + e.getMessage());
        }
    }

    // ---------------------------------------------------------------------------
    // Record helpers - treat a JSON file as a List<Map<String,Object>> "collection"
    // ---------------------------------------------------------------------------
    @SuppressWarnings("unchecked")
    private static List<Map<String, Object>> loadRecords(Path path) throws IOException {
        if (!Files.isRegularFile(path)) {
            return new ArrayList<>();
        }
        byte[] raw = readBytesUnlocked(path, maxReadBytes);
        Object parsed = json().readValue(raw, Object.class);
        if (!(parsed instanceof List)) {
            throw new FileStoreError(
                    "Record helpers expect a JSON array at '" + path + "', got "
                            + parsed.getClass().getSimpleName() + ".");
        }
        return (List<Map<String, Object>>) parsed;
    }

    private static void saveRecordsUnlocked(Path path, List<Map<String, Object>> data) throws IOException {
        String text = json().writerWithDefaultPrettyPrinter().writeValueAsString(data);
        atomicWriteUnlocked(path, text.getBytes(StandardCharsets.UTF_8));
    }

    public static List<Map<String, Object>> readAll(String path) {
        Path resolved = resolvePath(path);
        Lock lock = getLock(resolved);
        lock.lock();
        try {
            return loadRecords(resolved);
        } catch (IOException e) {
            throw new FileStoreError("Failed to read records '" + resolved + "': " + e.getMessage());
        } finally {
            lock.unlock();
        }
    }

    public static void saveAll(String path, List<Map<String, Object>> data) {
        writeJson(path, data);
    }

    public static Map<String, Object> findById(String path, Object recordId) {
        return findById(path, recordId, "id");
    }

    public static Map<String, Object> findById(String path, Object recordId, String idField) {
        for (Map<String, Object> record : readAll(path)) {
            if (equalsValue(record.get(idField), recordId)) {
                return record;
            }
        }
        return null;
    }

    public static List<Map<String, Object>> findByField(String path, String field, Object value) {
        List<Map<String, Object>> matches = new ArrayList<>();
        for (Map<String, Object> record : readAll(path)) {
            if (equalsValue(record.get(field), value)) {
                matches.add(record);
            }
        }
        return matches;
    }

    public static Map<String, Object> createRecord(String path, Map<String, Object> record) {
        Path resolved = resolvePath(path);
        Lock lock = getLock(resolved);
        lock.lock();
        try {
            List<Map<String, Object>> data = loadRecords(resolved);
            data.add(record);
            saveRecordsUnlocked(resolved, data);
            return record;
        } catch (IOException e) {
            throw new FileStoreError("Failed to create record in '" + resolved + "': " + e.getMessage());
        } finally {
            lock.unlock();
        }
    }

    public static Map<String, Object> updateRecord(String path, Object recordId,
                                                   Map<String, Object> updates, String idField) {
        Path resolved = resolvePath(path);
        Lock lock = getLock(resolved);
        lock.lock();
        try {
            List<Map<String, Object>> data = loadRecords(resolved);
            Map<String, Object> updated = null;
            for (Map<String, Object> record : data) {
                if (equalsValue(record.get(idField), recordId)) {
                    record.putAll(updates);
                    updated = record;
                    break;
                }
            }
            if (updated == null) {
                throw new IllegalArgumentException(
                        "Record with " + idField + "='" + recordId + "' not found in '" + resolved + "'.");
            }
            saveRecordsUnlocked(resolved, data);
            return updated;
        } catch (IOException e) {
            throw new FileStoreError("Failed to update record in '" + resolved + "': " + e.getMessage());
        } finally {
            lock.unlock();
        }
    }

    public static Map<String, Object> deleteRecord(String path, Object recordId, String idField) {
        Path resolved = resolvePath(path);
        Lock lock = getLock(resolved);
        lock.lock();
        try {
            List<Map<String, Object>> data = loadRecords(resolved);
            Map<String, Object> deleted = null;
            List<Map<String, Object>> remaining = new ArrayList<>();
            for (Map<String, Object> record : data) {
                if (deleted == null && equalsValue(record.get(idField), recordId)) {
                    deleted = record;
                } else {
                    remaining.add(record);
                }
            }
            if (deleted == null) {
                throw new IllegalArgumentException(
                        "Record with " + idField + "='" + recordId + "' not found in '" + resolved + "'.");
            }
            saveRecordsUnlocked(resolved, remaining);
            return deleted;
        } catch (IOException e) {
            throw new FileStoreError("Failed to delete record in '" + resolved + "': " + e.getMessage());
        } finally {
            lock.unlock();
        }
    }

    // Compares record values to query values across the loose numeric typing JSON uses.
    private static boolean equalsValue(Object a, Object b) {
        if (a == null || b == null) return a == b;
        if (a.equals(b)) return true;
        if (a instanceof Number && b instanceof Number) {
            return ((Number) a).doubleValue() == ((Number) b).doubleValue();
        }
        return a.toString().equals(b.toString());
    }

    // Example usage:
    //   import java_various_utils.SecureFileIo;
    //
    //   // (Optional) confine ALL access to a trusted directory - blocks ../ escapes:
    //   SecureFileIo.setAllowedRoot("src/resources");
    //
    //   String text = SecureFileIo.readText("src/resources/notes.md");
    //   SecureFileIo.writeText("src/resources/notes.md", "hello");
    //   List<Map<String,String>> rows = SecureFileIo.readCsv("src/resources/users.csv");
    //
    //   // JSON / records (needs Jackson):
    //   String users = "src/resources/users.json";
    //   Map<String,Object> ada = new LinkedHashMap<>();
    //   ada.put("id", "u1"); ada.put("name", "Ada");
    //   SecureFileIo.createRecord(users, ada);
    //   SecureFileIo.updateRecord(users, "u1", Map.of("name", "Ada Lovelace"), "id");
    //   Map<String,Object> found = SecureFileIo.findById(users, "u1");
    //   SecureFileIo.deleteRecord(users, "u1", "id");

    // Standalone smoke test (primitives + CSV only - no Jackson required).
    public static void main(String[] args) {
        String dir = "secure_file_io_test";
        String txt = dir + "/notes.txt";
        writeText(txt, "Hello, atomic world!");
        System.out.println("readText -> " + readText(txt));

        String csv = dir + "/rows.csv";
        Map<String, String> r1 = new LinkedHashMap<>();
        r1.put("id", "1");
        r1.put("name", "Ada, \"the\" pioneer");
        Map<String, String> r2 = new LinkedHashMap<>();
        r2.put("id", "2");
        r2.put("name", "Alan");
        List<Map<String, String>> rows = new ArrayList<>();
        rows.add(r1);
        rows.add(r2);
        writeCsv(csv, rows);
        System.out.println("readCsv -> " + readCsv(csv));
    }
}
