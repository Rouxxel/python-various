"""
Image to ASCII Art Converter

Converts raster images (PNG, JPEG, WEBP, BMP, GIF, TIFF) into ASCII art text files.
The core algorithm maps each pixel's grayscale luminance to a character from a
density-ordered ramp, producing a plain .txt file viewable in any monospaced font
editor or terminal.

Pipeline (step by step):

    image.png → [Load & Grayscale] → [Compute Width] → [Resize] → [Map pixels to chars] → image.txt

    1. Load & Grayscale: Open the image and convert to single-channel brightness (0-255).
    2. Compute Width: Read the image's native pixel width and apply the resolution
       percentage (1-500). 100 = image width in chars, 50 = half, 200 = double.
    3. Resize: Shrink/expand to computed character width, applying aspect ratio
       correction (terminal chars are ~2x taller than wide, so height is scaled by ~0.55).
    4. Map pixels to chars: Each pixel brightness maps to a character in the ramp.
       Dense characters (@, #, %) represent dark pixels, light characters (., space)
       represent bright pixels. The ramp is auto-selected based on effective width
       (extended 70-level ramp for width >= 150, standard 10-level otherwise).
    5. Write output: Join character rows with newlines and save as .txt file.

This module provides:

- Conversion of images to ASCII art .txt files
- Resolution-based width: automatically derives output width from image dimensions
- Resolution percentage (1-500): controls detail level relative to the source image
- Auto ramp selection: extended (70 levels) for high-res, standard (10 levels) for low-res
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

# Default resolution percentage (100 = image's native pixel width in characters)
DEFAULT_RESOLUTION = 100

# Min/max resolution bounds
MIN_RESOLUTION = 1
MAX_RESOLUTION = 500

# Threshold: use extended ramp when effective width >= this value
AUTO_RAMP_THRESHOLD = 150

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
# RESOLUTION LOGIC
# =========================

def compute_width_from_resolution(image_width: int, resolution: int) -> int:
    """
    Compute the output character width from the image's native width and a
    resolution percentage.

    resolution=100 means 1 pixel = 1 character (native width).
    resolution=50 means half the characters. resolution=200 means double.
    Clamped to [MIN_RESOLUTION, MAX_RESOLUTION].
    """
    resolution = max(MIN_RESOLUTION, min(MAX_RESOLUTION, resolution))
    width = int(image_width * (resolution / 100))
    return max(1, width)


def select_char_ramp(effective_width: int) -> str:
    """
    Auto-select character ramp based on effective output width.

    Uses the extended 70-level ramp for higher detail outputs (width >= 150),
    and the standard 10-level ramp for smaller outputs.
    """
    if effective_width >= AUTO_RAMP_THRESHOLD:
        return CHAR_RAMP_EXTENDED
    return CHAR_RAMP_STANDARD


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
    output_width: int = None,
    resolution: int = DEFAULT_RESOLUTION,
    char_ramp: str = None,
    use_extended_ramp: bool = None,
    aspect_ratio_correction: float = ASPECT_RATIO_CORRECTION,
    invert: bool = False
) -> Path:
    """
    Full pipeline: load → grayscale → compute width → resize → map → write.

    Width priority:
      - If output_width is set (not None): use that exact character width.
      - If output_width is None: derive from image width * (resolution / 100).

    Ramp priority:
      - If use_extended_ramp is True: force extended ramp (70 levels).
      - If use_extended_ramp is False: force standard ramp (10 levels).
      - If use_extended_ramp is None: auto-select based on effective width
        (extended if width >= 150, standard otherwise).
      - If char_ramp is explicitly provided, it overrides everything above.

    If output_path is None, writes to the same directory with .txt extension.
    Returns the path to the output file.
    """
    resolution = max(MIN_RESOLUTION, min(MAX_RESOLUTION, resolution))

    if output_path is None:
        output_path = image_path.with_suffix(".txt")

    img = load_and_prepare_image(image_path)

    # Determine effective width
    if output_width is not None:
        if output_width < 1:
            raise ValueError("output_width must be a positive integer.")
        effective_width = output_width
    else:
        effective_width = compute_width_from_resolution(img.width, resolution)

    # Determine character ramp
    if char_ramp is None:
        if use_extended_ramp is True:
            char_ramp = CHAR_RAMP_EXTENDED
        elif use_extended_ramp is False:
            char_ramp = CHAR_RAMP_STANDARD
        else:
            char_ramp = select_char_ramp(effective_width)

    if not char_ramp:
        raise ValueError("Character ramp must be a non-empty string.")

    img = resize_for_terminal(img, effective_width, aspect_ratio_correction)
    lines = map_pixels_to_chars(img, char_ramp, invert)
    write_output(lines, output_path)

    ramp_label = "extended" if len(char_ramp) > 10 else "standard"
    width_source = "manual" if output_width else f"{resolution}%"
    print(f"  Width: {effective_width} chars ({width_source}) | "
          f"Ramp: {ramp_label}")

    return output_path


# =========================
# SINGLE FILE MODE
# =========================

def process_single_file(
    file: str,
    output_width: int = None,
    resolution: int = DEFAULT_RESOLUTION,
    use_extended_ramp: bool = None,
    aspect_ratio_correction: float = ASPECT_RATIO_CORRECTION,
    invert: bool = False
) -> None:
    """
    Process one image file and convert to ASCII art .txt.

    Validates file exists and has a supported extension.
    If output_width is None, derives width from image size * resolution%.
    """
    path = Path(file)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = path.suffix.lower().replace(".", "")
    if ext not in INPUT_FORMATS:
        raise ValueError(
            f"Unsupported format: .{ext}. Supported: {INPUT_FORMATS}"
        )

    try:
        out = convert_to_ascii(
            path, output_width=output_width, resolution=resolution,
            use_extended_ramp=use_extended_ramp,
            aspect_ratio_correction=aspect_ratio_correction, invert=invert
        )
        print(f"Converted: {path} -> {out}")
    except Exception as e:
        print(f"Failed: {path} -> {e}")


# =========================
# DIRECTORY MODE
# =========================

def process_directory(
    root: str,
    source_formats: list[str] = None,
    output_width: int = None,
    resolution: int = DEFAULT_RESOLUTION,
    use_extended_ramp: bool = None,
    aspect_ratio_correction: float = ASPECT_RATIO_CORRECTION,
    invert: bool = False
) -> None:
    """
    Recursively scan a directory and convert all matching images to ASCII .txt files.

    Only files matching source_formats are processed.
    If output_width is None, each image's width is derived from its own
    native size * resolution%.
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
                out = convert_to_ascii(
                    file, output_width=output_width,
                    resolution=resolution,
                    use_extended_ramp=use_extended_ramp,
                    aspect_ratio_correction=aspect_ratio_correction,
                    invert=invert
                )
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

    folder_to_crawl = None              # e.g. "my_images"
    single_file = "sdf.png"             # e.g. "photo.png"

    output_width = None                 # explicit char width (overrides resolution)
                                        # set to None to auto-derive from image size
    resolution = 150                    # percentage of image width (1-500)
                                        # only used when output_width is None
                                        # 100 = native, 50 = half, 200 = double
    use_extended_ramp = True            # True = force extended (70 levels)
                                        # False = force standard (10 levels)
                                        # None = auto-select based on width
    invert_brightness = False           # True for dark terminal backgrounds

    # =========================
    # RUN
    # =========================

    if single_file:
        process_single_file(
            file=single_file,
            output_width=output_width,
            resolution=resolution,
            use_extended_ramp=use_extended_ramp,
            invert=invert_brightness
        )

    if folder_to_crawl:
        process_directory(
            root=folder_to_crawl,
            output_width=output_width,
            resolution=resolution,
            use_extended_ramp=use_extended_ramp,
            invert=invert_brightness
        )

    if not single_file and not folder_to_crawl:
        print("No input configured. Set 'single_file' or 'folder_to_crawl' "
              "in the CONFIG section.")

    print("\nDone.")
