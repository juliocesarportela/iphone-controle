# 🔧 Correção Rápida - Deploy Vercel

## ❌ Problemas Identificados:
1. Script `build_files.sh` não encontra `pip` e `python`
2. Configuração do Vercel muito complexa
3. Bibliotecas pesadas causando timeout

## ✅ Soluções Aplicadas:

### 1. **Vercel.json Simplificado**
- Removido script de build problemático
- Configuração mínima funcional
- Foco apenas no WSGI

### 2. **Requirements Otimizado**
- Criado `requirements-vercel.txt` mais leve
- Bibliotecas de relatório comentadas temporariamente
- Apenas dependências essenciais

## 🚀 Comandos para Corrigir:

```bash
# 1. Commit das correções
git add .
git commit -m "🔧 Fix Vercel deployment configuration

- Simplify vercel.json
- Remove problematic build script  
- Optimize requirements for Vercel
- Fix static files configuration"

# 2. Push para GitHub
git push
```

## ⚙️ Configuração Manual no Vercel:

### No painel do Vercel, configure:

**Build & Development Settings:**
- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- **Output Directory**: (deixe vazio)
- **Install Command**: `pip install -r requirements.txt`

**Environment Variables:**
```
DEBUG=False
USE_SQLITE=False
SECRET_KEY=django-insecure-change-this-in-production-vercel-2025
SUPABASE_URL=https://whkxlrzscxuctkwtdknj.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indoa3hscnpzY3h1Y3Rrd3Rka25qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY4NjQyNDMsImV4cCI6MjA3MjQ0MDI0M30.7mYZi_r7O2D8BLwUwbyyq1b9HINQY8LKP-U_5hJeVGc
SUPABASE_DB_PASSWORD=2518@Ago12##
```

## 🔄 Alternativa: Deploy Simples

Se ainda der problema, use esta configuração mínima:

**vercel.json**:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "iphone_import_system/wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "iphone_import_system/wsgi.py"
    }
  ]
}
```

## 🎯 Próximos Passos:

1. **Commit e push** as correções
2. **Aguardar novo deploy** automático
3. **Se falhar**, configurar manualmente no painel
4. **Após funcionar**, reativar bibliotecas de relatório

## 📊 Funcionalidades Temporariamente Desabilitadas:

- ❌ Exportação PDF/Excel (bibliotecas pesadas)
- ✅ Dashboard e CRUD funcionando
- ✅ Autenticação e usuários
- ✅ Banco Supabase conectado

## 🔧 Reativar Relatórios Depois:

Quando o deploy básico funcionar:
1. Descomentar bibliotecas no `requirements.txt`
2. Commit e push
3. Testar exportações

---

**🚀 Execute os comandos Git acima para corrigir o deploy!**
