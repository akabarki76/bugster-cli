#!/bin/bash
# Bugster CLI installer wrapper for Unix systems (macOS/Linux)

echo "============================================================"
echo "Bugster CLI Installer"
echo "============================================================"

install_python_macos() {
    echo "Attempting to install Python 3.12.7 automatically..."
    
    # Check if Homebrew is installed
    if command -v brew &>/dev/null; then
        echo "Homebrew found, using it to install Python 3.12.7..."
        brew install python@3.12
    else
        echo "Installing Homebrew first (may prompt for password)..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH temporarily
        if [[ -f /opt/homebrew/bin/brew ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f /usr/local/bin/brew ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        else
            echo "Unable to find Homebrew after installation"
            return 1
        fi
        
        echo "Installing Python 3.12.7 via Homebrew..."
        brew install python@3.12
    fi
    
    # Verify Python was installed
    if command -v python3 &>/dev/null; then
        echo "✅ Python 3 installed successfully!"
        return 0
    else
        echo "❌ Python installation failed"
        return 1
    fi
}

install_python_linux() {
    echo "Attempting to install Python 3.12 automatically (may prompt for password)..."
    
    # Detect package manager and install Python
    if command -v apt-get &>/dev/null; then
        echo "Using apt-get to install Python 3.12..."
        # Add deadsnakes PPA for newer Python versions
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt-get update && sudo apt-get install -y python3.12 python3.12-venv python3.12-distutils
        # Create symlinks if they don't exist
        sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
        sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1
    elif command -v dnf &>/dev/null; then
        echo "Using dnf to install Python 3.12..."
        sudo dnf install -y python3.12
    elif command -v yum &>/dev/null; then
        echo "Using yum to install Python 3.12..."
        # Enable EPEL repository for CentOS/RHEL
        sudo yum install -y epel-release
        sudo yum install -y python3.12
    elif command -v pacman &>/dev/null; then
        echo "Using pacman to install Python 3.12..."
        sudo pacman -S --noconfirm python
    else
        echo "❌ Unable to detect package manager. Please install Python 3.12 manually."
        return 1
    fi
    
    # Verify Python was installed
    if command -v python3.12 &>/dev/null; then
        echo "✅ Python 3.12 installed successfully!"
        return 0
    elif command -v python3 &>/dev/null; then
        # Check if python3 is version 3.12
        if python3 --version | grep -q "Python 3.12"; then
            echo "✅ Python 3.12 installed successfully!"
            return 0
        else
            echo "❌ Python 3.12 installation failed (different version found)"
            return 1
        fi
    else
        echo "❌ Python 3.12 installation failed"
        return 1
    fi
}

# Check if Python 3 is installed
if command -v python3 &>/dev/null; then
    echo "✅ Python 3 is installed, continuing with installation..."
elif command -v python &>/dev/null && python --version 2>&1 | grep -q "Python 3"; then
    echo "✅ Python 3 is installed, continuing with installation..."
else
    echo "❌ Python 3 is not installed or not in your PATH"
    echo ""
    
    # Try to install Python automatically
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Would you like to install Python 3 automatically? (y/n)"
        read -r choice
        if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
            if install_python_macos; then
                echo "Python 3 installed successfully, continuing with Bugster installation..."
            else
                echo "Unable to install Python automatically."
                echo "Please install Python 3 manually and run this script again."
                exit 1
            fi
        else
            echo "Please install Python 3 manually and run this script again."
            echo "To install Python on macOS, you can use Homebrew:"
            echo "  1. Install Homebrew (if not already installed):"
            echo "     /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "  2. Install Python 3:"
            echo "     brew install python@3.12"
            exit 1
        fi
    else
        # Linux
        echo "Would you like to install Python 3 automatically? (y/n)"
        read -r choice
        if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
            if install_python_linux; then
                echo "Python 3 installed successfully, continuing with Bugster installation..."
            else
                echo "Unable to install Python automatically."
                echo "Please install Python 3 manually and run this script again."
                exit 1
            fi
        else
            echo "Please install Python 3 manually and run this script again."
            echo "To install Python on your Linux distribution:"
            echo "  - Ubuntu/Debian: sudo apt-get update && sudo apt-get install python3 python3-pip"
            echo "  - Fedora: sudo dnf install python3 python3-pip"
            echo "  - Arch Linux: sudo pacman -S python python-pip"
            exit 1
        fi
    fi
fi

# Download and run the Python installer script
echo "Downloading the Bugster CLI installer..."
curl -sSL https://raw.githubusercontent.com/Bugsterapp/bugster-cli/main/install.py | python3

exit $? 