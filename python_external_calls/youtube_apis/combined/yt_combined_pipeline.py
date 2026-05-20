"""
YOUTUBE COMBINED EXTRACTION PIPELINE
-----------------------------------
Downloads video, audio, and/or transcript from a YouTube URL in a single call.

Supports:
- Video download (with or without audio)
- Audio-only download with configurable format and bitrate
- Transcript download with multi-language support (one file per language)
- Optional metadata embedding for video and audio
- Custom output filename prefix or auto-title from YouTube
- Clean reusable pipeline structure
"""

import json
import re
import yt_dlp
from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi


# ---------------------------------------------------------
# DEFAULTS
# ---------------------------------------------------------

DEFAULT_VIDEO_EXT       = "mp4"
DEFAULT_AUDIO_EXT       = "mp3"
DEFAULT_TRANSCRIPT_EXT  = "txt"
DEFAULT_LANGUAGES       = ["en"]
DEFAULT_BITRATE         = "192"


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def _extract_video_id(url: str) -> str:
    """Extracts the 11-char video ID from a YouTube URL."""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    if not match:
        raise ValueError(f"Could not extract video ID from URL: {url}")
    return match.group(1)


def _format_transcript_txt(transcript) -> str:
    lines = [f"[{entry.start:.2f}] {entry.text}" for entry in transcript]
    return "\n".join(lines)


def _format_transcript_json(transcript) -> list:
    return [
        {"text": entry.text, "start": entry.start, "duration": entry.duration}
        for entry in transcript
    ]


# ---------------------------------------------------------
# SUB-PIPELINES
# ---------------------------------------------------------

def _run_video(
    video_input: str,
    output_files_prefix: str | None,
    video_mute: bool,
    video_extension: str,
    embed_data: bool,
):
    print(f"\n--- [VIDEO] Processing: {video_input} ---")

    format_selector = "bestvideo" if video_mute else "bestvideo+bestaudio/best"

    postprocessors = []
    if embed_data:
        postprocessors.append({"key": "FFmpegMetadata"})

    ydl_opts = {
        "format": format_selector,
        "noplaylist": True,
        "outtmpl": (
            f"{output_files_prefix}.%(ext)s"
            if output_files_prefix
            else "%(title)s.%(ext)s"
        ),
        "postprocessors": postprocessors,
        "merge_output_format": video_extension,
        "quiet": False,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_input, download=True)

    mode = "VIDEO-ONLY (muted)" if video_mute else "VIDEO+AUDIO"
    label = output_files_prefix or info.get("title")
    print(f"SUCCESS ({mode}): saved as {label}.{video_extension}")


def _run_audio(
    video_input: str,
    output_files_prefix: str | None,
    aud_extension: str,
    bitrate: str,
    embed_data: bool,
):
    print(f"\n--- [AUDIO] Processing: {video_input} ---")

    postprocessors = [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": aud_extension,
            "preferredquality": bitrate,
        }
    ]
    if embed_data:
        postprocessors.append({"key": "FFmpegMetadata"})

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
        "noplaylist": True,
        "outtmpl": (
            f"{output_files_prefix}.%(ext)s"
            if output_files_prefix
            else "%(title)s.%(ext)s"
        ),
        "restrictfilenames": True,
        "postprocessors": postprocessors,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
            }
        },
        "quiet": False,
        "no_warnings": True,
        "retries": 10,
        "fragment_retries": 10,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_input])

    print(f"SUCCESS (AUDIO): saved as {output_files_prefix or '<video title>'}.{aud_extension}")


def _run_transcripts(
    video_input: str,
    output_files_prefix: str | None,
    transcript_extension: str,
    transcript_languages: List[str],
):
    print(f"\n--- [TRANSCRIPT] Processing: {video_input} ---")

    video_id = _extract_video_id(video_input)
    api = YouTubeTranscriptApi()

    for lang in transcript_languages:
        try:
            transcript = api.fetch(video_id, languages=[lang])
        except Exception as e:
            print(f"  WARNING: Could not fetch transcript for language '{lang}': {e}")
            continue

        # Build filename: <prefix>_<lang>.<ext>  or  <lang>.<ext> when no prefix
        base = f"{output_files_prefix}_{lang}" if output_files_prefix else lang
        filename = f"{base}.{transcript_extension}"

        if transcript_extension == "txt":
            content = _format_transcript_txt(transcript)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

        elif transcript_extension == "json":
            content = _format_transcript_json(transcript)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=4)

        else:
            raise ValueError(
                f"Unsupported transcript extension '{transcript_extension}'. Use 'txt' or 'json'."
            )

        print(f"  SUCCESS: Transcript [{lang}] saved to {filename}")


# ---------------------------------------------------------
# MAIN COMBINED PIPELINE
# ---------------------------------------------------------

