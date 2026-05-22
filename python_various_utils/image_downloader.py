#!/usr/bin/env python3
"""
Download images from a given URL.
This script uses the requests library to fetch image data and save it locally 
using a streamed approach to maintain memory efficiency.
"""

import requests
from urllib.parse import urlparse, unquote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

def download_image(
    url: str = None, 
    output_file_name: str = "downloaded_image",
    output_extension: str = "png",
    retries: int = 3,
    timeout: int = 10,
    chunk_size: int = 1024
) -> None:
    """
    Download an image from a URL and save it to the local directory.
    
    The output is saved in the same level as the script. 
    Uses stream=True to handle large files gracefully.
    """

    if url is None:
        print("Error: No URL provided.")
        return

    #session with retries
    session = requests.Session()
    retries = Retry(total=retries, backoff_factor=0.5, status_forcelist=(500,502,503,504))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.mount("http://", HTTPAdapter(max_retries=retries))

    headers = {"User-Agent": "python-image-downloader/1.0"}

    try:
        resp = session.get(url, stream=True, timeout=timeout, headers=headers, allow_redirects=True)
        resp.raise_for_status()

        # Prefer filename from argument, then Content-Disposition, then URL path
        file_name = f"{output_file_name}.{output_extension}" if output_file_name else None
        if not file_name:
            cd = resp.headers.get("content-disposition")
            if cd and "filename=" in cd:
                # crude parse; robust parsing can be added
                file_name = cd.split("filename=")[-1].strip('"; ')
            else:
                parsed = urlparse(resp.url)  # use resp.url to follow redirects
                file_name = os.path.basename(unquote(parsed.path)) or "downloaded_image"
        # Ensure extension if content-type says so
        ctype = resp.headers.get("content-type", "")
        if not ctype.startswith("image/"):
            print(f"Warning: content-type is '{ctype}'. Continuing if you explicitly want it.")

        # Save file
        print(f"--- Starting download: {file_name} ---")
        with open(file_name, "wb") as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
        print(f"Success! Image saved as: {file_name}")

    except requests.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    TARGET_URL = "https://www.lamborghini.com/sites/it-en/files/DAM/lamborghini/0_facelift_2025/model_details_new/temerario_2/mecha/Temerario_00-Mecha-H_Card-Powertrain-last.jpg"

    download_image(
        url=TARGET_URL,
        output_file_name="MaxxWatt_Logo",
        output_extension="png"
    )
