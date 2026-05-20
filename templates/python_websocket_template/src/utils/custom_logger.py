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

# --- CONFIGURATION AREA ---
#Map config string levels to logging module levels
LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "notset": logging.NOTSET,
}
LOG_FILE_NAME = config_loader["logging"]["log_file_name"]
LOG_LEVEL_STR = config_loader["logging"]["logging_level"]
LOG_DIRECTORY = config_loader["logging"]["dir_name"]

#Get log level string
log_level = LOG_LEVELS.get(LOG_LEVEL_STR.lower(), logging.INFO)

# --- Log basic configuration and formatting ---
log_handler = logging.getLogger(LOG_FILE_NAME)
log_handler.setLevel(log_level)

# --- Logger formatter ---
log_format = logging.Formatter(
    fmt="%(asctime)s %(msecs)03dZ | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# --- File handler (File accessible only when it runs locally) ---
#Create folder
os.makedirs(LOG_DIRECTORY,exist_ok=True)

#Create log file
log_file = os.path.join(
                    LOG_DIRECTORY,
                    datetime.datetime.now().strftime(
                        f"{LOG_FILE_NAME}_%Y-%m-%dT%H-%M-%S.log"))
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(log_format)

#Console handler to logs
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)

#Final log handler
if not log_handler.hasHandlers():
    log_handler.addHandler(file_handler)
    log_handler.addHandler(console_handler)

log_handler.info("WebSocket Template server starting")
log_handler.warning(f"Current working directory: {os.getcwd()}, Logs are written to '{log_file}'")

#Example usage
"""
from src.utils.custom_logger import log_handler

log_handler.debug("Debug message")
log_handler.info("Info message")
log_handler.warning("Warning message")
log_handler.error("Error message")
log_handler.critical("Critical message")
"""
