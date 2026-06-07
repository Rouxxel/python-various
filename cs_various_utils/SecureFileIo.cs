// NOTE: These helper files are intended to be copied into other projects.
// Change the namespace `cs_various_utils` below to match your project's namespace
// before integrating.
//
// Secure file I/O utility
//
// General-purpose, hardened helpers for reading and writing files by path.
//
// Features:
// - Optional allowed-root confinement (see SetAllowedRoot)
// - Atomic writes via temp file + replace
// - Configurable max-read-size guard (MaxReadBytes)
// - Per-path locking for serialized access
//
// Optional NuGet package (YAML helpers only):
// - YamlDotNet
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
// Change namespace based on whatever project is implemented
namespace cs_various_utils
{
    public class FileStoreError : Exception
    {
        public FileStoreError(string message) : base(message) { }
    }

    public class PathSecurityError : FileStoreError
    {
        public PathSecurityError(string message) : base(message) { }
    }

    public class FileTooLargeError : FileStoreError
    {
        public FileTooLargeError(string message) : base(message) { }
    }

    public static class SecureFileIo
    {
        private static readonly ConcurrentDictionary<string, object> PathLocks = new();
        private static readonly JsonSerializerOptions JsonOptions = new()
        {
            WriteIndented = true,
            Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
        };

        /// <summary>Maximum bytes any read helper will load into memory (50 MiB).</summary>
        public static int MaxReadBytes { get; set; } = 50 * 1024 * 1024;

        private static string? _allowedRoot;

        public static void SetAllowedRoot(
            string? root
            )
        {
            _allowedRoot = root == null ? null : Path.GetFullPath(root);
        }

        public static string? GetAllowedRoot() => _allowedRoot;

        // --- INTERNAL HELPERS ---

        private static string ResolvePath(
            string path
            )
        {
            var resolved = Path.GetFullPath(path);

            if (_allowedRoot != null)
            {
                var comparison = OperatingSystem.IsWindows()
                    ? StringComparison.OrdinalIgnoreCase
                    : StringComparison.Ordinal;

                var normalizedRoot = Path.GetFullPath(_allowedRoot);
                if (!resolved.Equals(normalizedRoot, comparison)
                    && !resolved.StartsWith(normalizedRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
                        + Path.DirectorySeparatorChar, comparison))
                {
                    throw new PathSecurityError(
                        $"Path '{resolved}' is outside the allowed root '{normalizedRoot}'."
                    );
                }
            }

            return resolved;
        }

        private static object GetLock(
            string path
            )
        {
            return PathLocks.GetOrAdd(path, _ => new object());
        }

        private static byte[] ReadBytesUnlocked(
            string path,
            int? maxBytes
            )
        {
            if (!File.Exists(path))
                throw new FileNotFoundException($"No such file: '{path}'");

            if (maxBytes != null)
            {
                var size = new FileInfo(path).Length;
                if (size > maxBytes.Value)
                {
                    throw new FileTooLargeError(
                        $"File '{path}' is {size} bytes, exceeds limit of {maxBytes.Value}."
                    );
                }
            }

            using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
            if (maxBytes == null)
            {
                using var ms = new MemoryStream();
                stream.CopyTo(ms);
                return ms.ToArray();
            }

            var buffer = new byte[maxBytes.Value + 1];
            var totalRead = 0;
            int read;
            while (totalRead < buffer.Length
                && (read = stream.Read(buffer, totalRead, buffer.Length - totalRead)) > 0)
            {
                totalRead += read;
            }

            if (totalRead > maxBytes.Value)
            {
                throw new FileTooLargeError(
                    $"File '{path}' exceeds the read limit of {maxBytes.Value} bytes."
                );
            }

            if (totalRead == buffer.Length)
                return buffer;

            return buffer[..totalRead];
        }

        private static void AtomicWriteUnlocked(
            string path,
            byte[] data
            )
        {
            var directory = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(directory))
                Directory.CreateDirectory(directory);

            var fileName = Path.GetFileName(path);
            var tmpPath = Path.Combine(
                directory ?? ".",
                $".{fileName}.{Guid.NewGuid():N}.tmp"
            );