def run_combined_pipeline(
    # --- Required ---
    video_input: str,
    video_download: bool,
    audio_download: bool,
    transcript_download: bool,

    # --- Optional ---
    output_files_prefix: str | None = None,

    # Video options (only relevant when video_download=True)
    video_mute: bool = False,
    video_extension: str = DEFAULT_VIDEO_EXT,

    # Audio options (only relevant when audio_download=True)
    aud_extension: str = DEFAULT_AUDIO_EXT,

    # Transcript options (only relevant when transcript_download=True)
    transcript_extension: str = DEFAULT_TRANSCRIPT_EXT,
    transcript_languages: List[str] | None = None,

    # Shared options
    embed_data: bool = True,
    bitrate: str = DEFAULT_BITRATE,
):
    """
    Combined YouTube download pipeline.

    Parameters
    ----------
    video_input : str
        A valid YouTube URL. Required.
    video_download : bool
        Whether to download the video stream.
    audio_download : bool
        Whether to download the audio as a standalone file.
    transcript_download : bool
        Whether to download the transcript.
    output_files_prefix : str | None
        Prefix for all output filenames. If None, the video's YouTube title is used.
    video_mute : bool
        If True, downloads video without audio. Ignored when video_download=False.
    video_extension : str
        Container format for the video file (e.g. "mp4", "mkv"). Ignored when video_download=False.
    aud_extension : str
        Audio format (e.g. "mp3", "m4a", "wav"). Ignored when audio_download=False.
    transcript_extension : str
        Transcript file format: "txt" or "json". Ignored when transcript_download=False.
    transcript_languages : list[str] | None
        List of BCP-47 language codes. One file is produced per language.
        Defaults to ["en"]. Ignored when transcript_download=False.
    embed_data : bool
        If True, embeds metadata tags into video/audio via FFmpegMetadata.
    bitrate : str
        Audio bitrate in kbps (e.g. "192"). Ignored when audio_download=False.
    """

    if not video_input:
        raise ValueError("'video_input' is required and must be a valid YouTube URL.")

    if not any([video_download, audio_download, transcript_download]):
        print("Nothing to do: all download flags are False.")
        return

    print(f"\n{'='*55}")
    print(f"  COMBINED YOUTUBE PIPELINE")
    print(f"  URL    : {video_input}")
    print(f"  Prefix : {output_files_prefix or '(use video title)'}")
    print(f"  Tasks  : "
          f"{'VIDEO ' if video_download else ''}"
          f"{'AUDIO ' if audio_download else ''}"
          f"{'TRANSCRIPT' if transcript_download else ''}")
    print(f"{'='*55}")

    errors = []

    # --- Video ---
    if video_download:
        try:
            _run_video(
                video_input=video_input,
                output_files_prefix=output_files_prefix,
                video_mute=video_mute,
                video_extension=video_extension,
                embed_data=embed_data,
            )
        except Exception as e:
            errors.append(f"[VIDEO] {e}")
            print(f"ERROR (VIDEO): {e}")

    # --- Audio ---
    if audio_download:
        try:
            _run_audio(
                video_input=video_input,
                output_files_prefix=output_files_prefix,
                aud_extension=aud_extension,
                bitrate=bitrate,
                embed_data=embed_data,
            )
        except Exception as e:
            errors.append(f"[AUDIO] {e}")
            print(f"ERROR (AUDIO): {e}")

    # --- Transcript ---
    if transcript_download:
        try:
            _run_transcripts(
                video_input=video_input,
                output_files_prefix=output_files_prefix,
                transcript_extension=transcript_extension,
                transcript_languages=transcript_languages or DEFAULT_LANGUAGES,
            )
        except Exception as e:
            errors.append(f"[TRANSCRIPT] {e}")
            print(f"ERROR (TRANSCRIPT): {e}")

    # --- Summary ---
    print(f"\n{'='*55}")
    if errors:
        print(f"  PIPELINE FINISHED WITH {len(errors)} ERROR(S):")
        for err in errors:
            print(f"    - {err}")
    else:
        print("  PIPELINE COMPLETED SUCCESSFULLY")
    print(f"{'='*55}\n")


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    try:
        run_combined_pipeline(
            video_input="https://www.youtube.com/shorts/C80whOpK-PY",

            # Choose what to download
            video_download=True,
            audio_download=True,
            transcript_download=True,

            # Optional:
            # output_files_prefix="my_video",

            # Video options
            video_mute=False,
            video_extension="mp4",

            # Audio options
            aud_extension="mp3",
            bitrate="192",

            # Transcript options
            transcript_extension="txt",
            transcript_languages=["en","es"],

            # Shared
            embed_data=True,
        )
    except Exception as e:
        print(f"PIPELINE ERROR: {str(e)}")
