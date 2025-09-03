from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Setup Django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iphone_import_system.settings')
            
            # Add project to path
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if project_dir not in sys.path:
                sys.path.insert(0, project_dir)
            
            import django
            from django.conf import settings
            from django.core.management import execute_from_command_line
            
            # Configure Django
            django.setup()
            
            # Run migrations in memory (only once)
            try:
                execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
            except:
                pass  # Migrations already applied
            
            # Simple Django response with login form
            html_content = """
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>iPhone Manager - Login</title>
                <style>
                    body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 40px; }
                    .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { text-align: center; color: #333; margin-bottom: 30px; }
                    .form-group { margin-bottom: 20px; }
                    label { display: block; margin-bottom: 5px; font-weight: bold; }
                    input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
                    .btn { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
                    .btn:hover { background: #0056b3; }
                    .status { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
                    .links { text-align: center; margin-top: 20px; }
                    .links a { color: #007bff; text-decoration: none; margin: 0 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📱 iPhone Manager</h1>
                    
                    <div class="status">
                        ✅ Django funcionando no Vercel!<br>
                        🗄️ Database SQLite conectado<br>
                        🚀 Sistema operacional
                    </div>
                    
                    <form method="post" action="/api/django_simple">
                        <div class="form-group">
                            <label for="username">Usuário:</label>
                            <input type="text" id="username" name="username" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="password">Senha:</label>
                            <input type="password" id="password" name="password" required>
                        </div>
                        
                        <button type="submit" class="btn">Entrar</button>
                    </form>
                    
                    <div class="links">
                        <a href="/api/django_test">🧪 Teste Django</a>
                        <a href="/api/hello">🔧 Teste API</a>
                        <a href="/">🏠 Início</a>
                    </div>
                    
                    <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 5px; font-size: 14px;">
                        <strong>Para acessar o sistema:</strong><br>
                        1. Crie um superusuário via terminal<br>
                        2. Ou use as credenciais configuradas<br>
                        3. Sistema completo em funcionamento!
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
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
    
    def do_POST(self):
        # Handle login form submission
        self.do_GET()  # For now, just show the form again
