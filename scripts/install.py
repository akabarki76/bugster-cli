#!/usr/bin/env python3
"""
Cross-platform installer for Bugster CLI
Can be run directly:
    python install.py [--version VERSION]

Or via curl:
    curl -sSL https://raw.githubusercontent.com/Bugsterapp/bugster-cli/main/scripts/install.py | python3 - --version VERSION
"""
import argparse
import os
import platform
import subprocess
import sys
import tempfile
import zipfile
import shutil
import json
import ssl
import re
from urllib.request import urlretrieve, Request, urlopen
from urllib.error import URLError

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# ANSI color codes
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Check Python version
if sys.version_info < (3, 10):
    print(f"{RED}Error: Python 3.10 or higher is required.")
    print(f"Current Python version: {platform.python_version()}")
    print(f"Please upgrade your Python installation and try again.{RESET}")
    sys.exit(1)

GITHUB_REPO = "https://github.com/Bugsterapp/bugster-cli"
GITHUB_API = "https://api.github.com/repos/Bugsterapp/bugster-cli"
DEFAULT_VERSION = "v0.1.0"


def print_step(message):
    """Print a step message."""
    print(f"\n{BLUE}=> {message}{RESET}")


def print_error(message):
    """Print an error message."""
    print(f"{RED}{message}{RESET}")


def print_success(message):
    """Print a success message."""
    print(f"{GREEN}{message}{RESET}")


def print_warning(message):
    """Print a warning message."""
    print(f"{YELLOW}{message}{RESET}")


