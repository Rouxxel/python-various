"""
Image Converter Utility

A lightweight, extensible image conversion tool supporting both raster and vector workflows.

This module provides:

- Conversion between PNG, JPG, JPEG, WEBP, and SVG
- Multi-target output generation (e.g. ["png", "jpg", "webp"])
- Recursive directory processing
- Single-file processing mode
- Optional image upscaling before export
- JPEG quality control
- Optional deletion of source files after successful conversion

Design Philosophy:
- Keep the conversion pipeline functional and explicit
- Avoid global mutable state inside core logic
- Separate IO (loading/saving) from transformation logic
- Ensure safe multi-target conversion without data loss

Supported Conversions:
- Raster ↔ Raster (PIL-based)
- SVG → Raster (via CairoSVG)
- Raster → SVG (embedded base64 image, NOT vectorization)

Dependencies:
- Pillow
- cairosvg
"""

from pathlib import Path
from base64 import b64encode
import io
import os
import sys

from PIL import Image
import cairosvg

# =========================
# CONFIG
# =========================

INPUT_FORMATS = ["png", "jpg", "jpeg", "webp", "svg"]

# =========================
# CORE UTILITIES
# =========================

def upscale(img: Image.Image, factor: float) -> Image.Image:
    if factor <= 1:
        return img
    return img.resize(
        (int(img.width * factor), int(img.height * factor)),
        Image.Resampling.LANCZOS
    )


def ensure_rgb(img: Image.Image) -> Image.Image:
    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        return bg
    return img.convert("RGB")


# =========================
# LOADERS
# =========================

def load_image(path: Path) -> Image.Image:
    """
    Loads an image from disk.

    Supports:
    - Raster formats via Pillow
    - SVG via CairoSVG (converted to PNG in-memory)
    """
    ext = path.suffix.lower()

    if ext == ".svg":
        png_bytes = cairosvg.svg2png(url=str(path))
        return Image.open(io.BytesIO(png_bytes))

    return Image.open(path)


# =========================
# SAVERS
# =========================

def save_image(img: Image.Image, out_path: Path, fmt: str, jpeg_quality:int = 85):
    """
    Saves an image to disk in the specified format.

    Handles:
    - JPEG conversion with RGB normalization
    - Quality and optimization settings for JPEG output
    """
    fmt = fmt.lower()

    out_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt in ("jpg", "jpeg"):
        img = ensure_rgb(img)
        img.save(out_path, quality=jpeg_quality, optimize=True)
    else:
        img.save(out_path)


def raster_to_svg(img_path: Path, out_path: Path):
    """
    Embeds a raster image inside an SVG file using base64 encoding.

    Note:
    This is NOT vectorization — the image is embedded as-is.
    """
    with open(img_path, "rb") as f:
        encoded = b64encode(f.read()).decode()

    img = Image.open(img_path)
    mime = "image/png" if img_path.suffix.lower() == ".png" else "image/jpeg"

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg"
         width="{img.width}" height="{img.height}">
        <image href="data:{mime};base64,{encoded}"
               width="{img.width}" height="{img.height}" />
    </svg>
    """

    out_path.write_text(svg, encoding="utf-8")


# =========================
# CONVERSION CORE
# =========================

def convert_file(
    path: Path, 
    targets: list[str] = INPUT_FORMATS, 
    upscale_factor:float = 1.0,
    jpeg_quality:int = 85,
    delete_original: bool = False
):
    """
    Converts a single image file into one or more target formats.

    Workflow:
    1. Detect input format
    2. Load image (SVG or raster)
    3. Apply optional upscaling
    4. Export to each target format
    5. Optionally delete original after successful conversion

    Note:
    - SVG → raster uses CairoSVG
    - Raster → SVG embeds image (no vectorization)
    """
    src_ext = path.suffix.lower().replace(".", "")

    img = None

    for target in targets:
        out_path = path.with_suffix(f".{target}")

        try:
            # SVG → raster
            if src_ext == "svg" and target != "svg":
                img = load_image(path)
                img = upscale(img, upscale_factor)
                save_image(img, out_path, target,jpeg_quality)

            # raster → SVG
            elif target == "svg" and src_ext != "svg":
                raster_to_svg(path, out_path)

            # raster → raster
            elif src_ext != "svg" and target != "svg":
                if img is None:
                    img = load_image(path)

                img = upscale(img, upscale_factor)
                save_image(img, out_path, target,jpeg_quality)

            else:
                continue

            print(f"Converted: {path} -> {out_path}")

            if delete_original:
                try:
                    path.unlink()
                    print(f"Deleted original: {path}")
                except Exception as e:
                    print(f"Failed to delete {path}: {e}")

        except Exception as e:
            print(f"Failed: {path} ({target}) -> {e}")


# =========================
# DIRECTORY MODE
# =========================

def process_directory(
    root: str,  
    targets: list[str],
    source_formats: list[str] = INPUT_FORMATS,
    upscale_factor:float = 1.0,
    jpeg_quality: int = 85,
    delete_original: bool = False
):
    """
    Recursively scans a directory and converts all matching image files.

    Only files matching `source_formats` are processed.
    Each file is passed to `convert_file`.
    """
    root_path = Path(root)

    for file in root_path.rglob("*"):
        if file.suffix.lower().replace(".", "") in source_formats:
            convert_file(file, targets,upscale_factor,jpeg_quality,delete_original)


# =========================
# SINGLE FILE MODE
# =========================

def process_single_file(
    file: str, 
    targets: list[str],
    upscale_factor:float = 1.0,
    jpeg_quality: int = 85,
    delete_original: bool = False
):
    """
    Processes a single image file and converts it to target formats.

    Wrapper around `convert_file` for CLI-style usage.
    """
    path = Path(file)

    if not path.exists():
        raise FileNotFoundError(path)

    convert_file(path, targets,upscale_factor,jpeg_quality,delete_original)


# =========================
# ENTRYPOINT
# =========================

if __name__ == "__main__":

    # =========================
    # CONFIG (USER-FACING)
    # =========================

    folder_to_crawl = None  # e.g. "my_project"
    single_file = None  # e.g. "image.png"

    input_formats = ["png", "jpg", "jpeg", "webp", "svg"]
    target_formats = ["jpg"]   # <- now supports MULTIPLE outputs

    if single_file:
        process_single_file(
            file=single_file,
            targets=target_formats,
            upscale_factor=1.0,
            jpeg_quality=85,
            delete_original=False
        )

    if folder_to_crawl:
        process_directory(
            root=folder_to_crawl,
            targets=target_formats,
            source_formats=input_formats,
            upscale_factor=1.0,
            jpeg_quality=85,
            delete_original=False
        )

    print("\nDone.")
