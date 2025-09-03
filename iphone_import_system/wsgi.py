"""
WSGI config for iphone_import_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iphone_import_system.settings')

# Add project directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # Fallback WSGI application for debugging
    def application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        error_msg = f"Django WSGI Error: {str(e)}\n\nEnviron: {environ.get('REQUEST_METHOD', 'Unknown')} {environ.get('PATH_INFO', '/')}"
        return [error_msg.encode('utf-8')]
