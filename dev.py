#!/usr/bin/env python3
"""
Development script for Bugster CLI.
Helps with local development, testing, and installation.
"""

import argparse
import os
import subprocess
import sys

def run_command(command, description=None):
    """Run a shell command and print its output."""
    if description:
        print(f"\n{description}...\n")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    
    return result

def setup_dev():
    """Set up the development environment."""
    run_command("pip install -e .", "Installing in development mode")

def run_tests():
    """Run tests for the project."""
    # You can replace this with proper test command once you have tests
    run_command("python -m bugster.cli --help", "Running basic CLI test")

def build_local():
    """Build the project locally using PyInstaller."""
    run_command("python build.py", "Building executable")

def main():
    parser = argparse.ArgumentParser(description="Development tools for Bugster CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Setup development environment
    subparsers.add_parser("setup", help="Install package in development mode")
    
    # Run tests
    subparsers.add_parser("test", help="Run tests")
    
    # Build executable
    subparsers.add_parser("build", help="Build executable")
    
    # All-in-one command
    subparsers.add_parser("all", help="Run setup, tests, and build")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        setup_dev()
    elif args.command == "test":
        run_tests()
    elif args.command == "build":
        build_local()
    elif args.command == "all":
        setup_dev()
        run_tests()
        build_local()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()