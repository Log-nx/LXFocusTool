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
        subprocess.run([sys.executable, focus_tool_path])
        
    except Exception as e:
        print(f"Error launching Focus Tool: {e}")
        input("Press Enter to continue...")
        sys.exit(1)

if __name__ == "__main__":
    main()
