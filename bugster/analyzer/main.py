import sys

from loguru import logger

from src.analyzer.core.app_analyzer import AppAnalyzer, detect_supported_framework
from src.analyzer.core.framework_detector import detect_framework


def analyze_codebase(options: dict = {}) -> None:
    """Analyze the repository codebase."""
    if options.get("show_logs", False) is False:
        logger.remove()
        logger.add(sys.stderr, level="CRITICAL")

    detect_framework(options=options)
    analyzer = AppAnalyzer(framework_info=detect_supported_framework())
    analyzer.execute(options=options)
