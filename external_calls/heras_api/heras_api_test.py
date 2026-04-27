"""
HERA MOTION GRAPHICS GENERATION ENGINE
--------------------------------------
This module automates the creation of AI-driven motion graphics. 
It handles local file hosting for API compatibility, job orchestration, 
and real-time status polling for high-fidelity video production.
"""

import requests
import time
import json
import os

# ---------------------------------------------------------
# #------------------ CONFIGURATION
# ---------------------------------------------------------

API_KEY = "api_key_here"  # Replace with actual API key
BASE_URL = "https://api.hera.video/v1"

# Input Settings
LOCAL_VIDEO_INPUT = "local_video_path.mp4" 
POLL_INTERVAL = 3  # Seconds between status checks

# ---------------------------------------------------------
# #------------------ DYNAMIC PROMPT DEFAULTS
# ---------------------------------------------------------

# Variables from video analysis
DURATION_OVERLAY = 53
RESOLUTION = "1080p" # from "resolution": "1080x1080",
FPS = 30
ASPECT_RATIO = "1:1" # from "ratio_string": "1:1",
TIMELINE_JSON_PATH = "video_analysis_output.json"

# User inputs/UI sliders
USER_CONFIG = {
    "style": "Modern / Apple Vision Pro glassmorphism",
    "color_palette": "Electric Blue and White",
    "font_family": "Inter or Helvetica (Clean Sans-Serif)",
    "opacity": "85%",
    "positioning": "Lower-third and right-side callouts",
    "symbols": "Minimalist tech icons and subtle glowing pulses",
    "context": "A scene from a war drama where a newly arrived, inexperienced lieutenant volunteers for a patrol but is turned down by his commanding officer."
}

# ---------------------------------------------------------
# #------------------- METHODS
# ---------------------------------------------------------

def build_temporal_context(json_path):
    """
    Parses the analysis JSON file and creates a text-based timeline 
    string for the AI prompt.
    """
    if not os.path.exists(json_path):
        return "No specific timeline data available."

    with open(json_path, 'r') as f:
        analysis_data = json.load(f)

    timeline_str = ""
    sections = analysis_data.get("analysis", {}).get("sections", {})
    
    for timestamp, data in sections.items():
        timeline_str += f"- [{timestamp}s]: {data.get('technical_description', '')}. "
        timeline_str += f"Visual focus: {', '.join(data.get('visual_tags', []))}.\n"
    return timeline_str

def get_generation_prompt(dynamic_timeline):
    """
    Constructs the final prompt string including the dynamic timeline.
    This prompt instructs Hera to generate ONLY the graphics on a solid background.
    """
    return f"""
TASK: Generate a high-fidelity motion graphics overlay.
BACKGROUND: Use a solid, pure black (#000000) background. Do not include any footage.
CONTEXT: {USER_CONFIG['context']}

TIMELINE OF ACTION (Follow this for timing):
{dynamic_timeline}

VISUAL STYLE SPECIFICATIONS:
- OVERALL STYLE: {USER_CONFIG['style']}
- COLOR PALETTE: {USER_CONFIG['color_palette']}
- FONT: {USER_CONFIG['font_family']}
- OPACITY: {USER_CONFIG['opacity']} opacity for background elements.
- POSITIONING: Focus all elements on the {USER_CONFIG['positioning']}.

INFOGRAPHIC ELEMENTS TO GENERATE:
1. Active labels and data callouts following the movement of key objects.
2. Animated symbols: {USER_CONFIG['symbols']}.
3. Progress bars or telemetry data reflecting the video context.
4. Smooth fade-in and slide animations.

STRICT RULE: Only return the infographics and the black background. 
NO background footage or environment should be visible.
"""

def upload_to_temp_storage(file_path):
    """
    Uploads local file to GoFile.io. 
    Returns a direct download URL that Hera can access.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Local video file not found: {file_path}")

    print(f"Provisioning temporary storage for: {file_path}...")
    
    try:
        # 1. Get an available server from GoFile
        server_data = requests.get("https://api.gofile.io/servers").json()
        if server_data["status"] != "ok":
            raise RuntimeError("Could not fetch GoFile server.")
        
        server = server_data["data"]["servers"][0]["name"]

        # 2. Upload the file
        with open(file_path, "rb") as f:
            upload_response = requests.post(
                f"https://{server}.gofile.io/contents/uploadfile",
                files={"file": f}
            )
        
        upload_data = upload_response.json()
        
        if upload_data["status"] == "ok":
            # NOTE: For some APIs, you might need to extract the direct link
            temp_url = upload_data["data"]["downloadPage"]
            print(f"Temporary link active: {temp_url}")
            return temp_url
        else:
            raise RuntimeError(f"GoFile Upload Failed: {upload_data}")

    except Exception as e:
        print(f"Storage Provisioning Error: {str(e)}")
        raise e

def create_video_job(prompt, reference_video_url):
    """
    Dispatches a new video generation job to the Hera API.
    Returns the unique Video ID and the Project Dashboard URL.
    """
    url = f"{BASE_URL}/videos"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    payload = {
        "prompt": prompt,
        "reference_video_url": reference_video_url,
        "duration_seconds": int(DURATION_OVERLAY),
        "outputs": [
            {
                "format": "mp4",
                "aspect_ratio": str(ASPECT_RATIO),
                "fps": str(FPS),
                "resolution": f"{RESOLUTION}p" if "p" not in str(RESOLUTION) else RESOLUTION
            }
        ]
    }
    
    print("Dispatching job to Hera Video API...")
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    return data["video_id"], data.get("project_url")

def wait_for_completion(video_id):
    """
    Polls the Hera API until the video generation is successful or fails.
    """
    print("Waiting for Hera to render motion graphics...", end="")
    url = f"{BASE_URL}/videos/{video_id}"
    headers = {"x-api-key": API_KEY}

    while True:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        status_data = response.json()
        
        status = status_data["status"]
        
        if status == "success":
            print("\nRendering complete.")
            return status_data
        elif status == "failed":
            print("\n")
            raise RuntimeError(f"Hera generation failed: {status_data.get('error')}")
        
        print(".", end="", flush=True)
        time.sleep(POLL_INTERVAL)

# ---------------------------------------------------------
# #------------------- CORE PIPELINE
# ---------------------------------------------------------

def run_generation_pipeline():
    """Executes the upload, job creation, and polling sequence."""
    start_time = time.time()

    # 1. Build Dynamic Context from JSON
    print(f"Reading analysis from: {TIMELINE_JSON_PATH}")
    dynamic_timeline = build_temporal_context(TIMELINE_JSON_PATH)
    final_prompt = get_generation_prompt(dynamic_timeline)

    # 2. Prepare Local File
    temp_url = upload_to_temp_storage(LOCAL_VIDEO_INPUT)

    # 3. Initiate Generation
    video_id, project_url = create_video_job(final_prompt, temp_url)
    
    print(f"ID: {video_id}")
    print(f"Project Dashboard: {project_url}")

    # 4. Wait for Results
    result = wait_for_completion(video_id)

    # 5. Extract Final Assets
    end_time = time.time()
    final_video_url = next(
        (out["file_url"] for out in result["outputs"] if out["status"] == "success"), 
        "No URL found"
    )

    print("\n" + "="*45)
    print(f"SUCCESS: Video generated in {round(end_time - start_time, 2)}s")
    print(f"DOWNLOAD: {final_video_url}")
    print("="*45)

# ---------------------------------------------------------
# MAIN ENTRY
# ---------------------------------------------------------

if __name__ == "__main__":
    try:
        run_generation_pipeline()
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")