"""
#############################################################################
### Data loader file
###
### @file data_loader.py
### @author Sebastian Russo
### @date 2025
#############################################################################

This module loads data from JSON files for the GraphQL API.
"""

import json
import sys
from src.core_specs.configuration.config_loader import config_loader

def read_data_from_json(file_path: str, exit_on_error: bool = True) -> dict:
    """
    Reads data from a JSON file.

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
        else:
            return None
    except json.JSONDecodeError:
        print(f"ERROR: Failed to parse JSON data file: {file_path}")
        if exit_on_error:
            sys.exit(1)
        else:
            return None

# Load general data
data_loader = read_data_from_json(
    config_loader["defaults"]["general_data_path"], 
    exit_on_error=True
)