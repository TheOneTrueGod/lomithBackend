"""
Vercel serverless function entry point for Django application.

Vercel's @vercel/python runtime expects a WSGI-compatible 'app' variable
at module level. It handles request/response conversion automatically.
"""
# #region agent log - debug instrumentation
import sys
print("[DEBUG-HYP-A] index.py module loading started", file=sys.stderr)
# #endregion

import os
from pathlib import Path

# #region agent log - debug instrumentation
print("[DEBUG-HYP-B] Setting up Python path and Django settings", file=sys.stderr)
# #endregion

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# #region agent log - debug instrumentation
print("[DEBUG-HYP-C] About to import Django WSGI application", file=sys.stderr)
# #endregion

try:
    # Import Django WSGI application
    # Vercel expects 'app' variable at module level
    from backend.wsgi import application as app
    
    # #region agent log - debug instrumentation
    print(f"[DEBUG-HYP-D] Django app loaded successfully, type: {type(app)}", file=sys.stderr)
    # #endregion
    
except Exception as e:
    # #region agent log - debug instrumentation
    import traceback
    print(f"[DEBUG-HYP-E] Error loading Django app: {e}", file=sys.stderr)
    print(f"[DEBUG-HYP-E] Traceback: {traceback.format_exc()}", file=sys.stderr)
    # #endregion
    raise

# #region agent log - debug instrumentation
print("[DEBUG-HYP-A] index.py module loading completed - app exported", file=sys.stderr)
# #endregion

