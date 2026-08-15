"""
Image to ASCII Art Converter

Converts raster images (PNG, JPEG, WEBP, BMP, GIF, TIFF) into ASCII art text files.
The core algorithm maps each pixel's grayscale luminance to a character from a
density-ordered ramp, producing a plain .txt file viewable in any monospaced font
editor or terminal.

Pipeline (step by step):

    image.png → [Load & Grayscale] → [Resize] → [Map pixels to chars] → image.txt

    1. Load & Grayscale: Open the image and convert to single-channel brightness (0-255).
    2. Resize: Shrink to target character width, applying aspect ratio correction
       (terminal chars are ~2x taller than wide, so height is scaled by ~0.55).
    3. Map pixels to chars: Each pixel brightness maps to a character in the ramp.
       Dense characters (@, #, %) represent dark pixels, light characters (., space)
       represent bright pixels.
    4. Write output: Join character rows with newlines and save as .txt file.

This module provides:

- Conversion of images to ASCII art .txt files
- Configurable output width (characters per line)
- Two character ramps: standard (10 levels) and extended (70 levels)
- Aspect ratio correction for terminal display
- Inverted mode for dark terminal backgrounds
- Single-file and recursive directory processing modes

Design Philosophy:
- Functional core with explicit helper functions
- Separate loading/resizing from character mapping
- Configurable via constants at the top

Dependencies:
- Pillow
"""

from pathlib import Path
from PIL import Image

# =========================
# CONFIG
# =========================

INPUT_FORMATS = ["png", "jpg", "jpeg", "webp", "bmp", "gif", "tiff", "tif"]

# Character ramp from darkest (most dense) to lightest (least dense)
CHAR_RAMP_STANDARD = "@%#*+=-:. "

# Extended ramp with more granularity (70 levels)
CHAR_RAMP_EXTENDED = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

# Default output width in characters
DEFAULT_WIDTH = 120

# Aspect ratio correction (terminal chars are ~2x taller than wide)
ASPECT_RATIO_CORRECTION = 0.55


# =========================
# IMAGE LOADING
# =========================

def load_and_prepare_image(path: Path) -> Image.Image:
    """
    Load an image file and convert to grayscale ('L' mode).

    Supports any format Pillow can open (PNG, JPEG, WEBP, BMP, GIF, TIFF).
    """
    img = Image.open(path)
    return img.convert("L")


# =========================
# RESIZE
# =========================

def resize_for_terminal(
    img: Image.Image,
    width: int,
    aspect_ratio_correction: float
) -> Image.Image:
    """
    Resize image to fit target character width with height correction.

    Terminal characters are taller than they are wide, so the height is
    scaled down by the correction factor to avoid vertical stretching.
    """
    original_width, original_height = img.size
    scale_factor = width / original_width
    new_height = int(original_height * scale_factor * aspect_ratio_correction)
    new_height = max(1, new_height)

    return img.resize((width, new_height), Image.Resampling.LANCZOS)


# =========================
# PIXEL TO CHARACTER MAPPING
# =========================

def map_pixels_to_chars(
    img: Image.Image,
    char_ramp: str,
    invert: bool
) -> list[str]:
    """
    Map each pixel row to a string of ASCII characters.

    Each pixel value [0, 255] is mapped to an index in the character ramp.
    In normal mode, dark pixels map to dense characters.
    In inverted mode, dark pixels map to light characters (for dark backgrounds).
    """
    pixels = list(img.getdata())
    width = img.width
    ramp_len = len(char_ramp)
    lines = []

    for row_start in range(0, len(pixels), width):
        row_pixels = pixels[row_start:row_start + width]
        row_chars = []

        for pixel_value in row_pixels:
            if invert:
                pixel_value = 255 - pixel_value

            index = pixel_value * (ramp_len - 1) // 255
            row_chars.append(char_ramp[index])

        lines.append("".join(row_chars))

    return lines


# =========================
# OUTPUT WRITER
# =========================

