"""
Configuration loader — reads config_file.json at import time.

Secrets and provider credentials stay in ``backend/.env`` (see ``app.config.settings``).
Structural settings (logging, network, routes, mock paths) live in JSON.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_CONFIG_DIR = Path(__file__).resolve().parent
CONFIG_FILE_PATH = _CONFIG_DIR / "config_file.json"


def read_data_from_config_json(file_path: Path | str, exit_on_error: bool = True) -> dict:
    """Read and parse a JSON configuration file."""
    path = Path(file_path)
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"ERROR: Config file not found: {path}")
        if exit_on_error:
            sys.exit(1)
        return {}
    except json.JSONDecodeError:
        print(f"ERROR: Failed to parse JSON config file: {path}")
        if exit_on_error:
            sys.exit(1)
        return {}


config_loader: dict = read_data_from_config_json(CONFIG_FILE_PATH, exit_on_error=True)
