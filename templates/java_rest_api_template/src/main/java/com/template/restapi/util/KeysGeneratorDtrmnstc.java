/**
 * #############################################################################
 * ### Deterministic Ed25519 key generator (passphrase + KDF)
 * ###
 * ### @file KeysGeneratorDtrmnstc.java
 * ### @author Sebastian Russo
 * ### @date 2026
 * #############################################################################
 *
 * Derives a reproducible Ed25519 key pair from a passphrase using PBKDF2-HMAC-SHA256.
 *
 * Unlike KeysGenerator.java (random RSA via OS CSPRNG), the same passphrase + salt +
 * KDF parameters always produce the same key pair. Salt and KDF settings are written
 * to key_derivation.json so keys can be reproduced later.
 *
 * Dependencies:
 *   - JDK 17+ (PBKDF2 + Ed25519 private key via EdECPrivateKeySpec)
 *   - Bouncy Castle bcprov (Ed25519 public key derivation from seed only)
 *
 * NOTE: Ed25519 keys are not compatible with EnDeCrypt.java in this template, which
 * expects RSA keys for OAEP encryption.
 *
 * Run standalone (after adding bcprov to the Gradle classpath):
 *   ./gradlew compileJava
 *   java -cp "build/classes/java/main;<path-to-bcprov.jar>" com.template.restapi.util.KeysGeneratorDtrmnstc -p "pass" -s "salt" -o ./keys
 */
package com.template.restapi.util;

import java.io.Console;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.KeyFactory;
import java.security.PrivateKey;
import java.security.SecureRandom;
import java.security.spec.EdECPrivateKeySpec;
import java.security.spec.NamedParameterSpec;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.Map;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

import org.bouncycastle.math.ec.rfc8032.Ed25519;

public final class KeysGeneratorDtrmnstc {

    public static final int DEFAULT_ITERATIONS = 200_000;
    public static final String DEFAULT_METADATA_NAME = "key_derivation.json";
    public static final String DEFAULT_PRIVATE_NAME = "private_key.pem";
    public static final String DEFAULT_PUBLIC_NAME = "public_key.pem";

    private KeysGeneratorDtrmnstc() { }

    public static final class GenerationResult {
        public final Path privatePath;
        public final Path publicPath;
        public final Path metadataPath;
        public final byte[] salt;
        public final int iterations;

        public GenerationResult(
                Path privatePath,
                Path publicPath,
                Path metadataPath,
                byte[] salt,
                int iterations) {
            this.privatePath = privatePath;
            this.publicPath = publicPath;
            this.metadataPath = metadataPath;
            this.salt = salt;
            this.iterations = iterations;
        }
    }

    public static byte[] deriveSeed(byte[] passphrase, byte[] salt, int iterations) throws Exception {
        if (passphrase == null || passphrase.length == 0)
            throw new IllegalArgumentException("Passphrase must not be empty.");
        if (salt == null || salt.length == 0)
            throw new IllegalArgumentException("Salt must not be empty.");
        if (iterations < 1)
            throw new IllegalArgumentException("PBKDF2 iterations must be at least 1.");

        PBEKeySpec spec = new PBEKeySpec(
                bytesToChars(passphrase),
                salt,
                iterations,
                256);
        return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
                .generateSecret(spec)
                .getEncoded();
    }

    public static byte[] deriveEd25519PublicKeyBytes(byte[] seed) {
        byte[] publicKey = new byte[Ed25519.PUBLIC_KEY_SIZE];
        Ed25519.generatePublicKey(seed, 0, publicKey, 0);
        return publicKey;
    }

    public static byte[] buildEd25519PrivateKeyPkcs8(byte[] seed) throws Exception {
        KeyFactory keyFactory = KeyFactory.getInstance("Ed25519");
        PrivateKey privateKey = keyFactory.generatePrivate(
                new EdECPrivateKeySpec(NamedParameterSpec.ED25519, seed));
        return privateKey.getEncoded();
    }

