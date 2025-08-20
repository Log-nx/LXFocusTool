#!/usr/bin/env python3
"""
Debug launcher for Focus Tool
 - Keeps console visible
 - Enables verbose logging
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

        print("Starting Focus Tool (DEBUG)...")
        env = os.environ.copy()
        env['FOCUS_DEBUG'] = '1'
        env['FOCUS_LOG_LEVEL'] = 'DEBUG'
        subprocess.run([sys.executable, focus_tool_path], env=env)

    except Exception as e:
        print(f"Error launching Focus Tool (DEBUG): {e}")
        input("Press Enter to continue...")
        sys.exit(1)


if __name__ == "__main__":
    main()


