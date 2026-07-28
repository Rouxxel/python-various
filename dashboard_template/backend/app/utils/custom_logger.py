"""
Custom logger — based on python_various_utils/custom_logger.py, wired to config_loader.

Use ``log_handler`` everywhere instead of ``print`` or ad-hoc ``logging.getLogger``.
"""

from __future__ import annotations

import datetime
import logging
import os
import sys

from app.core_specs.configuration.config_loader import config_loader

LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "notset": logging.NOTSET,
}

LOG_FILE_NAME = config_loader["logging"]["log_file_name"]
LOG_DIRECTORY = config_loader["logging"]["dir_name"]
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", config_loader["logging"]["logging_level"])

log_level = LOG_LEVELS.get(LOG_LEVEL_STR.lower(), logging.INFO)

log_handler = logging.getLogger(LOG_FILE_NAME)
log_handler.setLevel(log_level)

log_format = logging.Formatter(
    fmt="%(asctime)s %(msecs)03dZ | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

file_handler = None
log_file = None

try:
    os.makedirs(LOG_DIRECTORY, exist_ok=True)
    log_file = os.path.join(
        LOG_DIRECTORY,
        datetime.datetime.now().strftime(f"{LOG_FILE_NAME}_%Y-%m-%dT%H-%M-%S.log"),
    )
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_format)
except OSError as exc:
    sys.stderr.write(f"ERROR: Failed to create log file at '{log_file}': {exc}\n")
    sys.stderr.write("Continuing with console-only logging.\n")
    file_handler = None
except Exception as exc:
    sys.stderr.write(f"ERROR: Unexpected error during log file initialization: {exc}\n")
    sys.stderr.write("Continuing with console-only logging.\n")
    file_handler = None

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)

if not log_handler.hasHandlers():
    if file_handler is not None:
        log_handler.addHandler(file_handler)
    log_handler.addHandler(console_handler)

log_handler.info("Analytics dashboard backend logger initialized")
if log_file:
    log_handler.warning(
        "Current working directory: %s, logs written to '%s'",
        os.getcwd(),
        log_file,
    )
else:
    log_handler.warning(
        "Current working directory: %s, file logging unavailable — console only",
        os.getcwd(),
    )


def shutdown_logger() -> None:
    """Flush and close all log handlers before application exit."""
    try:
        for handler in log_handler.handlers[:]:
            try:
                handler.flush()
                handler.close()
                log_handler.removeHandler(handler)
            except Exception as exc:
                sys.stderr.write(f"Error closing log handler: {exc}\n")
    except Exception as exc:
        sys.stderr.write(f"Error during logger shutdown: {exc}\n")
