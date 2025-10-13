# Log's Nifty Focus Tool 💭

> A minimalist focus and productivity application designed for distraction-free work sessions and simple task management.

![Focus Tool](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🌟 What is Focus Tool?

Focus Tool is a lightweight desktop application built to help you maintain focus and manage tasks efficiently. Perfect for Pomodoro technique practitioners, students, developers, and anyone who wants a clean, distraction-free productivity tool.

### ✨ Key Features

- **⏱️ Flexible Focus Timer**
  - Pre-configured presets: 20, 50, and 120 minutes
  - Custom timer duration support
  - Visual countdown display
  - Completion notifications

- **📝 Integrated Task Management**
  - Add and organize tasks quickly
  - Mark tasks as complete
  - Delete individual or all tasks
  - Persistent task storage (survives app restarts)

- **🚀 Quick Application Launcher**
  - Launch frequently used apps instantly
  - Browse and select applications
  - Remember your preferred apps

- **💾 Smart Persistence**
  - Auto-saves tasks
  - Remembers window size and position
  - No manual saving required

- **🎨 Clean, Modern Interface**
  - Minimalist dark theme
  - Platform-optimized design
  - Fully resizable window
  - Intuitive controls

---

## 🚀 Getting Started

### Choose Your Platform

Focus Tool is available in **two optimized versions**. Please select the version for your operating system:

<table>
<tr>
<td width="50%" align="center">

### 🪟 Windows Version

**Branch:** `main`

**Requirements:**
- Windows 10/11
- Python 3.7+

**Installation:**
```bash
git clone https://github.com/Log-nx/LXFocusTool.git
cd LXFocusTool
git checkout Windows-&-Linux
python run_focus_tool.py
```

**Quick Start:**
- Double-click `run_focus_tool.bat`
- Or run: `python focus_tool.py`

**Features:**
- Windows-optimized UI
- Taskbar integration
- Segoe UI font
- Notepad integration

</td>
<td width="50%" align="center">

### 🍎 macOS Version

**Branch:** `MacOS`

**Requirements:**
- macOS 10.14+
- Python 3.11+ (Homebrew)

**Installation:**
```bash
git clone https://github.com/Log-nx/LXFocusTool.git
cd LXFocusTool
git checkout MacOS
./install_python_macos.sh
python3 run_focus_tool.py
```

**Quick Start:**
- Run: `./run_focus_tool.sh`
- Or: `python3 run_focus_tool.py`

**Features:**
- macOS-native UI
- Custom button widgets
- Helvetica Neue font
- TextEdit integration

</td>
</tr>
</table>

---

## 📦 Stable Releases

For production use, we recommend downloading the latest stable release rather than cloning the repository directly.

### Latest Stable Versions

| Platform | Version | Release Date | Download |
|----------|---------|--------------|----------|
| Windows | v1.0.3 | Check Releases → | [Latest Release](../../releases) |
| macOS | v1.0.3 | Check Releases → | [Latest Release](../../releases) |

**To download a stable release:**

1. Visit the [Releases Page](../../releases)
2. Find the latest release for your platform
3. Download the source code or executable
4. Follow the included installation instructions
---

## 🔧 Platform Differences

While both versions share the same core functionality, they are optimized for their respective platforms:

| Feature | Windows (main) | macOS (MacOS) |
|---------|----------------|---------------|
| **Python Version** | 3.7+ | 3.11+ |
| **Tkinter Version** | 8.5+ | 8.6+ |
| **UI Framework** | Standard Tkinter | Custom widgets |
| **Default Font** | Segoe UI | Helvetica Neue |
| **Background** | Hexagon pattern | Simplified UI |
| **App Launcher** | Windows apps | .app bundles |
| **Installation** | Standard Python | Homebrew Python |

---

## 🛠️ Development

### Contributing

We welcome contributions! Here's how to get started:

1. **Choose your platform branch:**
   - Windows development: `main`
   - macOS development: `MacOS`

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes and test thoroughly**

4. **Submit a pull request to the appropriate base branch**

### Development Guidelines

- Follow the existing code style
- Test on the target platform before submitting
- Update documentation for new features
- Keep Windows and macOS features separate
- Use proper commit messages

---

## 🐛 Troubleshooting

### Common Issues

**Q: Which version should I use?**
- Use the `main` branch for Windows
- Use the `MacOS` branch for macOS

**Q: Why are there separate branches?**
- Each platform has unique UI requirements and optimizations
- Separate branches allow for platform-specific enhancements without breaking the other version

**Q: Can I use the Windows version on macOS or vice versa?**
- Not recommended. Each version is optimized for its platform
- The macOS version uses custom widgets that won't work correctly on Windows
- The Windows version uses system calls that won't work on macOS

**Q: Where can I report bugs?**
- Open an issue on GitHub and specify your platform and version
- Include logs from `focus_tool.log` if available
- Mention which branch you're using

**Q: How do I update to the latest version?**
- Pull the latest changes from your platform's branch:
  ```bash
  git pull origin main      # For Windows
  git pull origin MacOS     # For macOS
  ```
- Or download the latest release from the Releases page

---

## 📋 Requirements

### Windows (`main` branch)
- Windows 10 or later
- Python 3.7 or higher
- No external dependencies (uses standard library only)

### macOS (`MacOS` branch)
- macOS 10.14 (Mojave) or later
- Python 3.11+ with Tkinter 8.6+ (via Homebrew)
- No external dependencies (uses standard library only)

### Common Requirements
- ~30MB free disk space
- 200MB RAM
- Display resolution: 800x600 minimum

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Quick Links

- [📥 Download Latest Release](../../releases)
- [🐛 Report a Bug](../../issues/new?template=bug_report.md)
- [💡 Request a Feature](../../issues/new?template=feature_request.md)
- [📖 Windows Documentation](../../tree/windows-&-linux)
- [📖 macOS Documentation](../../tree/MacOS)

---

## ⭐ Support

If you find Focus Tool helpful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🤝 Contributing code
- 📢 Sharing with others

---

<div align="center">

**Built with ❤️ using Tears 😭, Python and Tkinter**

[⬆ Back to Top](#logiiKxs-nifty-focus-tool-)

</div>

