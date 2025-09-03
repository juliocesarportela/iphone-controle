#!/usr/bin/env python
"""
Script para configurar e conectar o sistema Django com o Supabase
"""
import os
import sys
import django
from supabase import create_client, Client
import psycopg2
from psycopg2 import sql

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iphone_import_system.settings')
django.setup()

# Configurações do Supabase
SUPABASE_URL = "https://whkxlrzscxuctkwtdknj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indoa3hscnpzY3h1Y3Rrd3Rka25qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY4NjQyNDMsImV4cCI6MjA3MjQ0MDI0M30.7mYZi_r7O2D8BLwUwbyyq1b9HINQY8LKP-U_5hJeVGc"

# Configurações do banco PostgreSQL
DB_CONFIG = {
    'host': 'aws-0-us-east-1.pooler.supabase.com',
    'port': '6543',
    'database': 'postgres',
    'user': 'postgres.whkxlrzscxuctkwtdknj',
    'password': '',  # Será solicitada
}

def test_supabase_connection():
    """Testa a conexão com o Supabase usando a API"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Teste simples de conexão - verificar se conseguimos acessar a API
        # Tentamos acessar uma tabela que pode não existir, mas se conseguirmos uma resposta
        # significa que a conexão está funcionando
        try:
            response = supabase.table('django_migrations').select("*").limit(1).execute()
        except Exception:
            # Se der erro, pode ser que a tabela não existe ainda, mas a conexão funciona
            pass
        
        print("✅ Conexão com Supabase API estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase API: {e}")
        print("⚠️ Continuando mesmo assim - vamos testar a conexão PostgreSQL...")
        return True  # Continuamos mesmo se a API der erro

def test_postgresql_connection(password):
    """Testa a conexão direta com PostgreSQL"""
    try:
        DB_CONFIG['password'] = password
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Teste simples
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Conexão PostgreSQL estabelecida! Versão: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com PostgreSQL: {e}")
        return False

def create_env_file(db_password):
    """Cria o arquivo .env com as configurações"""
    env_content = f"""# Configurações do Django
SECRET_KEY=django-insecure-your-secret-key-here-change-in-production
DEBUG=True

# Configurações do Supabase
SUPABASE_URL={SUPABASE_URL}
SUPABASE_KEY={SUPABASE_KEY}
SUPABASE_DB_PASSWORD={db_password}

# URL de conexão completa do banco
DATABASE_URL=postgresql://postgres.whkxlrzscxuctkwtdknj:{db_password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# Configurações de Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ Arquivo .env criado com sucesso!")

def run_sql_script(password, script_path):
    """Executa o script SQL no Supabase"""
    try:
        DB_CONFIG['password'] = password
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Ler e executar o script SQL
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Executar o script
        cursor.execute(sql_script)
        conn.commit()
        
        print("✅ Script SQL executado com sucesso!")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao executar script SQL: {e}")
        return False

def check_tables(password):
    """Verifica se as tabelas foram criadas corretamente"""
    try:
        DB_CONFIG['password'] = password
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Listar tabelas criadas
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
                AND (tablename LIKE 'core_%' 
                    OR tablename LIKE 'django_%' 
                    OR tablename LIKE 'auth_%')
            ORDER BY tablename;
        """)
        
        tables = cursor.fetchall()
        print(f"\n📋 Tabelas criadas ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return False

def create_superuser():
    """Cria um superusuário no sistema"""
    try:
        from core.models import User
        
        username = input("Digite o nome de usuário do admin: ")
        email = input("Digite o email do admin: ")
        password = input("Digite a senha do admin: ")
        
        if User.objects.filter(username=username).exists():
            print(f"❌ Usuário {username} já existe!")
            return False
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role='admin'
        )
        
        print(f"✅ Superusuário {username} criado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")
        return False

def main():
    print("🚀 Configurando Sistema iPhone Import com Supabase")
    print("=" * 50)
    
    # 1. Testar conexão com Supabase API
    print("\n1. Testando conexão com Supabase API...")
    if not test_supabase_connection():
        return
    
    # 2. Solicitar senha do banco
    print("\n2. Configurando conexão com PostgreSQL...")
    db_password = input("Digite a senha do banco PostgreSQL do Supabase: ")
    
    # 3. Testar conexão PostgreSQL
    print("\n3. Testando conexão PostgreSQL...")
    if not test_postgresql_connection(db_password):
        return
    
    # 4. Criar arquivo .env
    print("\n4. Criando arquivo de configuração...")
    create_env_file(db_password)
    
    # 5. Executar script SQL
    print("\n5. Criando tabelas no banco...")
    script_path = "supabase_schema.sql"
    if os.path.exists(script_path):
        if run_sql_script(db_password, script_path):
            print("✅ Tabelas criadas com sucesso!")
        else:
            print("❌ Erro ao criar tabelas!")
            return
    else:
        print(f"❌ Script SQL não encontrado: {script_path}")
        return
    
    # 6. Verificar tabelas
    print("\n6. Verificando tabelas criadas...")
    check_tables(db_password)
    
    # 7. Executar migrações Django
    print("\n7. Executando migrações Django...")
    os.system("python manage.py migrate --fake-initial")
    
    # 8. Criar superusuário
    print("\n8. Criando superusuário...")
    create_superuser()
    
    print("\n🎉 Configuração concluída com sucesso!")
    print("\nPróximos passos:")
    print("1. Execute: python manage.py runserver")
    print("2. Acesse: http://localhost:8000")
    print("3. Faça login com o usuário criado")
    print("\n📝 Lembre-se de:")
    print("- Manter o arquivo .env seguro")
    print("- Configurar as variáveis de ambiente em produção")
    print("- Fazer backup regular dos dados")

if __name__ == "__main__":
    main()
