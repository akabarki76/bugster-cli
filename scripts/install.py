#!/usr/bin/env python3
"""
Cross-platform installer for Bugster CLI
Can be run directly:
    python install.py

Or via curl:
    curl -sSL https://raw.githubusercontent.com/Bugsterapp/bugster-cli/main/install.py | python3
"""
import os
import platform
import subprocess
import sys
import tempfile
import zipfile
import shutil
from urllib.request import urlretrieve

GITHUB_REPO = "https://github.com/Bugsterapp/bugster-cli"
DEFAULT_VERSION = "v0.1.0"

def print_step(message):
    """Print a step message."""
    print(f"\n=> {message}")

def run_command(command):
    """Run a shell command and print its output."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error output: {e.stderr}")
        return None

def get_latest_version():
    """Get the latest version from GitHub."""
    print_step("Checking for latest version...")
    
    # Try using the GitHub CLI first
    try:
        result = subprocess.run(
            "gh release list --limit 1 --repo " + GITHUB_REPO,
            shell=True, capture_output=True, text=True
        )
        if result.returncode == 0:
            # Parse the output to get the tag
            tag = result.stdout.strip().split("\t")[2]
            print(f"Latest version is {tag}")
            return tag
    except:
        pass
    
    # Fallback to default version if GitHub CLI is not available
    print(f"Using default version: {DEFAULT_VERSION}")
    return DEFAULT_VERSION

def download_and_extract(version):
    """Download and extract the appropriate asset for the current platform."""
    system = platform.system()
    temp_dir = tempfile.mkdtemp()
    
    print_step(f"Downloading Bugster CLI {version} for {system}...")
    
    # Determine the correct asset name for the current platform
    if system == "Windows":
        asset_name = "bugster-windows.exe.zip"
    elif system == "Darwin":  # macOS
        asset_name = "bugster-macos.zip"
    elif system == "Linux":
        asset_name = "bugster-linux.zip"
    else:
        print(f"Error: Unsupported platform: {system}")
        sys.exit(1)
    
    # Download the asset
    zip_path = os.path.join(temp_dir, "bugster.zip")
    download_url = f"{GITHUB_REPO}/releases/download/{version}/{asset_name}"
    
    try:
        print(f"Downloading from {download_url}...")
        urlretrieve(download_url, zip_path)
    except Exception as e:
        print(f"Error downloading release: {e}")
        print(f"Check if {asset_name} exists for version {version}")
        sys.exit(1)
    
    # Extract the zip file
    try:
        print_step("Extracting files...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    except Exception as e:
        print(f"Error extracting zip file: {e}")
        sys.exit(1)
    
    # Find the executable
    if system == "Windows":
        exe_path = os.path.join(temp_dir, "bugster.exe")
    else:
        exe_path = os.path.join(temp_dir, "bugster")
    
    # Make sure the file exists and is executable
    if not os.path.exists(exe_path):
        print(f"Error: Could not find executable in zip file")
        print(f"Expected path: {exe_path}")
        sys.exit(1)
    
    if system != "Windows":
        os.chmod(exe_path, 0o755)  # Make executable on Unix systems
    
    return exe_path, temp_dir

def install_executable(executable_path):
    """Install the executable to the appropriate location for the platform."""
    system = platform.system()
    home = os.path.expanduser("~")
    
    print_step("Installing Bugster CLI...")
    
    # Determine installation directory and executable name
    if system == "Windows":
        install_dir = os.path.join(home, "AppData", "Local", "Programs", "bugster")
        exe_name = "bugster.exe"
        
        # Add to PATH instructions
        path_instructions = (
            f"Please add {install_dir} to your PATH to use 'bugster' from any terminal.\n"
            "You can do this through System Properties > Advanced > Environment Variables."
        )
    else:  # macOS and Linux
        install_dir = os.path.join(home, ".local", "bin")
        exe_name = "bugster"
        
        # Add to PATH instructions
        shell = os.environ.get("SHELL", "").split("/")[-1] or "bash"
        profile = f"~/.{shell}rc" if shell in ["bash", "zsh"] else "~/.profile"
        path_instructions = (
            f"Please add {install_dir} to your PATH to use 'bugster' from any terminal.\n"
            f"You can do this by adding the following line to {profile}:\n"
            f"export PATH=\"$PATH:{install_dir}\""
        )
    
    # Create installation directory if it doesn't exist
    try:
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)
    except Exception as e:
        print(f"Error creating directory {install_dir}: {e}")
        sys.exit(1)
    
    # Copy executable to installation directory
    dest_path = os.path.join(install_dir, exe_name)
    try:
        shutil.copy2(executable_path, dest_path)
        if system != "Windows":
            os.chmod(dest_path, 0o755)  # Ensure it's executable
    except Exception as e:
        print(f"Error copying executable: {e}")
        sys.exit(1)
    
    # Check if the installation directory is in PATH
    path_var = os.environ.get("PATH", "").split(os.pathsep)
    if install_dir not in path_var:
        print("\nNOTE: " + path_instructions)
    
    return dest_path

def test_installation(executable_path):
    """Test the installation by running a simple command."""
    system = platform.system()
    
    print_step("Testing installation...")
    
    try:
        if system == "Windows":
            output = run_command(f'"{executable_path}" --help')
        else:
            output = run_command(f'"{executable_path}" --help')
        
        if output and "bugster" in output.lower():
            print("\n✅ Bugster CLI installed successfully!")
            print(f"Executable path: {executable_path}")
            return True
        else:
            print("\n❌ Installation test failed")
            return False
    except Exception as e:
        print(f"\n❌ Error testing installation: {e}")
        return False

def cleanup(temp_dir):
    """Clean up temporary files."""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except:
        pass

def main():
    """Main installation function."""
    print("=" * 60)
    print("Bugster CLI Installer")
    print("=" * 60)
    
    # Get version
    if len(sys.argv) > 1 and sys.argv[1].startswith("v"):
        version = sys.argv[1]
        print(f"Installing version: {version}")
    else:
        version = get_latest_version()
    
    # Download and extract
    executable_path, temp_dir = download_and_extract(version)
    
    # Install
    installed_path = install_executable(executable_path)
    
    # Test installation
    test_installation(installed_path)
    
    # Clean up
    cleanup(temp_dir)
    
    print("\nTo use Bugster CLI, run: bugster --help")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during installation: {e}")
        sys.exit(1) 