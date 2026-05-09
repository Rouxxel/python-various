#!/usr/bin/env python3
"""
Extract audio and video from a given video file.
This script uses the moviepy library to separate the audio and video components of a video file.
"""

import os
from multiprocessing import Process
from moviepy import VideoFileClip

def extract_audio(
    input_path=None,
    output_audio_format=None,
    ):
    """
    Extract audio from a given video file.
    
    The output is saved in the same level as the script, to change this
    modify the output path in the code.
    """

    # input file path
    if not os.path.exists(input_path) or input_path is None:
        print("Error: File not found.")
        return

    try:
        # Load the video clip
        clip = VideoFileClip(input_path)
        base_str = os.path.splitext(input_path)[0]
        print(f"--- Processing: {os.path.basename(input_path)} Audio extraction ---")

        # Get desired format, modify path for audio_output variable if needed
        audio_output = f"{base_str}_audio.{output_audio_format}"
        # Extract and save Audio
        print(f"Extracting audio to {audio_output}...")
        clip.audio.write_audiofile(audio_output)

        print(f"Success, Audio File have been saved in the {audio_output}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the clip
        if 'clip' in locals():
            clip.close()

def extract_video(
    input_path=None, 
    output_video_format=None
    ):
    """
    Extract video from a given video file.
    
    The output is saved in the same level as the script, to change this
    modify the output path in the code.
    """

    # input file path
    if not os.path.exists(input_path) or input_path is None:
        print("Error: File not found.")
        return

    try:
        # Load the video clip
        clip = VideoFileClip(input_path)
        base_str = os.path.splitext(input_path)[0]
        print(f"--- Processing: {os.path.basename(input_path)} video extraction ---")

        # Get desired format, to change the output path modify the video_output variable
        video_output = f"{base_str}_no_audio.{output_video_format}"
        # Save Video (without audio)
        print(f"Exporting video to {video_output}...")
        clip.without_audio().write_videofile(video_output)

        print(f"Success, video file have been saved in the {video_output}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the clip
        if 'clip' in locals():
            clip.close()

def parallel_extraction(
    input_path=None, 
    xtrct_audio=True,
    output_audio_format=None, 
    xtrct_video=True,
    output_video_format=None):
    """
    Run audio and video extraction in parallel using multiprocessing.
    """

    processes_list = []

    #start desired processes
    if xtrct_audio and output_audio_format is not None:
        audio_process = Process(target=extract_audio, args=(input_path, output_audio_format))
        audio_process.start()
    if xtrct_video and output_video_format is not None:
        video_process = Process(target=extract_video, args=(input_path, output_video_format))
        video_process.start()

    for process in processes_list:
        process.join()

    print("--- Task/s completed! ---")

if __name__ == "__main__":
    parallel_extraction(
        input_path="old_video.mp4",
        xtrct_audio=True,
        output_audio_format="mp3",
        xtrct_video=True,
        output_video_format="mp4"
    )
