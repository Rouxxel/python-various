"""
    Script to increase video resolution using ffmpeg and the Lanczos algorithm.
    Provides two main functions:
    1. upscale_video_lanczos: Doubles the resolution (or by a specified scale factor).
    2. scale_to_resolution: Scales the video to a specific resolution (e.g., 1920x1080).
"""

import subprocess

def upscale_video_lanczos(
    input_file: str = None, 
    output_file: str = None,
    scale_factor: int = 2
    ):
    """
    Doubles the resolution (or by scale_factor) using the Lanczos algorithm.
    """
    # scale=iw*2:ih*2 multiplies input width and height by 2
    cmd = [
        'ffmpeg', '-i', input_file,
        '-vf', f'scale=iw*{scale_factor}:ih*{scale_factor}:flags=lanczos',
        '-c:v', 'libx264', 
        '-crf', '18', 
        '-preset', 'slow', 
        output_file
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Success! Scaled video saved to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def scale_to_resolution(
    input_file: str, 
    output_file: str, 
    width: int = 1920,
    height: int = 1080
    ):
    """
    Scales a video to a specific resolution using the Lanczos algorithm.
    """
    cmd = [
        'ffmpeg', '-i', input_file,
        '-vf', f'scale={width}:{height}:flags=lanczos',
        '-c:v', 'libx264',
        '-crf', '18',
        '-preset', 'slow',
        output_file
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Success! Video scaled to {width}x{height} saved to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# --- Example Usage ---
if __name__ == "__main__":
    input_path = "old_vid.mp4" # Ensure this file exists in your folder
    output_file = "upscaled_video.mp4"

    # 1. Double the resolution
    upscale_video_lanczos(input_path, output_file)

    # 2. Scale to 1080p
    # scale_to_resolution(input_path, output_file, 1920, 1080)
