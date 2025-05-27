import json
import os
import subprocess

import yaml
from rich.console import Console

from bugster.analyzer.core.app_analyzer.utils.get_tree_structure import (
    filter_paths,
)
from bugster.libs.services.test_cases_service import TestCasesService
from bugster.libs.utils.files import get_all_files
from bugster.libs.utils.nextjs.finder import find_pages_using_file
from bugster.libs.utils.nextjs.import_tree_generator import ImportTreeGenerator

console = Console()


DIR_PATH = "."
TEST_CASES_PATH = "test_cases"


def find_pages_that_use_file(file_path: str) -> list[str]:
    """Find pages that use a file."""
    output_file = "import_tree.json"

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
    console.print("✓ Analyzing code changes...")
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
    cmd.insert(2, "--name-only")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    diff_files = result.stdout
    diff_files_paths = [path for path in diff_files.split("\n") if path.strip()]
    diff_files_paths = filter_paths(all_paths=diff_files_paths)
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

    specs_files_paths = get_all_files(directory=TEST_CASES_PATH)
    pages_specs = {}

    for spec_path in specs_files_paths:
        with open(spec_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            page = data["page"]
            pages_specs[page] = spec_path

    for page in affected_pages:
        service = TestCasesService()

        if page in pages_specs:
            console.print(f"Updating: {pages_specs[page]}")
            service.update_test_case_by_page(page=page, diff_changes=diff_changes)
        else:
            console.print(f"✗ Page '{page}' not found in test cases", markup=False)
