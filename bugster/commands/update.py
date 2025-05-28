import json
import os
import subprocess
import sys

import yaml
from loguru import logger
from rich.console import Console

from bugster.analyzer.core.app_analyzer.utils.get_tree_structure import (
    filter_paths,
    get_gitignore,
)
from bugster.analyzer.core.framework_detector.main import get_project_info
from bugster.constants import BUGSTER_DIR
from bugster.libs.services.test_cases_service import TestCasesService
from bugster.libs.utils.diff_parser import parse_git_diff
from bugster.libs.utils.files import get_all_files
from bugster.libs.utils.nextjs.finder import find_pages_using_file
from bugster.libs.utils.nextjs.import_tree_generator import ImportTreeGenerator

console = Console()


DIR_PATH = "."
TESTS_PATH = os.path.join(BUGSTER_DIR, "tests")


def find_pages_that_use_file(file_path: str) -> list[str]:
    """Find pages that use a file."""
    framework_id = get_project_info()["data"]["frameworks"][0]["id"]
    cache_framework_dir = os.path.join(BUGSTER_DIR, framework_id)
    output_file = os.path.join(cache_framework_dir, "import_tree.json")

    if not os.path.exists(output_file):
        generator = ImportTreeGenerator()
        tree = generator.generate_tree()
        generator.save_to_json(tree=tree, filename=output_file)
    else:
        with open(output_file, "r", encoding="utf-8") as file:
            tree = json.load(file)

    results = find_pages_using_file(tree_data=tree, target_file=file_path)

    if results:
        return [result["page"] for result in results]
    else:
        console.print(f"✗ File '{file_path}' is not imported by any page")
        return []


def update_command(options: dict = {}):
    """Run Bugster CLI update command."""
    logger.remove()
    logger.add(sys.stderr, level="CRITICAL")
    console.print("✓ Analyzing code changes...")
    cmd = ["git", "diff", "--", "."]

    for pattern in ["package-lock.json", ".env.local", ".gitignore", "tsconfig.json"]:
        cmd.append(f":!{pattern}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    diff_changes = result.stdout
    cmd.insert(2, "--name-only")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    diff_files = result.stdout
    diff_files_paths = [path for path in diff_files.split("\n") if path.strip()]
    gitignore = get_gitignore(dir_path=DIR_PATH)
    diff_files_paths = filter_paths(all_paths=diff_files_paths, gitignore=gitignore)
    console.print(f"✓ Found {len(diff_files_paths)} modified files")
    affected_pages = set()
    is_page_file = lambda file: file.endswith(".page.js")

    for file in diff_files_paths:
        if is_page_file(file=file):
            affected_pages.add(file)
        else:
            pages = find_pages_that_use_file(file_path=file)

            if pages:
                for page in pages:
                    affected_pages.add(page)

    specs_files_paths = get_all_files(directory=TESTS_PATH)
    pages_specs = {}

    for spec_path in specs_files_paths:
        with open(spec_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            page = data["page"]
            pages_specs[page] = spec_path

    diff_changes_per_page = {}
    parsed_diff = parse_git_diff(diff_text=diff_changes)

    for diff in parsed_diff.files:
        old_path = diff.old_path

        if is_page_file(file=old_path):
            diff_changes_per_page[old_path] = parsed_diff.to_llm_format(
                file_change=diff
            )
        else:
            pages = find_pages_that_use_file(file_path=old_path)

            if pages:
                for page in pages:
                    diff_changes_per_page[page] = parsed_diff.to_llm_format(
                        file_change=diff
                    )

    for page in affected_pages:
        service = TestCasesService()

        if page in pages_specs:
            console.print(f"Updating: {pages_specs[page]}")
            service.update_test_case_by_page(
                page=page, diff_changes=diff_changes_per_page[page]
            )
        else:
            console.print(f"✗ Page '{page}' not found in test cases", markup=False)
