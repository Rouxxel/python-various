// NOTE: These helper files are intended to be copied into other projects.
// Change the namespace `cs_various_utils` below to match your project's namespace
// before integrating.
//
// Image Converter Utility
//
// A lightweight, extensible image conversion tool supporting both raster and vector workflows.
//
// This module provides:
// - Conversion between PNG, JPG, JPEG, WEBP, and SVG
// - Multi-target output generation (e.g. ["png", "jpg", "webp"])
// - Recursive directory processing
// - Single-file processing mode
// - Optional image upscaling before export
// - JPEG quality control
// - Optional deletion of source files after successful conversion
//
// Supported Conversions:
// - Raster <-> Raster (SkiaSharp-based)
// - SVG -> Raster (via Svg.Skia)
// - Raster -> SVG (embedded base64 image, NOT vectorization)
//
// Required NuGet packages:
// - SkiaSharp
// - Svg.Skia
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using SkiaSharp;
using Svg.Skia;

// Change namespace based on whatever project is implemented
namespace cs_various_utils
{
    public static class ImageConverter
    {
        // =========================
        // CONFIG
        // =========================

        public static readonly string[] InputFormats = { "png", "jpg", "jpeg", "webp", "svg" };

        private static readonly SKSamplingOptions HighQualitySampling =
            new(SKCubicResampler.Mitchell);

        // =========================
        // CORE UTILITIES
        // =========================

        private static SKBitmap Upscale(
            SKBitmap bitmap,
            double factor
            )
        {
            if (factor <= 1)
                return bitmap;

            var newWidth = (int)(bitmap.Width * factor);
            var newHeight = (int)(bitmap.Height * factor);
            return bitmap.Resize(
                new SKImageInfo(newWidth, newHeight),
                HighQualitySampling
            ) ?? throw new InvalidOperationException("Failed to upscale image.");
        }

        private static SKBitmap FlattenOnWhite(
            SKBitmap bitmap
            )
        {
            var flattened = new SKBitmap(bitmap.Width, bitmap.Height, SKColorType.Rgba8888, SKAlphaType.Opaque);
            using var canvas = new SKCanvas(flattened);
            canvas.Clear(SKColors.White);
            canvas.DrawBitmap(bitmap, 0, 0);
            return flattened;
        }

        // =========================
        // LOADERS
        // =========================

        /// <summary>
        /// Loads an image from disk.
        /// Supports raster formats via SkiaSharp and SVG via Svg.Skia (rasterized in-memory).
        /// </summary>
        private static SKBitmap LoadImage(
            string path
            )
        {
            var ext = Path.GetExtension(path).ToLowerInvariant();

            if (ext == ".svg")
                return RasterizeSvg(path);

            var bitmap = SKBitmap.Decode(path);
            if (bitmap == null)
                throw new InvalidOperationException($"Failed to load image: {path}");

            return bitmap;
        }

        private static SKBitmap RasterizeSvg(
            string path
            )
        {
            using var svg = new SKSvg();
            svg.Load(path);

            if (svg.Picture == null)
                throw new InvalidOperationException($"Failed to load SVG: {path}");

            var bounds = svg.Picture.CullRect;
            var width = (int)Math.Ceiling(bounds.Width);
            var height = (int)Math.Ceiling(bounds.Height);

            if (width <= 0 || height <= 0)
            {
                width = 100;
                height = 100;
            }

            var bitmap = new SKBitmap(width, height);
            using var canvas = new SKCanvas(bitmap);
            canvas.Clear(SKColors.Transparent);
            canvas.DrawPicture(svg.Picture);
            return bitmap;
        }

        // =========================
        // SAVERS
        // =========================

        /// <summary>
        /// Saves an image to disk in the specified format.
        /// Handles JPEG conversion with RGB normalization and quality settings.
        /// </summary>
        private static void SaveImage(
            SKBitmap bitmap,
            string outPath,
            string fmt,
            int jpegQuality = 85
            )
        {
            fmt = fmt.ToLowerInvariant();

            var outDir = Path.GetDirectoryName(outPath);
            if (!string.IsNullOrEmpty(outDir))
                Directory.CreateDirectory(outDir);

            SKBitmap? flattened = null;
            var toEncode = bitmap;

            if (fmt is "jpg" or "jpeg" && bitmap.AlphaType != SKAlphaType.Opaque)
            {
                flattened = FlattenOnWhite(bitmap);
                toEncode = flattened;
            }

            try
            {
                using var image = SKImage.FromBitmap(toEncode);
                using var data = fmt switch
                {
                    "jpg" or "jpeg" => image.Encode(SKEncodedImageFormat.Jpeg, jpegQuality),
                    "png" => image.Encode(SKEncodedImageFormat.Png, 100),
                    "webp" => image.Encode(SKEncodedImageFormat.Webp, jpegQuality),
                    _ => throw new NotSupportedException($"Unsupported output format: {fmt}")
                };

                if (data == null)
                    throw new InvalidOperationException($"Failed to encode image as {fmt}.");

                using var stream = File.OpenWrite(outPath);
                data.SaveTo(stream);
            }
            finally
            {
                flattened?.Dispose();
            }
        }

