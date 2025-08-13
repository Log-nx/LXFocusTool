# PowerShell script to check Python installation and launch Focus Tool

Write-Host "Focus Tool - Python Environment Check" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

# Check for Python in PATH
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
$python3Path = Get-Command python3 -ErrorAction SilentlyContinue

if ($pythonPath) {
    Write-Host "✓ Python found in PATH: $($pythonPath.Source)" -ForegroundColor Green
    $pythonVersion = & python --version 2>&1
    Write-Host "  Version: $pythonVersion" -ForegroundColor Green
    
    # Check tkinter availability
    try {
        $tkinterCheck = & python -c "import tkinter; print('tkinter available')" 2>&1
        if ($tkinterCheck -like "*tkinter available*") {
            Write-Host "✓ tkinter is available" -ForegroundColor Green
            Write-Host ""
            Write-Host "Launching Focus Tool..." -ForegroundColor Yellow
            & python focus_tool.py
        } else {
            Write-Host "✗ tkinter not available" -ForegroundColor Red
            Write-Host "Please reinstall Python with tkinter support" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ Error checking tkinter: $_" -ForegroundColor Red
    }
}
elseif ($python3Path) {
    Write-Host "✓ Python3 found in PATH: $($python3Path.Source)" -ForegroundColor Green
    $pythonVersion = & python3 --version 2>&1
    Write-Host "  Version: $pythonVersion" -ForegroundColor Green
    
    try {
        $tkinterCheck = & python3 -c "import tkinter; print('tkinter available')" 2>&1
        if ($tkinterCheck -like "*tkinter available*") {
            Write-Host "✓ tkinter is available" -ForegroundColor Green
            Write-Host ""
            Write-Host "Launching Focus Tool..." -ForegroundColor Yellow
            & python3 focus_tool.py
        } else {
            Write-Host "✗ tkinter not available" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ Error checking tkinter: $_" -ForegroundColor Red
    }
}
else {
    Write-Host "✗ Python not found in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Python Installation Required:" -ForegroundColor Yellow
    Write-Host "1. Visit https://python.org/downloads/" -ForegroundColor Cyan
    Write-Host "2. Download Python 3.x for Windows" -ForegroundColor Cyan
    Write-Host "3. Install with 'Add Python to PATH' checked" -ForegroundColor Cyan
    Write-Host "4. Restart PowerShell and run this script again" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Alternative: Use Microsoft Store to install Python" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