    public static byte[] buildEd25519SubjectPublicKeyInfo(byte[] rawPublicKey) {
        if (rawPublicKey.length != Ed25519.PUBLIC_KEY_SIZE)
            throw new IllegalArgumentException("Ed25519 public key must be 32 bytes.");

        byte[] algorithmIdentifier = new byte[] {
                0x30, 0x05,
                0x06, 0x03, 0x2B, 0x65, 0x70
        };
        byte[] bitString = new byte[3 + rawPublicKey.length];
        bitString[0] = 0x03;
        bitString[1] = (byte) (1 + rawPublicKey.length);
        bitString[2] = 0x00;
        System.arraycopy(rawPublicKey, 0, bitString, 3, rawPublicKey.length);

        return derSequence(concat(algorithmIdentifier, bitString));
    }

    public static GenerationResult generateDeterministicKeys(
            byte[] passphrase,
            Path outputDir,
            byte[] salt,
            int iterations,
            String privateName,
            String publicName,
            String metadataName) throws Exception {
        validateOutputPath(outputDir.toString());
        validateOutputPath(privateName);
        validateOutputPath(publicName);
        validateOutputPath(metadataName);

        Files.createDirectories(outputDir);

        byte[] usedSalt = salt != null ? salt : randomSalt(16);
        byte[] seed = deriveSeed(passphrase, usedSalt, iterations);
        byte[] privateDer = buildEd25519PrivateKeyPkcs8(seed);
        byte[] publicDer = buildEd25519SubjectPublicKeyInfo(deriveEd25519PublicKeyBytes(seed));

        Path privatePath = outputDir.resolve(privateName);
        Path publicPath = outputDir.resolve(publicName);
        Path metadataPath = outputDir.resolve(metadataName);

        Files.writeString(privatePath, pemEncode("PRIVATE KEY", privateDer), StandardCharsets.UTF_8);
        Files.writeString(publicPath, pemEncode("PUBLIC KEY", publicDer), StandardCharsets.UTF_8);
        writeMetadata(metadataPath, usedSalt, iterations, privateName, publicName);

        return new GenerationResult(privatePath, publicPath, metadataPath, usedSalt, iterations);
    }

    public static byte[] parseSalt(String value) {
        if (value == null || value.isEmpty())
            throw new IllegalArgumentException("Salt must not be empty.");
        if (value.startsWith("b64:"))
            return Base64.getDecoder().decode(value.substring(4));
        return value.getBytes(StandardCharsets.UTF_8);
    }

    public static void printUsage() {
        System.out.println("Usage: KeysGeneratorDtrmnstc [-p passphrase] [-s salt] [-o outputDir]");
        System.out.println("       [--iterations N] [--private-name NAME] [--public-name NAME]");
        System.out.println("       [--metadata-name NAME]");
    }

    public static int runCli(String[] args) throws Exception {
        String passphrase = null;
        String saltValue = null;
        String outputDir = ".";
        int iterations = DEFAULT_ITERATIONS;
        String privateName = DEFAULT_PRIVATE_NAME;
        String publicName = DEFAULT_PUBLIC_NAME;
        String metadataName = DEFAULT_METADATA_NAME;

        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            switch (arg) {
                case "-h":
                case "--help":
                    printUsage();
                    return 0;
                case "-p":
                case "--passphrase":
                    passphrase = requireValue(args, ++i, arg);
                    break;
                case "-s":
                case "--salt":
                    saltValue = requireValue(args, ++i, arg);
                    break;
                case "-o":
                case "--output-dir":
                    outputDir = requireValue(args, ++i, arg);
                    break;
                case "--iterations":
                    iterations = Integer.parseInt(requireValue(args, ++i, arg));
                    break;
                case "--private-name":
                    privateName = requireValue(args, ++i, arg);
                    break;
                case "--public-name":
                    publicName = requireValue(args, ++i, arg);
                    break;
                case "--metadata-name":
                    metadataName = requireValue(args, ++i, arg);
                    break;
                default:
                    System.err.println("Unknown argument: " + arg);
                    printUsage();
                    return 1;
            }
        }

        validateOutputPath(outputDir);

        if (passphrase == null) {
            Console console = System.console();
            if (console == null) {
                System.err.println("Error: passphrase required (-p) when no console is available.");
                return 1;
            }
            char[] first = console.readPassword("Passphrase: ");
            char[] second = console.readPassword("Confirm passphrase: ");
            if (first == null || second == null || !charsEqual(first, second)) {
                System.err.println("Error: passphrases do not match.");
                return 1;
            }
            passphrase = new String(first);
        }

