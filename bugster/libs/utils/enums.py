from enum import Enum


class BugsterApiPath(str, Enum):
    """Bugster API paths."""

    TEST_CASES = "/api/v1/test-cases"
    TEST_CASES_NEW = "/api/v1/test-cases/new"


class GitCommand(list, Enum):
    """Git commands.

    - DIFF_STATUS_PORCELAIN: Get all the file paths of the files that have been added, deleted or modified in the repository.
    - DIFF_CHANGES: Get all the changed content of only deleted or modified files.
    - DIFF_CACHED: Get the changed content of only new files that are staged.
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
