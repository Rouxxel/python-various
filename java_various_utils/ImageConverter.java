// NOTE: These helper files are intended to be copied into other projects.
// Change the package `java_various_utils` below to match your project's package
// before integrating.
//
// Image Converter Utility
//
// A lightweight image conversion tool supporting raster workflows plus raster->SVG
// embedding.
//
// This module provides:
// - Conversion between PNG, JPG, JPEG, BMP, GIF (and WEBP if a codec is installed)
// - Multi-target output generation (e.g. ["png", "jpg"])
// - Recursive directory processing
// - Single-file processing mode
// - Optional image upscaling before export (bicubic)
// - JPEG quality control
// - Optional deletion of source files after successful conversion
//
// Supported Conversions:
// - Raster <-> Raster        (javax.imageio.ImageIO, built into the JDK)
// - Raster  -> SVG           (embedded base64 image, NOT vectorization; pure JDK)
//
// Optional dependencies (only if you need these formats):
// - WEBP read/write : TwelveMonkeys imageio-webp (registers a WEBP ImageIO plugin)
// - SVG  -> Raster  : Apache Batik (not implemented here; svg input prints a notice)
//
// HOW TO TEST (standalone)
//   javac ImageConverter.java
//   java ImageConverter
//   -> edit singleFile / folderToCrawl in main() to point at real images first.

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
import java.util.Base64;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import javax.imageio.IIOImage;
import javax.imageio.ImageIO;
import javax.imageio.ImageWriteParam;
import javax.imageio.ImageWriter;
import javax.imageio.stream.ImageOutputStream;

public final class ImageConverter {

    // =========================
    // CONFIG
    // =========================

    public static final List<String> INPUT_FORMATS =
            Arrays.asList("png", "jpg", "jpeg", "webp", "svg");

    private ImageConverter() { }

    // =========================
    // CORE UTILITIES
    // =========================

    private static BufferedImage upscale(BufferedImage img, double factor) {
        if (factor <= 1) return img;

        int newWidth = (int) (img.getWidth() * factor);
        int newHeight = (int) (img.getHeight() * factor);

        BufferedImage scaled = new BufferedImage(newWidth, newHeight, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g = scaled.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_INTERPOLATION,
                RenderingHints.VALUE_INTERPOLATION_BICUBIC);
        g.drawImage(img, 0, 0, newWidth, newHeight, null);
        g.dispose();
        return scaled;
    }

    // Flatten any alpha channel onto a white background (needed before JPEG export).
    private static BufferedImage ensureRgb(BufferedImage img) {
        if (!img.getColorModel().hasAlpha()
                && img.getType() == BufferedImage.TYPE_INT_RGB) {
            return img;
        }
        BufferedImage rgb = new BufferedImage(img.getWidth(), img.getHeight(), BufferedImage.TYPE_INT_RGB);
        Graphics2D g = rgb.createGraphics();
        g.setColor(java.awt.Color.WHITE);
        g.fillRect(0, 0, img.getWidth(), img.getHeight());
        g.drawImage(img, 0, 0, null);
        g.dispose();
        return rgb;
    }

    // =========================
    // LOADERS
    // =========================

    private static BufferedImage loadImage(Path path) throws IOException {
        BufferedImage img = ImageIO.read(path.toFile());
        if (img == null) {
            throw new IOException("Unsupported or unreadable image (no ImageIO codec): " + path
                    + ". For WEBP, add the TwelveMonkeys imageio-webp plugin.");
        }
        return img;
    }

    // =========================
    // SAVERS
    // =========================

    private static void saveImage(BufferedImage img, Path outPath, String fmt, int jpegQuality)
            throws IOException {
        fmt = fmt.toLowerCase();

        Path parent = outPath.getParent();
        if (parent != null) Files.createDirectories(parent);

        if (fmt.equals("jpg") || fmt.equals("jpeg")) {
            writeJpeg(ensureRgb(img), outPath, jpegQuality);
        } else {
            String formatName = fmt.equals("jpg") ? "jpeg" : fmt;
            if (!ImageIO.write(img, formatName, outPath.toFile())) {
                throw new IOException("No ImageIO writer available for format '" + fmt + "'.");
            }
        }
    }

    private static void writeJpeg(BufferedImage img, Path outPath, int jpegQuality) throws IOException {
        Iterator<ImageWriter> writers = ImageIO.getImageWritersByFormatName("jpeg");
        if (!writers.hasNext()) {
            throw new IOException("No JPEG writer available.");
        }
        ImageWriter writer = writers.next();
        ImageWriteParam param = writer.getDefaultWriteParam();
        if (param.canWriteCompressed()) {
            param.setCompressionMode(ImageWriteParam.MODE_EXPLICIT);
            param.setCompressionQuality(Math.max(0f, Math.min(1f, jpegQuality / 100f)));
        }
        try (ImageOutputStream ios = ImageIO.createImageOutputStream(outPath.toFile())) {
            writer.setOutput(ios);
            writer.write(null, new IIOImage(img, null, null), param);
        } finally {
            writer.dispose();
        }
    }

