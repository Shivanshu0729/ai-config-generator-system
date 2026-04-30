"""Logging utilities."""

import logging
import sys
from datetime import datetime


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get or create a logger instance."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    
    return logger