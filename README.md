# 🎯 Log's Little Focus Tool

> A minimalist focus and productivity application.

![Focus Tool](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **⏱️ Focus Timer** - Perfect for Pomodoro sessions
- **📝 Task Management** - Add, complete, delete, and clear tasks
- **🚀 Quick App Launcher** - Launch applications instantly
- **🎨 Glass Style UI** - Borderless design with custom controls
- **🔧 Fully Resizable** - Custom resize handles for perfect positioning
- **💾 Persistent Storage** - Tasks saved automatically

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Windows OS

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/focus-tool.git
cd focus-tool

# Run directly
python focus_tool.py
```

### Alternative Launch Methods
- **Windows Batch**: Double-click `run_focus_tool.bat`
- **PowerShell**: Run `check_python.ps1` for environment check
- **Cross-platform**: Use `run_focus_tool.py`

## 🎮 Usage

### Timer Controls
- **Start** - Begin 50-minute focus session
- **Stop** - Pause the timer
- **Reset** - Return to 50:00

### Task Management
- **Add Task** - Type and press Enter or click Add
- **Complete** - Mark tasks as done (green checkmark)
- **Delete** - Remove individual tasks
- **Clear All** - Remove all tasks with confirmation

## 📁 Project Structure

```
focus-tool/
├── focus_tool.py          # Main application
├── run_focus_tool.bat     # Windows batch launcher
├── run_focus_tool.py      # Cross-platform launcher
├── check_python.ps1       # PowerShell environment check
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── tasks.json             # Task storage (auto-created)
```

## 🔧 Customization

The application automatically saves your preferences and tasks. Customize colors, fonts, and behavior by modifying the configuration in `focus_tool.py`.

## 🐛 Troubleshooting

- **Python not found**: Run `check_python.ps1` for installation guidance
- **Application crashes**: Check the terminal for error messages
- **Performance issues**: The app automatically optimizes animation performance

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using Python and Tkinter**
