from enum import Enum


class BugsterApiPath(str, Enum):
    """Bugster API paths."""

    TEST_CASES = "/api/v1/test-cases"
    TEST_CASES_NEW = "/api/v1/test-cases/new"


class GitCommand(list, Enum):
    """Git commands.

    - DIFF_STATUS_PORCELAIN: Get the file paths of all files that have been added, deleted, or modified in the repository.
    - DIFF_CHANGES: Get the changed content of only the deleted or modified files.
    - DIFF_CACHED: Get the changed content of only the newly staged files.
    """

    DIFF_STATUS_PORCELAIN = [
        "git",
        "status",
        "--porcelain",
        "--",
        "*.tsx",
        "*.ts",
        "*.js",
        "*.jsx",
    ]
    DIFF_CHANGES = ["git", "diff", "--", "*.tsx", "*.ts", "*.js", "*.jsx"]
    DIFF_CACHED = ["git", "diff", "--cached", "--", "*.tsx", "*.ts", "*.js", "*.jsx"]
