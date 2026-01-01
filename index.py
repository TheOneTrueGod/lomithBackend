"""
Vercel serverless function entry point for Django application.
This file serves as the handler for all requests to the Django app on Vercel.

Vercel's Python runtime provides a 'vercel' module with Request and Response classes.
This handler adapts Vercel's request format to Django's WSGI interface.
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Don't set Django settings or import Django at module level
# This avoids issues with Vercel's runtime inspection

# Lazy load Django WSGI application to avoid import-time issues
_application = None

def get_application():
    """Lazy load Django WSGI application"""
    global _application
    if _application is None:
        # Set Django settings before importing
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        from backend.wsgi import application as app
        _application = app
    return _application

# Vercel Python runtime handler
# Export handler as a callable that Vercel can invoke
def handler(request):
    """
    Vercel serverless function handler.
    Converts Vercel's request format to WSGI format and processes through Django.
    
    Note: The 'vercel' module is automatically provided by Vercel's Python runtime.
    """
    from vercel import Response
    import io
    
    # Extract request details
    method = request.method
    path = request.path
    query_string = getattr(request, 'query_string', '') or ''
    headers = dict(request.headers) if hasattr(request, 'headers') else {}
    
    # Handle request body - Vercel may provide it as bytes, string, or None
    body = b''
    if hasattr(request, 'body'):
        body_raw = request.body
        if isinstance(body_raw, str):
            body = body_raw.encode('utf-8')
        elif isinstance(body_raw, bytes):
            body = body_raw
        elif body_raw is not None:
            body = str(body_raw).encode('utf-8')
    
    # Get host header safely
    host = headers.get('host', 'localhost')
    server_name = host.split(':')[0] if ':' in host else host
    server_port = host.split(':')[1] if ':' in host else '80'
    
    # Build WSGI environ dictionary
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body)),
        'SERVER_NAME': server_name,
        'SERVER_PORT': server_port,
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': headers.get('x-forwarded-proto', 'https'),
        'wsgi.input': io.BytesIO(body),  # Always set, even if empty
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add HTTP headers to environ (WSGI format: HTTP_*)
    for key, value in headers.items():
        key_upper = key.upper().replace('-', '_')
        if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH', 'HOST'):
            environ[f'HTTP_{key_upper}'] = value
    
    # Response data collector
    response_data = {'status': 200, 'headers': {}, 'body': b''}
    
    def start_response(status, response_headers):
        """WSGI start_response callback"""
        response_data['status'] = int(status.split()[0])
        response_data['headers'] = dict(response_headers)
    
    # Call Django WSGI application (lazy loaded)
    try:
        app = get_application()
        result = app(environ, start_response)
        response_data['body'] = b''.join(result)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        # Log error to stderr (visible in Vercel logs)
        print(f"ERROR in Django handler: {error_trace}", file=sys.stderr)
        
        # Return error response
        response_data['status'] = 500
        response_data['headers'] = {'Content-Type': 'application/json'}
        error_message = {
            'error': 'Internal Server Error',
            'message': str(e),
            'type': type(e).__name__
        }
        # Only include traceback in debug mode
        if os.environ.get('DEBUG', 'False') == 'True':
            error_message['traceback'] = error_trace
        import json
        response_data['body'] = json.dumps(error_message).encode('utf-8')
    
    return Response(
        response_data['body'],
        status=response_data['status'],
        headers=response_data['headers']
    )

