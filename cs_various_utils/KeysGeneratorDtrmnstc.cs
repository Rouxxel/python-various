// NOTE: These helper files are intended to be copied into other projects.
// Change the namespace `cs_various_utils` below to match your project's namespace
// before integrating.
//
// Deterministic Ed25519 key generator (passphrase + PBKDF2 salt).
//
// Derives a reproducible Ed25519 key pair from a passphrase using PBKDF2-HMAC-SHA256.
// Unlike KeysGenerator.cs (random RSA via OS CSPRNG), the same passphrase + salt +
// KDF parameters always produce the same key pair. Salt and KDF settings are written
// to key_derivation.json so keys can be reproduced later.
//
// Dependencies:
//   - .NET 8+ (PBKDF2 via Rfc2898DeriveBytes, PKCS#8 / SPKI builders)
//   - NuGet package BouncyCastle.Cryptography (Ed25519 public key derivation from seed)
//
// NOTE: Ed25519 keys are not compatible with RSA-OAEP utilities that expect the
// random RSA keys produced by KeysGenerator.cs.
//
// HOW TO TEST (standalone)
//   dotnet new console -n KeysGenTest && cd KeysGenTest
//   dotnet add package BouncyCastle.Cryptography
//   copy KeysGeneratorDtrmnstc.cs into the project and adjust namespace / add Program.cs:
//       KeysGeneratorDtrmnstc.Main(args);
//   dotnet run -- -p "pass" -s "salt" -o ./keys

using System.Formats.Asn1;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Org.BouncyCastle.Crypto.Parameters;

namespace cs_various_utils
{
    public static class KeysGeneratorDtrmnstc
    {
        public const int DefaultIterations = 200_000;
        public const string DefaultMetadataName = "key_derivation.json";
        public const string DefaultPrivateName = "private_key.pem";
        public const string DefaultPublicName = "public_key.pem";

        public sealed record GenerationResult(
            string PrivatePath,
            string PublicPath,
            string MetadataPath,
            byte[] Salt,
            int Iterations);

        public static byte[] DeriveSeed(byte[] passphrase, byte[] salt, int iterations)
        {
            if (passphrase.Length == 0)
                throw new ArgumentException("Passphrase must not be empty.");
            if (salt.Length == 0)
                throw new ArgumentException("Salt must not be empty.");
            if (iterations < 1)
                throw new ArgumentException("PBKDF2 iterations must be at least 1.");

            return Rfc2898DeriveBytes.Pbkdf2(
                passphrase,
                salt,
                iterations,
                HashAlgorithmName.SHA256,
                32);
        }

        public static byte[] DeriveEd25519PublicKeyBytes(byte[] seed)
        {
            return new Ed25519PrivateKeyParameters(seed, 0).GeneratePublicKey().GetEncoded();
        }

        public static byte[] BuildEd25519PrivateKeyPkcs8(ReadOnlySpan<byte> seed)
        {
            if (seed.Length != 32)
                throw new ArgumentException("Ed25519 seed must be 32 bytes.");

            var inner = new AsnWriter(AsnEncodingRules.DER);
            inner.WriteOctetString(seed);
            var innerBytes = inner.Encode();

            var writer = new AsnWriter(AsnEncodingRules.DER);
            writer.PushSequence();
            writer.WriteInteger(0);
            writer.PushSequence();
            writer.WriteObjectIdentifier("1.3.101.112");
            writer.PopSequence();
            writer.WriteOctetString(innerBytes);
            writer.PopSequence();
            return writer.Encode();
        }

        public static byte[] BuildEd25519SubjectPublicKeyInfo(byte[] rawPublicKey)
        {
            if (rawPublicKey.Length != 32)
                throw new ArgumentException("Ed25519 public key must be 32 bytes.");

            var writer = new AsnWriter(AsnEncodingRules.DER);
            writer.PushSequence();
            writer.PushSequence();
            writer.WriteObjectIdentifier("1.3.101.112");
            writer.PopSequence();
            writer.WriteBitString(rawPublicKey);
            writer.PopSequence();
            return writer.Encode();
        }

        public static GenerationResult GenerateDeterministicKeys(
            byte[] passphrase,
            string outputDir,
            byte[]? salt = null,
            int iterations = DefaultIterations,
            string privateName = DefaultPrivateName,
            string publicName = DefaultPublicName,
            string metadataName = DefaultMetadataName)
        {
            ValidateOutputPath(outputDir);
            ValidateOutputPath(privateName);
            ValidateOutputPath(publicName);
            ValidateOutputPath(metadataName);

            Directory.CreateDirectory(outputDir);

            var usedSalt = salt ?? RandomSalt(16);
            var seed = DeriveSeed(passphrase, usedSalt, iterations);
            var privateDer = BuildEd25519PrivateKeyPkcs8(seed);
            var publicDer = BuildEd25519SubjectPublicKeyInfo(DeriveEd25519PublicKeyBytes(seed));

            var privatePath = Path.Combine(outputDir, privateName);
            var publicPath = Path.Combine(outputDir, publicName);
            var metadataPath = Path.Combine(outputDir, metadataName);

            File.WriteAllText(privatePath, PemEncode("PRIVATE KEY", privateDer));
            File.WriteAllText(publicPath, PemEncode("PUBLIC KEY", publicDer));
            WriteMetadata(metadataPath, usedSalt, iterations, privateName, publicName);

            return new GenerationResult(privatePath, publicPath, metadataPath, usedSalt, iterations);
        }

