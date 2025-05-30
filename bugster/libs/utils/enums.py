from enum import Enum


class BugsterApiPath(str, Enum):
    """Bugster API paths."""

    TEST_CASES = "/api/v1/test-cases"


class GitCommand(str, Enum):
    """Git commands."""

    DIFF_STATUS = "diff_status"
    DIFF_FILES = "diff_files"
    DIFF_CHANGES = "diff_changes"
