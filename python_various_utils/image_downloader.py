#!/usr/bin/env python3
"""
Download images from a given URL.
This script uses the requests library to fetch image data and save it locally 
using a streamed approach to maintain memory efficiency.
"""

import requests

def download_image(
    url: str = None, 
    file_name: str = "downloaded_image.png",
    timeout: int = 10
) -> None:
    """
    Download an image from a URL and save it to the local directory.
    
    The output is saved in the same level as the script. 
    Uses stream=True to handle large files gracefully.
    """

    if url is None:
        print("Error: No URL provided.")
        return

    try:
        print(f"--- Starting download: {file_name} ---")

        # Send a GET request to the URL
        response = requests.get(url, stream=True, timeout=timeout)
        response.encoding = 'utf-8'

        # Raise an exception for 4XX or 5XX status codes
        response.raise_for_status()

        # Write the image to a file in binary mode
        print(f"Streaming content to {file_name}...")
        with open(file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # Filter out keep-alive new chunks
                    file.write(chunk)

        print(f"Success! Image has been saved as: {file_name}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("--- Task completed ---")

if __name__ == "__main__":
    TARGET_URL = "url here"

    download_image(
        url=TARGET_URL,
        file_name="MaxxWatt_Logo.png"
    )
