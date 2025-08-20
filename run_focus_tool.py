#!/usr/bin/env python3
"""
Launcher script for Focus Tool
"""

import subprocess
import sys
import os

def main():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        focus_tool_path = os.path.join(script_dir, 'focus_tool.py')
        
        if not os.path.exists(focus_tool_path):
            print(f"Error: focus_tool.py not found at {focus_tool_path}")
            sys.exit(1)
        
        print("Starting Focus Tool...")
        # On Windows, prefer pythonw.exe to hide the console window
        python_exec = sys.executable
        if os.name == 'nt':
            base, exe = os.path.split(python_exec)
            if exe.lower().startswith('python') and exe.lower().endswith('.exe'):
                pythonw = os.path.join(base, 'pythonw.exe')
                if os.path.exists(pythonw):
                    python_exec = pythonw
        # Ensure debug is off for this launcher unless user explicitly sets it
        env = os.environ.copy()
        env.setdefault('FOCUS_LOG_LEVEL', 'INFO')
        env.setdefault('FOCUS_DEBUG', '0')
        # Launch without inheriting a console window (pythonw on Windows)
        subprocess.Popen([python_exec, focus_tool_path], env=env, shell=False)
        
    except Exception as e:
        print(f"Error launching Focus Tool: {e}")
        input("Press Enter to continue...")
        sys.exit(1)

if __name__ == "__main__":
    main()
