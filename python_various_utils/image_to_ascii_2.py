"""
Image to ASCII Art Converter

Converts raster images (PNG, JPEG, WEBP, BMP, GIF, TIFF) into ASCII art text files.

Pipeline:
    image → load (EXIF + alpha) → grayscale + RGB → compute width → resize → map → write

Batch features:
    - Recursive directory processing with per-file error isolation
    - Optional output directory (mirrors source tree)
    - Skip unchanged outputs (--skip-existing)
    - Hard caps on output dimensions (OOM guard)
    - Atomic writes and closed image handles
    - Structured BatchStats + argparse CLI

Dependencies:
    - Pillow

Output formats:
    - txt  : plain text (default)
    - ansi : terminal true-color (RGB ANSI escape codes per character)
    - html : zoomable viewer in any browser (optional per-character color)
    - png  : raster image you can open/resize in any image viewer
    - all  : write txt + ansi + html + png (when --color, ansi/html/png use color)

Examples (run from ``python_various_utils/``):

Plain text (writes ``photo.txt`` next to the source image)::

    python image_to_ascii_2.py --file photo.png

Fixed character width (80 columns)::

    python image_to_ascii_2.py --file photo.png --width 80

Scale by resolution (% of image width, default 100)::

    python image_to_ascii_2.py --file photo.png --resolution 50

Zoomable HTML viewer (open ``photo.html`` in a browser; use the slider to resize)::

    python image_to_ascii_2.py --file photo.png --width 120 --format html

PNG image you can zoom in any viewer/editor (``photo.png`` ASCII raster)::

    python image_to_ascii_2.py --file photo.png --width 120 --format png

Terminal colors (``photo.ansi.txt`` — view with Windows Terminal, iTerm, etc.)::

    python image_to_ascii_2.py --file photo.png --width 80 --format ansi

Colored HTML + PNG + plain txt + ANSI in one run::

    python image_to_ascii_2.py --file photo.png --width 80 --format all --color

Dark terminal / inverted brightness::

    python image_to_ascii_2.py --file photo.png --width 80 --format ansi --invert

One character per source pixel (large output; may need ``--allow-large``)::

    python image_to_ascii_2.py --file photo.png --pixel-grid --allow-large

Batch: convert every image under a folder, mirror tree into ``./ascii_out/``::

    python image_to_ascii_2.py --dir ./photos --output-dir ./ascii_out --width 100 --format html

Re-run batch but skip files whose outputs are already up to date::

    python image_to_ascii_2.py --dir ./photos --output-dir ./ascii_out --skip-existing
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFont, ImageOps

# =========================
# CONFIG
# =========================

INPUT_FORMATS = ["png", "jpg", "jpeg", "webp", "bmp", "gif", "tiff", "tif"]

CHAR_RAMP_STANDARD = "@%#*+=-:. "
CHAR_RAMP_EXTENDED = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

DEFAULT_RESOLUTION = 100
MIN_RESOLUTION = 1
MAX_RESOLUTION = 500

AUTO_RAMP_THRESHOLD = 150
ASPECT_RATIO_CORRECTION = 0.55

# Safety caps for batch runs (character cells, post-resize)
MAX_OUTPUT_WIDTH = 800
MAX_OUTPUT_HEIGHT = 800

BackgroundName = Literal["white", "black"]
ConversionStatus = Literal["converted", "skipped", "failed"]
OutputFormat = Literal["txt", "ansi", "html", "png", "all"]

DEFAULT_PNG_FONT_SIZE = 8
RGB = tuple[int, int, int]


@dataclass(frozen=True)
class AsciiCell:
    """One ASCII character plus its display color."""

    char: str
    rgb: RGB

logger = logging.getLogger("image_to_ascii")


# =========================
# RESULT TYPES
# =========================


@dataclass
class ConversionResult:
    """Outcome of a single file conversion."""

    source: Path
    output: Path | None = None
    status: ConversionStatus = "failed"
    message: str = ""


@dataclass
class BatchStats:
    """Aggregated results for directory processing."""

    converted: int = 0
    skipped: int = 0
    failed: int = 0
    failures: list[tuple[Path, str]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.converted + self.skipped + self.failed


# =========================
# LOGGING
# =========================


def configure_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure module logger for CLI batch runs."""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(levelname)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )
    logger.setLevel(level)


