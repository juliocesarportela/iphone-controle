# 🚀 Guia de Configuração do Supabase para iPhone Import System

Este guia irá te ajudar a configurar o sistema para usar o Supabase como banco de dados PostgreSQL.

## 📋 Pré-requisitos

- Python 3.12+
- Conta no Supabase
- Projeto criado no Supabase
- Credenciais do banco de dados

## 🔧 Configurações do Supabase

### Informações do seu projeto:
- **URL**: https://whkxlrzscxuctkwtdknj.supabase.co
- **API Key**: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indoa3hscnpzY3h1Y3Rrd3Rka25qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY4NjQyNDMsImV4cCI6MjA3MjQ0MDI0M30.7mYZi_r7O2D8BLwUwbyyq1b9HINQY8LKP-U_5hJeVGc

### Configurações do PostgreSQL:
- **Host**: aws-0-us-east-1.pooler.supabase.com
- **Port**: 6543
- **Database**: postgres
- **User**: postgres.whkxlrzscxuctkwtdknj
- **Password**: [Você precisará obter no painel do Supabase]

## 🛠️ Passo a Passo da Instalação

### 1. Instalar Dependências

```bash
# Ativar o ambiente virtual
venv\Scripts\activate

# Instalar novas dependências
pip install -r requirements.txt
```

### 2. Obter Senha do Banco de Dados

1. Acesse o painel do Supabase: https://supabase.com/dashboard
2. Vá para seu projeto
3. Clique em "Settings" → "Database"
4. Copie a senha do banco de dados (ou redefina se necessário)

### 3. Executar Script de Configuração

```bash
python setup_supabase.py
```

Este script irá:
- ✅ Testar conexão com Supabase
- ✅ Criar arquivo `.env` com configurações
- ✅ Executar script SQL para criar tabelas
- ✅ Configurar migrações Django
- ✅ Criar superusuário

### 4. (Opcional) Migrar Dados Existentes

Se você já tem dados no SQLite:

```bash
python migrate_to_supabase.py
```

### 5. Executar Migrações Django

```bash
python manage.py migrate --fake-initial
```

### 6. Criar Superusuário (se não criado no passo 3)

```bash
python manage.py createsuperuser
```

### 7. Testar o Sistema

```bash
python manage.py runserver
```

Acesse: http://localhost:8000

## 📁 Arquivos Criados

### `.env`
Arquivo com configurações sensíveis (não commitar no Git):
```env
SECRET_KEY=your-secret-key
SUPABASE_URL=https://whkxlrzscxuctkwtdknj.supabase.co
SUPABASE_KEY=your-api-key
SUPABASE_DB_PASSWORD=your-db-password
DATABASE_URL=postgresql://user:pass@host:port/db
```

### `supabase_schema.sql`
Script SQL completo com todas as tabelas:
- ✅ Tabelas de usuários com roles
- ✅ Tabelas de importações
- ✅ Tabelas de configurações
- ✅ Tabelas de histórico
- ✅ Índices otimizados
- ✅ Triggers para updated_at
- ✅ Políticas de segurança RLS

## 🔒 Segurança

### Row Level Security (RLS)
O sistema implementa RLS para garantir que:
- Usuários só veem seus próprios dados
- Administradores têm acesso completo
- Dados são isolados por usuário

### Variáveis de Ambiente
- Todas as credenciais ficam no arquivo `.env`
- Nunca commitar credenciais no código
- Usar variáveis de ambiente em produção

## 📊 Estrutura do Banco

### Tabelas Principais:
1. **core_user** - Usuários com roles (admin/user)
2. **core_importacao** - Importações de iPhone
3. **core_configuracaopadrao** - Configurações por usuário
4. **core_historicopreco** - Histórico de preços

### Relacionamentos:
- User → ConfiguracaoPadrao (1:1)
- User → Importacao (1:N)
- User → HistoricoPreco (1:N)

## 🚀 Deploy em Produção

### Variáveis de Ambiente:
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
SUPABASE_URL=https://whkxlrzscxuctkwtdknj.supabase.co
SUPABASE_KEY=your-api-key
SUPABASE_DB_PASSWORD=your-production-password
ALLOWED_HOSTS=your-domain.com
```

### Comandos de Deploy:
```bash
# Coletar arquivos estáticos
python manage.py collectstatic

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

## 🔧 Troubleshooting

### Erro de Conexão PostgreSQL
- Verifique se a senha está correta
- Confirme se o IP está liberado no Supabase
- Teste a conexão com psql ou pgAdmin

### Erro de Migração
```bash
# Resetar migrações se necessário
python manage.py migrate --fake core zero
python manage.py migrate --fake-initial
```

### Erro de Permissões
- Verifique as políticas RLS no Supabase
- Confirme se o usuário tem role 'admin' ou 'user'

## 📞 Suporte

### Logs Úteis:
```bash
# Ver logs do Django
python manage.py runserver --verbosity=2

# Testar conexão com banco
python manage.py dbshell
```

### Comandos de Diagnóstico:
```bash
# Verificar configurações
python manage.py check

# Listar migrações
python manage.py showmigrations

# Testar importações
python -c "from core.models import User; print(User.objects.count())"
```

## ✅ Checklist Final

- [ ] Dependências instaladas
- [ ] Arquivo `.env` criado
- [ ] Conexão com Supabase testada
- [ ] Tabelas criadas no banco
- [ ] Migrações executadas
- [ ] Superusuário criado
- [ ] Sistema funcionando
- [ ] Dados migrados (se aplicável)
- [ ] Backup dos dados antigos
- [ ] Testes de funcionalidade

## 🎉 Próximos Passos

1. **Testar todas as funcionalidades**
   - Login/logout
   - CRUD de importações
   - Relatórios
   - Gerenciamento de usuários

2. **Configurar backup automático**
   - Backup diário dos dados
   - Versionamento do banco

3. **Monitoramento**
   - Logs de acesso
   - Performance do banco
   - Uso de recursos

4. **Deploy em produção**
   - Configurar domínio
   - SSL/HTTPS
   - CDN para arquivos estáticos

---

**🔥 Seu sistema agora está pronto para usar o Supabase como banco de dados!**