            try
            {
                using (var stream = new FileStream(tmpPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                {
                    stream.Write(data, 0, data.Length);
                    stream.Flush(true);
                }

                if (File.Exists(path))
                    File.Replace(tmpPath, path, null);
                else
                    File.Move(tmpPath, path);
            }
            finally
            {
                if (File.Exists(tmpPath))
                {
                    try { File.Delete(tmpPath); } catch { /* best effort */ }
                }
            }
        }

        // ---------------------------------------------------------------------------
        // Primitives: bytes & text
        // ---------------------------------------------------------------------------

        public static byte[] ReadBytes(
            string path,
            int? maxBytes = null
            )
        {
            maxBytes ??= MaxReadBytes;
            var resolved = ResolvePath(path);
            lock (GetLock(resolved))
                return ReadBytesUnlocked(resolved, maxBytes);
        }

        public static void WriteBytes(
            string path,
            byte[] data
            )
        {
            var resolved = ResolvePath(path);
            lock (GetLock(resolved))
                AtomicWriteUnlocked(resolved, data);
        }

        public static string ReadText(
            string path,
            string encoding = "utf-8",
            int? maxBytes = null
            )
        {
            return Encoding.GetEncoding(encoding).GetString(ReadBytes(path, maxBytes));
        }

        public static void WriteText(
            string path,
            string text,
            string encoding = "utf-8"
            )
        {
            WriteBytes(path, Encoding.GetEncoding(encoding).GetBytes(text));
        }

        // ---------------------------------------------------------------------------
        // JSON
        // ---------------------------------------------------------------------------

        public static T ReadJson<T>(
            string path,
            T? defaultValue = default,
            bool throwIfMissing = true,
            string encoding = "utf-8",
            int? maxBytes = null
            )
        {
            var resolved = ResolvePath(path);
            lock (GetLock(resolved))
            {
                if (!File.Exists(resolved))
                {
                    if (throwIfMissing)
                        throw new FileNotFoundException($"No such file: '{resolved}'");
                    return defaultValue!;
                }

                var raw = ReadBytesUnlocked(resolved, maxBytes ?? MaxReadBytes);
                return JsonSerializer.Deserialize<T>(Encoding.GetEncoding(encoding).GetString(raw), JsonOptions)!;
            }
        }

        public static void WriteJson(
            string path,
            object data,
            int indent = 2,
            bool sortKeys = false,
            string encoding = "utf-8"
            )
        {
            var options = new JsonSerializerOptions(JsonOptions)
            {
                WriteIndented = indent > 0
            };

            if (sortKeys)
                options.TypeInfoResolver = null; // caller can plug source-gen if needed

            var text = JsonSerializer.Serialize(data, options);
            WriteText(path, text, encoding);
        }

        // ---------------------------------------------------------------------------
        // CSV  (returns / accepts list of row dicts)
        // ---------------------------------------------------------------------------

        public static List<Dictionary<string, string>> ReadCsv(
            string path,
            string encoding = "utf-8",
            int? maxBytes = null,
            char delimiter = ','
            )
        {
            var text = ReadText(path, encoding, maxBytes);
            var rows = new List<Dictionary<string, string>>();
            using var reader = new StringReader(text);
            var headerLine = reader.ReadLine();
            if (headerLine == null)
                return rows;

            var headers = ParseCsvLine(headerLine, delimiter);
            string? line;
            while ((line = reader.ReadLine()) != null)
            {
                if (string.IsNullOrWhiteSpace(line))
                    continue;

                var values = ParseCsvLine(line, delimiter);
                var row = new Dictionary<string, string>(StringComparer.Ordinal);
                for (var i = 0; i < headers.Count; i++)
                {
                    row[headers[i]] = i < values.Count ? values[i] : string.Empty;
                }
                rows.Add(row);
            }

            return rows;
        }

        public static void WriteCsv(
            string path,
            IReadOnlyList<Dictionary<string, string>> rows,
            IReadOnlyList<string>? fieldnames = null,
            string encoding = "utf-8",
            char delimiter = ','
            )
        {
            var columns = fieldnames?.ToList() ?? DeriveFieldnames(rows);
            var buffer = new StringBuilder();
            buffer.AppendLine(string.Join(delimiter, columns.Select(EscapeCsvField)));

            foreach (var row in rows)
            {
                var values = columns.Select(col => EscapeCsvField(row.TryGetValue(col, out var value) ? value : string.Empty));
                buffer.AppendLine(string.Join(delimiter, values));
            }

            WriteText(path, buffer.ToString(), encoding);
        }

        private static List<string> DeriveFieldnames(
            IReadOnlyList<Dictionary<string, string>> rows
            )
        {
            var fieldnames = new List<string>();
            var seen = new HashSet<string>(StringComparer.Ordinal);
            foreach (var row in rows)
            {
                foreach (var key in row.Keys)
                {
                    if (seen.Add(key))
                        fieldnames.Add(key);
                }
            }
            return fieldnames;
        }

        private static List<string> ParseCsvLine(
            string line,
            char delimiter
            )
        {
            var fields = new List<string>();
            var current = new StringBuilder();
            var inQuotes = false;

            for (var i = 0; i < line.Length; i++)
            {
                var ch = line[i];
                if (inQuotes)
                {
                    if (ch == '"')
                    {
                        if (i + 1 < line.Length && line[i + 1] == '"')
                        {
                            current.Append('"');
                            i++;
                        }
                        else
                        {
                            inQuotes = false;
                        }
                    }
                    else
                    {
                        current.Append(ch);
                    }
                }
                else if (ch == '"')
                {
                    inQuotes = true;
                }
                else if (ch == delimiter)
                {
                    fields.Add(current.ToString());
                    current.Clear();
                }
                else
                {
                    current.Append(ch);
                }
            }

            fields.Add(current.ToString());
            return fields;
        }

        private static string EscapeCsvField(
            string field
            )
        {
            if (field.Contains('"') || field.Contains(',') || field.Contains('\n') || field.Contains('\r'))
                return $"\"{field.Replace("\"", "\"\"")}\"";
            return field;
        }

