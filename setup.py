from setuptools import setup, find_packages

setup(
    name="bugster",
    version="0.1.0",
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
