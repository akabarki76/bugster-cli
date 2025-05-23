from bugster.analyzer.utils.errors import BugsterError


def assert_condition(condition, msg="Assertion failed"):
    """Assert that a condition is true, otherwise raise a BugsterError."""
    if not condition:
        raise BugsterError(msg)


def assert_defined(value, msg="Value is undefined or null"):
    """Assert that a value is not None, otherwise raise a BugsterError."""
    assert_condition(value is not None, msg)
    return value