        // ---------------------------------------------------------------------------
        // YAML  (requires YamlDotNet; uses safe load/dump semantics)
        // ---------------------------------------------------------------------------

        private static void RequireYaml()
        {
            var yamlType = Type.GetType("YamlDotNet.Serialization.DeserializerBuilder, YamlDotNet");
            if (yamlType == null)
            {
                throw new FileStoreError(
                    "YamlDotNet is not installed. Add the 'YamlDotNet' package " +
                    "to use ReadYaml / WriteYaml."
                );
            }
        }

        public static T ReadYaml<T>(
            string path,
            T? defaultValue = default,
            bool throwIfMissing = true,
            string encoding = "utf-8",
            int? maxBytes = null
            )
        {
            RequireYaml();
            var resolved = ResolvePath(path);
            lock (GetLock(resolved))
            {
                if (!File.Exists(resolved))
                {
                    if (throwIfMissing)
                        throw new FileNotFoundException($"No such file: '{resolved}'");
                    return defaultValue!;
                }

                var raw = ReadBytesUnlocked(resolved, maxBytes ?? MaxReadBytes);
                var text = Encoding.GetEncoding(encoding).GetString(raw);
                return DeserializeYaml<T>(text);
            }
        }

        public static void WriteYaml(
            string path,
            object data,
            string encoding = "utf-8"
            )
        {
            RequireYaml();
            var text = SerializeYaml(data);
            WriteText(path, text, encoding);
        }

        private static T DeserializeYaml<T>(
            string text
            )
        {
            var builderType = Type.GetType("YamlDotNet.Serialization.DeserializerBuilder, YamlDotNet")
                ?? throw new FileStoreError("YamlDotNet is not installed.");
            var builder = Activator.CreateInstance(builderType)!;
            var buildMethod = builderType.GetMethod("Build")!;
            var deserializer = buildMethod.Invoke(builder, null)!;
            var deserializeMethod = deserializer.GetType().GetMethod("Deserialize", new[] { typeof(string) })!;
            return (T)deserializeMethod.Invoke(deserializer, new object[] { text })!;
        }

        private static string SerializeYaml(
            object data
            )
        {
            var builderType = Type.GetType("YamlDotNet.Serialization.SerializerBuilder, YamlDotNet")
                ?? throw new FileStoreError("YamlDotNet is not installed.");
            var builder = Activator.CreateInstance(builderType)!;

            var configureMethod = builderType.GetMethod("ConfigureDefaultValuesHandling");
            if (configureMethod != null)
            {
                var handlingType = Type.GetType("YamlDotNet.Serialization.DefaultValuesHandling, YamlDotNet");
                if (handlingType != null)
                {
                    var omitNull = Enum.Parse(handlingType, "OmitNull");
                    builder = configureMethod.Invoke(builder, new[] { omitNull })!;
                }
            }

            var buildMethod = builder.GetType().GetMethod("Build")!;
            var serializer = buildMethod.Invoke(builder, null)!;
            var serializeMethod = serializer.GetType().GetMethod("Serialize", new[] { typeof(object) })!;
            return (string)serializeMethod.Invoke(serializer, new[] { data })!;
        }

        // ---------------------------------------------------------------------------
        // Record helpers - treat a JSON file as a list of dict "collection"
        // ---------------------------------------------------------------------------

