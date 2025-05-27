import os
import subprocess

import yaml
from git import Repo
from rich.console import Console

from bugster.analyzer.core.app_analyzer.utils.get_tree_structure import (
    filter_paths,
    get_gitignore,
)
from bugster.libs.services.test_cases_service import TestCasesService

console = Console()


DIR_PATH = "."
TEST_CASES_PATH = "test_cases"


def get_all_files(directory):
    """Get all files in a directory."""
    file_paths = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))

    return file_paths


def find_pages_that_use_file(file: str) -> list[str]:
    """Find pages that use a file."""
    # TODO
    pass


def update_command(options: dict = {}):
    """Run Bugster CLI update command."""
    console.print("✓ Analyzing code changes...")
    gitignore = get_gitignore(dir_path=DIR_PATH)
    repo = Repo(DIR_PATH)
    cmd = ["git", "diff", "--", "."]

    for pattern in ["package-lock.json", ".env.local", ".gitignore"]:
        cmd.append(f":!{pattern}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    diff_changes = result.stdout
    diff_files = repo.git.diff("--name-only")
    diff_files_paths = diff_files.split("\n") if diff_files else []
    diff_files_paths = filter_paths(all_paths=diff_files_paths, gitignore=gitignore)
    console.print(f"✓ Found {len(diff_files_paths)} modified files")
    affected_pages = set()
    is_page_file = lambda file: file.endswith(".page.js")

    for file in diff_files_paths:
        if is_page_file(file):
            affected_pages.add(file)
        else:
            pages = find_pages_that_use_file(file=file)

            if pages:
                for page in pages:
                    affected_pages.add(page)

    specs_files_paths = get_all_files(directory=TEST_CASES_PATH)
    pages_specs = {}

    for spec_path in specs_files_paths:
        with open(spec_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            page = data["page"]
            pages_specs[page] = spec_path

    for page in affected_pages:
        service = TestCasesService()
        console.print(f"Updating: {pages_specs[page]}")
        service.update_test_case_by_page(page=page, diff_changes=diff_changes)
