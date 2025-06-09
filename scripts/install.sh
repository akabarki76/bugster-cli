#!/bin/bash
# Bugster CLI installer wrapper for Unix systems (macOS/Linux)

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_step() {
    echo -e "\n${BLUE}=> $1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

# Help message
show_help() {
    cat << EOF
Bugster CLI Installer

Usage: 
    ./install.sh [options]
    curl -sSL https://raw.githubusercontent.com/Bugsterapp/bugster-cli/main/scripts/install.sh | bash -s -- [options]

Options:
    -v, --version VERSION    Install specific version (e.g., v0.2.8, v0.2.8-beta.1)
    -h, --help              Show this help message

Examples:
    ./install.sh                           # Install latest version
    ./install.sh -v v0.2.8                # Install specific version
    ./install.sh -v v0.2.8-beta.1         # Install beta version
EOF
}

# Parse command line arguments
VERSION="latest"
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

print_step "Detected operating system: $OS"

install_python_macos() {
    print_step "Attempting to install Python 3.12 automatically..."
    
    # Check if Homebrew is installed
    if command -v brew &>/dev/null; then
        print_step "Homebrew found, using it to install Python 3.12..."
        brew install python@3.12
    else
        print_step "Installing Homebrew first (may prompt for password)..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH temporarily
        if [[ -f /opt/homebrew/bin/brew ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f /usr/local/bin/brew ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        else
            print_error "Unable to find Homebrew after installation"
            return 1
        fi
        
        print_step "Installing Python 3.12 via Homebrew..."
        brew install python@3.12
    fi
    
    # Verify Python was installed
    if command -v python3 &>/dev/null; then
        print_success "✅ Python 3 installed successfully!"
        return 0
    else
        print_error "❌ Python installation failed"
        return 1
    fi
}

install_python_linux() {
    print_step "Attempting to install Python 3.12 automatically (may prompt for password)..."
    
    # Detect package manager and install Python
    if command -v apt-get &>/dev/null; then
        print_step "Using apt-get to install Python 3.12..."
        # Add deadsnakes PPA for newer Python versions
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt-get update && sudo apt-get install -y python3.12 python3.12-venv python3.12-distutils
        # Create symlinks if they don't exist
        sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
        sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1
    elif command -v dnf &>/dev/null; then
        print_step "Using dnf to install Python 3.12..."
        sudo dnf install -y python3.12
    elif command -v yum &>/dev/null; then
        print_step "Using yum to install Python 3.12..."
        # Enable EPEL repository for CentOS/RHEL
        sudo yum install -y epel-release
        sudo yum install -y python3.12
    elif command -v pacman &>/dev/null; then
        print_step "Using pacman to install Python 3.12..."
        sudo pacman -S --noconfirm python
    else
        print_error "❌ Unable to detect package manager. Please install Python 3.12 manually."
        return 1
    fi
    
    # Verify Python was installed
    if command -v python3.12 &>/dev/null; then
        print_success "✅ Python 3.12 installed successfully!"
        return 0
    elif command -v python3 &>/dev/null; then
        # Check if python3 is version 3.12
        if python3 --version | grep -q "Python 3.12"; then
            print_success "✅ Python 3.12 installed successfully!"
            return 0
        else
            print_error "❌ Python 3.12 installation failed (different version found)"
            return 1
        fi
    else
        print_error "❌ Python 3.12 installation failed"
        return 1
    fi
}

# Check for minimum Python version
check_python_version() {
    local version=$1
    if [[ $version =~ ^Python\ 3\.([0-9]+) ]]; then
        local minor=${BASH_REMATCH[1]}
        if (( minor >= 10 )); then
            return 0
        fi
    fi
    return 1
}

# Check if Python 3.10+ is installed
if command -v python3 &>/dev/null; then
    version=$(python3 --version 2>&1)
    if check_python_version "$version"; then
        print_success "✅ Python 3.10+ is installed ($version), continuing with installation..."
    else
        print_error "❌ Python 3.10 or higher is required (found $version)"
        print_warning "Would you like to install Python 3.12? (y/n)"
        read -r choice
        if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
            if [[ "$OS" == "macOS" ]]; then
                install_python_macos
            else
                install_python_linux
            fi
        else
            print_error "Please install Python 3.10 or higher manually and try again."
            exit 1
        fi
    fi
elif command -v python &>/dev/null; then
    version=$(python --version 2>&1)
    if check_python_version "$version"; then
        print_success "✅ Python 3.10+ is installed ($version), continuing with installation..."
    else
        print_error "❌ Python 3.10 or higher is required (found $version)"
        print_warning "Would you like to install Python 3.12? (y/n)"
        read -r choice
        if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
            if [[ "$OS" == "macOS" ]]; then
                install_python_macos
            else
                install_python_linux
            fi
        else
            print_error "Please install Python 3.10 or higher manually and try again."
            exit 1
        fi
    fi
else
    print_error "❌ Python 3 is not installed or not in your PATH"
    print_warning "Would you like to install Python 3.12? (y/n)"
    read -r choice
    if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
        if [[ "$OS" == "macOS" ]]; then
            install_python_macos
        else
            install_python_linux
        fi
    else
        print_error "Please install Python 3.10 or higher manually and try again."
        if [[ "$OS" == "macOS" ]]; then
            cat << EOF
To install Python on macOS:
  1. Install Homebrew (if not already installed):
     /bin/bash -c "\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  2. Install Python 3.12:
     brew install python@3.12
EOF
        else
            cat << EOF
To install Python on your Linux distribution:
  - Ubuntu/Debian: sudo apt-get update && sudo apt-get install python3.12 python3-pip
  - Fedora: sudo dnf install python3.12 python3-pip
  - Arch Linux: sudo pacman -S python python-pip
EOF
        fi
        exit 1
    fi
fi

# Download and run the Python installer script with version argument
print_step "Downloading the Bugster CLI installer..."
if [[ "$VERSION" == "latest" ]]; then
    curl -sSL https://raw.githubusercontent.com/Bugsterapp/bugster-cli/main/scripts/install.py | python3
else
    curl -sSL https://raw.githubusercontent.com/Bugsterapp/bugster-cli/main/scripts/install.py | python3 - -v "$VERSION"
fi

exit_code=$?
if [[ $exit_code -eq 0 ]]; then
    # Show shell reload instructions
    shell=${SHELL##*/}
    config_file="$HOME/.${shell}rc"
    print_warning "Please restart your terminal or run:"
    echo -e "${BLUE}source $config_file${NC}"
    echo -e "\nTo use Bugster CLI, run: ${GREEN}bugster --help${NC}"
fi

exit $exit_code 