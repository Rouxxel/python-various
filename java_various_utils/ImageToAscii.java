// NOTE: These helper files are intended to be copied into other projects.
// Change the package `java_various_utils` below to match your project's package
// before integrating.
//
// Image to ASCII Art Converter
//
// Converts raster images (PNG, JPEG, BMP, GIF, WEBP) into ASCII art text files.
// The core algorithm maps each pixel's grayscale luminance to a character from a
// density-ordered ramp, producing a plain .txt file viewable in any monospaced font
// editor or terminal.
//
// Pipeline (step by step):
//
//   image.png -> [Load & Grayscale] -> [Compute Width] -> [Resize] -> [Map pixels to chars] -> image.txt
//
//   1. Load & Grayscale: Open the image and convert to single-channel brightness (0-255).
//   2. Compute Width: Read the image's native pixel width and apply the resolution
//      percentage (1-500). 100 = image width in chars, 50 = half, 200 = double.
//   3. Resize: Shrink/expand to computed character width, applying aspect ratio
//      correction (terminal chars are ~2x taller than wide, so height is scaled by ~0.55).
//   4. Map pixels to chars: Each pixel brightness maps to a character in the ramp.
//      Dense characters (@, #, %) represent dark pixels, light characters (., space)
//      represent bright pixels. The ramp is auto-selected based on effective width
//      (extended 70-level ramp for width >= 150, standard 10-level otherwise).
//   5. Write output: Join character rows with newlines and save as .txt file.
//
// This module provides:
// - Conversion of images to ASCII art .txt files
// - Resolution-based width: automatically derives output width from image dimensions
// - Resolution percentage (1-500): controls detail level relative to the source image
// - Auto ramp selection: extended (70 levels) for high-res, standard (10 levels) for low-res
// - Aspect ratio correction for terminal display
// - Inverted mode for dark terminal backgrounds
// - Single-file and recursive directory processing modes
//
// Dependencies:
// - Java AWT / ImageIO (built into JDK)
// - WEBP support requires TwelveMonkeys imageio-webp plugin
//
// HOW TO TEST (standalone)
//   javac ImageToAscii.java
//   java ImageToAscii
//   -> edit singleFile / folderToCrawl in main() first.

// Change package based on whatever project is implemented
package java_various_utils;

import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import javax.imageio.ImageIO;

public final class ImageToAscii {

    // =========================
    // CONFIG
    // =========================

    public static final List<String> INPUT_FORMATS =
            Arrays.asList("png", "jpg", "jpeg", "webp", "bmp", "gif", "tiff", "tif");

    // Character ramp from darkest (most dense) to lightest (least dense)
    public static final String CHAR_RAMP_STANDARD = "@%#*+=-:. ";

    // Extended ramp with more granularity (70 levels)
    public static final String CHAR_RAMP_EXTENDED =
            "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ";

    // Default resolution percentage (100 = image's native pixel width in characters)
    public static final int DEFAULT_RESOLUTION = 100;

    // Min/max resolution bounds
    public static final int MIN_RESOLUTION = 1;
    public static final int MAX_RESOLUTION = 500;

    // Threshold: use extended ramp when effective width >= this value
    public static final int AUTO_RAMP_THRESHOLD = 150;

    // Aspect ratio correction (terminal chars are ~2x taller than wide)
    public static final double ASPECT_RATIO_CORRECTION = 0.55;

    private ImageToAscii() { }

    // =========================
    // IMAGE LOADING
    // =========================

    // Load an image file and convert to grayscale.
    // Returns a BufferedImage of TYPE_BYTE_GRAY.
    private static BufferedImage loadAndPrepareImage(Path path) throws IOException {
        BufferedImage img = ImageIO.read(path.toFile());
        if (img == null) {
            throw new IOException("Failed to load image (no ImageIO codec): " + path);
        }

        // Convert to grayscale
        BufferedImage gray = new BufferedImage(img.getWidth(), img.getHeight(),
                BufferedImage.TYPE_BYTE_GRAY);
        Graphics2D g = gray.createGraphics();
        g.drawImage(img, 0, 0, null);
        g.dispose();
        return gray;
    }

    // =========================
    // RESOLUTION LOGIC
    // =========================

    // Compute the output character width from the image's native width
    // and a resolution percentage (1-500).
    public static int computeWidthFromResolution(int imageWidth, int resolution) {
        resolution = Math.max(MIN_RESOLUTION, Math.min(MAX_RESOLUTION, resolution));
        int width = (int) (imageWidth * (resolution / 100.0));
        return Math.max(1, width);
    }

