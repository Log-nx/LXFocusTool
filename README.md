# LOGiiKx's Nifty Focus Tool 💭

> A minimalist focus and productivity application for macOS - simple, beautiful task management.

![Focus Tool](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **⏱️ Focus Timer** - Perfect for Pomodoro sessions
- **📝 Task Management** - Add, complete, delete, and clear tasks
- **🚀 Quick App Launcher** - Launch applications instantly
- **🔧 Fully Resizable** - Custom resize handles for perfect positioning
- **💾 Persistent Storage** - Tasks saved automatically

## 🚀 Quick Start

### Prerequisites
- **macOS** 10.14 (Mojave) or later
- **Python 3.11+** with **Tkinter 8.6+**

> ⚠️ **Important**: The Apple-bundled Python has an outdated Tkinter that won't display the UI correctly. You **must** use Homebrew Python or python.org Python.

### Installation

#### Step 1: Install Python with Tkinter
```bash
# Option 1: Use our automated installer (recommended)
chmod +x install_python_macos.sh
./install_python_macos.sh

# Option 2: Install manually via Homebrew
brew install python-tk@3.11

# Option 3: Download from python.org
# Visit https://www.python.org/downloads/macos/
```

#### Step 2: Run Focus Tool
```bash
# Option 1: Use the Python launcher (automatically finds correct Python)
python3 run_focus_tool.py

# Option 2: Use the shell script (recommended)
chmod +x run_focus_tool.sh  # First time only
./run_focus_tool.sh

# Option 3: Run directly with Homebrew Python
/opt/homebrew/bin/python3.11 focus_tool.py

# Option 4: Debug mode (verbose logging)
python3 run_focus_tool_debug.py
```

## 📁 Project Structure

```
LXFocusTool/
├── focus_tool.py              # Main application
├── run_focus_tool.py          # Python launcher (finds correct Python)
├── run_focus_tool.sh          # Shell launcher
├── run_focus_tool_debug.py    # Debug launcher (verbose logging)
├── install_python_macos.sh    # Automated Python installer
├── requirements.txt           # Dependencies (none required!)
├── README.md                  # This file
├── LICENSE                    # MIT License
├── tasks.json                 # Task storage (auto-created)
├── window_config.json         # Window size (auto-created)
└── focus_tool.log             # Application logs (auto-created)
```

## 🔧 Customization

The application automatically saves your preferences and tasks:
- **Font**: Helvetica Neue (macOS native)
- **Default App**: TextEdit
- **Color Theme**: Dark theme optimized for macOS
- **Tasks**: Auto-saved to `tasks.json`
- **Window Size**: Auto-saved to `window_config.json`

To customize colors and behavior, edit the configuration in `focus_tool.py`.

<center>
  <img width="240" height="540" alt="image" src="https://github.com/user-attachments/assets/7c489023-795b-4aa8-b5cb-3468ae438786" />
</center>

## 🐛 Troubleshooting

### UI not displaying correctly (blank white page)
- **Cause**: Using Apple's bundled Python with outdated Tkinter 8.5
- **Solution**: Install Python 3.11+ with Tkinter 8.6+ via Homebrew
```bash
brew install python-tk@3.11
```

### Buttons appear gray with unreadable text
- **Cause**: Using native macOS Button widgets
- **Solution**: Already fixed in latest version with custom button widgets

### Python not found
- **Solution**: Run the installer script:
```bash
./install_python_macos.sh
```

### Application won't launch
- Check the logs: `cat focus_tool.log`
- Try debug mode: `python3 run_focus_tool_debug.py`
- Verify Python version: `/opt/homebrew/bin/python3.11 --version`

### App doesn't appear in Dock
- This is normal - the app uses Tkinter which doesn't always create a Dock icon
- You can still access it from the menu bar or by clicking the window

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

**Built with ❤️ using Tears😭, Python and Tkinter**