# =========================
# HELPERS
# =========================


def is_supported_image(path: Path, source_formats: list[str] | None = None) -> bool:
    ext = path.suffix.lower().lstrip(".")
    formats = source_formats or INPUT_FORMATS
    return ext in formats


def background_rgb(name: BackgroundName) -> tuple[int, int, int]:
    return (255, 255, 255) if name == "white" else (0, 0, 0)


def resolve_output_base(
    image_path: Path,
    output_path: Path | None,
    *,
    root: Path | None = None,
    output_dir: Path | None = None,
) -> Path:
    """Resolve output base path (extension chosen by output format)."""
    if output_path is not None:
        return output_path.with_suffix("")
    if output_dir is not None and root is not None:
        relative = image_path.relative_to(root)
        return (output_dir / relative).with_suffix("")
    return image_path.with_suffix("")


def output_paths_for_format(
    base: Path,
    output_format: OutputFormat,
    *,
    use_color: bool = False,
) -> list[Path]:
    if output_format == "all":
        paths = [base.with_suffix(".txt"), base.with_suffix(".html"), base.with_suffix(".png")]
        if use_color:
            paths.insert(1, base.with_suffix(".ansi.txt"))
        return paths
    if output_format == "ansi":
        return [base.with_suffix(".ansi.txt")]
    return [base.with_suffix(f".{output_format}")]


def resolve_output_path(
    image_path: Path,
    output_path: Path | None,
    *,
    root: Path | None = None,
    output_dir: Path | None = None,
) -> Path:
    """Backward-compatible helper: returns .txt path."""
    return resolve_output_base(
        image_path, output_path, root=root, output_dir=output_dir
    ).with_suffix(".txt")


def should_skip_existing(source: Path, output: Path) -> bool:
    """True when output exists and is at least as new as the source."""
    if not output.is_file():
        return False
    try:
        return output.stat().st_mtime >= source.stat().st_mtime
    except OSError:
        return False


def ramp_label(char_ramp: str) -> str:
    if char_ramp == CHAR_RAMP_EXTENDED:
        return "extended"
    if char_ramp == CHAR_RAMP_STANDARD:
        return "standard"
    return f"custom({len(char_ramp)})"


def clamp_output_dimensions(
    width: int,
    height: int,
    *,
    allow_large: bool = False,
) -> tuple[int, int]:
    """Clamp resize target to configured max dimensions unless allow_large."""
    width = max(1, width)
    height = max(1, height)
    if allow_large:
        return width, height
    width = min(width, MAX_OUTPUT_WIDTH)
    height = min(height, MAX_OUTPUT_HEIGHT)
    return width, height


# =========================
# IMAGE LOADING
# =========================


def load_image_pair(
    path: Path,
    *,
    background: tuple[int, int, int] = (255, 255, 255),
    gif_frame: int = 0,
) -> tuple[Image.Image, Image.Image]:
    """
    Load image as grayscale + RGB pair (same preprocessing for both).

    Grayscale drives character selection; RGB drives color in ansi/html/png output.
    """
    with Image.open(path) as opened:
        if getattr(opened, "is_animated", False) and gif_frame:
            opened.seek(gif_frame)

        img = ImageOps.exif_transpose(opened)

        has_alpha = img.mode in ("RGBA", "LA") or (
            img.mode == "P" and "transparency" in opened.info
        )
        if has_alpha:
            rgba = img.convert("RGBA")
            base = Image.new("RGBA", rgba.size, background + (255,))
            img = Image.alpha_composite(base, rgba)

        rgb = img.convert("RGB")
        return rgb.convert("L"), rgb


