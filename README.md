# Programming Projects Collection

A curated collection of reusable programming utilities, sample projects, and starter templates.

## Overview

This repository is organized by language and purpose, with small utilities, examples, and templates for C#, Java, Python, TypeScript, and web projects.

> Note: This is an asset collection rather than a single packaged project. Most folders contain standalone scripts or sample code.

## Folder Summary

- `cs_various_utils/`
  - C# utility classes for common tasks such as logging, image conversion, file downloading, key generation, secure file I/O, input validation, and media extraction.
  - Useful as reusable components or as reference implementations for .NET projects.

- `java_various_utils/`
  - Java utility classes with functionality similar to the C# utilities: logging, image/video conversion, downloading, secure file operations, key generation, validation, and media extraction.
  - Designed as simple, reusable examples for Java projects.

- `java_card_game/`
  - A standalone Java card game sample with build scripts (`build.bat`, `build.sh`, `quick-start.bat`), a `README.md`, and source code organized under `src/`.
  - Includes support libraries and a minimal playable game structure.

- `python_various_utils/`
  - General-purpose Python utility scripts.
  - Key files include:
    - `image_downloader.py` - download images from URLs
    - `img_converter.py` - convert image file formats
    - `video_audio_extractor.py` - extract audio from video files
    - `ffmpeg_video_resolution_increaser.py` - change video resolution via ffmpeg
    - `secure_file_io.py` - secure file read/write helpers
    - `custom_logger.py` - reusable logging helper
    - `keys_generator.py` - key and token generator utilities
    - `remove_emojis.py` - strip emojis from text
    - `pycache_n_logs_deleter.py` - cleanup script for caches and log files
    - `validators.py` - data validation helpers

- `python_external_calls/`
  - Sample Python code for calling external services and APIs.
  - Subfolders:
    - `google_apis/` - examples for Google API calls and embedding tests.
    - `youtube_apis/` - YouTube download and transcript extraction utilities.
    - `heras_api/` - Heras API integration example.

- `python_games/`
  - Lightweight Python game scripts and generators intended for learning or reuse.
  - Includes:
    - `21_blackjack.py` - a simple blackjack game example
    - `num_guess_game.py` - number guessing game
    - `rock_paper_scissors_game.py` - rock-paper-scissors game
    - `password_generator.py` - random password generator

- `python_shapes/`
  - Visual Python scripts that render 2D/3D shapes and animations.
  - Example scripts include:
    - `2d_beating_heart.py`
    - `2d_beating_strawberry.py`
    - `2d_rose.py`
    - `3d_beating_red_globule_stream.py`
    - `3d_infinity_symbol.py`
    - `3d_jellyfish.py`
    - `3d_mobius.py`
    - `3d_rotating_donut.py`
    - `geometric_figures.py`

- `typescript_various/`
  - TypeScript assets and UI utilities, including background components and logo templates.
  - Useful for frontend design experiments or component libraries.

- `templates/`
  - Starter templates for several project types.
  - Includes:
    - `chrome_extensions/` - popup and sidepanel templates for Chrome extensions.
    - `java_rest_api_template/` - a Java REST API starter project.
    - `python_graphql_template/` - Python GraphQL app template.
    - `python_rest_api_template/` - Python REST API starter with Docker support.
    - `python_websocket_template/` - Python WebSocket service template.
    - `react_ts_template/` - React + TypeScript application template.

## How to Use

Browse the folder that matches the language or utility you need. Each folder contains standalone scripts, reusable utilities, or template boilerplate.

- For Python scripts, run them directly with `python`.
- For Java and C# utilities, inspect the source files as reusable components or copy the patterns into your own projects.
- For templates, use the folder contents as a base for a new app or service.

## License

See the `LICENSE` file for license details.
