from bugster.analyzer.core.app_analyzer import AppAnalyzer, detect_supported_framework
from bugster.analyzer.core.framework_detector import detect_framework


def analyze_codebase() -> None:
    """Analyze the repository codebase."""
    detect_framework(options={"force": True})
    analyzer = AppAnalyzer(framework_info=detect_supported_framework())
    analyzer.execute(options={"force": True})
