"""
GEMINI 3.1 PRO VIDEO ANALYSIS ENGINE
------------------------------------
This module performs deep multimodal analysis of event footage. 
It extracts technical metadata, shot types, and transcripts, 
formatting them into a structured JSON for automated video editing.
"""

import json
import time
import requests
import os
from google import genai
from google.genai import types
from cv2 import VideoCapture, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT
import math

# ---------------------------------------------------------
# #------------------ CONFIGURATION
# ---------------------------------------------------------

# Initialize the Gemini Client with API Key
client = genai.Client(api_key='api_key_here')  # Replace with actual API key

# Input/Output Settings
VIDEO_INPUT = "local_video_path.mp4" 
OUTPUT_FILE = "video_analysis_output.json"
MODEL_NAME = "gemini-3.1-pro-preview"

# Technical Prompt for the Model
ANALYSIS_PROMPT = """
Analyze this event footage for automated video editing software. 
SUBDIVISION RULES:
1. Break the video into sections based on NATURAL CUTS, POV SHIFTS, or CAMERA ANGLE CHANGES.
2. If the camera switches from Character/Thing A to Character/Thing B, end the current section and start a new one at that exact second.
3. If a continuous take (Long Take) lasts more than 7 seconds without a cut, you may then subdivide it based on significant narrative shifts.
4. Each section must represent a single, cohesive visual shot or technical camera movement.

Return ONLY a JSON object with this exact structure:
{
    "duration": number,
    "event_type": "e.g., Wedding, Conference, Concert",
    "context": "Brief high-level overall summary of the whole video",
    "sections": {
        "0-3": {
            "transcript": "Exact speech or '[Music Only]'",
            "shot_type": "e.g., Wide, Medium, Close-up, POV",
            "visual_tags": ["list", "of", "keywords"],
            "technical_description": "Objective summary of actions and focus state."
        }
    }
}
Focus on identifying 'clean' vs 'shaky' shots.
"""

# ---------------------------------------------------------
# #------------------- METHODS
# ---------------------------------------------------------

def get_aspect_ratio(video_path):
    """
    Opens the video file locally and extracts dimensions to compute aspect ratio.
    """
    try:
        video = VideoCapture(video_path)
        width  = int(video.get(CAP_PROP_FRAME_WIDTH))
        height = int(video.get(CAP_PROP_FRAME_HEIGHT))
        video.release()

        if width == 0 or height == 0:
            return "Unknown"

        # Calculate Simplified Aspect Ratio (e.g., 16:9)
        gcd = math.gcd(width, height)
        ratio_w = width // gcd
        ratio_h = height // gcd
        
        return {
            "resolution": f"{width}x{height}",
            "ratio_string": f"{ratio_w}:{ratio_h}",
            "decimal": round(width / height, 3)
        }
    except Exception as e:
        return f"Error extracting aspect ratio: {str(e)}"

def get_video_file(source):
    """
    Handles video ingestion from multiple sources. 
    Downloads remote files if necessary and uploads to Gemini File API.
    Returns (video_handle, local_path_for_cv2)
    """
    local_path = source
    
    if source.startswith("http"):
        print(f"Downloading remote video from: {source}...")
        r = requests.get(source, stream=True)
        local_path = "temp_video.mp4"
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
        print("Download complete. Uploading to Gemini...")
        return client.files.upload(file=local_path), local_path
    
    elif source.startswith("gs://"):
        print(f"Note: Handling {source} via direct upload path...")
        return client.files.upload(file=source), source
    
    else:
        print(f"Uploading local file: {source}")
        if not os.path.exists(source):
            raise FileNotFoundError(f"File not found: {source}")
        return client.files.upload(file=source), source

def wait_for_video_active(video_handle):
    """
    Polls the Gemini File API until the video has finished processing.
    """
    print("Waiting for Gemini to process video...", end="")
    while True:
        file_info = client.files.get(name=video_handle.name)
        if file_info.state.name == "ACTIVE":
            print("\nVideo is ACTIVE and ready for analysis.")
            break
        elif file_info.state.name == "FAILED":
            raise RuntimeError("Video processing failed on Google servers.")
        
        print(".", end="", flush=True)
        time.sleep(5)

# ---------------------------------------------------------
# #------------------- CORE PIPELINE
# ---------------------------------------------------------

def run_analysis_pipeline():
    """Executes the upload, wait loop, and LLM generation."""
    
    # 1. Ingestion & Upload
    # Fixed: Correctly unpacking the two return values from get_video_file
    video_upload, local_path = get_video_file(VIDEO_INPUT)
    
    # 2. Local Technical Analysis
    aspect_data = get_aspect_ratio(local_path)
    
    # 3. Server-side processing wait
    wait_for_video_active(video_upload)

    print(f"Gemini 3.1 Pro is indexing event footage...")
    start_time = time.time()

    # 4. Model Request
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[video_upload, ANALYSIS_PROMPT],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1 
        )
    )

    end_time = time.time()
    
    # 5. Data Formatting & Metadata Assembly
    analysis_content = json.loads(response.text)
    usage = response.usage_metadata

    final_output = {
        "analysis": analysis_content,
        "metadata": {
            "model_used": MODEL_NAME,
            "aspect_ratio": aspect_data,
            "tokens_used": {
                "prompt_tokens": usage.prompt_token_count,
                "output_tokens": usage.candidates_token_count,
                "total_tokens": usage.total_token_count
            },
            "processing_duration": f"{round(end_time - start_time, 2)} seconds",
            "vid_duration": analysis_content.get("duration", 0)
        }
    }

    # 6. Result Serialization
    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_output, f, indent=4)

    print("\n" + "="*40)
    print(f"SUCCESS: Metadata saved to {OUTPUT_FILE}")
    print(f"Aspect Ratio: {aspect_data['ratio_string'] if isinstance(aspect_data, dict) else 'N/A'}")
    print(f"Process Time: {final_output['metadata']['processing_duration']}")
    print("="*40)

# ---------------------------------------------------------
# MAIN ENTRY
# ---------------------------------------------------------

if __name__ == "__main__":
    try:
        run_analysis_pipeline()
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")