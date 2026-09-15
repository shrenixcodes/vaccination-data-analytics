"""Small shared helpers."""

import logging


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def standardize_text(series):
    """Trim whitespace and upper-case a categorical text column."""
    return series.astype(str).str.strip().str.upper()
