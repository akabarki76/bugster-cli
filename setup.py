from setuptools import setup, find_packages
import re

# Read version from bugster/__init__.py
with open("bugster/__init__.py", "r") as f:
    version_match = re.search(r'__version__ = ["\']([^"\']*)["\']', f.read())
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name="bugster",
    version=version,
    packages=find_packages(),
    install_requires=[
        "typer[all]==0.15.4",
        "rich==14.0.0",
        "PyYAML==6.0.2",
    ],
    entry_points={
        "console_scripts": [
            "bugster=bugster.cli:main",
        ],
    },
    author="Bugster Team",
    description="A CLI tool for managing test cases",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="testing, cli, automation",
    python_requires=">=3.7",
)