def write_output(lines: list[str], output_path: Path) -> None:
    """Write ASCII art lines to a text file (UTF-8)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


# =========================
# CONVERSION CORE
# =========================

def convert_to_ascii(
    image_path: Path,
    output_path: Path = None,
    width: int = DEFAULT_WIDTH,
    char_ramp: str = CHAR_RAMP_STANDARD,
    aspect_ratio_correction: float = ASPECT_RATIO_CORRECTION,
    invert: bool = False
) -> Path:
    """
    Full pipeline: load → grayscale → resize → map → write.

    If output_path is None, writes to the same directory with .txt extension.
    Returns the path to the output file.
    """
    if width < 1:
        raise ValueError("Width must be a positive integer.")

    if not char_ramp:
        raise ValueError("Character ramp must be a non-empty string.")

    if output_path is None:
        output_path = image_path.with_suffix(".txt")

    img = load_and_prepare_image(image_path)
    img = resize_for_terminal(img, width, aspect_ratio_correction)
    lines = map_pixels_to_chars(img, char_ramp, invert)
    write_output(lines, output_path)

    return output_path


# =========================
# SINGLE FILE MODE
# =========================

def process_single_file(
    file: str,
    width: int = DEFAULT_WIDTH,
    char_ramp: str = CHAR_RAMP_STANDARD,
    aspect_ratio_correction: float = ASPECT_RATIO_CORRECTION,
    invert: bool = False
) -> None:
    """
    Process one image file and convert to ASCII art .txt.

    Validates file exists and has a supported extension.
    """
    path = Path(file)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = path.suffix.lower().replace(".", "")
    if ext not in INPUT_FORMATS:
        raise ValueError(f"Unsupported format: .{ext}. Supported: {INPUT_FORMATS}")

    try:
        out = convert_to_ascii(path, width=width, char_ramp=char_ramp,
                               aspect_ratio_correction=aspect_ratio_correction, invert=invert)
        print(f"Converted: {path} -> {out}")
    except Exception as e:
        print(f"Failed: {path} -> {e}")


# =========================
# DIRECTORY MODE
# =========================

def process_directory(
    root: str,
    source_formats: list[str] = None,
    width: int = DEFAULT_WIDTH,
    char_ramp: str = CHAR_RAMP_STANDARD,
    aspect_ratio_correction: float = ASPECT_RATIO_CORRECTION,
    invert: bool = False
) -> None:
    """
    Recursively scan a directory and convert all matching images to ASCII .txt files.

    Only files matching source_formats are processed.
    Failed conversions print an error but don't halt processing.
    """
    if source_formats is None:
        source_formats = INPUT_FORMATS

    root_path = Path(root)

    if not root_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {root_path}")

    count = 0
    for file in root_path.rglob("*"):
        if file.suffix.lower().replace(".", "") in source_formats:
            try:
                out = convert_to_ascii(file, width=width, char_ramp=char_ramp,
                                       aspect_ratio_correction=aspect_ratio_correction, invert=invert)
                print(f"Converted: {file} -> {out}")
                count += 1
            except Exception as e:
                print(f"Failed: {file} -> {e}")

    print(f"\nProcessed {count} file(s).")


# =========================
# ENTRYPOINT
# =========================

if __name__ == "__main__":

    # =========================
    # CONFIG (USER-FACING)
    # =========================

    folder_to_crawl = None      # e.g. "my_images"
    single_file = "logo (16).png"          # e.g. "photo.png"

    output_width = 120          # characters per line
    use_extended_ramp = False   # True for 70-level detail, False for 10-level
    invert_brightness = False   # True for dark terminal backgrounds

    # =========================
    # RUN
    # =========================

    ramp = CHAR_RAMP_EXTENDED if use_extended_ramp else CHAR_RAMP_STANDARD

    if single_file:
        process_single_file(
            file=single_file,
            width=output_width,
            char_ramp=ramp,
            invert=invert_brightness
        )

    if folder_to_crawl:
        process_directory(
            root=folder_to_crawl,
            width=output_width,
            char_ramp=ramp,
            invert=invert_brightness
        )

    if not single_file and not folder_to_crawl:
        print("No input configured. Set 'single_file' or 'folder_to_crawl' in the CONFIG section.")

    print("\nDone.")
