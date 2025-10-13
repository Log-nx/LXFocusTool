#!/usr/bin/env python3
"""
Launcher script for Focus Tool - macOS Edition
Automatically finds and uses Python with working Tkinter
"""

import subprocess
import sys
import os

def find_working_python():
    """Find Python 3.11+ with Tkinter support"""
    candidates = [
        '/opt/homebrew/bin/python3.11',  # Homebrew on Apple Silicon
        '/usr/local/bin/python3.11',      # Homebrew on Intel
        '/opt/homebrew/bin/python3.12',
        '/usr/local/bin/python3.12',
    ]
    
    # Check each candidate
    for python_path in candidates:
        if os.path.exists(python_path):
            try:
                # Test if Tkinter works
                result = subprocess.run(
                    [python_path, '-c', 'import tkinter; print(tkinter.TkVersion)'],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    tk_version = float(result.stdout.decode().strip())
                    if tk_version >= 8.6:
                        return python_path
            except:
                continue
    
    return None

def main():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        focus_tool_path = os.path.join(script_dir, 'focus_tool.py')
        
        if not os.path.exists(focus_tool_path):
            print(f"❌ Error: focus_tool.py not found at {focus_tool_path}")
            sys.exit(1)
        
        # Find working Python
        python_exec = find_working_python()
        
        if python_exec is None:
            print("❌ Error: Python 3.11+ with Tkinter 8.6+ not found")
            print("")
            print("Please install it:")
            print("  ./install_python_macos.sh")
            print("")
            print("Or manually:")
            print("  brew install python-tk@3.11")
            print("")
            input("Press Enter to exit...")
            sys.exit(1)
        
        print(f"✅ Using Python: {python_exec}")
        print("Starting Focus Tool...")
        
        # Ensure debug is off for this launcher unless user explicitly sets it
        env = os.environ.copy()
        env.setdefault('FOCUS_LOG_LEVEL', 'INFO')
        env.setdefault('FOCUS_DEBUG', '0')
        
        # Launch the application
        subprocess.Popen([python_exec, focus_tool_path], env=env, shell=False)
        
        print("✅ Focus Tool launched successfully!")
        
    except Exception as e:
        print(f"❌ Error launching Focus Tool: {e}")
        input("Press Enter to continue...")
        sys.exit(1)

if __name__ == "__main__":
    main()