def load_and_prepare_image(
    path: Path,
    *,
    background: tuple[int, int, int] = (255, 255, 255),
    gif_frame: int = 0,
) -> Image.Image:
    """Load grayscale image (backward-compatible helper)."""
    gray, _ = load_image_pair(path, background=background, gif_frame=gif_frame)
    return gray


# =========================
# RESOLUTION / RAMP
# =========================


def compute_width_from_resolution(
    image_width: int,
    resolution: int,
    *,
    allow_large: bool = False,
) -> int:
    resolution = max(MIN_RESOLUTION, min(MAX_RESOLUTION, resolution))
    width = int(image_width * (resolution / 100))
    width = max(1, width)
    if not allow_large:
        width = min(width, MAX_OUTPUT_WIDTH)
    return width


def compute_effective_width(
    img: Image.Image,
    *,
    output_width: int | None,
    resolution: int,
    native_size: bool,
    allow_large: bool,
) -> int:
    """Resolve character width from CLI flags."""
    if output_width is not None:
        width = output_width
    elif native_size:
        width = img.width
    else:
        width = compute_width_from_resolution(
            img.width, resolution, allow_large=allow_large
        )

    if width < 1:
        raise ValueError("output width must be a positive integer.")
    if not allow_large:
        width = min(width, MAX_OUTPUT_WIDTH)
    return width


def select_char_ramp(effective_width: int) -> str:
    if effective_width >= AUTO_RAMP_THRESHOLD:
        return CHAR_RAMP_EXTENDED
    return CHAR_RAMP_STANDARD


# =========================
# RESIZE / MAP / WRITE
# =========================


def resize_for_terminal(
    img: Image.Image,
    width: int,
    aspect_ratio_correction: float,
    *,
    allow_large: bool = False,
) -> Image.Image:
    original_width, original_height = img.size
    scale_factor = width / original_width
    new_height = int(original_height * scale_factor * aspect_ratio_correction)
    width, new_height = clamp_output_dimensions(
        width, max(1, new_height), allow_large=allow_large
    )
    return img.resize((width, new_height), Image.Resampling.LANCZOS)


def map_pixels_to_cells(
    gray: Image.Image,
    rgb: Image.Image,
    char_ramp: str,
    invert: bool,
) -> list[list[AsciiCell]]:
    """Map pixels to characters (from luminance) with colors (from RGB)."""
    if gray.size != rgb.size:
        raise ValueError("grayscale and RGB images must be the same size")

    ramp_len = len(char_ramp)
    max_index = ramp_len - 1
    rows: list[list[AsciiCell]] = []

    for y in range(gray.height):
        row: list[AsciiCell] = []
        for x in range(gray.width):
            pixel_value = gray.getpixel((x, y))
            if invert:
                pixel_value = 255 - pixel_value
            index = pixel_value * max_index // 255
            color = rgb.getpixel((x, y))
            if invert:
                color = (255 - color[0], 255 - color[1], 255 - color[2])
            row.append(AsciiCell(char=char_ramp[index], rgb=color))
        rows.append(row)

    return rows


def cells_to_plain_lines(cells: list[list[AsciiCell]]) -> list[str]:
    return ["".join(cell.char for cell in row) for row in cells]


def map_pixels_to_chars(img: Image.Image, char_ramp: str, invert: bool) -> list[str]:
    rgb = img.convert("RGB")
    cells = map_pixels_to_cells(img, rgb, char_ramp, invert)
    return cells_to_plain_lines(cells)


