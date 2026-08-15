// NOTE: These helper files are intended to be copied into other projects.
// Change the namespace `cs_various_utils` below to match your project's namespace
// before integrating.
//
// Image to ASCII Art Converter
//
// Converts raster images (PNG, JPEG, BMP, GIF, WEBP, TIFF) into ASCII art text files.
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
// Required NuGet packages:
// - SkiaSharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using SkiaSharp;

// Change namespace based on whatever project is implemented
namespace cs_various_utils
{
    public static class ImageToAscii
    {
        // =========================
        // CONFIG
        // =========================

        public static readonly string[] InputFormats =
            { "png", "jpg", "jpeg", "webp", "bmp", "gif", "tiff", "tif" };

        // Character ramp from darkest (most dense) to lightest (least dense)
        public const string CharRampStandard = "@%#*+=-:. ";

        // Extended ramp with more granularity (70 levels)
        public const string CharRampExtended =
            "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ";

        // Default resolution percentage (100 = image's native pixel width in characters)
        public const int DefaultResolution = 100;

        // Min/max resolution bounds
        public const int MinResolution = 1;
        public const int MaxResolution = 500;

        // Threshold: use extended ramp when effective width >= this value
        public const int AutoRampThreshold = 150;

        // Aspect ratio correction (terminal chars are ~2x taller than wide)
        public const double AspectRatioCorrection = 0.55;

        // =========================
        // IMAGE LOADING
        // =========================

        /// <summary>
        /// Load an image file and convert to grayscale.
        /// Returns pixel brightness values as a 2D conceptual array via SKBitmap.
        /// </summary>
        private static SKBitmap LoadAndPrepareImage(string path)
        {
            var bitmap = SKBitmap.Decode(path)
                ?? throw new InvalidOperationException($"Failed to load image: {path}");

            // Convert to grayscale by drawing onto a Gray8 bitmap
            var gray = new SKBitmap(bitmap.Width, bitmap.Height, SKColorType.Gray8, SKAlphaType.Opaque);
            using var canvas = new SKCanvas(gray);
            using var paint = new SKPaint();
            paint.ColorFilter = SKColorFilter.CreateColorMatrix(new float[]
            {
                0.2126f, 0.7152f, 0.0722f, 0, 0,
                0.2126f, 0.7152f, 0.0722f, 0, 0,
                0.2126f, 0.7152f, 0.0722f, 0, 0,
                0,       0,       0,       1, 0
            });
            canvas.DrawBitmap(bitmap, 0, 0, paint);
            bitmap.Dispose();

            return gray;
        }

        // =========================
        // RESOLUTION LOGIC
        // =========================

        /// <summary>
        /// Compute the output character width from the image's native width
        /// and a resolution percentage (1-500).
        /// </summary>
        public static int ComputeWidthFromResolution(int imageWidth, int resolution)
        {
            resolution = Math.Max(MinResolution, Math.Min(MaxResolution, resolution));
            int width = (int)(imageWidth * (resolution / 100.0));
            return Math.Max(1, width);
        }

        /// <summary>
        /// Auto-select character ramp based on effective output width.
        /// Uses extended 70-level ramp for width >= 150, standard 10-level otherwise.
        /// </summary>
        public static string SelectCharRamp(int effectiveWidth)
        {
            return effectiveWidth >= AutoRampThreshold ? CharRampExtended : CharRampStandard;
        }

        // =========================
        // RESIZE
        // =========================

        /// <summary>
        /// Resize image to fit target character width with height correction.
        /// Terminal characters are taller than they are wide, so the height is
        /// scaled down by the correction factor to avoid vertical stretching.
        /// </summary>
        private static SKBitmap ResizeForTerminal(SKBitmap img, int width, double aspectRatioCorrection)
        {
            int originalWidth = img.Width;
            int originalHeight = img.Height;
            double scaleFactor = (double)width / originalWidth;
            int newHeight = Math.Max(1, (int)(originalHeight * scaleFactor * aspectRatioCorrection));

            var resized = img.Resize(new SKImageInfo(width, newHeight, img.ColorType, img.AlphaType),
                new SKSamplingOptions(SKCubicResampler.Mitchell));

            return resized ?? throw new InvalidOperationException("Failed to resize image.");
        }

        // =========================
        // PIXEL TO CHARACTER MAPPING
        // =========================