        /// <summary>
        /// Embeds a raster image inside an SVG file using base64 encoding.
        /// Note: This is NOT vectorization — the image is embedded as-is.
        /// </summary>
        private static void RasterToSvg(
            string imgPath,
            string outPath
            )
        {
            var encoded = Convert.ToBase64String(File.ReadAllBytes(imgPath));

            using var bitmap = SKBitmap.Decode(imgPath)
                ?? throw new InvalidOperationException($"Failed to load image: {imgPath}");

            var ext = Path.GetExtension(imgPath).ToLowerInvariant();
            var mime = ext == ".png" ? "image/png" : "image/jpeg";

            var svg = $"""
                <svg xmlns="http://www.w3.org/2000/svg"
                     width="{bitmap.Width}" height="{bitmap.Height}">
                    <image href="data:{mime};base64,{encoded}"
                           width="{bitmap.Width}" height="{bitmap.Height}" />
                </svg>
                """;

            var outDir = Path.GetDirectoryName(outPath);
            if (!string.IsNullOrEmpty(outDir))
                Directory.CreateDirectory(outDir);

            File.WriteAllText(outPath, svg);
        }

        // =========================
        // CONVERSION CORE
        // =========================

        /// <summary>
        /// Converts a single image file into one or more target formats.
        /// SVG -> raster uses Svg.Skia; raster -> SVG embeds image (no vectorization).
        /// </summary>
        public static void ConvertFile(
            string path,
            IEnumerable<string>? targets = null,
            double upscaleFactor = 1.0,
            int jpegQuality = 85,
            bool deleteOriginal = false
            )
        {
            var targetList = targets?.ToArray() ?? InputFormats;
            var srcExt = Path.GetExtension(path).TrimStart('.').ToLowerInvariant();

            SKBitmap? img = null;

            try
            {
                foreach (var target in targetList)
                {
                    var outPath = Path.ChangeExtension(path, target);

                    try
                    {
                        // SVG -> raster
                        if (srcExt == "svg" && target != "svg")
                        {
                            img?.Dispose();
                            img = LoadImage(path);
                            using var upscaled = Upscale(img, upscaleFactor);
                            SaveImage(upscaled, outPath, target, jpegQuality);
                        }
                        // raster -> SVG
                        else if (target == "svg" && srcExt != "svg")
                        {
                            RasterToSvg(path, outPath);
                        }
                        // raster -> raster
                        else if (srcExt != "svg" && target != "svg")
                        {
                            if (img == null)
                                img = LoadImage(path);

                            var previous = img;
                            img = Upscale(img, upscaleFactor);
                            if (!ReferenceEquals(previous, img))
                                previous.Dispose();

                            SaveImage(img, outPath, target, jpegQuality);
                        }
                        else
                        {
                            continue;
                        }

                        Console.WriteLine($"Converted: {path} -> {outPath}");

                        if (deleteOriginal)
                        {
                            try
                            {
                                File.Delete(path);
                                Console.WriteLine($"Deleted original: {path}");
                            }
                            catch (Exception e)
                            {
                                Console.WriteLine($"Failed to delete {path}: {e.Message}");
                            }
                        }
                    }
                    catch (Exception e)
                    {
                        Console.WriteLine($"Failed: {path} ({target}) -> {e.Message}");
                    }
                }
            }
            finally
            {
                img?.Dispose();
            }
        }

        // =========================
        // DIRECTORY MODE
        // =========================

        /// <summary>
        /// Recursively scans a directory and converts all matching image files.
        /// Only files matching sourceFormats are processed.
        /// </summary>
        public static void ProcessDirectory(
            string root,
            IEnumerable<string> targets,
            IEnumerable<string>? sourceFormats = null,
            double upscaleFactor = 1.0,
            int jpegQuality = 85,
            bool deleteOriginal = false
            )
        {
            var formats = new HashSet<string>(
                (sourceFormats ?? InputFormats).Select(f => f.ToLowerInvariant())
            );

            foreach (var file in Directory.EnumerateFiles(root, "*", SearchOption.AllDirectories))
            {
                var ext = Path.GetExtension(file).TrimStart('.').ToLowerInvariant();
                if (formats.Contains(ext))
                {
                    ConvertFile(file, targets, upscaleFactor, jpegQuality, deleteOriginal);
                }
            }
        }

        // =========================
        // SINGLE FILE MODE
        // =========================

        /// <summary>
        /// Processes a single image file and converts it to target formats.
        /// Wrapper around ConvertFile for CLI-style usage.
        /// </summary>
        public static void ProcessSingleFile(
            string file,
            IEnumerable<string> targets,
            double upscaleFactor = 1.0,
            int jpegQuality = 85,
            bool deleteOriginal = false
            )
        {
            if (!File.Exists(file))
                throw new FileNotFoundException("File not found.", file);

            ConvertFile(file, targets, upscaleFactor, jpegQuality, deleteOriginal);
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

            string? folderToCrawl = null; // e.g. "my_project"
            string? singleFile = null;    // e.g. "image.png"

            var inputFormats = new[] { "png", "jpg", "jpeg", "webp", "svg" };
            var targetFormats = new[] { "jpg" }; // supports MULTIPLE outputs

            if (!string.IsNullOrEmpty(singleFile))
            {
                ProcessSingleFile(
                    file: singleFile,
                    targets: targetFormats,
                    upscaleFactor: 1.0,
                    jpegQuality: 85,
                    deleteOriginal: false
                );
            }

            if (!string.IsNullOrEmpty(folderToCrawl))
            {
                ProcessDirectory(
                    root: folderToCrawl,
                    targets: targetFormats,
                    sourceFormats: inputFormats,
                    upscaleFactor: 1.0,
                    jpegQuality: 85,
                    deleteOriginal: false
                );
            }

            Console.WriteLine("\nDone.");
        }
    }
}