        byte[] salt = saltValue != null ? parseSalt(saltValue) : null;
        GenerationResult result = generateDeterministicKeys(
                passphrase.getBytes(StandardCharsets.UTF_8),
                Paths.get(outputDir),
                salt,
                iterations,
                privateName,
                publicName,
                metadataName);

        System.out.println("Deterministic Ed25519 keys generated successfully!");
        System.out.println("Private key: " + result.privatePath);
        System.out.println("Public key:  " + result.publicPath);
        System.out.println("Metadata:    " + result.metadataPath);
        if (saltValue == null) {
            System.out.println(
                    "A random salt was generated and saved in the metadata file. "
                            + "Keep that file to reproduce the same keys later.");
        }
        return 0;
    }

    public static void main(String[] args) throws Exception {
        System.exit(runCli(args));
    }

    private static void writeMetadata(
            Path metadataPath,
            byte[] salt,
            int iterations,
            String privateName,
            String publicName) throws Exception {
        Map<String, Object> metadata = new LinkedHashMap<>();
        metadata.put("algorithm", "Ed25519");
        metadata.put("kdf", "PBKDF2-HMAC-SHA256");
        metadata.put("iterations", iterations);
        metadata.put("salt_b64", Base64.getEncoder().encodeToString(salt));
        metadata.put("private_key_file", privateName);
        metadata.put("public_key_file", publicName);
        Files.writeString(metadataPath, toPrettyJson(metadata) + System.lineSeparator(), StandardCharsets.UTF_8);
    }

    private static String toPrettyJson(Map<String, Object> metadata) {
        StringBuilder sb = new StringBuilder();
        sb.append('{').append(System.lineSeparator());
        int index = 0;
        for (Map.Entry<String, Object> entry : metadata.entrySet()) {
            sb.append("  \"").append(entry.getKey()).append("\": ");
            Object value = entry.getValue();
            if (value instanceof Number) {
                sb.append(value);
            } else {
                sb.append('"').append(escapeJson(String.valueOf(value))).append('"');
            }
            if (++index < metadata.size())
                sb.append(',');
            sb.append(System.lineSeparator());
        }
        sb.append('}');
        return sb.toString();
    }

    private static String escapeJson(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static byte[] randomSalt(int size) {
        byte[] salt = new byte[size];
        new SecureRandom().nextBytes(salt);
        return salt;
    }

    private static char[] bytesToChars(byte[] bytes) {
        char[] chars = new char[bytes.length];
        for (int i = 0; i < bytes.length; i++)
            chars[i] = (char) (bytes[i] & 0xFF);
        return chars;
    }

    private static boolean charsEqual(char[] left, char[] right) {
        if (left.length != right.length)
            return false;
        int diff = 0;
        for (int i = 0; i < left.length; i++)
            diff |= left[i] ^ right[i];
        return diff == 0;
    }

    private static String requireValue(String[] args, int index, String flag) {
        if (index >= args.length)
            throw new IllegalArgumentException("Missing value for " + flag);
        return args[index];
    }

    private static void validateOutputPath(String path) {
        if (path == null || path.trim().isEmpty() || path.contains(".."))
            throw new IllegalArgumentException("Invalid file path: " + path);
    }

    private static byte[] concat(byte[] left, byte[] right) {
        byte[] combined = new byte[left.length + right.length];
        System.arraycopy(left, 0, combined, 0, left.length);
        System.arraycopy(right, 0, combined, left.length, right.length);
        return combined;
    }

    private static byte[] derSequence(byte[] content) {
        return concat(concat(new byte[] { 0x30 }, derLength(content.length)), content);
    }

    private static byte[] derLength(int length) {
        if (length < 128)
            return new byte[] { (byte) length };
        if (length < 256)
            return new byte[] { (byte) 0x81, (byte) length };
        return new byte[] { (byte) 0x82, (byte) (length >> 8), (byte) length };
    }

    private static String pemEncode(String label, byte[] der) {
        String b64 = Base64.getEncoder().encodeToString(der);
        StringBuilder sb = new StringBuilder();
        sb.append("-----BEGIN ").append(label).append("-----").append(System.lineSeparator());
        int pos = 0;
        while (pos < b64.length()) {
            int take = Math.min(64, b64.length() - pos);
            sb.append(b64, pos, pos + take).append(System.lineSeparator());
            pos += take;
        }
        sb.append("-----END ").append(label).append("-----").append(System.lineSeparator());
        return sb.toString();
    }
}
