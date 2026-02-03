"""Logging configuration."""
import logging
import sys

from app.config import settings


def setup_logging() -> None:
    """Setup application logging."""
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    if settings.LOG_FORMAT == "json":
        # JSON logging for production
        logging.basicConfig(
            level=level,
            format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
    else:
        # Text logging for development
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)]
        )
