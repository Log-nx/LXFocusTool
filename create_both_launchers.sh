#!/bin/bash
# create_both_launchers.sh
# Creates both normal and debug launchers for Focus Tool

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Creating both Focus Tool launchers..."

# Create normal launcher
NORMAL_FILE="$SCRIPT_DIR/Launch Focus Tool.command"
cat > "$NORMAL_FILE" << 'EOF'
#!/bin/bash
# Focus Tool Launcher - Normal Mode
# Double-click to run in normal mode

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting Focus Tool (Normal Mode)..."
echo ""

python3 run_focus_tool.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Focus Tool encountered an error."
    echo "Press Enter to close..."
    read
fi
EOF

# Create debug launcher
DEBUG_FILE="$SCRIPT_DIR/Launch Focus Tool (Debug).command"
cat > "$DEBUG_FILE" << 'EOF'
#!/bin/bash
# Focus Tool Launcher - Debug Mode
# Double-click to run in debug mode with verbose logging

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🐛 Starting Focus Tool (Debug Mode)..."
echo "📋 Debug logging enabled"
echo ""

python3 run_focus_tool_debug.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Focus Tool (Debug) encountered an error."
    echo "Press Enter to close..."
    read
fi
EOF

# Make both executable
chmod +x "$NORMAL_FILE"
chmod +x "$DEBUG_FILE"

echo "✅ Created launchers:"
echo "   📱 Normal: Launch Focus Tool.command"
echo "   🐛 Debug:  Launch Focus Tool (Debug).command"
echo ""
echo "You can now double-click either file to launch Focus Tool!"
echo ""
echo "Normal mode: Clean interface, minimal logging"
echo "Debug mode:  Verbose logging, console output visible"
