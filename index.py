# Simple WSGI application for Vercel
import os
import sys
from datetime import datetime

def application(environ, start_response):
    """Ultra-simple WSGI app to test Vercel deployment"""
    
    # Basic HTML response
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>iPhone Manager - Vercel Test</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .success {{ color: #28a745; }}
            .info {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .error {{ color: #dc3545; }}
            h1 {{ color: #333; }}
            pre {{ background: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 iPhone Manager - Vercel Deployment Test</h1>
            
            <div class="success">
                <h2>✅ Basic Python/WSGI is Working!</h2>
                <p>This confirms that Vercel can run Python applications.</p>
            </div>
            
            <div class="info">
                <h3>📊 Environment Information:</h3>
                <pre>
Python Version: {sys.version}
Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Environment: {'Vercel' if os.environ.get('VERCEL') else 'Local'}
Request Method: {environ.get('REQUEST_METHOD', 'Unknown')}
Path Info: {environ.get('PATH_INFO', '/')}
Query String: {environ.get('QUERY_STRING', 'None')}
                </pre>
            </div>
            
            <div class="info">
                <h3>🔧 Next Steps:</h3>
                <ol>
                    <li>✅ Vercel deployment is working</li>
                    <li>🔄 Now we need to fix Django initialization</li>
                    <li>🗄️ Configure database connection properly</li>
                    <li>🚀 Deploy full Django application</li>
                </ol>
            </div>
            
            <div class="info">
                <h3>🎯 Test Links:</h3>
                <ul>
                    <li><a href="/">Home (this page)</a></li>
                    <li><a href="/test">Test endpoint</a></li>
                    <li><a href="/django">Django app (may not work yet)</a></li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Set response headers
    status = '200 OK'
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(html_content.encode('utf-8'))))
    ]
    
    start_response(status, headers)
    return [html_content.encode('utf-8')]

# For Vercel compatibility
def handler(request):
    """Handler for Vercel serverless function"""
    return application(request.environ, request.start_response)