def write_output(lines: list[str], output_path: Path) -> None:
    """Write ASCII art atomically (temp file + replace)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    content = "\n".join(lines)
    try:
        tmp_path.write_text(content, encoding="utf-8")
        tmp_path.replace(output_path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def _load_monospace_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Best-effort monospace font for PNG rendering."""
    candidates = [
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/cour.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"),
        Path("/System/Library/Fonts/Menlo.ttc"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    logger.warning(
        "No monospace TTF found; PNG quality will be low. "
        "Install Consolas/DejaVu Sans Mono or pass --png-font-size."
    )
    return ImageFont.load_default()


def write_ansi(cells: list[list[AsciiCell]], output_path: Path) -> None:
    """Write true-color ANSI escape codes (view with ``type``, ``cat``, Windows Terminal)."""
    lines: list[str] = []
    for row in cells:
        parts: list[str] = []
        for cell in row:
            r, g, b = cell.rgb
            parts.append(f"\033[38;2;{r};{g};{b}m{cell.char}")
        lines.append("".join(parts) + "\033[0m")
    write_output(lines, output_path)


def _render_html_art(
    lines: list[str],
    cells: list[list[AsciiCell]] | None,
) -> str:
    import html as html_module

    if cells is None:
        return html_module.escape("\n".join(lines))

    rows: list[str] = []
    for row in cells:
        spans = [
            f'<span style="color:rgb({cell.rgb[0]},{cell.rgb[1]},{cell.rgb[2]})">'
            f"{html_module.escape(cell.char)}</span>"
            for cell in row
        ]
        rows.append("".join(spans))
    return "\n".join(rows)


def write_html(
    lines: list[str],
    output_path: Path,
    *,
    title: str,
    invert: bool,
    cells: list[list[AsciiCell]] | None = None,
) -> None:
    """
    Write a self-contained HTML viewer with zoom controls.

    Open in any browser and use the slider to shrink/enlarge the ASCII art.
    Pass ``cells`` for per-character color from the source image.
    """
    import html as html_module

    art_html = _render_html_art(lines, cells)
    bg = "#111" if invert else "#f8f8f8"
    fg = "#eee" if invert else "#111"

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html_module.escape(title)}</title>
  <style>
    body {{
      margin: 0;
      font-family: system-ui, sans-serif;
      background: {bg};
      color: {fg};
    }}
    .toolbar {{
      position: sticky;
      top: 0;
      z-index: 1;
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
      padding: 10px 14px;
      background: rgba(0, 0, 0, 0.05);
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }}
    #viewport {{
      overflow: auto;
      padding: 12px;
      height: calc(100vh - 52px);
    }}
    pre {{
      margin: 0;
      font-family: Consolas, "Courier New", monospace;
      line-height: 1;
      white-space: pre;
      transform-origin: top left;
    }}
  </style>
