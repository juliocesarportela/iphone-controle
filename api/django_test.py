from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Test Django import
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iphone_import_system.settings')
            
            # Add project to path
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if project_dir not in sys.path:
                sys.path.insert(0, project_dir)
            
            # Try to import Django
            import django
            from django.conf import settings
            
            # Configure Django
            django.setup()
            
            # Test database connection
            from django.db import connection
            db_status = "Connected" if connection.ensure_connection() is None else "Failed"
            
            response_data = {
                'status': 'success',
                'message': 'Django is working on Vercel!',
                'django_version': django.get_version(),
                'database_status': db_status,
                'database_engine': settings.DATABASES['default']['ENGINE'],
                'timestamp': datetime.now().isoformat(),
                'python_version': sys.version,
                'environment': 'Vercel' if os.environ.get('VERCEL') else 'Local'
            }
            
        except Exception as e:
            response_data = {
                'status': 'error',
                'message': f'Django failed: {str(e)}',
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat(),
                'python_version': sys.version,
                'environment': 'Vercel' if os.environ.get('VERCEL') else 'Local'
            }
        
        # Set response headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Send JSON response
        self.wfile.write(json.dumps(response_data, indent=2).encode('utf-8'))
        return