        /// <summary>
        /// Map each pixel row to a string of ASCII characters.
        /// Each pixel value [0, 255] is mapped to an index in the character ramp.
        /// In normal mode, dark pixels map to dense characters.
        /// In inverted mode, dark pixels map to light characters (for dark backgrounds).
        /// </summary>
        private static string[] MapPixelsToChars(SKBitmap img, string charRamp, bool invert)
        {
            int width = img.Width;
            int height = img.Height;
            int rampLen = charRamp.Length;
            var lines = new string[height];

            for (int y = 0; y < height; y++)
            {
                var row = new StringBuilder(width);
                for (int x = 0; x < width; x++)
                {
                    // Gray8 format: the color's Red channel holds the grayscale value
                    var color = img.GetPixel(x, y);
                    int pixelValue = color.Red;

                    if (invert)
                        pixelValue = 255 - pixelValue;

                    int index = pixelValue * (rampLen - 1) / 255;
                    row.Append(charRamp[index]);
                }
                lines[y] = row.ToString();
            }

            return lines;
        }

        // =========================
        // OUTPUT WRITER
        // =========================

        /// <summary>
        /// Write ASCII art lines to a text file (UTF-8).
        /// </summary>
        private static void WriteOutput(string[] lines, string outputPath)
        {
            var dir = Path.GetDirectoryName(outputPath);
            if (!string.IsNullOrEmpty(dir))
                Directory.CreateDirectory(dir);

            File.WriteAllLines(outputPath, lines, Encoding.UTF8);
        }

        // =========================
        // CONVERSION CORE
        // =========================

        /// <summary>
        /// Full pipeline: load -> grayscale -> compute width -> resize -> map -> write.
        ///
        /// Width priority:
        ///   - If outputWidth > 0: use that exact character width.
        ///   - If outputWidth &lt;= 0 (or null): derive from image width * (resolution / 100).
        ///
        /// Ramp priority:
        ///   - If useExtendedRamp is true: force extended ramp (70 levels).
        ///   - If useExtendedRamp is false: force standard ramp (10 levels).
        ///   - If useExtendedRamp is null: auto-select based on effective width.
        ///   - If charRamp is explicitly provided (non-null), it overrides everything above.
        /// </summary>
        public static string ConvertToAscii(
            string imagePath,
            string? outputPath = null,
            int? outputWidth = null,
            int resolution = DefaultResolution,
            string? charRamp = null,
            bool? useExtendedRamp = null,
            double aspectRatioCorrection = AspectRatioCorrection,
            bool invert = false)
        {
            resolution = Math.Max(MinResolution, Math.Min(MaxResolution, resolution));

            if (string.IsNullOrEmpty(outputPath))
                outputPath = Path.ChangeExtension(imagePath, ".txt");

            using var img = LoadAndPrepareImage(imagePath);

            // Determine effective width
            int effectiveWidth;
            if (outputWidth.HasValue && outputWidth.Value > 0)
            {
                effectiveWidth = outputWidth.Value;
            }
            else
            {
                effectiveWidth = ComputeWidthFromResolution(img.Width, resolution);
            }

            // Determine character ramp
            if (charRamp == null)
            {
                if (useExtendedRamp == true)
                    charRamp = CharRampExtended;
                else if (useExtendedRamp == false)
                    charRamp = CharRampStandard;
                else
                    charRamp = SelectCharRamp(effectiveWidth);
            }

            if (string.IsNullOrEmpty(charRamp))
                throw new ArgumentException("Character ramp must be a non-empty string.");

            using var resized = ResizeForTerminal(img, effectiveWidth, aspectRatioCorrection);
            var lines = MapPixelsToChars(resized, charRamp, invert);
            WriteOutput(lines, outputPath);

            var rampLabel = charRamp.Length > 10 ? "extended" : "standard";
            var widthSource = (outputWidth.HasValue && outputWidth.Value > 0) ? "manual" : $"{resolution}%";
            Console.WriteLine($"  Width: {effectiveWidth} chars ({widthSource}) | Ramp: {rampLabel}");

            return outputPath;
        }

        // =========================
        // SINGLE FILE MODE
        // =========================

