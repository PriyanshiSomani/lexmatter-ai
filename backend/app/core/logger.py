"""
LexMatter AI — Centralized Application Logger Module
Provides structured logging across FastAPI routers, LangGraph multi-agent orchestration engine,
retrieval services, and document ingestion pipelines.
"""

import logging
import os
import sys
from typing import Optional


def setup_logger(
    name: str = "lexmatter",
    log_level: Optional[str] = None,
    log_to_file: bool = True,
    log_file_path: str = "logs/lexmatter.log",
) -> logging.Logger:
    """
    Creates and configures a structured logger with console and file handlers.
    """
    logger = logging.getLogger(name)

    # Determine log level from env or parameter
    if log_level is None:
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    else:
        log_level_str = log_level.upper()

    level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if already configured
    if logger.handlers:
        return logger

    # Standard log format: timestamp level [logger_name] message
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional File Handler
    if log_to_file:
        try:
            log_dir = os.path.dirname(log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # Fallback if file handler creation fails (e.g. permission restriction)
            logger.warning(f"Could not create file log handler at {log_file_path}: {e}")

    logger.propagate = False
    return logger


# Default application-wide logger instance
logger = setup_logger("lexmatter")


def get_logger(module_name: str) -> logging.Logger:
    """
    Returns a child logger scoped under the main 'lexmatter' logger namespace.
    Example: get_logger("agents.supervisor") -> logger named "lexmatter.agents.supervisor"
    """
    return logging.getLogger(f"lexmatter.{module_name}")
