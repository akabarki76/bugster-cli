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
        "annotated-types==0.7.0",
        "anyio==4.9.0",
        "certifi==2025.4.26",
        "click==8.1.8",
        "h11==0.16.0",
        "httpcore==1.0.9",
        "httpx==0.28.1",
        "httpx-sse==0.4.0",
        "idna==3.10",
        "markdown-it-py==3.0.0",
        "mcp==1.9.0",
        "mdurl==0.1.2",
        "pydantic==2.11.4",
        "pydantic-settings==2.9.1",
        "pydantic_core==2.33.2",
        "Pygments==2.19.1",
        "python-dotenv==1.1.0",
        "python-multipart==0.0.20",
        "PyYAML==6.0.2",
        "rich==14.0.0",
        "shellingham==1.5.4",
        "sniffio==1.3.1",
        "sse-starlette==2.3.5",
        "starlette==0.46.2",
        "typer==0.15.4",
        "typing-inspection==0.4.0",
        "typing_extensions==4.13.2",
        "uvicorn==0.34.2",
        "websockets==15.0.1",
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
    python_requires=">=3.10",
)
