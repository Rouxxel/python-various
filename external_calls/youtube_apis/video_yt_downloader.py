"""
YOUTUBE VIDEO-ONLY EXTRACTION MODULE
-----------------------------------
Downloads the highest quality video stream without audio.

Supports:
- Automatic selection of best video-only stream
- Customizable output containers (mp4, mkv, etc.)
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

def run_video_only_pipeline(
    video_input: str,
    output_filename: str = "downloaded_video",
    video_ext: str = DEFAULT_VIDEO_EXT
):
    """
    Main pipeline function to fetch video without audio.
    """

    print(f"--- Processing Video (Silent): {video_input} ---")

    # 1. Define yt-dlp options
    # 'bestvideo' ensures we don't get the combined (often lower quality) file.
    ydl_opts = {
        'format': 'bestvideo', 
        'outtmpl': f'{output_filename}.%(ext)s',
        'merge_output_format': video_ext,
        'quiet': False,
        'no_warnings': True,
    }

    # 2. Execute Download
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We extract info first to see what extension we're actually getting
            info = ydl.extract_info(video_input, download=True)
            actual_ext = info.get('ext', video_ext)

        print(f"SUCCESS: Silent video saved as {output_filename}.{actual_ext}")

    except Exception as e:
        raise Exception(f"Video download failed: {str(e)}")


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    try:
        run_video_only_pipeline(
            video_input="https://www.youtube.com/shorts/C80whOpK-PY",
            output_filename="downloaded_video",
            video_ext="mp4"
        )
    except Exception as e:
        print(f"PIPELINE ERROR: {str(e)}")
