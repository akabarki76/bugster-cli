from enum import Enum


class BugsterApiPath(str, Enum):
    """Bugster API paths."""

    TEST_CASES = "/api/v1/test-cases"
    TEST_CASES_NEW = "/api/v1/test-cases/new"


class GitCommand(str, Enum):
    """Git commands."""

    DIFF_STATUS = "diff_status"
    DIFF_FILES = "diff_files"
    DIFF_CHANGES = "diff_changes"
