# How to Run the Flask App

## Quick Start (Recommended - Solves the Reload Loop Issue)

Run this command from your terminal in the project directory:

### Windows (PowerShell or CMD):
```powershell
.venv\Scripts\python app.py
```

Or if using the Python launcher:
```powershell
python app.py
```

### Windows (Git Bash with spaces in path):
```bash
".venv/Scripts/python.exe" app.py
```

## Why the Infinite Reload?

Flask's `watchdog` reloader is detecting changes in your virtual environment files (in `.venv\Lib\site-packages\~ip\`) because:
1. Your project path had spaces: `...CSS 382\littleAiApplication` (now fixed to `CSS_382`)
2. Watchdog is overly sensitive to changes in the venv folder on Windows
3. This causes infinite reload cycles (harmless but annoying)

## Solutions

### Option 1: Disable Auto-Reload (Simplest)
The app now has `use_reloader=True` which is fine. Just run normally - Flask will still detect your own file changes for reloading.

### Option 2: Remove Spaces from Path (Best Long-term)
Move your project to a path without spaces:
```
C:\Users\bleux\Projects\littleAiApplication
```

The folder has been renamed to:
```
C:\Users\bleux\OneDrive\Documents\UWB\Spring 2025-2026\CSS_382\littleAiApplication
```

### Option 3: Use Production Server (For Testing)
```bash
pip install gunicorn
gunicorn -w 1 -b 127.0.0.1:5000 app:app
```

## Testing After Running

1. Open your browser to: `http://localhost:5000`
2. You should see the Guild Request Board homepage
3. Try the demo features (register user, create guild, etc.)

## If pip Install Still Fails

The error from before was due to unquoted paths. Use this instead:

```bash
# PowerShell or CMD
.venv\Scripts\python -m pip install -r requirements.txt

# Git Bash  
".venv/Scripts/python.exe" -m pip install -r requirements.txt
```

## Verify Installation

```bash
python -m flask --version
```

Should output something like: `Flask 2.3.0`
