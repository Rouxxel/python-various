"""
YOUTUBE VIDEO EXTRACTION MODULE
-----------------------------------
Downloads YouTube videos with optional audio removal and transcripts.

Supports:
- Best quality video + audio (default)
- Optional video-only download (no audio)
- Optional transcript download (.txt)
- Automatic merging via FFmpeg
- Clean reusable pipeline structure
"""

import yt_dlp

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

DEFAULT_VIDEO_EXT = "mp4"

# ---------------------------------------------------------
# CORE PIPELINE
# ---------------------------------------------------------

def run_video_pipeline(
    video_input: str,
    output_filename: str | None = None,
    video_ext: str = DEFAULT_VIDEO_EXT,
    video_only: bool = False,
):
    """
    Main pipeline function for YouTube video downloads.
    """

    print(f"--- Processing Video: {video_input} ---")

    # Choose format strategy
    if video_only:
        format_selector = "bestvideo"
    else:
        format_selector = "bestvideo+bestaudio/best"

    # options
    ydl_opts = {
        'format': format_selector,
        'noplaylist': True,
        'outtmpl': f'{output_filename}.%(ext)s' if output_filename else '%(title)s.%(ext)s',

        # Metadata
        'postprocessors': [
            {'key': 'FFmpegMetadata'}
        ],

        'merge_output_format': video_ext,

        'quiet': False,
        'no_warnings': True,
    }

    # Execute download
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_input, download=True)
            actual_ext = info.get('ext', video_ext)

        mode = "VIDEO-ONLY" if video_only else "VIDEO+AUDIO"

        print(f"SUCCESS ({mode}): saved as {output_filename or info.get('title')}")

    except Exception as e:
        raise Exception(f"Video download failed: {str(e)}")


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    try:

        # Default: full video with audio
        run_video_pipeline(
            video_input="https://www.youtube.com/shorts/C80whOpK-PY",
            output_filename="normal_video",
            video_only=False,
        )

        # Optional: video only
        # run_video_pipeline(
        #     video_input="https://www.youtube.com/shorts/C80whOpK-PY",
        #     video_only=True,
        # )

    except Exception as e:
        print(f"PIPELINE ERROR: {str(e)}")