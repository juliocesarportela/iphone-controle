from http.server import BaseHTTPRequestHandler
import os
import sys
from urllib.parse import urlparse, parse_qs
import io

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def _handle_request(self):
        try:
            # Setup Django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iphone_import_system.settings')
            
            # Add project to path
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if project_dir not in sys.path:
                sys.path.insert(0, project_dir)
            
            import django
            from django.conf import settings
            from django.core.wsgi import get_wsgi_application
            from django.core.management import execute_from_command_line
            
            # Configure Django
            django.setup()
            
            # Run migrations in memory (only once)
            try:
                execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
                # Create superuser if doesn't exist
                from django.contrib.auth import get_user_model
                User = get_user_model()
                if not User.objects.filter(username='admin').exists():
                    User.objects.create_superuser('admin', 'admin@vercel.app', 'admin123')
            except Exception as e:
                pass  # Migrations already applied or other error
            
            # Create WSGI application
            application = get_wsgi_application()
            
            # Get request body for POST requests
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length) if content_length > 0 else b''
            
            # Create environ for WSGI
            environ = {
                'REQUEST_METHOD': self.command,
                'PATH_INFO': urlparse(self.path).path,
                'QUERY_STRING': urlparse(self.path).query or '',
                'CONTENT_TYPE': self.headers.get('Content-Type', ''),
                'CONTENT_LENGTH': str(content_length),
                'SERVER_NAME': self.headers.get('Host', 'localhost').split(':')[0],
                'SERVER_PORT': '443',
                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'https',
                'wsgi.input': io.BytesIO(request_body),
                'wsgi.errors': sys.stderr,
                'wsgi.multithread': False,
                'wsgi.multiprocess': True,
                'wsgi.run_once': False,
                'HTTP_HOST': self.headers.get('Host', 'localhost'),
                'REMOTE_ADDR': '127.0.0.1',
                'SCRIPT_NAME': '',
            }
            
            # Add all headers to environ
            for header, value in self.headers.items():
                key = 'HTTP_%s' % header.upper().replace('-', '_')
                if key not in environ:
                    environ[key] = value
            
            # Response data
            response_data = []
            response_status = None
            response_headers = []
            
            def start_response(status, headers, exc_info=None):
                nonlocal response_status, response_headers
                response_status = status
                response_headers = headers
                return lambda s: None
            
            # Call Django WSGI application
            response_iter = application(environ, start_response)
            response_data = b''.join(response_iter)
            
            # Send response
            status_code = int(response_status.split(' ')[0]) if response_status else 200
            self.send_response(status_code)
            
            # Send headers
            for header_name, header_value in response_headers:
                self.send_header(header_name, header_value)
            
            self.end_headers()
            
            # Send response body
            if response_data:
                self.wfile.write(response_data)
            
        except Exception as e:
            # Error response with detailed information
            import traceback
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Django Application Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
                    .error {{ color: #dc3545; background: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 12px; }}
                    .links {{ margin-top: 20px; }}
                    .links a {{ color: #007bff; text-decoration: none; margin: 0 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚨 Django Application Error</h1>
                    
                    <div class="error">
                        <h3>Error Details:</h3>
                        <p><strong>Error:</strong> {str(e)}</p>
                        <p><strong>Type:</strong> {type(e).__name__}</p>
                    </div>
                    
                    <h3>Full Traceback:</h3>
                    <pre>{traceback.format_exc()}</pre>
                    
                    <div class="links">
                        <a href="/api/django_test">🧪 Test Django</a>
                        <a href="/api/hello">🔧 Test API</a>
                        <a href="/api/django_simple">📱 Simple Django</a>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.send_response(500)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(error_html.encode('utf-8'))
