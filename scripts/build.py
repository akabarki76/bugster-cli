#!/usr/bin/env python3
"""
Build script for Bugster CLI using PyInstaller.

PURPOSE: This script is for developers to build the executable distribution.
USAGE:   python scripts/build.py
"""

import os
import platform
import subprocess
import shutil

def main():
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Run PyInstaller
    subprocess.run(["pyinstaller", "bugster.spec", "--clean"], check=True)
    
    system = platform.system()
    print(f"Build completed for {system}.")
    
    # Output location
    if system == "Windows":
        print("Executable is at: dist\\bugster\\bugster.exe")
    else:
        print("Executable is at: dist/bugster/bugster")
    
    print("\nYou can distribute the entire 'dist/bugster' directory or just the executable file.")

if __name__ == "__main__":
    main() 