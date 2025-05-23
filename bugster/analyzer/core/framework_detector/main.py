import json
import os
import re
import time

from loguru import logger

from bugster.analyzer.cache import DOT_BUGSTER_DIR_PATH
from bugster.analyzer.core.app_analyzer.utils.get_tree_structure import get_paths
from bugster.analyzer.utils.errors import BugsterError
from bugster.analyzer.utils.get_git_info import get_git_info

PROJECT_JSON_PATH = os.path.join(DOT_BUGSTER_DIR_PATH, "project.json")


def get_project_info():
    """Get the project info."""
    logger.info("Getting project info...")

    try:
        with open(PROJECT_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as error:
        logger.error("Failed to read cached project data: {}", error)
        raise BugsterError(
            "Failed to read cached project data, execute bugster detect-framework first"
        )


def detect_next_js_dir_path_from_config():
    """Detect the Next.js directory path from the config file."""
    paths = get_paths(os.getcwd())
    next_dir_config_paths = [
        os.path.dirname(file_path)
        for file_path in paths
        if re.search(r"next\.config\.(js|ts|mjs|cjs)$", file_path)
    ]

    if next_dir_config_paths:
        logger.info(
            "Detected Next.js config paths: {}",
            {"nextDirConfigPaths": next_dir_config_paths},
        )
        next_named_dir = next(
            (
                dir_path
                for dir_path in next_dir_config_paths
                if re.search(r"next", dir_path, re.IGNORECASE)
            ),
            None,
        )
        return os.path.join(os.getcwd(), next_named_dir or next_dir_config_paths[0])

    return None


def detect_framework(options={}):
    """Detect the framework of the project."""
    logger.info("Detecting framework...")

    if not options.get("force") and os.path.exists(PROJECT_JSON_PATH):
        try:
            with open(PROJECT_JSON_PATH, "r", encoding="utf-8") as f:
                project_info = json.load(f)

            return project_info
        except Exception as error:
            logger.error("Failed to read cached project data: {}", error)

    framework_infos = []
    next_js_dir_path = detect_next_js_dir_path_from_config()

    if next_js_dir_path:
        framework_infos.append(
            {
                "id": "next",
                "name": "Next.js",
                "dir_path": next_js_dir_path,
            }
        )

    logger.info("Frameworks detected: {}", {"frameworkInfos": framework_infos})
    os.makedirs(DOT_BUGSTER_DIR_PATH, exist_ok=True)

    try:
        VERSION = 2
        project_info = {
            "metadata": {
                "timestamp": int(time.time() * 1000),
                "version": VERSION,
                "git": get_git_info(),
            },
            "data": {
                "frameworks": framework_infos,
            },
        }

        with open(PROJECT_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(project_info, f, indent=2)

        logger.info("Saved project information to {}", PROJECT_JSON_PATH)
        return project_info
    except Exception as error:
        logger.error("Failed to save project information: {}", error)
        raise BugsterError("Failed to save project information")
