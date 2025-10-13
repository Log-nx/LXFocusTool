#!/bin/bash
# Focus Tool Launcher for macOS
# This script uses the correct Python with working Tkinter

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Try to find Python 3.11 from Homebrew
PYTHON_EXEC=""

if [ -f "/opt/homebrew/bin/python3.11" ]; then
    PYTHON_EXEC="/opt/homebrew/bin/python3.11"
elif [ -f "/usr/local/bin/python3.11" ]; then
    PYTHON_EXEC="/usr/local/bin/python3.11"
elif command -v python3.11 &> /dev/null; then
    PYTHON_EXEC="python3.11"
else
    echo "❌ Error: Python 3.11 with Tkinter not found."
    echo ""
    echo "Please run the installer first:"
    echo "  ./install_python_macos.sh"
    echo ""
    echo "Or install manually:"
    echo "  brew install python-tk@3.11"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Using Python: $PYTHON_EXEC"
echo "Starting Focus Tool..."

# Run in background with output
$PYTHON_EXEC focus_tool.py &

echo "✅ Focus Tool launched!"