    // Embeds a raster image inside an SVG file using base64 (NOT vectorization).
    private static void rasterToSvg(Path imgPath, Path outPath) throws IOException {
        byte[] bytes = Files.readAllBytes(imgPath);
        String encoded = Base64.getEncoder().encodeToString(bytes);

        BufferedImage img = loadImage(imgPath);
        String ext = extensionOf(imgPath);
        String mime = ext.equals("png") ? "image/png" : "image/jpeg";

        String svg = "<svg xmlns=\"http://www.w3.org/2000/svg\"\n"
                + "     width=\"" + img.getWidth() + "\" height=\"" + img.getHeight() + "\">\n"
                + "    <image href=\"data:" + mime + ";base64," + encoded + "\"\n"
                + "           width=\"" + img.getWidth() + "\" height=\"" + img.getHeight() + "\" />\n"
                + "</svg>\n";

        Path parent = outPath.getParent();
        if (parent != null) Files.createDirectories(parent);
        Files.write(outPath, svg.getBytes(StandardCharsets.UTF_8));
    }

    // =========================
    // CONVERSION CORE
    // =========================

    public static void convertFile(Path path, List<String> targets, double upscaleFactor,
                                   int jpegQuality, boolean deleteOriginal) {
        List<String> targetList = (targets == null) ? INPUT_FORMATS : targets;
        String srcExt = extensionOf(path);

        BufferedImage img = null;

        for (String target : targetList) {
            Path outPath = withExtension(path, target);

            try {
                if (srcExt.equals("svg") && !target.equals("svg")) {
                    // SVG -> raster requires a rasterizer (e.g. Apache Batik); not bundled.
                    System.out.println("Skipped: " + path + " (SVG -> " + target
                            + " needs Apache Batik; not implemented in this standalone util)");
                    continue;
                } else if (target.equals("svg") && !srcExt.equals("svg")) {
                    // raster -> SVG (embed)
                    rasterToSvg(path, outPath);
                } else if (!srcExt.equals("svg") && !target.equals("svg")) {
                    // raster -> raster
                    if (img == null) img = loadImage(path);
                    BufferedImage out = upscale(img, upscaleFactor);
                    saveImage(out, outPath, target, jpegQuality);
                } else {
                    continue;
                }

                System.out.println("Converted: " + path + " -> " + outPath);

                if (deleteOriginal) {
                    try {
                        Files.delete(path);
                        System.out.println("Deleted original: " + path);
                    } catch (IOException e) {
                        System.out.println("Failed to delete " + path + ": " + e.getMessage());
                    }
                }
            } catch (Exception e) {
                System.out.println("Failed: " + path + " (" + target + ") -> " + e.getMessage());
            }
        }
    }

    // =========================
    // DIRECTORY MODE
    // =========================

    public static void processDirectory(String root, List<String> targets, List<String> sourceFormats,
                                        double upscaleFactor, int jpegQuality, boolean deleteOriginal) {
        Set<String> formats = (sourceFormats == null ? INPUT_FORMATS : sourceFormats)
                .stream().map(String::toLowerCase).collect(Collectors.toCollection(HashSet::new));

        try (Stream<Path> walk = Files.walk(Paths.get(root))) {
            walk.filter(Files::isRegularFile)
                .filter(p -> formats.contains(extensionOf(p)))
                .forEach(p -> convertFile(p, targets, upscaleFactor, jpegQuality, deleteOriginal));
        } catch (IOException e) {
            System.out.println("Failed to scan " + root + ": " + e.getMessage());
        }
    }

    // =========================
    // SINGLE FILE MODE
    // =========================

    public static void processSingleFile(String file, List<String> targets, double upscaleFactor,
                                         int jpegQuality, boolean deleteOriginal) throws IOException {
        Path path = Paths.get(file);
        if (!Files.exists(path)) {
            throw new IOException("File not found: " + file);
        }
        convertFile(path, targets, upscaleFactor, jpegQuality, deleteOriginal);
    }

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

    public static void main(String[] args) throws IOException {
        // =========================
        // CONFIG (USER-FACING)
        // =========================

        String folderToCrawl = null; // e.g. "my_project"
        String singleFile = null;     // e.g. "image.png"

        List<String> inputFormats = Arrays.asList("png", "jpg", "jpeg", "webp", "svg");
        List<String> targetFormats = Arrays.asList("jpg"); // supports MULTIPLE outputs

        if (singleFile != null && !singleFile.isEmpty()) {
            processSingleFile(singleFile, targetFormats, 
                1.0, 85, false);
        }

        if (folderToCrawl != null && !folderToCrawl.isEmpty()) {
            processDirectory(folderToCrawl, targetFormats, inputFormats, 
                1.0, 85, false);
        }

        System.out.println("\nDone.");
    }
}
