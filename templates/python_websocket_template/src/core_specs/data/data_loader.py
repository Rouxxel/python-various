"""
#############################################################################
### Data loader file
###
### @file data_loader.py
### @author Sebastian Russo
### @date 2025
#############################################################################

This module loads general data from a JSON file.
"""

# Native imports
import json
import sys


def read_data_from_data_json(file_path: str, exit_on_error: bool = True) -> dict:
    """
    Reads data from a JSON data file.

    Parameters:
        file_path (str): Path to the JSON data file.
        exit_on_error (bool): Whether to exit on error or return None.

    Returns:
        dict: Parsed JSON data.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"ERROR: Data file not found: {file_path}")
        if exit_on_error:
            sys.exit(1)
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Failed to parse JSON data file: {file_path}")
        if exit_on_error:
            sys.exit(1)
        return None


DATA_FILE_PATH = "src/core_specs/data/general_data.json"
data_loader = read_data_from_data_json(DATA_FILE_PATH, exit_on_error=True)
