#!/usr/bin/env python3
"""
Script to install released versions of Bugster CLI from GitHub releases.
"""

import argparse
import os
import platform
import subprocess
import sys
import tempfile
import shutil
from urllib.request import urlretrieve
import zipfile

GITHUB_REPO = "https://github.com/Bugsterapp/bugster-cli"  # Update with your actual repo

def run_command(command):
    """Run a shell command and print its output."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    
    return result

def get_latest_release():
    """Get the latest release tag from GitHub."""
    # This requires the 'gh' CLI to be installed
    # You can also use the GitHub API directly with requests
    try:
        result = subprocess.run(
            "gh release list --limit 1 --repo " + GITHUB_REPO,
            shell=True, capture_output=True, text=True
        )
        if result.returncode != 0:
            print("Could not fetch latest release. Make sure 'gh' CLI is installed and authenticated.")
            print("Alternatively, specify a version with --version.")
            sys.exit(1)
        
        # Parse the output to get the tag
        tag = result.stdout.strip().split("\t")[2]
        return tag
    except Exception as e:
        print(f"Error fetching latest release: {e}")
        sys.exit(1)

def download_release(version):
    """Download the release for the current platform."""
    system = platform.system()
    temp_dir = tempfile.mkdtemp()
    
    if system == "Windows":
        asset_name = "bugster-windows.exe.zip"
        zip_path = os.path.join(temp_dir, "bugster.zip")
        dest_path = os.path.join(temp_dir, "bugster.exe")
    elif system == "Darwin":  # macOS
        asset_name = "bugster-macos.zip"
        zip_path = os.path.join(temp_dir, "bugster.zip")
        dest_path = os.path.join(temp_dir, "bugster")
    elif system == "Linux":
        asset_name = "bugster-linux.zip"
        zip_path = os.path.join(temp_dir, "bugster.zip")
        dest_path = os.path.join(temp_dir, "bugster")
    else:
        print(f"Unsupported platform: {system}")
        sys.exit(1)
    
    download_url = f"{GITHUB_REPO}/releases/download/{version}/{asset_name}"
    
    try:
        print(f"Downloading {download_url}...")
        urlretrieve(download_url, zip_path)
        
        # Extract the zip file
        print(f"Extracting zip file...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # The macOS zip contains just a single 'bugster' file
        # other platforms might have different structures
        if system == "Darwin":  # macOS
            dest_path = os.path.join(temp_dir, "bugster")
        elif system == "Windows":
            dest_path = os.path.join(temp_dir, "bugster.exe")
        else:  # Linux
            dest_path = os.path.join(temp_dir, "bugster")
        
        if not os.path.exists(dest_path):
            print(f"Could not find executable in zip file at: {dest_path}")
            sys.exit(1)
        
        if system != "Windows":
            os.chmod(dest_path, 0o755)  # Make executable
        
        return dest_path
    except Exception as e:
        print(f"Error downloading or extracting release: {e}")
        print(f"Please make sure the asset {asset_name} exists in the release {version}")
        sys.exit(1)

def install_executable(executable_path):
    """Install the executable to the user's local bin directory."""
    home = os.path.expanduser("~")
    
    if platform.system() == "Windows":
        bin_dir = os.path.join(home, "AppData", "Local", "Programs", "bugster")
        if not os.path.exists(bin_dir):
            os.makedirs(bin_dir)
        
        dest = os.path.join(bin_dir, "bugster.exe")
        shutil.copy2(executable_path, dest)
        
        # Add to PATH if not already there
        path_var = os.environ.get("PATH", "")
        if bin_dir not in path_var:
            print(f"\nPlease add {bin_dir} to your PATH to use 'bugster' from any terminal.")
    else:
        bin_dir = os.path.join(home, ".local", "bin")
        # Ensure the directory exists
        if not os.path.exists(bin_dir):
            os.makedirs(bin_dir)
        
        dest = os.path.join(bin_dir, "bugster")
        shutil.copy2(executable_path, dest)
        
        # Make sure it's executable
        os.chmod(dest, 0o755)
        
        # Check if bin_dir is in PATH
        path_var = os.environ.get("PATH", "")
        if bin_dir not in path_var:
            print(f"\nPlease add {bin_dir} to your PATH to use 'bugster' from any terminal.")
            print(f"You can do this by adding the following to your shell profile:")
            print(f"export PATH=\"$PATH:{bin_dir}\"")
    
    print(f"\nBugster CLI installed to: {dest}")
    return dest

def main():
    parser = argparse.ArgumentParser(description="Install Bugster CLI from GitHub releases")
    parser.add_argument("--version", help="Version to install (default: latest)", default=None)
    
    args = parser.parse_args()
    
    version = args.version
    if not version:
        version = get_latest_release()
        print(f"Installing latest version: {version}")
    
    executable_path = download_release(version)
    install_path = install_executable(executable_path)
    
    # Clean up
    if os.path.exists(os.path.dirname(executable_path)):
        shutil.rmtree(os.path.dirname(executable_path))
    
    print("\nTesting installation...")
    try:
        if platform.system() == "Windows":
            run_command(f'"{install_path}" --version')
        else:
            run_command(f'"{install_path}" --help')
        print("\nInstallation successful!")
    except Exception as e:
        print(f"Installation test failed: {e}")

if __name__ == "__main__":
    main() 