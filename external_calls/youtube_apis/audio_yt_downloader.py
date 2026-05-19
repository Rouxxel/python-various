"""
YOUTUBE AUDIO EXTRACTION MODULE
-----------------------------------
Downloads and converts YouTube video audio to high-quality MP3.

Supports:
- Single video IDs or full URLs
- Automatic FFmpeg post-processing
- Clean reusable pipeline structure
"""

import yt_dlp

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

DEFAULT_AUDIO_FORMAT = "mp3"
DEFAULT_BITRATE = "192"  # kilobits per second

# ---------------------------------------------------------
# CORE PIPELINE
# ---------------------------------------------------------

def run_audio_pipeline(
    video_input: str,
    output_filename: str = "downloaded_audio",
    audio_format: str = DEFAULT_AUDIO_FORMAT,
    bitrate: str = DEFAULT_BITRATE
):
    """
    Main pipeline function using yt-dlp.
    """

    print(f"--- Processing Audio: {video_input} ---")

    # 1. Define yt-dlp options
    # The 'outtmpl' handles the filename. 'postprocessors' handles the MP3 conversion.
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'outtmpl': f'{output_filename}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': bitrate,
        }],
        'quiet': False,
        'no_warnings': True,
    }

    # 2. Execute Download
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_input])

        # Note: yt-dlp adds the extension automatically
        print(f"SUCCESS: Audio saved as {output_filename}.{audio_format}")

    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    try:
        run_audio_pipeline(
            video_input="https://www.youtube.com/shorts/C80whOpK-PY",
            output_filename="my_audio_track",
            audio_format="mp3"
        )
    except Exception as e:
        print(f"PIPELINE ERROR: {str(e)}")
