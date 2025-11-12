import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

from .config import settings

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(name: str = "app") -> logging.Logger:
    """
    Set up logging configuration for the application.

    Args:
        name: The name of the logger

    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(console_handler)

    # File handler
    file_handler = RotatingFileHandler(
        logs_dir / f"{name}.log", maxBytes=10485760, backupCount=5, encoding="utf-8"  # 10MB
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(file_handler)

    return logger


def log_request_info(request_data: Dict[str, Any]) -> None:
    """
    Log incoming request information.

    Args:
        request_data: Dictionary containing request information
    """
    logger = logging.getLogger("app.request")
    logger.info(
        "Request: %s %s from %s",
        request_data.get("method"),
        request_data.get("url"),
        request_data.get("client"),
    )


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log error information with context.

    Args:
        error: The exception that occurred
        context: Additional context information
    """
    logger = logging.getLogger("app.error")
    logger.error("Error occurred: %s", str(error), exc_info=error, extra={"context": context or {}})
