import os
from typing import Any

import requests
import yaml
from loguru import logger

from bugster.analyzer.core.framework_detector import get_project_info
from bugster.constants import BUGSTER_DIR, TESTS_DIR
from bugster.libs.settings import libs_settings
from bugster.libs.utils.enums import BugsterApiPath
from bugster.libs.utils.errors import BugsterError


class TestCasesService:
    """Service to generate test cases for a given codebase analysis."""

    TEST_CASES_DIR_NAME = "test_cases"

    def __init__(self):
        """Initialize the service."""
        self.analysis_json_path = None
        self.full_url = (
            f"{libs_settings.bugster_api_url}{BugsterApiPath.TEST_CASES.value}"
        )

    def _set_analysis_json_path(self) -> str:
        """Set the `analysis.json` file path."""
        project_info = get_project_info()
        cache_framework_dir = os.path.join(
            BUGSTER_DIR, project_info["data"]["frameworks"][0]["id"]
        )
        self.analysis_json_path = os.path.join(cache_framework_dir, "analysis.json")

    def _post_analysis_json(self) -> list[dict[Any, str]]:
        """Post the `analysis.json` file to the API and receive the test cases."""
        logger.info("Posting analysis.json file to the API...")
        if not self.analysis_json_path:
            raise BugsterError("Analysis JSON path is not set")

        if not os.path.exists(self.analysis_json_path):
            raise BugsterError(
                "Analysis JSON file not found, execute bugster analyze first"
            )

        try:
            with open(self.analysis_json_path, "rb") as file:
                files = {"file": ("analysis.json", file, "application/json")}
                response = requests.post(self.full_url, files=files)

            logger.info("Response status code: {}", response.status_code)
            response.raise_for_status()
            data = response.json()
            logger.info("Received test cases from the API: {}", data)
            return data
        except requests.exceptions.HTTPError as err:
            logger.error(
                "Error posting analysis.json file to the API: {}. Response text: {}",
                err,
                response.text,
            )
        except Exception as err:
            logger.error("Error posting analysis.json file to the API: {}", err)
            raise err

    def _save_test_cases_as_yaml(self, test_cases: list[dict[Any, str]]):
        """Save test cases as individual YAML files."""
        logger.info("Saving test cases as YAML files...")
        output_dir = TESTS_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, test_case in enumerate(test_cases):
            file_name = f"{i + 1}_{test_case['name'].lower().replace(' ', '_')}.yaml"
            file_path = output_dir / file_name

            with open(file_path, "w") as f:
                yaml.dump(test_case, f, default_flow_style=False)

            logger.info("Saved test case to {}", file_path)

        logger.info("Test cases saved successfully")
        return output_dir

    def generate_test_cases(self):
        """Generate test cases for the given codebase analysis."""
        self._set_analysis_json_path()
        test_cases = self._post_analysis_json()
        return self._save_test_cases_as_yaml(test_cases=test_cases)

    def update_spec_by_diff(
        self, spec_data: dict[Any, str], diff_changes: str, spec_path: str
    ):
        """Update a spec file by diff changes."""
        try:
            payload = {"test_case": spec_data, "git_diff": diff_changes}
            response = requests.put(self.full_url, json=payload)
            logger.info("Response status code: {}", response.status_code)
            response.raise_for_status()
            data = response.json()
            logger.info("Received test cases from the API: {}", data)
            return data
        except requests.exceptions.HTTPError as err:
            logger.error(
                "Error updating spec by diff: {}. Response text: {}", err, response.text
            )
            raise err
        except Exception as err:
            logger.error("Error updating spec by diff: {}", err)
            raise err
