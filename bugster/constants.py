"""
Bugster CLI constants and configurations.
"""

from pathlib import Path

# Directory Structure
WORKING_DIR = Path.cwd()
BUGSTER_DIR = WORKING_DIR / ".bugster"
CONFIG_PATH = BUGSTER_DIR / "config.yaml"
TESTS_DIR = BUGSTER_DIR / "tests"
EXAMPLE_DIR = TESTS_DIR / "example"
EXAMPLE_TEST_FILE = EXAMPLE_DIR / "tests.yaml"

# Example Test Template
EXAMPLE_TEST = """# @META:{"id":"97e3fc25-bc8d-42e6-aece-0d9205fd1abc","version":1}
# This comment contains machine-readable metadata that should not be modified
- name: Basic Login Test
  task: Verify that users can log in with valid credentials
  expected_result: User should be successfully logged in and redirected to the dashboard
  steps:
    - Navigate to login page
    - Enter valid credentials
    - Click login button
    - Verify successful login
"""
