"""
#############################################################################
### Custom logger file
###
### @file custom_logger.py
### @author Sebastian Russo
### @date 2025
#############################################################################

This module initializes a custom logger for the WebSocket backend.
"""

# Native imports
import os
import logging
import sys
import datetime

# Other files imports
from src.core_specs.configuration.config_loader import config_loader

LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "notset": logging.NOTSET,
}

log_level_str = config_loader["logging"].get("logging_level", "info").lower()
log_level = LOG_LEVELS.get(log_level_str, logging.INFO)

log_handler = logging.getLogger(config_loader["logging"]["log_file_name"])
log_handler.setLevel(log_level)

log_format = logging.Formatter(
    fmt="%(asctime)s %(msecs)03dZ | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

log_directory = config_loader["logging"]["dir_name"]
os.makedirs(log_directory, exist_ok=True)

log_file = os.path.join(
    log_directory,
    datetime.datetime.now().strftime(
        f"{config_loader['logging']['log_file_name']}_%Y-%m-%dT%H-%M-%S.log"
    ),
)
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(log_format)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)

if not log_handler.hasHandlers():
    log_handler.addHandler(file_handler)
    log_handler.addHandler(console_handler)

log_handler.info("WebSocket Template server starting")
log_handler.warning(f"Current working directory: {os.getcwd()}, Logs: '{log_file}'")
