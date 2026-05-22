// NOTE: These helper files are intended to be copied into other projects.
// Change the namespace `cs_various_utils` below to match your project's namespace
// before integrating.
using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;

// Change namespace based on whatever project is implemented
namespace cs_various_utils
{
    public static class KeysGenerator
    {
        public static void GenerateRsaKeys(
            string privatePath = "private_rsa_key.pem",
            string publicPath = "public_rsa_key.pem"
            ){
            using var rsa = RSA.Create(2048);

            var privDer = rsa.ExportRSAPrivateKey();
            var pubDer = rsa.ExportSubjectPublicKeyInfo();

            File.WriteAllText(privatePath, PemEncode("RSA PRIVATE KEY", privDer));
            File.WriteAllText(publicPath, PemEncode("PUBLIC KEY", pubDer));

            Console.WriteLine("Keys generated successfully!");
            Console.WriteLine($"Private key saved as {privatePath}");
            Console.WriteLine($"Public key saved as {publicPath}");
        }

        //Private method only should be used internally by the latter
        private static string PemEncode(
            string label, 
            byte[] der
            ){
            var b64 = Convert.ToBase64String(der);
            var sb = new StringBuilder();
            sb.AppendLine($"-----BEGIN {label}-----");
            int pos = 0;
            while (pos < b64.Length)
            {
                int take = Math.Min(64, b64.Length - pos);
                sb.AppendLine(b64.Substring(pos, take));
                pos += take;
            }
            sb.AppendLine($"-----END {label}-----");
            return sb.ToString();
        }

        //Main execution entry point - requires only to call the method
        public static void Main(string[] args)
        {
            //Enable for command-line argument parsing
            //if (args.Length > 0 && (args[0] == "-h" || args[0] == "--help"))
            //{
            //    Console.WriteLine("Usage: KeysGenerator [privateKeyPath] [publicKeyPath]");
            //    Console.WriteLine("Example: KeysGenerator my_private.pem my_public.pem");
            //    return;
            //}

            var privatePath = "private_rsa_key.pem"; //args.Length > 0 ? args[0] : "private_rsa_key.pem";
            var publicPath = "public_rsa_key.pem"; //args.Length > 1 ? args[1] : "public_rsa_key.pem";
            GenerateRsaKeys(privatePath, publicPath);
        }
    }
}
