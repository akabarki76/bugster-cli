import sys

from loguru import logger


def setup_logger(show_logs: bool = False):
    """Setup logger."""
    if show_logs is False:
        logger.remove()
        logger.add(sys.stderr, level="CRITICAL")