        private static List<Dictionary<string, JsonElement>> LoadRecords(
            string path,
            int? maxBytes
            )
        {
            if (!File.Exists(path))
                return new List<Dictionary<string, JsonElement>>();

            var raw = ReadBytesUnlocked(path, maxBytes ?? MaxReadBytes);
            using var document = JsonDocument.Parse(Encoding.UTF8.GetString(raw));
            if (document.RootElement.ValueKind != JsonValueKind.Array)
            {
                throw new FileStoreError(
                    $"Record helpers expect a JSON array at '{path}', got {document.RootElement.ValueKind}."
                );
            }

            var records = new List<Dictionary<string, JsonElement>>();
            foreach (var element in document.RootElement.EnumerateArray())
            {
                if (element.ValueKind != JsonValueKind.Object)
                {
                    throw new FileStoreError(
                        $"Record helpers expect JSON objects in the array at '{path}'."
                    );
                }

                var record = new Dictionary<string, JsonElement>(StringComparer.Ordinal);
                foreach (var property in element.EnumerateObject())
                    record[property.Name] = property.Value.Clone();
                records.Add(record);
            }

            return records;
        }

        private static void SaveRecordsUnlocked(
            string path,
            List<Dictionary<string, JsonElement>> data
            )
        {
            var json = JsonSerializer.Serialize(data, JsonOptions);
            AtomicWriteUnlocked(path, Encoding.UTF8.GetBytes(json));
        }

        public static List<Dictionary<string, JsonElement>> ReadAll(
            string path,
            int? maxBytes = null
            )
        {
            var resolved = ResolvePath(path);
            lock (GetLock(resolved))
                return LoadRecords(resolved, maxBytes);
        }

        public static void SaveAll(
            string path,
            List<Dictionary<string, JsonElement>> data
            )
        {
            WriteJson(path, data);
        }

        public static Dictionary<string, JsonElement>? FindById(
            string path,
            object recordId,
            string idField = "id"
            )
        {
            foreach (var record in ReadAll(path))
            {
                if (RecordFieldEquals(record, idField, recordId))
                    return record;
            }
            return null;
        }

        public static List<Dictionary<string, JsonElement>> FindByField(
            string path,
            string field,
            object value
            )
        {
            return ReadAll(path)
                .Where(record => RecordFieldEquals(record, field, value))
                .ToList();
        }

        public static Dictionary<string, JsonElement> CreateRecord(
            string path,
            Dictionary<string, JsonElement> record
            )
        {
            var resolved = ResolvePath(path);
            lock (GetLock(resolved))
            {
                var data = LoadRecords(resolved, MaxReadBytes);
                data.Add(record);
                SaveRecordsUnlocked(resolved, data);
            }
            return record;
        }

        public static Dictionary<string, JsonElement> UpdateRecord(
            string path,
            object recordId,
            Dictionary<string, JsonElement> updates,
            string idField = "id"
            )
        {
            var resolved = ResolvePath(path);
            lock (GetLock(resolved))
            {
                var data = LoadRecords(resolved, MaxReadBytes);
                Dictionary<string, JsonElement>? updatedRecord = null;

                foreach (var record in data)
                {
                    if (RecordFieldEquals(record, idField, recordId))
                    {
                        foreach (var (key, value) in updates)
                            record[key] = value;
                        updatedRecord = record;
                        break;
                    }
                }

                if (updatedRecord == null)
                {
                    throw new ArgumentException(
                        $"Record with {idField}='{recordId}' not found in '{resolved}'."
                    );
                }

                SaveRecordsUnlocked(resolved, data);
                return updatedRecord;
            }
        }

        public static Dictionary<string, JsonElement> DeleteRecord(
            string path,
            object recordId,
            string idField = "id"
            )
        {
            var resolved = ResolvePath(path);
            lock (GetLock(resolved))
            {
                var data = LoadRecords(resolved, MaxReadBytes);
                Dictionary<string, JsonElement>? deletedRecord = null;
                var remaining = new List<Dictionary<string, JsonElement>>();

                foreach (var record in data)
                {
                    if (deletedRecord == null && RecordFieldEquals(record, idField, recordId))
                        deletedRecord = record;
                    else
                        remaining.Add(record);
                }

                if (deletedRecord == null)
                {
                    throw new ArgumentException(
                        $"Record with {idField}='{recordId}' not found in '{resolved}'."
                    );
                }

                SaveRecordsUnlocked(resolved, remaining);
                return deletedRecord;
            }
        }

        private static bool RecordFieldEquals(
            Dictionary<string, JsonElement> record,
            string field,
            object value
            )
        {
            if (!record.TryGetValue(field, out var element))
                return false;

            return element.ValueKind switch
            {
                JsonValueKind.String => element.GetString() == Convert.ToString(value, CultureInfo.InvariantCulture),
                JsonValueKind.Number when value is IConvertible convertible =>
                    element.TryGetInt64(out var longValue) && longValue == convertible.ToInt64(CultureInfo.InvariantCulture),
                JsonValueKind.True => value is true,
                JsonValueKind.False => value is false,
                JsonValueKind.Null => value == null,
                _ => element.ToString() == Convert.ToString(value, CultureInfo.InvariantCulture)
            };
        }
    }
}
