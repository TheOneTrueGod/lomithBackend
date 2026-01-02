"""
Vercel serverless function entry point for Django application.

Vercel's @vercel/python runtime expects a WSGI-compatible 'app' variable
at module level. It handles request/response conversion automatically.
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Import Django WSGI application
# Vercel expects 'app' variable at module level
from backend.wsgi import application as app

