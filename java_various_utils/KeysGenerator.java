// NOTE: These helper files are intended to be copied into other projects.
// Change the package `java_various_utils` below to match your project's package
// before integrating.
//
// Asymmetric (RSA) key generator.
//
// Generates a public/private RSA key pair for asymmetric encryption and writes
// them to PEM files. Run once; the generated private key must never be shared.
// The parameters (key size) can be tinkered with as desired.
//
// No external dependencies (pure JDK java.security).
//
// NOTE on PEM formats:
// - The private key is exported in PKCS#8 ("BEGIN PRIVATE KEY"), which is what
//   the JDK produces natively. The Python/C# equivalents used PKCS#1
//   ("BEGIN RSA PRIVATE KEY"); both are interoperable with OpenSSL.
// - The public key is exported as SubjectPublicKeyInfo ("BEGIN PUBLIC KEY").
//
// HOW TO TEST (standalone)
//   javac KeysGenerator.java
//   java KeysGenerator
//   -> writes private_rsa_key.pem and public_rsa_key.pem in the working directory.

// Change package based on whatever project is implemented
package java_various_utils;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.util.Base64;

public final class KeysGenerator {

    private KeysGenerator() { }

    public static void generateRsaKeys(String privatePath, String publicPath) throws Exception {
        if (privatePath == null || privatePath.trim().isEmpty() || privatePath.contains(".."))
            throw new IllegalArgumentException("Invalid file path");

        if (publicPath == null || publicPath.trim().isEmpty() || publicPath.contains(".."))
            throw new IllegalArgumentException("Invalid file path");

        KeyPairGenerator generator = KeyPairGenerator.getInstance("RSA");
        generator.initialize(2048); // Can be modified (e.g. 3072, 4096)
        KeyPair keyPair = generator.generateKeyPair();

        byte[] privDer = keyPair.getPrivate().getEncoded();  // PKCS#8
        byte[] pubDer = keyPair.getPublic().getEncoded();    // SubjectPublicKeyInfo

        Files.write(Paths.get(privatePath),
                pemEncode("PRIVATE KEY", privDer).getBytes(StandardCharsets.UTF_8));
        Files.write(Paths.get(publicPath),
                pemEncode("PUBLIC KEY", pubDer).getBytes(StandardCharsets.UTF_8));

        System.out.println("Keys generated successfully!");
        System.out.println("Private key saved as " + privatePath);
        System.out.println("Public key saved as " + publicPath);
    }

    // Private helper - wraps DER bytes into a 64-column PEM block.
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

    // Main execution entry point - requires only to call the method.
    public static void main(String[] args) throws Exception {
        String privatePath = "private_rsa_key.pem";
        String publicPath = "public_rsa_key.pem";
        generateRsaKeys(privatePath, publicPath);
    }
}
