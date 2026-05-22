// NOTE: These helper files are intended to be copied into other projects.
// Change the namespace `cs_various_utils` below to match your project's namespace
// before integrating.
using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Net;

// Change namespace based on whatever project is implemented
namespace cs_various_utils
{
    public static class ImageDownloader
    {
        private static readonly HttpClient _httpClient = new HttpClient(new HttpClientHandler { AllowAutoRedirect = true });
        private static readonly string[] DefaultImageExtensions = new[] { ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg" };

        private static string GetFileNameFromContentDisposition(
            HttpResponseMessage response
            ){
            if (response.Content.Headers.ContentDisposition?.FileNameStar != null)
            {
                return response.Content.Headers.ContentDisposition.FileNameStar.Trim('"');
            }

            if (response.Content.Headers.ContentDisposition?.FileName != null)
            {
                return response.Content.Headers.ContentDisposition.FileName.Trim('"');
            }

            return null;
        }

        private static string NormalizeFileName(
            string fileName, 
            string? extension = "png"
            ){
            if (string.IsNullOrWhiteSpace(fileName))
            {
                return $"downloaded_image{extension}";
            }

            fileName = fileName.Trim();
            var actualExtension = Path.GetExtension(fileName);
            if (string.IsNullOrEmpty(actualExtension))
            {
                return fileName + extension;
            }

            if (!string.IsNullOrEmpty(extension) && !actualExtension.Equals(extension, StringComparison.OrdinalIgnoreCase))
            {
                return Path.ChangeExtension(fileName, extension);
            }

            return fileName;
        }

        private static string GetExtensionFromContentType(
            string contentType
            )
        {
            if (string.IsNullOrEmpty(contentType)) return ".png";
            contentType = contentType.Split(';')[0].Trim().ToLowerInvariant();

            return contentType switch
            {
                "image/jpeg" => ".jpg",
                "image/png" => ".png",
                "image/gif" => ".gif",
                "image/bmp" => ".bmp",
                "image/webp" => ".webp",
                "image/svg+xml" => ".svg",
                _ => ".png"
            };
        }

        private static string GetFileNameFromUrl(
            Uri uri
            ){
            var path = uri.LocalPath;
            var fileName = Path.GetFileName(path);
            if (string.IsNullOrEmpty(fileName)) return null;
            return WebUtility.UrlDecode(fileName);
        }

        public static async Task DownloadImageAsync(
            string url,
            string? outputFileName = null,
            string? outputExtension = "png",
            int timeoutSeconds = 10,
            int retryCount = 3
        ){
            if (string.IsNullOrEmpty(url))
            {
                Console.WriteLine("Error: No URL provided.");
                return;
            }

            var uri = new Uri(url);
            _httpClient.DefaultRequestHeaders.UserAgent.ParseAdd("python-various-image-downloader/1.0");
            _httpClient.Timeout = TimeSpan.FromSeconds(timeoutSeconds);

            for (var attempt = 1; attempt <= retryCount; attempt++)
            {
                try
                {
                    using var request = new HttpRequestMessage(HttpMethod.Get, uri);
                    request.Headers.Accept.ParseAdd("image/*, */*");
                    using var response = await _httpClient.SendAsync(request, HttpCompletionOption.ResponseHeadersRead);
                    response.EnsureSuccessStatusCode();

                    var contentType = response.Content.Headers.ContentType?.MediaType;
                    var effectiveExtension = outputExtension != null && !outputExtension.StartsWith('.')
                        ? "." + outputExtension
                        : outputExtension ?? GetExtensionFromContentType(contentType);

                    var fileName = outputFileName;
                    if (string.IsNullOrWhiteSpace(fileName))
                    {
                        fileName = GetFileNameFromContentDisposition(response) ?? GetFileNameFromUrl(response.RequestMessage?.RequestUri ?? uri) ?? "downloaded_image";
                    }

                    fileName = NormalizeFileName(fileName, effectiveExtension);
                    Console.WriteLine($"--- Starting download: {fileName} ---");

                    if (!string.IsNullOrEmpty(contentType) && !contentType.StartsWith("image/", StringComparison.OrdinalIgnoreCase))
                    {
                        Console.WriteLine($"Warning: content-type is '{contentType}'. Proceeding anyway.");
                    }

                    using var stream = await response.Content.ReadAsStreamAsync();
                    await using var fs = new FileStream(fileName, FileMode.Create, FileAccess.Write, FileShare.None);
                    await stream.CopyToAsync(fs);

                    Console.WriteLine($"Success! Image has been saved as: {fileName}");
                    return;
                }
                catch (HttpRequestException e) when (attempt < retryCount)
                {
                    Console.WriteLine($"Request failed (attempt {attempt}/{retryCount}): {e.Message}. Retrying...");
                    await Task.Delay(TimeSpan.FromSeconds(1));
                }
                catch (Exception e)
                {
                    Console.WriteLine($"An error occurred: {e.Message}");
                    return;
                }
                finally
                {
                    if (attempt == retryCount)
                    {
                        Console.WriteLine("--- Task completed ---");
                    }
                }
            }
        }

        // Main execution entry point - accepts command-line 
        // arguments for URL, optional file name, extension, 
        // and timeout.
        static void Main(string[] args)
        {
            //Enable for command-line argument parsing
            //if (args.Length == 0 || args[0] == "-h" || args[0] == "--help")
            //{
            //    Console.WriteLine("Usage: ImageDownloader <url> [fileName] [outputFormat] [timeoutSeconds]");
            //    Console.WriteLine("Example: ImageDownloader https://example.com/image.jpg my_image jpg 15");
            //    return;
            //}

            var url = "https://www.lamborghini.com/sites/it-en/files/DAM/lamborghini/0_facelift_2025/model_details_new/temerario_2/mecha/Temerario_00-Mecha-H_Card-Powertrain-last.jpg"; //args[0];
            var fileName = "MaxxWatt_Logo"; //args.Length > 1 ? args[1] : null;
            var outputFormat = "png"; //args.Length > 2 ? args[2] : null;
            var timeoutSeconds = 10; //args.Length > 3 && int.TryParse(args[3], out var t) ? t : 10;

            DownloadImageAsync(url, fileName, outputFormat, timeoutSeconds).Wait();
        }
    }
}
