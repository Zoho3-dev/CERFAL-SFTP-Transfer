"""Logging configuration with daily rotation and configurable retention."""

import logging
import os
from logging.handlers import TimedRotatingFileHandler


def setup_logging(log_directory: str, log_level: str = "INFO", retention_days: int = 90) -> logging.Logger:
    """Configure logger with console output and daily-rotated file handler."""
    os.makedirs(log_directory, exist_ok=True)

    logger = logging.getLogger("SFTPService")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Avoid duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler (daily rotation)
    log_file = os.path.join(log_directory, "sftp_service.log")
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=retention_days,
        encoding="utf-8",
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("Logging initialisé : %s | Niveau : %s | Rétention : %d jours",
                log_file, log_level, retention_days)

    return logger
