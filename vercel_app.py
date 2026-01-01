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

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Import Django WSGI application
from backend.wsgi import application

# Vercel Python runtime expects a handler function
def handler(request):
    """
    Vercel serverless function handler.
    Converts Vercel's request format to WSGI format and processes through Django.
    
    Note: The 'vercel' module is automatically provided by Vercel's Python runtime.
    """
    from vercel import Response
    
    # Extract request details
    method = request.method
    path = request.path
    query_string = getattr(request, 'query_string', '') or ''
    headers = request.headers
    body = getattr(request, 'body', b'') or b''
    
    # Build WSGI environ dictionary
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body)),
        'SERVER_NAME': headers.get('host', 'localhost').split(':')[0],
        'SERVER_PORT': headers.get('host', 'localhost').split(':')[1] if ':' in headers.get('host', 'localhost') else '80',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': headers.get('x-forwarded-proto', 'https'),
        'wsgi.input': None,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add HTTP headers to environ (WSGI format: HTTP_*)
    for key, value in headers.items():
        key_upper = key.upper().replace('-', '_')
        if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key_upper}'] = value
    
    # Handle request body
    if body:
        import io
        environ['wsgi.input'] = io.BytesIO(body)
    
    # Response data collector
    response_data = {'status': 200, 'headers': {}, 'body': b''}
    
    def start_response(status, response_headers):
        """WSGI start_response callback"""
        response_data['status'] = int(status.split()[0])
        response_data['headers'] = dict(response_headers)
    
    # Call Django WSGI application
    try:
        result = application(environ, start_response)
        response_data['body'] = b''.join(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        response_data['status'] = 500
        response_data['headers'] = {'Content-Type': 'text/plain'}
        response_data['body'] = f'Internal Server Error: {str(e)}'.encode()
    
    return Response(
        response_data['body'],
        status=response_data['status'],
        headers=response_data['headers']
    )

