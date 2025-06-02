from enum import Enum


class BugsterApiPath(str, Enum):
    """Bugster API paths."""

    TEST_CASES = "/api/v1/test-cases"
    TEST_CASES_NEW = "/api/v1/test-cases/new"


class GitCommand(list, Enum):
    """Git commands."""

    DIFF_STATUS = ["git", "status", "--porcelain"]
    DIFF_FILES = ["git", "diff", "--name-only"]
    DIFF_CHANGES = ["git", "diff", "--", "."]
    DIFF_CACHED = ["git", "diff", "--cached"]
