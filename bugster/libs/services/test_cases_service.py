from bugster.libs.settings import libs_settings
from bugster.utils.enums import BugsterApiPath
from bugster.analyzer.cache import DOT_BUGSTER_DIR_PATH
from bugster.analyzer.core.framework_detector import get_project_info
import os
from loguru import logger
import httpx
from typing import Any
import yaml
from pathlib import Path

TEST_CASES_DIR_NAME = "test_cases"


class TestCasesService:
    """Service to generate test cases for a given codebase analysis."""

    def _set_analysis_json_path(self) -> str:
        """Set the `analysis.json` file path."""
        project_info = get_project_info()
        cache_framework_dir = os.path.join(
            DOT_BUGSTER_DIR_PATH, project_info["data"]["framework_id"]
        )
        self.analysis_json_path = os.path.join(cache_framework_dir, "analysis.json")

    async def _post_analysis(self) -> list[dict[Any, str]]:
        """Post the `analysis.json` file to the API and receive the test cases."""
        async with httpx.AsyncClient() as client:
            with open(self.analysis_json_path, "rb") as file:
                files = {"file": ("analysis.json", file, "application/json")}
                response = await client.post(
                    f"{libs_settings.bugster_api_url}{BugsterApiPath.TEST_CASES}",
                    files=files,
                )

            response.raise_for_status()
            return response.json()

    def _save_test_cases_as_yaml(self, test_cases: list[dict[Any, str]]):
        """Save test cases as individual YAML files."""
        output_dir = Path(TEST_CASES_DIR_NAME)
        output_dir.mkdir(exist_ok=True)

        for i, test_case in enumerate(test_cases):
            file_name = f"{i + 1}_{test_case.name.lower().replace(' ', '_')}.yaml"
            file_path = output_dir / file_name
            test_case_dict = test_case.dict()

            with open(file_path, "w") as f:
                yaml.dump(test_case_dict, f, default_flow_style=False)

            logger.info("Saved test case to {}", file_path)

        return output_dir

    def generate(self):
        """Generate test cases for the given codebase analysis."""
        self._set_analysis_json_path()
        test_cases = self._post_analysis()
        self._save_test_cases_as_yaml(test_cases=test_cases)