        public static byte[] ParseSalt(string value)
        {
            if (string.IsNullOrEmpty(value))
                throw new ArgumentException("Salt must not be empty.");
            if (value.StartsWith("b64:", StringComparison.Ordinal))
                return Convert.FromBase64String(value[4..]);
            return Encoding.UTF8.GetBytes(value);
        }

        public static int RunCli(string[] args)
        {
            string? passphrase = null;
            string? saltValue = null;
            var outputDir = ".";
            var iterations = DefaultIterations;
            var privateName = DefaultPrivateName;
            var publicName = DefaultPublicName;
            var metadataName = DefaultMetadataName;

            for (var i = 0; i < args.Length; i++)
            {
                var arg = args[i];
                switch (arg)
                {
                    case "-h":
                    case "--help":
                        PrintUsage();
                        return 0;
                    case "-p":
                    case "--passphrase":
                        passphrase = RequireValue(args, ref i, arg);
                        break;
                    case "-s":
                    case "--salt":
                        saltValue = RequireValue(args, ref i, arg);
                        break;
                    case "-o":
                    case "--output-dir":
                        outputDir = RequireValue(args, ref i, arg);
                        break;
                    case "--iterations":
                        iterations = int.Parse(RequireValue(args, ref i, arg));
                        break;
                    case "--private-name":
                        privateName = RequireValue(args, ref i, arg);
                        break;
                    case "--public-name":
                        publicName = RequireValue(args, ref i, arg);
                        break;
                    case "--metadata-name":
                        metadataName = RequireValue(args, ref i, arg);
                        break;
                    default:
                        Console.Error.WriteLine($"Unknown argument: {arg}");
                        PrintUsage();
                        return 1;
                }
            }

            if (string.IsNullOrEmpty(passphrase))
            {
                Console.Write("Passphrase: ");
                var first = Console.ReadLine();
                Console.Write("Confirm passphrase: ");
                var second = Console.ReadLine();
                if (!string.Equals(first, second, StringComparison.Ordinal))
                {
                    Console.Error.WriteLine("Error: passphrases do not match.");
                    return 1;
                }
                passphrase = first;
            }

            if (string.IsNullOrEmpty(passphrase))
            {
                Console.Error.WriteLine("Error: passphrase must not be empty.");
                return 1;
            }

            try
            {
                var salt = saltValue != null ? ParseSalt(saltValue) : null;
                var result = GenerateDeterministicKeys(
                    Encoding.UTF8.GetBytes(passphrase),
                    outputDir,
                    salt,
                    iterations,
                    privateName,
                    publicName,
                    metadataName);

                Console.WriteLine("Deterministic Ed25519 keys generated successfully!");
                Console.WriteLine($"Private key: {result.PrivatePath}");
                Console.WriteLine($"Public key:  {result.PublicPath}");
                Console.WriteLine($"Metadata:    {result.MetadataPath}");
                if (saltValue == null)
                {
                    Console.WriteLine(
                        "A random salt was generated and saved in the metadata file. "
                        + "Keep that file to reproduce the same keys later.");
                }
                return 0;
            }
            catch (Exception ex) when (ex is ArgumentException or FormatException)
            {
                Console.Error.WriteLine($"Error: {ex.Message}");
                return 1;
            }
        }

        public static void Main(string[] args)
        {
            Environment.Exit(RunCli(args));
        }

        private static void WriteMetadata(
            string metadataPath,
            byte[] salt,
            int iterations,
            string privateName,
            string publicName)
        {
            var metadata = new
            {
                algorithm = "Ed25519",
                kdf = "PBKDF2-HMAC-SHA256",
                iterations,
                salt_b64 = Convert.ToBase64String(salt),
                private_key_file = privateName,
                public_key_file = publicName
            };

            var json = JsonSerializer.Serialize(metadata, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(metadataPath, json + Environment.NewLine);
        }

        private static byte[] RandomSalt(int size)
        {
            var salt = new byte[size];
            RandomNumberGenerator.Fill(salt);
            return salt;
        }

        private static void ValidateOutputPath(string path)
        {
            if (string.IsNullOrWhiteSpace(path) || path.Contains(".."))
                throw new ArgumentException($"Invalid file path: {path}");
        }

        private static string RequireValue(string[] args, ref int index, string flag)
        {
            if (++index >= args.Length)
                throw new ArgumentException($"Missing value for {flag}");
            return args[index];
        }

        private static void PrintUsage()
        {
            Console.WriteLine("Usage: KeysGeneratorDtrmnstc [-p passphrase] [-s salt] [-o outputDir]");
            Console.WriteLine("       [--iterations N] [--private-name NAME] [--public-name NAME]");
            Console.WriteLine("       [--metadata-name NAME]");
            Console.WriteLine();
            Console.WriteLine("  -s salt     Plain text or b64:<base64>. Random if omitted.");
            Console.WriteLine("  -o dir      Output directory (default: current directory).");
        }

        private static string PemEncode(string label, byte[] der)
        {
            var b64 = Convert.ToBase64String(der);
            var sb = new StringBuilder();
            sb.AppendLine($"-----BEGIN {label}-----");
            for (var pos = 0; pos < b64.Length; pos += 64)
            {
                var take = Math.Min(64, b64.Length - pos);
                sb.AppendLine(b64.Substring(pos, take));
            }
            sb.AppendLine($"-----END {label}-----");
            return sb.ToString();
        }
    }
}
