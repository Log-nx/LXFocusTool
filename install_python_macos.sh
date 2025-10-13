#!/bin/bash
# Quick installer for Python with working Tkinter on macOS

echo "=================================================="
echo "Focus Tool - macOS Python Installer"
echo "=================================================="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found."
    echo ""
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ $(uname -m) == 'arm64' ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi

echo "✅ Homebrew is installed"
echo ""

# Install Python with Tk
echo "Installing Python 3.11 with Tkinter support..."
brew install python-tk@3.11 2>&1

# Link python3.11 if needed
brew link python@3.11 2>/dev/null

echo ""
echo "✅ Installation complete!"
echo ""

# Test installation
echo "Testing Tkinter..."
/opt/homebrew/bin/python3.11 -c "import tkinter; print('✅ Tkinter version:', tkinter.TkVersion)" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "SUCCESS! Python is ready to use."
    echo "=================================================="
    echo ""
    echo "To run Focus Tool:"
    echo "  /opt/homebrew/bin/python3.11 focus_tool.py"
    echo ""
    echo "Or use the launcher script:"
    echo "  ./run_focus_tool.sh"
    echo ""
else
    echo ""
    echo "❌ Tkinter test failed. Installing python-tk package..."
    brew install python-tk@3.11 --force
    echo ""
    echo "Try running Focus Tool:"
    echo "  /opt/homebrew/bin/python3.11 focus_tool.py"
    echo ""
fi