</head>
<body>
  <div class="toolbar">
    <label>Zoom <input id="zoom" type="range" min="5" max="200" value="100"> <span id="pct">100%</span></label>
    <button type="button" id="fit">Fit width</button>
    <span id="dims"></span>
  </div>
  <div id="viewport">
    <pre id="art">{art_html}</pre>
  </div>
  <script>
    const art = document.getElementById("art");
    const zoom = document.getElementById("zoom");
    const pct = document.getElementById("pct");
    const dims = document.getElementById("dims");
    const viewport = document.getElementById("viewport");

    function applyScale(value) {{
      const scale = value / 100;
      art.style.transform = "scale(" + scale + ")";
      pct.textContent = value + "%";
      dims.textContent = art.textContent.split("\\n")[0].length + " cols × " + art.textContent.split("\\n").length + " rows";
    }}

    zoom.addEventListener("input", () => applyScale(Number(zoom.value)));

    document.getElementById("fit").addEventListener("click", () => {{
      const naturalWidth = art.scrollWidth;
      const target = Math.max(5, Math.min(200, Math.floor((viewport.clientWidth - 24) / naturalWidth * 100)));
      zoom.value = String(target);
      applyScale(target);
    }});

    applyScale(100);
  </script>
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    try:
        tmp_path.write_text(document, encoding="utf-8")
        tmp_path.replace(output_path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def write_png(
    lines: list[str],
    output_path: Path,
    *,
    font_size: int = DEFAULT_PNG_FONT_SIZE,
    invert: bool,
    cells: list[list[AsciiCell]] | None = None,
) -> None:
    """Render ASCII lines to a PNG image (zoomable in any image viewer)."""
    fg = (255, 255, 255) if invert else (0, 0, 0)
    bg = (0, 0, 0) if invert else (255, 255, 255)
    font = _load_monospace_font(font_size)

    probe = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(probe)
    bbox = draw.textbbox((0, 0), "M", font=font)
    char_w = max(1, bbox[2] - bbox[0])
    char_h = max(1, bbox[3] - bbox[1])

    cols = max(len(line) for line in lines) if lines else 1
    rows = len(lines) or 1
    img = Image.new("RGB", (cols * char_w, rows * char_h), bg)
    draw = ImageDraw.Draw(img)

    if cells is None:
        for row_index, line in enumerate(lines):
            draw.text((0, row_index * char_h), line, font=font, fill=fg)
    else:
        for row_index, row in enumerate(cells):
            x = 0
            for cell in row:
                draw.text((x, row_index * char_h), cell.char, font=font, fill=cell.rgb)
                x += char_w

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG")


def write_outputs(
    lines: list[str],
    base_path: Path,
    output_format: OutputFormat,
    *,
    cells: list[list[AsciiCell]] | None = None,
    title: str,
    invert: bool,
    png_font_size: int,
    use_color: bool = False,
) -> list[Path]:
    """Write one or more output formats for the same ASCII result."""
    written: list[Path] = []
    if output_format == "all":
        jobs: list[tuple[str, Path]] = [("txt", base_path.with_suffix(".txt"))]
        if use_color:
            jobs.append(("ansi", base_path.with_suffix(".ansi.txt")))
        jobs.extend(
            [
                ("html", base_path.with_suffix(".html")),
                ("png", base_path.with_suffix(".png")),
            ]
        )
    elif output_format == "ansi":
        jobs = [("ansi", base_path.with_suffix(".ansi.txt"))]
    else:
        jobs = [(output_format, base_path.with_suffix(f".{output_format}"))]

    color_cells = cells if use_color else None

    for fmt, path in jobs:
        if fmt == "txt":
            write_output(lines, path)
        elif fmt == "ansi":
            if cells is None:
                raise ValueError("ANSI output requires color cell data")
            write_ansi(cells, path)
        elif fmt == "html":
            write_html(
                lines,
                path,
                title=title,
                invert=invert,
                cells=color_cells,
            )
        elif fmt == "png":
            write_png(
                lines,
                path,
                font_size=png_font_size,
                invert=invert,
                cells=color_cells,
            )
        written.append(path)
    return written


# =========================
# CONVERSION CORE
# =========================


def convert_to_ascii(
    image_path: Path,
    output_path: Path | None = None,
    *,
    output_width: int | None = None,
    resolution: int = DEFAULT_RESOLUTION,
    char_ramp: str | None = None,
    use_extended_ramp: bool | None = None,
    aspect_ratio_correction: float = ASPECT_RATIO_CORRECTION,
    invert: bool = False,
    background: tuple[int, int, int] = (255, 255, 255),
    gif_frame: int = 0,
    skip_existing: bool = False,
    dry_run: bool = False,
    root: Path | None = None,
    output_dir: Path | None = None,
    native_size: bool = False,
    pixel_grid: bool = False,
    allow_large: bool = False,
    output_format: OutputFormat = "txt",
    png_font_size: int = DEFAULT_PNG_FONT_SIZE,
    use_color: bool = False,
) -> ConversionResult:
    """
    Full pipeline: load → grayscale/RGB → compute width → resize → map → write.

    Native / large outputs:
      - ``native_size``: one character per source pixel (width = image width).
      - ``pixel_grid``: skip resize entirely (width × height = pixel grid).
      - ``allow_large``: bypass 800×800 safety caps (required for big native grids).

    Visual exports (resize/zoom without re-converting):
      - ``output_format=html`` → browser viewer with zoom slider.
      - ``output_format=png``  → raster image for any viewer/editor.
      - ``output_format=ansi`` → true-color terminal file (.ansi.txt).
      - ``output_format=all``  → txt + (ansi if color) + html + png.

    Color (``use_color`` or ``--color``):
      - Character shape from luminance; color from source pixel RGB.
      - ANSI uses 24-bit escape codes; HTML/PNG tint each character.
    """
    resolution = max(MIN_RESOLUTION, min(MAX_RESOLUTION, resolution))
    image_path = Path(image_path)
    use_color = use_color or output_format == "ansi"

    base = resolve_output_base(
        image_path,
        output_path,
        root=root,
        output_dir=output_dir,
    )
    destinations = output_paths_for_format(base, output_format, use_color=use_color)
    primary = destinations[0]

    if skip_existing and all(should_skip_existing(image_path, dest) for dest in destinations):
        logger.debug("Skip unchanged: %s", image_path)
        return ConversionResult(
            source=image_path,
            output=primary,
            status="skipped",
            message="output up to date",
        )

    if dry_run:
        logger.info("[dry-run] would convert: %s -> %s", image_path, destinations)
        return ConversionResult(
            source=image_path,
            output=primary,
            status="skipped",
            message="dry run",
        )

    gray, rgb = load_image_pair(
        image_path,
        background=background,
        gif_frame=gif_frame,
    )

    if pixel_grid:
        if gray.width > MAX_OUTPUT_WIDTH or gray.height > MAX_OUTPUT_HEIGHT:
            if not allow_large:
                raise ValueError(
                    f"Pixel grid is {gray.width}x{gray.height} chars — too large. "
                    f"Pass --allow-large to proceed, or use --native-size / lower --resolution."
                )
            logger.warning(
                "Large pixel grid: %sx%s characters (%s cells)",
                gray.width,
                gray.height,
                gray.width * gray.height,
            )
        working_gray = gray
        working_rgb = rgb
        width_source = "pixel-grid"
    else:
        effective_width = compute_effective_width(
            gray,
            output_width=output_width,
            resolution=resolution,
            native_size=native_size,
            allow_large=allow_large,
        )
        if native_size and not allow_large and gray.width > MAX_OUTPUT_WIDTH:
            logger.warning(
                "Native width %s clamped to %s — pass --allow-large for full size",
                gray.width,
                MAX_OUTPUT_WIDTH,
            )
        working_gray = resize_for_terminal(
            gray,
            effective_width,
            aspect_ratio_correction,
            allow_large=allow_large,
        )
        working_rgb = resize_for_terminal(
            rgb,
            effective_width,
            aspect_ratio_correction,
            allow_large=allow_large,
        )
        width_source = (
            "native"
            if native_size
            else "manual"
            if output_width is not None
            else f"{resolution}%"
        )

    if char_ramp is None:
        if use_extended_ramp is True:
            char_ramp = CHAR_RAMP_EXTENDED
        elif use_extended_ramp is False:
            char_ramp = CHAR_RAMP_STANDARD
        else:
            char_ramp = select_char_ramp(working_gray.width)

    if not char_ramp:
        raise ValueError("Character ramp must be a non-empty string.")

    cells = map_pixels_to_cells(working_gray, working_rgb, char_ramp, invert)
    lines = cells_to_plain_lines(cells)
    written = write_outputs(
        lines,
        base,
        output_format,
        cells=cells,
        title=image_path.stem,
        invert=invert,
        png_font_size=png_font_size,
        use_color=use_color,
    )

    logger.info(
        "Converted: %s -> %s (grid=%sx%s [%s], ramp=%s%s)",
        image_path,
        ", ".join(str(p) for p in written),
        working_gray.width,
        working_gray.height,
        width_source,
        ramp_label(char_ramp),
        ", color" if use_color else "",
    )

    return ConversionResult(
        source=image_path,
        output=written[0],
        status="converted",
        message=f"{working_gray.width}x{working_gray.height}",
    )


# =========================
# SINGLE / BATCH ENTRYPOINTS
# =========================


def process_single_file(
    file: str | Path,
    *,
    output_path: Path | None = None,
    output_width: int | None = None,
    resolution: int = DEFAULT_RESOLUTION,
    use_extended_ramp: bool | None = None,
    aspect_ratio_correction: float = ASPECT_RATIO_CORRECTION,
    invert: bool = False,
    background: BackgroundName = "white",
    gif_frame: int = 0,
    skip_existing: bool = False,
    dry_run: bool = False,
    raise_on_error: bool = True,
    native_size: bool = False,
    pixel_grid: bool = False,
    allow_large: bool = False,
    output_format: OutputFormat = "txt",
    png_font_size: int = DEFAULT_PNG_FONT_SIZE,
    use_color: bool = False,
) -> ConversionResult:
    """Convert one image; optionally re-raise on failure."""
    path = Path(file)

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    if not is_supported_image(path):
        raise ValueError(
            f"Unsupported format: {path.suffix}. Supported: {INPUT_FORMATS}"
        )

    try:
        return convert_to_ascii(
            path,
            output_path=output_path,
            output_width=output_width,
            resolution=resolution,
            use_extended_ramp=use_extended_ramp,
            aspect_ratio_correction=aspect_ratio_correction,
            invert=invert,
            background=background_rgb(background),
            gif_frame=gif_frame,
            skip_existing=skip_existing,
            dry_run=dry_run,
            native_size=native_size,
            pixel_grid=pixel_grid,
            allow_large=allow_large,
            output_format=output_format,
            png_font_size=png_font_size,
            use_color=use_color,
        )
    except Exception as exc:
        logger.error("Failed: %s -> %s", path, exc)
        result = ConversionResult(source=path, status="failed", message=str(exc))
        if raise_on_error:
            raise
        return result


def iter_image_files(root: Path, source_formats: list[str] | None = None) -> list[Path]:
    """Collect supported image files under root (sorted for stable batch order)."""
    formats = source_formats or INPUT_FORMATS
    files = [
        path
        for path in root.rglob("*")
        if path.is_file() and is_supported_image(path, formats)
    ]
    return sorted(files)


def process_directory(
    root: str | Path,
    *,
    source_formats: list[str] | None = None,
    output_dir: str | Path | None = None,
    output_width: int | None = None,
    resolution: int = DEFAULT_RESOLUTION,
    use_extended_ramp: bool | None = None,
    aspect_ratio_correction: float = ASPECT_RATIO_CORRECTION,
    invert: bool = False,
    background: BackgroundName = "white",
    gif_frame: int = 0,
    skip_existing: bool = False,
    dry_run: bool = False,
    native_size: bool = False,
    pixel_grid: bool = False,
    allow_large: bool = False,
    output_format: OutputFormat = "txt",
    png_font_size: int = DEFAULT_PNG_FONT_SIZE,
    use_color: bool = False,
) -> BatchStats:
    """
    Recursively convert images under ``root``.

    Failures are logged and recorded in ``BatchStats.failures``; processing continues.
    """
    root_path = Path(root).resolve()
    out_dir = Path(output_dir).resolve() if output_dir else None

    if not root_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {root_path}")

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)

    stats = BatchStats()
    files = iter_image_files(root_path, source_formats)

    if not files:
        logger.warning("No supported images found under %s", root_path)
        return stats

    logger.info("Batch start: %s file(s) under %s", len(files), root_path)

    for index, file_path in enumerate(files, start=1):
        logger.debug("Processing %s/%s: %s", index, len(files), file_path)
        try:
            result = convert_to_ascii(
                file_path,
                output_width=output_width,
                resolution=resolution,
                use_extended_ramp=use_extended_ramp,
                aspect_ratio_correction=aspect_ratio_correction,
                invert=invert,
                background=background_rgb(background),
                gif_frame=gif_frame,
                skip_existing=skip_existing,
                dry_run=dry_run,
                root=root_path,
                output_dir=out_dir,
                native_size=native_size,
                pixel_grid=pixel_grid,
                allow_large=allow_large,
                output_format=output_format,
                png_font_size=png_font_size,
                use_color=use_color,
            )
        except Exception as exc:
            stats.failed += 1
            stats.failures.append((file_path, str(exc)))
            logger.error("Failed (%s/%s): %s -> %s", index, len(files), file_path, exc)
            continue

        if result.status == "converted":
            stats.converted += 1
        elif result.status == "skipped":
            stats.skipped += 1
        else:
            stats.failed += 1
            stats.failures.append((file_path, result.message))

    logger.info(
        "Batch done: converted=%s skipped=%s failed=%s total=%s",
        stats.converted,
        stats.skipped,
        stats.failed,
        stats.total,
    )
    return stats


