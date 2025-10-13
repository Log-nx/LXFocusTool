#!/usr/bin/env python3
"""
Debug launcher for Focus Tool - macOS
 - Keeps console visible
 - Enables verbose logging
 - Uses correct Python with Tkinter 8.6+
"""

import subprocess
import sys
import os


def find_working_python():
    """Find Python 3.11+ with Tkinter 8.6+"""
    candidates = [
        "/opt/homebrew/bin/python3.11",
        "/opt/homebrew/bin/python3.12",
        "/usr/local/bin/python3.11",
        "/usr/local/bin/python3.12",
    ]
    
    for python_path in candidates:
        if os.path.exists(python_path):
            return python_path
    
    return None


def main():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        focus_tool_path = os.path.join(script_dir, 'focus_tool.py')

        if not os.path.exists(focus_tool_path):
            print(f"❌ Error: focus_tool.py not found at {focus_tool_path}")
            sys.exit(1)

        python_exec = find_working_python()
        if not python_exec:
            print("❌ Error: Python 3.11+ with Tkinter 8.6+ not found.")
            print("\nPlease install via Homebrew:")
            print("  brew install python-tk@3.11")
            print("\nOr run the installer:")
            print("  ./install_python_macos.sh")
            sys.exit(1)

        print(f"🔍 Using Python: {python_exec}")
        print("🐛 Starting Focus Tool (DEBUG MODE)...")
        print("📋 Logging enabled at DEBUG level\n")
        
        env = os.environ.copy()
        env['FOCUS_DEBUG'] = '1'
        env['FOCUS_LOG_LEVEL'] = 'DEBUG'
        
        subprocess.run([python_exec, focus_tool_path], env=env)

    except Exception as e:
        print(f"❌ Error launching Focus Tool (DEBUG): {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()


