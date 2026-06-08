// NOTE: These helper files are intended to be copied into other projects.
// Change the package `java_various_utils` below to match your project's package
// before integrating.
//
// Download images from a given URL.
//
// Uses the JDK's built-in java.net.http.HttpClient to fetch image data and save
// it locally using a streamed approach to maintain memory efficiency. Includes
// a simple retry loop with exponential-ish backoff, follows redirects, and
// guards the output path against directory traversal.
//
// No external dependencies (requires Java 11+ for java.net.http).
//
// HOW TO TEST (standalone)
//   javac ImageDownloader.java
//   java ImageDownloader
//   -> downloads the sample image into a `downloads/` folder.

// Change package based on whatever project is implemented
package java_various_utils;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.URI;
import java.net.URLDecoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.time.Duration;
import java.util.Optional;

public final class ImageDownloader {

    private static final HttpClient HTTP_CLIENT = HttpClient.newBuilder()
            .followRedirects(HttpClient.Redirect.NORMAL)
            .connectTimeout(Duration.ofSeconds(10))
            .build();

    private ImageDownloader() { }

    /**
     * Download an image from a URL and save it under a local `downloads/` directory.
     *
     * @param url             source URL (required)
     * @param outputFileName  preferred base file name (without extension), or null
     * @param outputExtension preferred extension, e.g. "png" (defaults to "png")
     * @param timeoutSeconds  per-request timeout
     * @param retryCount      number of attempts before giving up
     */
    public static void downloadImage(String url, String outputFileName, String outputExtension,
                                     int timeoutSeconds, int retryCount) {
        if (url == null || url.isEmpty()) {
            System.out.println("Error: No URL provided.");
            return;
        }

        URI uri = URI.create(url);
        String effectiveExtension = normalizeExtension(outputExtension);

        for (int attempt = 1; attempt <= retryCount; attempt++) {
            try {
                HttpRequest request = HttpRequest.newBuilder(uri)
                        .timeout(Duration.ofSeconds(timeoutSeconds))
                        .header("User-Agent", "java-image-downloader/1.0")
                        .header("Accept", "image/*, */*")
                        .GET()
                        .build();

                HttpResponse<InputStream> response =
                        HTTP_CLIENT.send(request, HttpResponse.BodyHandlers.ofInputStream());

                if (response.statusCode() >= 400) {
                    throw new IOException("HTTP " + response.statusCode());
                }

                String contentType = response.headers().firstValue("content-type").orElse("");
                String ext = (outputExtension == null || outputExtension.isEmpty())
                        ? extensionFromContentType(contentType)
                        : effectiveExtension;

                String fileName = outputFileName;
                if (fileName == null || fileName.trim().isEmpty()) {
                    fileName = fileNameFromContentDisposition(response)
                            .or(() -> fileNameFromUri(response.uri()))
                            .orElse("downloaded_image");
                }
                fileName = normalizeFileName(fileName, ext);

                if (!contentType.isEmpty() && !contentType.toLowerCase().startsWith("image/")) {
                    System.out.println("Warning: content-type is '" + contentType + "'. Proceeding anyway.");
                }

                System.out.println("--- Starting download: " + fileName + " ---");

                Path baseDir = Paths.get("downloads").toAbsolutePath().normalize();
                Files.createDirectories(baseDir);

                Path fullPath = baseDir.resolve(fileName).normalize();
                if (!fullPath.startsWith(baseDir)) {
                    throw new IllegalArgumentException("Invalid file path (path traversal detected)");
                }

                try (InputStream in = response.body();
                     OutputStream out = Files.newOutputStream(fullPath,
                             StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING)) {
                    byte[] buffer = new byte[8192];
                    int read;
                    while ((read = in.read(buffer)) != -1) {
                        out.write(buffer, 0, read);
                    }
                }

                System.out.println("Success! Image has been saved as: " + fullPath);
                return;
            } catch (IOException e) {
                if (attempt < retryCount) {
                    System.out.println("Request failed (attempt " + attempt + "/" + retryCount
                            + "): " + e.getMessage() + ". Retrying...");
                    try {
                        Thread.sleep(500L * attempt);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        return;
                    }
                } else {
                    System.out.println("Request error: " + e.getMessage());
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                System.out.println("Download interrupted.");
                return;
            } catch (Exception e) {
                System.out.println("Unexpected error: " + e.getMessage());
                return;
            }
        }
        System.out.println("--- Task completed ---");
    }

    private static String normalizeExtension(String extension) {
        if (extension == null || extension.isEmpty()) return ".png";
        return extension.startsWith(".") ? extension : "." + extension;
    }

    private static String normalizeFileName(String fileName, String extension) {
        if (fileName == null || fileName.trim().isEmpty()) {
            return "downloaded_image" + extension;
        }
        fileName = fileName.trim();
        int dot = fileName.lastIndexOf('.');
        String actualExt = dot >= 0 ? fileName.substring(dot) : "";
        if (actualExt.isEmpty()) {
            return fileName + extension;
        }
        if (!extension.isEmpty() && !actualExt.equalsIgnoreCase(extension)) {
            return fileName.substring(0, dot) + extension;
        }
        return fileName;
    }

    private static String extensionFromContentType(String contentType) {
        if (contentType == null || contentType.isEmpty()) return ".png";
        String ct = contentType.split(";")[0].trim().toLowerCase();
        switch (ct) {
            case "image/jpeg": return ".jpg";
            case "image/png":  return ".png";
            case "image/gif":  return ".gif";
            case "image/bmp":  return ".bmp";
            case "image/webp": return ".webp";
            case "image/svg+xml": return ".svg";
            default: return ".png";
        }
    }

    private static Optional<String> fileNameFromContentDisposition(HttpResponse<?> response) {
        return response.headers().firstValue("content-disposition").flatMap(cd -> {
            int idx = cd.toLowerCase().indexOf("filename=");
            if (idx < 0) return Optional.empty();
            String name = cd.substring(idx + "filename=".length()).trim();
            // strip surrounding quotes/semicolons
            name = name.replaceAll("^\"|\";?$|;$", "").trim();
            return name.isEmpty() ? Optional.empty() : Optional.of(name);
        });
    }

    private static Optional<String> fileNameFromUri(URI uri) {
        String path = uri.getPath();
        if (path == null || path.isEmpty()) return Optional.empty();
        String name = path.substring(path.lastIndexOf('/') + 1);
        if (name.isEmpty()) return Optional.empty();
        try {
            return Optional.of(URLDecoder.decode(name, StandardCharsets.UTF_8));
        } catch (Exception e) {
            return Optional.of(name);
        }
    }

    // Main execution entry point - accepts a hardcoded URL for testing.
    public static void main(String[] args) {
        String url = "https://www.lamborghini.com/sites/it-en/files/DAM/lamborghini/0_facelift_2025/"
                + "model_details_new/temerario_2/mecha/Temerario_00-Mecha-H_Card-Powertrain-last.jpg";

        downloadImage(url, "MaxxWatt_Logo", "png", 10, 3);
    }
}