    // Auto-select character ramp based on effective output width.
    public static String selectCharRamp(int effectiveWidth) {
        if (effectiveWidth >= AUTO_RAMP_THRESHOLD) {
            return CHAR_RAMP_EXTENDED;
        }
        return CHAR_RAMP_STANDARD;
    }

    // =========================
    // RESIZE
    // =========================

    // Resize image to fit target character width with height correction.
    // Terminal characters are taller than they are wide, so height is scaled
    // down by the correction factor.
    private static BufferedImage resizeForTerminal(BufferedImage img, int width,
                                                   double aspectRatioCorrection) {
        int originalWidth = img.getWidth();
        int originalHeight = img.getHeight();
        double scaleFactor = (double) width / originalWidth;
        int newHeight = Math.max(1, (int) (originalHeight * scaleFactor * aspectRatioCorrection));

        BufferedImage resized = new BufferedImage(width, newHeight, BufferedImage.TYPE_BYTE_GRAY);
        Graphics2D g = resized.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_INTERPOLATION,
                RenderingHints.VALUE_INTERPOLATION_BICUBIC);
        g.drawImage(img, 0, 0, width, newHeight, null);
        g.dispose();
        return resized;
    }

    // =========================
    // PIXEL TO CHARACTER MAPPING
    // =========================

    // Map each pixel row to a string of ASCII characters.
    // Each pixel value [0, 255] maps to an index in the character ramp.
    private static String[] mapPixelsToChars(BufferedImage img, String charRamp, boolean invert) {
        int width = img.getWidth();
        int height = img.getHeight();
        int rampLen = charRamp.length();
        String[] lines = new String[height];

        for (int y = 0; y < height; y++) {
            StringBuilder row = new StringBuilder(width);
            for (int x = 0; x < width; x++) {
                // TYPE_BYTE_GRAY: the red channel holds the grayscale value
                int pixelValue = img.getRaster().getSample(x, y, 0);

                if (invert) {
                    pixelValue = 255 - pixelValue;
                }

                int index = pixelValue * (rampLen - 1) / 255;
                row.append(charRamp.charAt(index));
            }
            lines[y] = row.toString();
        }
        return lines;
    }

    // =========================
    // OUTPUT WRITER
    // =========================

    // Write ASCII art lines to a text file (UTF-8).
    private static void writeOutput(String[] lines, Path outputPath) throws IOException {
        Path parent = outputPath.getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }
        Files.write(outputPath, Arrays.asList(lines), StandardCharsets.UTF_8);
    }

    // =========================
    // CONVERSION CORE
    // =========================

    // Full pipeline: load -> grayscale -> compute width -> resize -> map -> write.
    //
    // Width priority:
    //   - If outputWidth > 0: use that exact character width.
    //   - If outputWidth <= 0: derive from image width * (resolution / 100).
    //
    // Ramp priority:
    //   - If useExtendedRamp is Boolean.TRUE: force extended ramp (70 levels).
    //   - If useExtendedRamp is Boolean.FALSE: force standard ramp (10 levels).
    //   - If useExtendedRamp is null: auto-select based on effective width.
    //   - If charRamp is explicitly provided (non-null), it overrides everything above.
    public static Path convertToAscii(Path imagePath, Path outputPath, int outputWidth,
                                       int resolution, String charRamp,
                                       Boolean useExtendedRamp,
                                       double aspectRatioCorrection,
                                       boolean invert) throws IOException {
        resolution = Math.max(MIN_RESOLUTION, Math.min(MAX_RESOLUTION, resolution));

        if (outputPath == null) {
            outputPath = withExtension(imagePath, "txt");
        }

        BufferedImage img = loadAndPrepareImage(imagePath);

        // Determine effective width
        int effectiveWidth;
        if (outputWidth > 0) {
            effectiveWidth = outputWidth;
        } else {
            effectiveWidth = computeWidthFromResolution(img.getWidth(), resolution);
        }

        // Determine character ramp
        if (charRamp == null) {
            if (Boolean.TRUE.equals(useExtendedRamp)) {
                charRamp = CHAR_RAMP_EXTENDED;
            } else if (Boolean.FALSE.equals(useExtendedRamp)) {
                charRamp = CHAR_RAMP_STANDARD;
            } else {
                charRamp = selectCharRamp(effectiveWidth);
            }
        }

        img = resizeForTerminal(img, effectiveWidth, aspectRatioCorrection);
        String[] lines = mapPixelsToChars(img, charRamp, invert);
        writeOutput(lines, outputPath);

        String rampLabel = charRamp.length() > 10 ? "extended" : "standard";
        String widthSource = outputWidth > 0 ? "manual" : resolution + "%";
        System.out.println("  Width: " + effectiveWidth + " chars (" + widthSource + ") | "
                + "Ramp: " + rampLabel);

        return outputPath;
    }

    // =========================
    // SINGLE FILE MODE
    // =========================

    // Process one image file and convert to ASCII art .txt.
    // Validates file exists and has a supported extension.
    public static void processSingleFile(String file, int outputWidth, int resolution,
                                          Boolean useExtendedRamp, boolean invert) {
        Path path = Paths.get(file);

        if (!Files.exists(path)) {
            System.out.println("File not found: " + path);
            return;
        }

        String ext = extensionOf(path);
        if (!INPUT_FORMATS.contains(ext)) {
            System.out.println("Unsupported format: ." + ext + ". Supported: " + INPUT_FORMATS);
            return;
        }

        try {
            Path out = convertToAscii(path, null, outputWidth, resolution, null,
                    useExtendedRamp, ASPECT_RATIO_CORRECTION, invert);
            System.out.println("Converted: " + path + " -> " + out);
        } catch (Exception e) {
            System.out.println("Failed: " + path + " -> " + e.getMessage());
        }
    }

    // =========================
    // DIRECTORY MODE
    // =========================

    // Recursively scan a directory and convert all matching images to ASCII .txt files.
    // If outputWidth <= 0, each image's width is derived from its native size * resolution%.
    public static void processDirectory(String root, List<String> sourceFormats,
                                         int outputWidth, int resolution,
                                         Boolean useExtendedRamp, boolean invert) {
        Set<String> formats = new HashSet<>(
                (sourceFormats == null ? INPUT_FORMATS : sourceFormats)
                        .stream().map(String::toLowerCase).collect(Collectors.toList())
        );

        int count = 0;
        try (Stream<Path> walk = Files.walk(Paths.get(root))) {
            List<Path> files = walk
                    .filter(Files::isRegularFile)
                    .filter(p -> formats.contains(extensionOf(p)))
                    .collect(Collectors.toList());

            for (Path file : files) {
                try {
                    Path out = convertToAscii(file, null, outputWidth, resolution, null,
                            useExtendedRamp, ASPECT_RATIO_CORRECTION, invert);
                    System.out.println("Converted: " + file + " -> " + out);
                    count++;
                } catch (Exception e) {
                    System.out.println("Failed: " + file + " -> " + e.getMessage());
                }
            }
        } catch (IOException e) {
            System.out.println("Failed to scan " + root + ": " + e.getMessage());
        }

        System.out.println("\nProcessed " + count + " file(s).");
    }

    // =========================
    // HELPERS
    // =========================

    private static String extensionOf(Path p) {
        String name = p.getFileName().toString();
        int dot = name.lastIndexOf('.');
        return dot >= 0 ? name.substring(dot + 1).toLowerCase() : "";
    }

    private static Path withExtension(Path p, String ext) {
        String name = p.getFileName().toString();
        int dot = name.lastIndexOf('.');
        String base = dot >= 0 ? name.substring(0, dot) : name;
        Path parent = p.getParent();
        String newName = base + "." + ext;
        return parent != null ? parent.resolve(newName) : Paths.get(newName);
    }

    // =========================
    // ENTRYPOINT
    // =========================

    public static void main(String[] args) {
        // =========================
        // CONFIG (USER-FACING)
        // =========================

        String folderToCrawl = null;        // e.g. "my_images"
        String singleFile = null;           // e.g. "photo.png"

        int outputWidth = 0;                // explicit char width (overrides resolution)
                                            // set to 0 to auto-derive from image size
        int resolution = 100;              // percentage of image width (1-500)
                                            // only used when outputWidth is 0
                                            // 100 = native, 50 = half, 200 = double
        Boolean useExtendedRamp = null;     // true = force extended (70 levels)
                                            // false = force standard (10 levels)
                                            // null = auto-select based on width
        boolean invertBrightness = false;   // true for dark terminal backgrounds

        // =========================
        // RUN
        // =========================

        if (singleFile != null && !singleFile.isEmpty()) {
            processSingleFile(singleFile, outputWidth, resolution,
                    useExtendedRamp, invertBrightness);
        }

        if (folderToCrawl != null && !folderToCrawl.isEmpty()) {
            processDirectory(folderToCrawl, null, outputWidth, resolution,
                    useExtendedRamp, invertBrightness);
        }

        if ((singleFile == null || singleFile.isEmpty())
                && (folderToCrawl == null || folderToCrawl.isEmpty())) {
            System.out.println("No input configured. Set 'singleFile' or 'folderToCrawl' "
                    + "in the CONFIG section.");
        }

        System.out.println("\nDone.");
    }
}
