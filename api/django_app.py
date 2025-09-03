from http.server import BaseHTTPRequestHandler
import os
import sys
from urllib.parse import urlparse, parse_qs

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
            except:
                pass  # Migrations already applied
            
            # Create WSGI application
            application = get_wsgi_application()
            
            # Create environ for WSGI
            environ = {
                'REQUEST_METHOD': self.command,
                'PATH_INFO': self.path,
                'QUERY_STRING': urlparse(self.path).query or '',
                'CONTENT_TYPE': self.headers.get('Content-Type', ''),
                'CONTENT_LENGTH': self.headers.get('Content-Length', '0'),
                'SERVER_NAME': 'localhost',
                'SERVER_PORT': '80',
                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'https',
                'wsgi.input': self.rfile,
                'wsgi.errors': sys.stderr,
                'wsgi.multithread': False,
                'wsgi.multiprocess': True,
                'wsgi.run_once': False,
            }
            
            # Add headers to environ
            for header, value in self.headers.items():
                key = 'HTTP_%s' % header.upper().replace('-', '_')
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
            status_code = int(response_status.split(' ')[0])
            self.send_response(status_code)
            
            for header_name, header_value in response_headers:
                self.send_header(header_name, header_value)
            
            self.end_headers()
            self.wfile.write(response_data)
            
        except Exception as e:
            # Error response
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Django Error</title></head>
            <body>
                <h1>Django Application Error</h1>
                <p><strong>Error:</strong> {str(e)}</p>
                <p><strong>Type:</strong> {type(e).__name__}</p>
                <p><a href="/api/django_test">Test Django</a> | <a href="/api/hello">Test API</a></p>
            </body>
            </html>
            """
            
            self.send_response(500)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(error_html.encode('utf-8'))
