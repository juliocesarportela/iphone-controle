from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Set response headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Create response data
        response_data = {
            'status': 'success',
            'message': 'iPhone Manager - Vercel API Test',
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'environment': 'Vercel' if os.environ.get('VERCEL') else 'Local',
            'path': self.path,
            'method': self.command
        }
        
        # Send JSON response
        self.wfile.write(json.dumps(response_data, indent=2).encode('utf-8'))
        return
