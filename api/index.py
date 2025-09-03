# Simple test endpoint for Vercel
from django.http import JsonResponse
import os
import sys

def handler(request):
    """Simple test handler to check if basic Python works on Vercel"""
    try:
        # Basic environment info
        env_info = {
            'python_version': sys.version,
            'django_settings': os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set'),
            'vercel_env': os.environ.get('VERCEL', 'Not on Vercel'),
            'path_info': request.META.get('PATH_INFO', '/'),
            'method': request.method,
            'status': 'Django is working!'
        }
        
        return JsonResponse(env_info, json_dumps_params={'indent': 2})
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'type': type(e).__name__,
            'status': 'Django has issues'
        }, status=500)
