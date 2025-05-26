from git import Repo
from rich.console import Console

from bugster.analyzer.core.app_analyzer.utils.get_tree_structure import (
    filter_paths,
    get_gitignore,
)

console = Console()


def update_command(options: dict = {}):
    """Run Bugster CLI update command."""
    # 1. Get the modified files
    dir_path = "."
    gitignore = get_gitignore(dir_path=dir_path)
    repo = Repo(dir_path)
    diff_files = repo.git.diff("--name-only")
    diff_files_paths = diff_files.split("\n") if diff_files else []
    diff_files_paths = filter_paths(all_paths=diff_files_paths, gitignore=gitignore)

    # 2. Analyze what pages/components/layouts/hooks/etc. were affected by the changes
    pass
