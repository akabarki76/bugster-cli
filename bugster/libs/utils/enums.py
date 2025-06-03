from enum import Enum


class BugsterApiPath(str, Enum):
    """Bugster API paths."""

    TEST_CASES = "/api/v1/test-cases"
    TEST_CASES_NEW = "/api/v1/test-cases/new"


class GitCommand(list, Enum):
    """Git commands.

    - DIFF_STATUS: Get the status of the files in the repository.
    - DIFF_CHANGES: Get the changes in the files that have changed in the repository.
    - DIFF_CACHED: Get the changes in the files that have been staged in the repository.
    - DIFF_FILES: Get the files that have changed in the repository.
    """

    DIFF_STATUS = [
        "git",
        "status",
        "--porcelain",
        "--",
        "*.tsx",
        "*.ts",
        "*.js",
        "*.jsx",
        "*.tsx",
        "*.ts",
        "*.js",
        "*.jsx",
    ]
    DIFF_CHANGES = ["git", "diff", "--", "*.tsx", "*.ts", "*.js", "*.jsx"]
    DIFF_CACHED = ["git", "diff", "--cached", "--", "*.tsx", "*.ts", "*.js", "*.jsx"]
    DIFF_FILES = ["git", "diff", "--name-only"]  # Unused
