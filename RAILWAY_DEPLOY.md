# 🚀 Deploy no Railway - Guia Completo

## ✅ Pré-requisitos Atendidos

Seu projeto já está configurado com:
- ✅ `requirements.txt` otimizado para produção
- ✅ `Procfile` configurado
- ✅ `railway.json` configurado
- ✅ `start.sh` script de inicialização
- ✅ `production_settings.py` para produção
- ✅ `ALLOWED_HOSTS` configurado para Railway

## 🔧 Passos para Deploy

### 1. Acesse o Railway
1. Vá para [railway.app](https://railway.app)
2. Faça login com sua conta GitHub
3. Clique em "New Project"

### 2. Conecte seu Repositório
1. Selecione "Deploy from GitHub repo"
2. Escolha o repositório `iphone-manager`
3. Clique em "Deploy Now"

### 3. Configure as Variáveis de Ambiente
No painel do Railway, vá em "Variables" e adicione:

```
SECRET_KEY=django-insecure-railway-key-change-in-production-12345
DEBUG=False
DJANGO_SETTINGS_MODULE=iphone_import_system.production_settings
USE_SQLITE=True
```

### 4. Adicione PostgreSQL (Opcional)
1. No painel do Railway, clique em "New"
2. Selecione "Database" → "PostgreSQL"
3. Após criar, copie a `DATABASE_URL`
4. Adicione nas variáveis:
```
DATABASE_URL=postgresql://user:pass@host:port/db
USE_SQLITE=False
```

### 5. Deploy Automático
- O Railway detectará automaticamente o `Procfile`
- O build começará automaticamente
- Aguarde ~5-10 minutos para conclusão

## 🌐 URL do Projeto
Após o deploy, sua aplicação estará disponível em:
`https://seu-projeto.railway.app`

## 🔍 Monitoramento
- Logs: Disponíveis no painel do Railway
- Métricas: CPU, RAM, requests
- Redeploy: Automático a cada push no GitHub

## ⚡ Vantagens do Railway
- ✅ 500MB RAM gratuitos
- ✅ PostgreSQL incluído
- ✅ Deploy automático
- ✅ SSL automático
- ✅ Sem timeout de build
- ✅ Suporte nativo ao Django