def run_command(command):
    """Run a shell command and print its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"Error executing command: {command}")
        print_error(f"Error output: {e.stderr}")
        return None


def is_development_version(version):
    """Check if the version is a development version (beta, rc, alpha)."""
    return bool(re.search(r"-beta|-rc|-alpha", version))


def get_api_endpoint(version):
    """Get the API endpoint based on version."""
    if is_development_version(version):
        return "dev.bugster.api"
    return "api.bugster.app"


def validate_version(version):
    """Validate version format."""
    if version == "latest":
        return True
    if not re.match(r"^v\d+\.\d+\.\d+(-beta\.\d+|-rc\.\d+|-alpha\.\d+)?$", version):
        print_error("Invalid version format. Examples of valid versions:")
        print("  - v0.2.8")
        print("  - v0.2.8-beta.1")
        print("  - v0.2.8-rc.1")
        print("  - v0.2.8-alpha.1")
        print("  - latest")
        return False
    return True


def get_latest_version():
    """Get the latest version from GitHub."""
    print_step("Checking for latest version...")

    try:
        # Create request with headers
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        request = Request(f"{GITHUB_API}/releases/latest", headers=headers)

        # Make the request
        with urlopen(request) as response:
            release = json.loads(response.read())

        if release:
            tag = release["tag_name"]
            print_success(f"Latest version is {tag}")
            return tag
    except URLError as e:
        print_error(f"Error fetching latest version: {e}")
        print_warning("Network connection error. Please check your internet connection.")
    except Exception as e:
        print_error(f"Error fetching latest version: {e}")

    # Fallback to default version if API request fails
    print_warning(f"Using default version: {DEFAULT_VERSION}")
    return DEFAULT_VERSION


def check_version_exists(version):
    """Check if the specified version exists in GitHub releases."""
    try:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        request = Request(f"{GITHUB_API}/releases/tags/{version}", headers=headers)
        
        with urlopen(request) as response:
            return response.getcode() == 200
    except URLError:
        return False


def download_with_progress(url, destination):
    """Download a file with progress indicator."""
    try:
        with urlopen(url) as response:
            total_size = int(response.headers.get("content-length", 0))
            block_size = 8192
            current_size = 0

            with open(destination, "wb") as f:
                while True:
                    block = response.read(block_size)
                    if not block:
                        break
                    current_size += len(block)
                    f.write(block)
                    
                    if total_size > 0:
                        progress = current_size / total_size * 100
                        print(f"\rDownloading... {progress:.1f}%", end="", flush=True)

            print("\rDownload complete!      ")
            return True
    except Exception as e:
        print_error(f"\nError during download: {e}")
        return False


def download_and_extract(version):
    """Download and extract the appropriate asset for the current platform."""
    system = platform.system()
    temp_dir = tempfile.mkdtemp()

    print_step(f"Downloading Bugster CLI {version} for {system}...")

    # Determine the correct asset name for the current platform
    if system == "Windows":
        asset_name = "bugster-windows.zip"
    elif system == "Darwin":  # macOS
        asset_name = "bugster-macos.zip"
    elif system == "Linux":
        asset_name = "bugster-linux.zip"
    else:
        print_error(f"Unsupported platform: {system}")
        sys.exit(1)

    # Download the asset
    zip_path = os.path.join(temp_dir, "bugster.zip")
    download_url = f"{GITHUB_REPO}/releases/download/{version}/{asset_name}"

    try:
        print(f"Downloading from {download_url}...")
        if not download_with_progress(download_url, zip_path):
            raise Exception("Download failed")
    except Exception as e:
        print_error(f"Error downloading release: {e}")
        print_error(f"Check if {asset_name} exists for version {version}")
        sys.exit(1)

    # Extract the zip file
    try:
        print_step("Extracting files...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
    except Exception as e:
        print_error(f"Error extracting zip file: {e}")
        sys.exit(1)

    # Find the executable
    if system == "Windows":
        exe_path = os.path.join(temp_dir, "bugster.exe")
    else:
        exe_path = os.path.join(temp_dir, "bugster")

    # Make sure the file exists and is executable
    if not os.path.exists(exe_path):
        print_error("Could not find executable in zip file")
        print_error(f"Expected path: {exe_path}")
        sys.exit(1)

    if system != "Windows":
        os.chmod(exe_path, 0o755)  # Make executable on Unix systems

    return exe_path, temp_dir


def add_to_path(install_dir):
    """Add the installation directory to PATH in shell configuration file."""
    shell = os.environ.get("SHELL", "").split("/")[-1] or "bash"
    home = os.path.expanduser("~")

    if shell in ["bash", "zsh"]:
        config_file = os.path.join(home, f".{shell}rc")
    else:
        config_file = os.path.join(home, ".profile")

    export_line = f'\nexport PATH="$PATH:{install_dir}"\n'

    try:
        # Check if the line already exists
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                content = f.read()
                if install_dir in content:
                    return False

        # Append the export line
        with open(config_file, "a") as f:
            f.write(export_line)
        print_success(f"\nAdded Bugster to PATH in {config_file}")
        return True
    except Exception as e:
        print_warning(f"\nWarning: Could not add to PATH automatically: {e}")
        return False


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

        # Create .local/bin if it doesn't exist
        if not os.path.exists(install_dir):
            os.makedirs(install_dir, exist_ok=True)

        # Add to PATH automatically for Unix systems
        shell = os.environ.get("SHELL", "").split("/")[-1] or "bash"
        profile = f"~/.{shell}rc" if shell in ["bash", "zsh"] else "~/.profile"

        # Only show manual instructions if automatic addition fails
        if not add_to_path(install_dir):
            path_instructions = (
                f"Please add {install_dir} to your PATH to use 'bugster' from any terminal.\n"
                f"You can do this by adding the following line to {profile}:\n"
                f'export PATH="$PATH:{install_dir}"'
            )

    # Create installation directory if it doesn't exist
    try:
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)
    except Exception as e:
        print_error(f"Error creating directory {install_dir}: {e}")
        sys.exit(1)

    # Backup existing installation if it exists
    dest_path = os.path.join(install_dir, exe_name)
    if os.path.exists(dest_path):
        backup_path = f"{dest_path}.bak"
        try:
            shutil.move(dest_path, backup_path)
            print_warning(f"Backed up existing installation to {backup_path}")
        except Exception as e:
            print_warning(f"Could not backup existing installation: {e}")

    # Copy executable to installation directory
    try:
        shutil.copy2(executable_path, dest_path)
        if system != "Windows":
            os.chmod(dest_path, 0o755)  # Ensure it's executable
    except Exception as e:
        print_error(f"Error copying executable: {e}")
        sys.exit(1)

    # Check if the installation directory is in PATH
    path_var = os.environ.get("PATH", "").split(os.pathsep)
    if install_dir not in path_var and system == "Windows":
        print_warning("\nNOTE: " + path_instructions)

    return dest_path


def test_installation(executable_path, version):
    """Test the installation by running a simple command."""
    system = platform.system()

    print_step("Testing installation...")

    try:
        # First check if the file exists and is executable
        if not os.path.exists(executable_path):
            print_error(f"Executable not found at: {executable_path}")
            return False

        # Check file permissions on Unix systems
        if system != "Windows":
            mode = os.stat(executable_path).st_mode
            if not mode & 0o111:
                print_error(f"Executable does not have execute permissions: {executable_path}")
                return False

        # Try to run the version command
        try:
            result = subprocess.run(
                [executable_path, "--version"],
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on non-zero exit
            )
            
            if result.returncode != 0:
                print_error(f"Command failed with exit code {result.returncode}")
                if result.stdout:
                    print_error(f"stdout: {result.stdout}")
                if result.stderr:
                    print_error(f"stderr: {result.stderr}")
                return False

            # If we get any output and no error, consider it a success
            if result.stdout:
                print_success("\n✅ Bugster CLI installed successfully!")
                print(f"Executable path: {executable_path}")
                
                # Show environment info
                api_endpoint = get_api_endpoint(version)
                print_success(f"Environment: {'Development' if is_development_version(version) else 'Production'}")
                print_success(f"API Endpoint: {api_endpoint}")
                
                # Show version info
                installed_version = result.stdout.strip()
                if installed_version != version:
                    print_warning(f"\nNote: Installed version shows as {installed_version}")
                    print_warning("This is expected as the version is currently hardcoded in bugster/__init__.py")
                    print_warning(f"The correct version {version} has been installed but will show after the next release")
                
                return True
            else:
                print_error("No output from --version command")
                if result.stderr:
                    print_error(f"stderr: {result.stderr}")
                return False

        except subprocess.SubprocessError as e:
            print_error(f"Error running version command: {e}")
            return False

    except Exception as e:
        print_error(f"Error testing installation: {e}")
        return False

    print_error("Installation test failed")
    return False


def cleanup(temp_dir):
    """Clean up temporary files."""
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print_warning(f"Warning: Could not clean up temporary files: {e}")


def main():
    """Main installation function."""
    parser = argparse.ArgumentParser(description="Install Bugster CLI", add_help=False)
    parser.add_argument("-v", "--version", help="Version to install (e.g., v0.2.8, v0.2.8-beta.1, or 'latest')", default="latest")
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    args = parser.parse_args()

    version = args.version.lower()

    # Validate version format
    if not validate_version(version):
        sys.exit(1)

    # Get latest version if requested
    if version == "latest":
        version = get_latest_version()

    # Check if version exists
    if not check_version_exists(version):
        print_error(f"Version {version} not found")
        print_warning("Use 'latest' to install the latest version")
        sys.exit(1)

    # Show environment info
    api_endpoint = get_api_endpoint(version)
    print_step(f"Installing Bugster CLI {version}")
    print(f"Environment: {'Development' if is_development_version(version) else 'Production'}")
    print(f"API Endpoint: {api_endpoint}")

    # Download and install
    exe_path, temp_dir = download_and_extract(version)
    installed_path = install_executable(exe_path)
    success = test_installation(installed_path, version)
    cleanup(temp_dir)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