        /// <summary>
        /// Process one image file and convert to ASCII art .txt.
        /// Validates file exists and has a supported extension.
        /// If outputWidth is null/0, derives width from image size * resolution%.
        /// </summary>
        public static void ProcessSingleFile(
            string file,
            int? outputWidth = null,
            int resolution = DefaultResolution,
            bool? useExtendedRamp = null,
            bool invert = false)
        {
            if (!File.Exists(file))
            {
                Console.WriteLine($"File not found: {file}");
                return;
            }

            var ext = Path.GetExtension(file).TrimStart('.').ToLowerInvariant();
            if (!InputFormats.Contains(ext))
            {
                Console.WriteLine($"Unsupported format: .{ext}. Supported: {string.Join(", ", InputFormats)}");
                return;
            }

            try
            {
                var outPath = ConvertToAscii(file, outputWidth: outputWidth,
                    resolution: resolution, useExtendedRamp: useExtendedRamp, invert: invert);
                Console.WriteLine($"Converted: {file} -> {outPath}");
            }
            catch (Exception e)
            {
                Console.WriteLine($"Failed: {file} -> {e.Message}");
            }
        }

        // =========================
        // DIRECTORY MODE
        // =========================

        /// <summary>
        /// Recursively scan a directory and convert all matching images to ASCII .txt files.
        /// If outputWidth is null/0, each image's width is derived from its own
        /// native size * resolution%.
        /// Failed conversions print an error but don't halt processing.
        /// </summary>
        public static void ProcessDirectory(
            string root,
            IEnumerable<string>? sourceFormats = null,
            int? outputWidth = null,
            int resolution = DefaultResolution,
            bool? useExtendedRamp = null,
            bool invert = false)
        {
            var formats = new HashSet<string>(
                (sourceFormats ?? InputFormats).Select(f => f.ToLowerInvariant())
            );

            if (!Directory.Exists(root))
            {
                Console.WriteLine($"Not a directory: {root}");
                return;
            }

            int count = 0;
            foreach (var file in Directory.EnumerateFiles(root, "*", SearchOption.AllDirectories))
            {
                var ext = Path.GetExtension(file).TrimStart('.').ToLowerInvariant();
                if (!formats.Contains(ext))
                    continue;

                try
                {
                    var outPath = ConvertToAscii(file, outputWidth: outputWidth,
                        resolution: resolution, useExtendedRamp: useExtendedRamp, invert: invert);
                    Console.WriteLine($"Converted: {file} -> {outPath}");
                    count++;
                }
                catch (Exception e)
                {
                    Console.WriteLine($"Failed: {file} -> {e.Message}");
                }
            }

            Console.WriteLine($"\nProcessed {count} file(s).");
        }

        // =========================
        // ENTRYPOINT
        // =========================

        // Main execution entry point - can be adapted to command-line arguments
        // or hardcoded values for testing.
        public static void Main(string[] args)
        {
            // =========================
            // CONFIG (USER-FACING)
            // =========================

            string? folderToCrawl = null;        // e.g. "my_images"
            string? singleFile = null;           // e.g. "photo.png"

            int? outputWidth = null;             // explicit char width (overrides resolution)
                                                 // set to null to auto-derive from image size
            int resolution = 100;               // percentage of image width (1-500)
                                                 // only used when outputWidth is null
                                                 // 100 = native, 50 = half, 200 = double
            bool? useExtendedRamp = null;        // true = force extended (70 levels)
                                                 // false = force standard (10 levels)
                                                 // null = auto-select based on width
            bool invertBrightness = false;       // true for dark terminal backgrounds

            // =========================
            // RUN
            // =========================

            if (!string.IsNullOrEmpty(singleFile))
            {
                ProcessSingleFile(
                    file: singleFile,
                    outputWidth: outputWidth,
                    resolution: resolution,
                    useExtendedRamp: useExtendedRamp,
                    invert: invertBrightness
                );
            }

            if (!string.IsNullOrEmpty(folderToCrawl))
            {
                ProcessDirectory(
                    root: folderToCrawl,
                    outputWidth: outputWidth,
                    resolution: resolution,
                    useExtendedRamp: useExtendedRamp,
                    invert: invertBrightness
                );
            }

            if (string.IsNullOrEmpty(singleFile) && string.IsNullOrEmpty(folderToCrawl))
            {
                Console.WriteLine("No input configured. Set 'singleFile' or 'folderToCrawl' "
                    + "in the CONFIG section.");
            }

            Console.WriteLine("\nDone.");
        }
    }
}
