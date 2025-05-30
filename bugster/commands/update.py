import os
import time
from collections import defaultdict

import typer
import yaml
from rich.console import Console
from rich.status import Status
from rich.text import Text

from bugster.analyzer.core.app_analyzer.utils.get_tree_structure import (
    filter_paths,
)
from bugster.constants import TESTS_DIR
from bugster.libs.services.test_cases_service import TestCasesService
from bugster.libs.utils.diff_parser import parse_git_diff, parse_git_status
from bugster.libs.utils.files import get_specs_paths
from bugster.libs.utils.git import run_git_command
from bugster.libs.utils.log import setup_logger
from bugster.libs.utils.nextjs.pages_finder import (
    find_pages_that_use_file,
    generate_and_save_import_tree,
    is_nextjs_page,
)

console = Console()


def update_command(
    update_only: bool = False,
    suggest_only: bool = False,
    delete_only: bool = False,
):
    """Run Bugster CLI update command."""
    try:
        setup_logger()
        console.print("✓ Analyzing code changes...")
        diff_changes = run_git_command(
            cmd=["git", "diff", "--diff-filter=d", "--", "."]
        )
        diff_files = run_git_command(
            cmd=["git", "diff", "--diff-filter=d", "--", ".", "--name-only"]
        )
        diff_files_paths = [path for path in diff_files.split("\n") if path.strip()]
        diff_files_paths = filter_paths(all_paths=diff_files_paths)
        console.print(f"✓ Found {len(diff_files_paths)} modified files")
        affected_pages = set()
        import_tree = generate_and_save_import_tree()

        for file in diff_files_paths:
            if is_nextjs_page(file_path=file):
                affected_pages.add(file)
            else:
                pages = find_pages_that_use_file(file_path=file, tree=import_tree)

                if pages:
                    for page in pages:
                        affected_pages.add(page)

        specs_files_paths = get_specs_paths()
        specs_pages = {}

        for spec_path in specs_files_paths:
            with open(spec_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                page_path = data["page_path"]
                relative_path = os.path.relpath(spec_path, TESTS_DIR)
                specs_pages[page_path] = {
                    "data": data,
                    "path": relative_path,
                }

        diff_changes_per_page = defaultdict(list)
        parsed_diff = parse_git_diff(diff_text=diff_changes)
        diff_status = run_git_command(cmd=["git", "status", "--porcelain"])
        parsed_status = parse_git_status(status_output=diff_status)
        deleted_pages = [
            deleted
            for deleted in parsed_status["deleted"]
            if is_nextjs_page(file_path=deleted)
        ]
        added_pages = [
            new for new in parsed_status["new"] if is_nextjs_page(file_path=new)
        ]
        DIFF_SEPARATOR = "\n==========\n"

        for diff in parsed_diff.files:
            old_path = diff.old_path

            if is_nextjs_page(file_path=old_path):
                diff_changes_per_page[old_path] = parsed_diff.to_llm_format(
                    file_change=diff
                )
            else:
                pages = find_pages_that_use_file(file_path=old_path, tree=import_tree)

                if pages:
                    for page in pages:
                        new_diff = parsed_diff.to_llm_format(file_change=diff)
                        diff_changes_per_page[page].append(new_diff)

        service = TestCasesService()
        updated_specs = 0
        suggested_specs = []

        for page in affected_pages:
            if page in specs_pages:
                spec = specs_pages[page]
                spec_data = spec["data"]
                spec_path = spec["path"]

                with Status(
                    f"[yellow]Updating: {spec_path}[/yellow]", spinner="dots"
                ) as status:
                    diff = DIFF_SEPARATOR.join(diff_changes_per_page[page])
                    service.update_spec_by_diff(
                        spec_data=spec_data, diff_changes=diff, spec_path=spec_path
                    )
                    status.update(f"✓ [green]{spec_path}[/green] updated")
                    time.sleep(3)
                    updated_specs += 1
            else:
                text = Text("✗ Page ")
                text.append(page, style="red")
                text.append(" not found in test cases")
                console.print(text)

                # TODO: Implement the real logic for this
                import re

                def camel_to_kebab(text):
                    """Convert camelCase to kebab-case."""
                    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text).lower()

                def suggest_spec_from_page(page_path):
                    """Suggest a spec file name from a page path."""
                    clean_path = re.sub(r"^src/pages/", "", page_path)
                    clean_path = re.sub(r"\.(tsx?|jsx?)$", "", clean_path)

                    def replace_dynamic(match):
                        param = match.group(1)
                        return camel_to_kebab(param)

                    clean_path = re.sub(r"\[([^\]]+)\]", replace_dynamic, clean_path)

                    clean_path = camel_to_kebab(clean_path)
                    return f"{clean_path}.yaml"

                suggested_specs.append(suggest_spec_from_page(page))

        if len(suggested_specs) > 0:
            for spec in suggested_specs:
                console.print(f"⚠️  Suggested new spec: {spec}")

        if updated_specs > 0 and len(suggested_specs) > 0:
            console.print(
                f"✓ Updated {updated_specs} spec{'' if updated_specs == 1 else 's'}, {len(suggested_specs)} suggestion{'' if len(suggested_specs) == 1 else 's'}"
            )
        elif updated_specs > 0:
            console.print(
                f"✓ Updated {updated_specs} spec{'' if updated_specs == 1 else 's'}"
            )
    except Exception as err:
        console.print(f"[red]Error: {str(err)}[/red]")
        raise typer.Exit(1)
