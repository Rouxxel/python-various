"""
YOUTUBE AUDIO EXTRACTION MODULE
-----------------------------------
Downloads and converts YouTube video audio to high-quality MP3.

Supports:
- Single video IDs or full URLs
- Automatic FFmpeg post-processing
- Automatic filename from video title (default)
- Optional custom filename override
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
    output_filename: str | None = None,
    audio_format: str = DEFAULT_AUDIO_FORMAT,
    bitrate: str = DEFAULT_BITRATE
):
    """
    Main pipeline function using yt-dlp.
    """

    print(f"--- Processing Audio: {video_input} ---")

    # Define yt-dlp options
    # 'outtmpl' handles filename. 'postprocessors' handles MP3 conversion + metadata.
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
        'noplaylist': True,
        'outtmpl': f'{output_filename}.%(ext)s' if output_filename else '%(title)s.%(ext)s',

        # Ensure safer filenames from YouTube titles
        'restrictfilenames': True,

        # Post-processing pipeline
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': bitrate,
            }
        ],
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        },
        'quiet': False,
        'no_warnings': True,
        'retries': 10,
        'fragment_retries': 10,
    }

    # Execute Download
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_input])

        #NOTE: yt-dlp automatically applies title-based filename if used
        print("SUCCESS: Audio saved successfully.")

    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    try:

        # Uses YouTube title as filename
        run_audio_pipeline(
            video_input="https://www.youtube.com/shorts/C80whOpK-PY",
            output_filename=None
        )

        # Uses custom filename override
        # run_audio_pipeline(
        #     video_input="https://www.youtube.com/shorts/C80whOpK-PY",
        #     output_filename="my_audio_track",
        #     audio_format="mp3"
        # )

    except Exception as e:
        print(f"PIPELINE ERROR: {str(e)}")
