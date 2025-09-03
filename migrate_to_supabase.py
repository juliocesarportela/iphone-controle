#!/usr/bin/env python
"""
Script para migrar dados do SQLite local para o Supabase PostgreSQL
"""
import os
import sys
import django
import sqlite3
import psycopg2
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iphone_import_system.settings')
django.setup()

from core.models import User, ConfiguracaoPadrao, Importacao, HistoricoPreco

def backup_sqlite_data():
    """Faz backup dos dados do SQLite antes da migração"""
    try:
        # Conectar ao SQLite
        sqlite_path = 'db.sqlite3'
        if not os.path.exists(sqlite_path):
            print("❌ Banco SQLite não encontrado!")
            return False
        
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Backup dos usuários
        cursor.execute("SELECT * FROM core_user")
        users = cursor.fetchall()
        
        cursor.execute("SELECT * FROM core_configuracaopadrao")
        configs = cursor.fetchall()
        
        cursor.execute("SELECT * FROM core_importacao")
        importacoes = cursor.fetchall()
        
        cursor.execute("SELECT * FROM core_historicopreco")
        historico = cursor.fetchall()
        
        conn.close()
        
        # Salvar backup em arquivo
        backup_data = {
            'users': users,
            'configs': configs,
            'importacoes': importacoes,
            'historico': historico,
            'backup_date': datetime.now().isoformat()
        }
        
        import json
        with open(f'backup_sqlite_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        print(f"✅ Backup criado com sucesso!")
        print(f"   - Usuários: {len(users)}")
        print(f"   - Configurações: {len(configs)}")
        print(f"   - Importações: {len(importacoes)}")
        print(f"   - Histórico: {len(historico)}")
        
        return backup_data
    except Exception as e:
        print(f"❌ Erro ao fazer backup: {e}")
        return False

def migrate_data_to_supabase(backup_data):
    """Migra os dados para o Supabase usando Django ORM"""
    try:
        print("\n📦 Iniciando migração de dados...")
        
        # Migrar usuários
        print("👤 Migrando usuários...")
        users_migrated = 0
        for user_data in backup_data['users']:
            try:
                # Verificar se usuário já existe
                if not User.objects.filter(username=user_data[3]).exists():
                    user = User(
                        id=user_data[0],
                        password=user_data[1],
                        last_login=user_data[2],
                        is_superuser=user_data[3],
                        username=user_data[4],
                        first_name=user_data[5],
                        last_name=user_data[6],
                        email=user_data[7],
                        is_staff=user_data[8],
                        is_active=user_data[9],
                        date_joined=user_data[10],
                        role=user_data[11] if len(user_data) > 11 else 'user'
                    )
                    user.save()
                    users_migrated += 1
            except Exception as e:
                print(f"   ⚠️ Erro ao migrar usuário {user_data[4]}: {e}")
        
        print(f"   ✅ {users_migrated} usuários migrados")
        
        # Migrar configurações
        print("⚙️ Migrando configurações...")
        configs_migrated = 0
        for config_data in backup_data['configs']:
            try:
                user = User.objects.get(id=config_data[1])
                if not ConfiguracaoPadrao.objects.filter(user=user).exists():
                    config = ConfiguracaoPadrao(
                        user=user,
                        cambio_usdt_padrao=config_data[2],
                        frete_py_padrao=config_data[3],
                        taxa_adm_padrao=config_data[4],
                        frete_eua_padrao=config_data[5],
                        pol_eua_padrao=config_data[6]
                    )
                    config.save()
                    configs_migrated += 1
            except Exception as e:
                print(f"   ⚠️ Erro ao migrar configuração: {e}")
        
        print(f"   ✅ {configs_migrated} configurações migradas")
        
        # Migrar importações
        print("📱 Migrando importações...")
        importacoes_migrated = 0
        for imp_data in backup_data['importacoes']:
            try:
                user = User.objects.get(id=imp_data[1])
                importacao = Importacao(
                    user=user,
                    modelo=imp_data[2],
                    capacidade_gb=imp_data[3],
                    grade=imp_data[4],
                    quantidade=imp_data[5],
                    valor_eua_unitario=imp_data[6],
                    # Adicionar outros campos conforme necessário
                    data_importacao=imp_data[-3] if len(imp_data) > 10 else datetime.now().date(),
                    status=imp_data[-2] if len(imp_data) > 10 else 'planejado'
                )
                importacao.save()
                importacoes_migrated += 1
            except Exception as e:
                print(f"   ⚠️ Erro ao migrar importação: {e}")
        
        print(f"   ✅ {importacoes_migrated} importações migradas")
        
        # Migrar histórico
        print("📊 Migrando histórico de preços...")
        historico_migrated = 0
        for hist_data in backup_data['historico']:
            try:
                user = User.objects.get(id=hist_data[1])
                historico = HistoricoPreco(
                    user=user,
                    modelo=hist_data[2],
                    capacidade_gb=hist_data[3],
                    grade=hist_data[4],
                    preco_eua=hist_data[5],
                    preco_venda_brl=hist_data[6],
                    data_registro=hist_data[7]
                )
                historico.save()
                historico_migrated += 1
            except Exception as e:
                print(f"   ⚠️ Erro ao migrar histórico: {e}")
        
        print(f"   ✅ {historico_migrated} registros de histórico migrados")
        
        print("\n🎉 Migração concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        return False

def verify_migration():
    """Verifica se a migração foi bem-sucedida"""
    try:
        print("\n🔍 Verificando migração...")
        
        users_count = User.objects.count()
        configs_count = ConfiguracaoPadrao.objects.count()
        importacoes_count = Importacao.objects.count()
        historico_count = HistoricoPreco.objects.count()
        
        print(f"📊 Dados no Supabase:")
        print(f"   - Usuários: {users_count}")
        print(f"   - Configurações: {configs_count}")
        print(f"   - Importações: {importacoes_count}")
        print(f"   - Histórico: {historico_count}")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar migração: {e}")
        return False

def main():
    print("🔄 Migração SQLite → Supabase")
    print("=" * 40)
    
    # 1. Fazer backup dos dados SQLite
    print("\n1. Fazendo backup dos dados SQLite...")
    backup_data = backup_sqlite_data()
    if not backup_data:
        return
    
    # 2. Confirmar migração
    print(f"\n2. Dados encontrados para migração:")
    print(f"   - Usuários: {len(backup_data['users'])}")
    print(f"   - Configurações: {len(backup_data['configs'])}")
    print(f"   - Importações: {len(backup_data['importacoes'])}")
    print(f"   - Histórico: {len(backup_data['historico'])}")
    
    confirm = input("\nDeseja continuar com a migração? (s/N): ")
    if confirm.lower() != 's':
        print("❌ Migração cancelada pelo usuário.")
        return
    
    # 3. Migrar dados
    print("\n3. Migrando dados para Supabase...")
    if not migrate_data_to_supabase(backup_data):
        return
    
    # 4. Verificar migração
    print("\n4. Verificando migração...")
    verify_migration()
    
    print("\n✅ Migração concluída!")
    print("\n📝 Próximos passos:")
    print("1. Teste o sistema com os dados migrados")
    print("2. Verifique se todas as funcionalidades estão funcionando")
    print("3. Faça backup do banco SQLite original")
    print("4. Configure o sistema para usar apenas o Supabase")

if __name__ == "__main__":
    main()