# =========================
# CLI
# =========================


def _parse_extended_ramp(value: str | None) -> bool | None:
    if value is None or value == "auto":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    raise argparse.ArgumentTypeError("expected auto, true, or false")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert images to ASCII art .txt files (single file or batch directory)."
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--file", "-f", help="Single image file to convert")
    target.add_argument("--dir", "-d", help="Directory to scan recursively")

    parser.add_argument(
        "--output-dir",
        "-o",
        help="Write outputs here, mirroring source tree (batch mode only)",
    )
    parser.add_argument(
        "--width",
        type=int,
        help="Exact output character width (overrides --resolution)",
    )
    parser.add_argument(
        "--resolution",
        type=int,
        default=DEFAULT_RESOLUTION,
        help=f"Width as %% of image width ({MIN_RESOLUTION}-{MAX_RESOLUTION}, default {DEFAULT_RESOLUTION})",
    )
    parser.add_argument(
        "--native-size",
        action="store_true",
        help="Use source image pixel width as ASCII width (same as --resolution 100)",
    )
    parser.add_argument(
        "--pixel-grid",
        action="store_true",
        help="One character per pixel (no resize). Very large for big images — use with --allow-large",
    )
    parser.add_argument(
        "--allow-large",
        action="store_true",
        help=f"Bypass {MAX_OUTPUT_WIDTH}x{MAX_OUTPUT_HEIGHT} safety caps for native/pixel-grid output",
    )
    parser.add_argument(
        "--format",
        choices=["txt", "ansi", "html", "png", "all"],
        default="txt",
        help="Output format: txt, ansi (terminal colors), html, png, or all",
    )
    parser.add_argument(
        "--color",
        action="store_true",
        help="Tint each character with source pixel color (html/png; adds .ansi.txt with --format all)",
    )
    parser.add_argument(
        "--png-font-size",
        type=int,
        default=DEFAULT_PNG_FONT_SIZE,
        help="Font size when rendering --format png (default: 8)",
    )
    parser.add_argument(
        "--extended-ramp",
        choices=["auto", "true", "false"],
        default="auto",
        help="Character ramp: auto (default), true, or false",
    )
    parser.add_argument(
        "--invert",
        action="store_true",
        help="Invert brightness (for dark terminal backgrounds)",
    )
    parser.add_argument(
        "--background",
        choices=["white", "black"],
        default="white",
        help="Background for transparent images (default: white)",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip when output .txt exists and is newer than source",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List conversions without writing files",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug logging")
    parser.add_argument("--quiet", "-q", action="store_true", help="Errors only")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.quiet and args.verbose:
        parser.error("Use either --quiet or --verbose, not both.")

    configure_logging(verbose=args.verbose, quiet=args.quiet)
    use_extended_ramp = _parse_extended_ramp(args.extended_ramp)

    if args.pixel_grid and args.native_size:
        parser.error("Use either --pixel-grid or --native-size, not both.")

    common = dict(
        output_width=args.width,
        resolution=args.resolution,
        use_extended_ramp=use_extended_ramp,
        invert=args.invert,
        background=args.background,
        skip_existing=args.skip_existing,
        dry_run=args.dry_run,
        native_size=args.native_size,
        pixel_grid=args.pixel_grid,
        allow_large=args.allow_large,
        output_format=args.format,
        png_font_size=args.png_font_size,
        use_color=args.color or args.format == "ansi",
    )

    if args.file:
        result = process_single_file(args.file, raise_on_error=True, **common)
        return 0 if result.status != "failed" else 1

    stats = process_directory(
        args.dir,
        output_dir=args.output_dir,
        **common,
    )
    return 0 if stats.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
