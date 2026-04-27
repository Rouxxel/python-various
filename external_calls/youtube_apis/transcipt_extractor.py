"""
YOUTUBE TRANSCRIPT EXTRACTION MODULE
-----------------------------------
Fetches and stores transcripts from YouTube videos.

Supports:
- Single video IDs or full URLs
- Language selection / fallback
- Multiple output formats (txt, json)
- Clean reusable pipeline structure

Useful for:
- NLP pipelines
- Embedding workflows
- Audio/text alignment tasks
"""

import json
import re
from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

DEFAULT_LANGUAGES = ["en"]
OUTPUT_FORMAT = "txt"  # options: "txt", "json"


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def extract_video_id(url_or_id: str) -> str:
    """
    Extracts the video ID from a full YouTube URL or returns the ID directly.
    """
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url_or_id)
        if not match:
            raise ValueError(f"Invalid YouTube URL: {url_or_id}")
        return match.group(1)
    return url_or_id


def fetch_transcript(video_id: str, languages: Optional[List[str]] = None):
    """
    Fetch transcript using YouTubeTranscriptApi.
    """
    api = YouTubeTranscriptApi()
    return api.fetch(video_id, languages=languages or DEFAULT_LANGUAGES)


def format_transcript_txt(transcript) -> str:
    """
    Formats transcript into readable text with timestamps.
    """
    lines = []
    for entry in transcript:
        lines.append(f"[{entry.start:.2f}] {entry.text}")
    return "\n".join(lines)


def format_transcript_json(transcript):
    """
    Converts transcript into JSON-serializable format.
    """
    return [
        {
            "text": entry.text,
            "start": entry.start,
            "duration": entry.duration,
        }
        for entry in transcript
    ]


# ---------------------------------------------------------
# CORE PIPELINE
# ---------------------------------------------------------

def run_transcript_pipeline(
    video_input: str,
    output_filename: str = "transcript_output",
    languages: Optional[List[str]] = None,
    output_format: str = OUTPUT_FORMAT,
):
    """
    Main pipeline function.
    """

    print(f"--- Processing: {video_input} ---")

    # 1. Normalize input
    video_id = extract_video_id(video_input)

    # 2. Fetch transcript
    transcript = fetch_transcript(video_id, languages)

    # 3. Format output
    if output_format == "txt":
        formatted = format_transcript_txt(transcript)
        filename = f"{output_filename}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(formatted)

    elif output_format == "json":
        formatted = format_transcript_json(transcript)
        filename = f"{output_filename}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(formatted, f, indent=4)

    else:
        raise ValueError("Unsupported format. Use 'txt' or 'json'.")

    print(f"SUCCESS: Transcript saved to {filename}")


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    try:
        run_transcript_pipeline(
            video_input="https://www.youtube.com/watch?v=uXalS69hPrE",
            output_filename="transcript",
            languages=["en"],
            output_format="txt",
        )
    except Exception as e:
        print(f"PIPELINE ERROR: {str(e)}")