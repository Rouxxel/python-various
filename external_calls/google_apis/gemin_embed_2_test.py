"""
GEMINI MULTIMODAL EMBEDDING ENGINE
----------------------------------
This module generates high-dimensional (3072) semantic vectors from video files.
Supports Local Files, Public HTTPS URLs, and Google Cloud Storage (GS) URIs.
Designed for automated event photography and drone performance analysis.
"""

import json
import requests
import os
from google import genai
from google.genai import types

# ---------------------------------------------------------
# CONFIGURATION & INITIALIZATION
# ---------------------------------------------------------

# Initialize the Vertex AI Client
client = genai.Client(
    vertexai=True, 
    project="project_name_google_cloud", 
    location="us-central1"
)

# Define your inputs and outputs here
VIDEO_SOURCE = "local_video_path.mp4" 
OUTPUT_FILENAME = "video_metadata_embed_output.json"
EMBEDDING_MODEL = "gemini-embedding-2-preview"

# ---------------------------------------------------------
# HELPER METHODS
# ---------------------------------------------------------

def prepare_video_part(source):
    """
    Normalizes different video input sources into a Gemini-compatible.
    
    Args:
        source (str): Local path, https:// URL, or gs:// URI.
        
    Returns:
        google.genai.types.Part: The formatted data part for the API request.
    """
    # Case 1: Google Cloud Storage
    if source.startswith("gs://"):
        print(f"Directly referencing Cloud Storage: {source}")
        return types.Part.from_uri(file_uri=source, mime_type="video/mp4")
    
    # Case 2: Public Web URL
    elif source.startswith("http"):
        print(f"Downloading remote video for embedding: {source}")
        r = requests.get(source)
        return types.Part.from_bytes(data=r.content, mime_type="video/mp4")
    
    # Case 3: Local Filesystem
    else:
        print(f"Reading local file: {source}")
        if not os.path.exists(source):
            raise FileNotFoundError(f"Could not find local file: {source}")
            
        with open(source, "rb") as f:
            video_bytes = f.read()
        return types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")

# ---------------------------------------------------------
# CORE PROCESSING EXECUTION
# ---------------------------------------------------------

def run_embedding_pipeline():
    """Executes the data preparation, API call, and result serialization."""
    
    # 1. Prepare data
    video_part = prepare_video_part(VIDEO_SOURCE)

    print(f"--- Generating Gemini Embedding 2 for {VIDEO_SOURCE} ---")

    # 2. Call the Embedding Model
    # Instruction is provided as a text part alongside the video part
    result = client.models.embed_content(
        model=EMBEDDING_MODEL, 
        contents=[
            video_part,
            "Task: Analyze drone flight behavior and battery status for automated editing"
        ],
        config=types.EmbedContentConfig(output_dimensionality=3072)
    )

    # 3. Extract the high-dimensional vector
    embedding = result.embeddings[0].values

    # 4. Consolidate results for JSON storage
    data_to_save = {
        "video_source": VIDEO_SOURCE,
        "model_used": EMBEDDING_MODEL,
        "dimensions": len(embedding),
        "embedding": embedding 
    }

    # 5. Write to local file
    with open(OUTPUT_FILENAME, "w") as f:
        json.dump(data_to_save, f, indent=4)

    print("\n" + "="*40)
    print(f"SUCCESS: Embedding saved to {OUTPUT_FILENAME}")
    print(f"Vector Dimensions: {len(embedding)}")
    print("="*40)

# ---------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    try:
        run_embedding_pipeline()
    except Exception as e:
        print(f"PIPELINE ERROR: {str(e)}")