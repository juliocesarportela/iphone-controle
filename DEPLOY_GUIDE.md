# 🚀 Guia de Deploy - GitHub + Vercel

## 📋 Checklist Pré-Deploy

- ✅ Sistema funcionando localmente
- ✅ Arquivos de configuração criados
- ✅ .gitignore configurado
- ✅ README.md criado
- ✅ Configurações Vercel prontas
- ✅ Supabase configurado

## 🔧 Comandos Git para GitHub

Execute estes comandos no terminal (dentro do diretório do projeto):

```bash
# 1. Inicializar repositório Git
git init

# 2. Adicionar remote do GitHub
git remote add origin https://github.com/juliocesarportela/iphone-controle.git

# 3. Adicionar todos os arquivos
git add .

# 4. Primeiro commit
git commit -m "🚀 Initial commit: iPhone Import Management System

✨ Features:
- Complete Django 5.0 application
- Supabase PostgreSQL integration
- Advanced reporting (PDF/Excel)
- User management with roles
- Real-time dashboard
- HTMX + Tailwind CSS UI
- Vercel deployment ready

🛠️ Tech Stack:
- Django 5.0 + Python 3.12
- PostgreSQL (Supabase)
- Tailwind CSS + Alpine.js
- ReportLab + XlsxWriter
- HTMX for dynamic interactions

📊 Modules:
- Import management (CRUD)
- Advanced reports with charts
- User authentication & roles
- Configuration management
- Dashboard with metrics"

# 5. Push para GitHub
git branch -M main
git push -u origin main
```

## 🌐 Deploy no Vercel

### Método 1: Deploy Automático (Recomendado)

1. **Acesse**: https://vercel.com/new
2. **Conecte sua conta GitHub**
3. **Selecione o repositório**: `juliocesarportela/iphone-controle`
4. **Configure as variáveis de ambiente** (veja seção abaixo)
5. **Clique em "Deploy"**

### Método 2: Vercel CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Login no Vercel
vercel login

# Deploy
vercel --prod
```

## ⚙️ Variáveis de Ambiente no Vercel

No painel do Vercel, adicione estas variáveis:

| Variável | Valor |
|----------|-------|
| `DEBUG` | `False` |
| `USE_SQLITE` | `False` |
| `SECRET_KEY` | `django-insecure-change-this-in-production-vercel-2025` |
| `ALLOWED_HOST` | `iphone-controle.vercel.app` |
| `SUPABASE_URL` | `https://whkxlrzscxuctkwtdknj.supabase.co` |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `SUPABASE_DB_PASSWORD` | `2518@Ago12##` |

## 🗄️ Configurar Banco de Dados

### 1. Criar Tabelas no Supabase

1. **Acesse**: https://whkxlrzscxuctkwtdknj.supabase.co/project/whkxlrzscxuctkwtdknj/sql
2. **Copie o conteúdo** do arquivo `supabase_schema.sql`
3. **Cole no SQL Editor** e execute
4. **Verifique** se as tabelas foram criadas

### 2. Criar Superusuário

Após o deploy, acesse o terminal do Vercel e execute:
```bash
python manage.py createsuperuser
```

## 🔍 Verificar Deploy

### URLs Importantes:
- **Site**: https://iphone-controle.vercel.app
- **Admin**: https://iphone-controle.vercel.app/admin/
- **Dashboard**: https://iphone-controle.vercel.app/dashboard/

### Testes Pós-Deploy:
1. ✅ Site carrega sem erros
2. ✅ Login funciona
3. ✅ Dashboard mostra dados
4. ✅ CRUD de importações funciona
5. ✅ Relatórios são gerados
6. ✅ Exportação PDF/Excel funciona

## 🐛 Troubleshooting

### Erro de Build
```bash
# Verificar logs no Vercel
vercel logs
```

### Erro de Banco
- Verificar se as tabelas foram criadas no Supabase
- Confirmar variáveis de ambiente
- Testar conexão com banco

### Erro de Static Files
```bash
# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

## 🔄 Atualizações Futuras

Para atualizar o sistema:

```bash
# 1. Fazer mudanças no código
# 2. Commit e push
git add .
git commit -m "✨ Nova funcionalidade"
git push

# 3. Deploy automático no Vercel
```

## 📊 Monitoramento

### Métricas Importantes:
- Tempo de resposta
- Uso de memória
- Conexões com banco
- Erros 500/404

### Logs:
- Vercel Dashboard
- Supabase Logs
- Django Debug Toolbar (desenvolvimento)

## 🎉 Deploy Concluído!

Seu sistema está agora disponível em:
**https://iphone-controle.vercel.app**

### Próximos Passos:
1. 🔐 Criar usuários de produção
2. 📊 Importar dados iniciais
3. 🧪 Testar todas as funcionalidades
4. 📈 Monitorar performance
5. 🔄 Configurar backups automáticos

---

**🚀 Sistema de Gestão de Importações iPhone em produção!**
