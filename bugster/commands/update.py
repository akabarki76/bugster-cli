import os
import subprocess

import yaml
from git import Repo
from rich.console import Console

from bugster.analyzer.core.app_analyzer.utils.get_tree_structure import (
    filter_paths,
    get_gitignore,
)

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


def is_page_file(file: str) -> bool:
    """Check if a file is a page file."""
    return file.endswith(".page.js")


def find_pages_that_use_file(file: str) -> list[str]:
    """Find pages that use a file."""
    # TODO
    pass


def find_specs_that_use_file(file: str) -> list[str]:
    """Find specs that use a file."""
    pass


def update_command(options: dict = {}):
    """Run Bugster CLI update command."""
    # 1. Get the modified files
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

    # 2. Analyze what pages (ultimate unit of measurement) were affected by the changes (components, layouts, hooks, pages, etc.)
    affected_pages = set()

    for file in diff_files_paths:
        if is_page_file(file=file):
            affected_pages.add(file)
        else:
            pages = find_pages_that_use_file(file=file)

            if pages:
                for page in pages:
                    affected_pages.add(page)

    # 3. Link specs to pages
    specs_files_paths = get_all_files(directory=TEST_CASES_PATH)
    d = {}

    for spec_path in specs_files_paths:
        with open(spec_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            d[data["page"]] = spec_path

    # 4. Send to LLM
    pass
