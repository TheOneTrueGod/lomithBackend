#!/usr/bin/env python
"""
Start script for Django development server.
Activates the virtual environment and runs the Django server.
"""
import os
import sys
import subprocess
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).resolve().parent
venv_python = project_root / "venv" / "Scripts" / "python.exe"

# Check if virtual environment exists
if not venv_python.exists():
    print("Error: Virtual environment not found!")
    print("Please run 'setup.ps1' first to create the virtual environment.")
    sys.exit(1)

# Change to project root directory
os.chdir(project_root)

# Run the Django development server using venv's Python
print("Starting Django development server...")
print("Server will be available at http://127.0.0.1:8000/")
print("Press Ctrl+C to stop the server\n")

try:
    subprocess.run([str(venv_python), "manage.py", "runserver"], check=True)
except KeyboardInterrupt:
    print("\n\nServer stopped.")
except subprocess.CalledProcessError as e:
    print(f"\nError starting server: {e}")
    sys.exit(1)

