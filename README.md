# 📱 iPhone Import Management System

Sistema completo de gestão de importações de iPhone com Django, Supabase e relatórios avançados.

## 🚀 Demo

**Live Demo**: [iphone-controle.vercel.app](https://iphone-controle.vercel.app)

## ✨ Funcionalidades

### 📊 Dashboard Completo
- Estatísticas em tempo real
- Gráficos de performance
- Métricas de rentabilidade
- Visão geral das importações

### 📱 Gestão de Importações
- ✅ CRUD completo de importações
- ✅ Cálculos automáticos de custos e lucros
- ✅ Controle de status (Planejado → Em Trânsito → Recebido → Vendido)
- ✅ Grades de qualidade (A+, A, B+, B, C)
- ✅ Múltiplas rotas (EUA e Paraguay)

### 📈 Relatórios Avançados
- **Estatísticas Gerais**: Métricas principais do negócio
- **Rentabilidade por Modelo**: Análise de lucro por iPhone
- **Status das Importações**: Distribuição por status
- **Análise de Custos**: Comparação EUA vs Paraguay
- **Performance por Grade**: Análise por qualidade
- **Importações Recentes**: Últimas atividades

### 📄 Exportação
- ✅ **PDF**: Relatórios profissionais
- ✅ **Excel**: Planilhas detalhadas
- ✅ **Gráficos**: Visualizações com matplotlib/seaborn

### 👥 Gestão de Usuários
- ✅ Sistema de roles (Admin/User)
- ✅ Autenticação segura
- ✅ Permissões granulares
- ✅ CRUD de usuários (apenas admins)

### ⚙️ Configurações
- ✅ Configurações padrão por usuário
- ✅ Câmbio USDT personalizável
- ✅ Taxas e fretes configuráveis

## 🛠️ Stack Tecnológica

### Backend
- **Django 5.0** - Framework web Python
- **PostgreSQL** - Banco de dados (Supabase)
- **Django ORM** - Mapeamento objeto-relacional

### Frontend
- **Tailwind CSS** - Framework CSS utilitário
- **Alpine.js** - JavaScript reativo
- **HTMX** - Interações dinâmicas
- **Flowbite** - Componentes UI

### Relatórios
- **ReportLab** - Geração de PDF
- **XlsxWriter** - Geração de Excel
- **Matplotlib** - Gráficos
- **Seaborn** - Visualizações estatísticas

### Deploy
- **Vercel** - Hospedagem e deploy
- **Supabase** - Banco de dados PostgreSQL
- **GitHub** - Controle de versão

## 🚀 Deploy Rápido

### 1. Deploy no Vercel (1-click)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/juliocesarportela/iphone-controle)

### 2. Configurar Variáveis de Ambiente

No painel do Vercel, adicione:

```env
DEBUG=False
USE_SQLITE=False
SECRET_KEY=sua-chave-secreta-aqui
SUPABASE_URL=https://whkxlrzscxuctkwtdknj.supabase.co
SUPABASE_KEY=sua-api-key-aqui
SUPABASE_DB_PASSWORD=sua-senha-db-aqui
```

### 3. Configurar Banco de Dados

1. Acesse: [Supabase SQL Editor](https://whkxlrzscxuctkwtdknj.supabase.co/project/whkxlrzscxuctkwtdknj/sql)
2. Execute o script `supabase_schema.sql`
3. Verifique se as tabelas foram criadas

## 💻 Desenvolvimento Local

### Pré-requisitos
- Python 3.12+
- Git

### Instalação

```bash
# 1. Clonar repositório
git clone https://github.com/juliocesarportela/iphone-controle.git
cd iphone-controle

# 2. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 5. Executar migrações
python manage.py migrate

# 6. Criar superusuário
python manage.py createsuperuser

# 7. Iniciar servidor
python manage.py runserver
```

### Configuração Local

Arquivo `.env`:
```env
DEBUG=True
USE_SQLITE=True
SECRET_KEY=sua-chave-local
SUPABASE_URL=https://whkxlrzscxuctkwtdknj.supabase.co
SUPABASE_KEY=sua-api-key
```

## 📊 Estrutura do Projeto

```
iphone-controle/
├── core/                   # App principal
│   ├── models.py          # Modelos de dados
│   ├── views.py           # Lógica de negócio
│   ├── forms.py           # Formulários
│   └── urls.py            # Rotas
├── templates/             # Templates HTML
│   ├── base.html         # Template base
│   ├── dashboard/        # Dashboard
│   ├── importacoes/      # Gestão de importações
│   ├── relatorios/       # Relatórios
│   └── admin/            # Administração
├── static/               # Arquivos estáticos
├── requirements.txt      # Dependências Python
├── vercel.json          # Configuração Vercel
└── supabase_schema.sql  # Schema do banco
```

## 🔧 Configuração Avançada

### Banco de Dados

O sistema suporta dois modos:

**Desenvolvimento (SQLite)**:
```env
USE_SQLITE=True
```

**Produção (PostgreSQL/Supabase)**:
```env
USE_SQLITE=False
SUPABASE_DB_PASSWORD=sua-senha
```

### Relatórios

Para habilitar exportação PDF/Excel:
```bash
pip install reportlab xlsxwriter matplotlib seaborn
```

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `DEBUG` | Modo debug | `True` |
| `USE_SQLITE` | Usar SQLite | `True` |
| `SECRET_KEY` | Chave secreta Django | - |
| `SUPABASE_URL` | URL do Supabase | - |
| `SUPABASE_KEY` | API Key Supabase | - |
| `SUPABASE_DB_PASSWORD` | Senha do banco | - |

## 📈 Funcionalidades Detalhadas

### Cálculos Automáticos

O sistema calcula automaticamente:
- **Custo total EUA**: Valor + taxas + frete + POL
- **Custo total Paraguay**: Conversão USDT + frete
- **Margem de lucro**: Baseada no preço de venda
- **ROI**: Retorno sobre investimento

### Relatórios Disponíveis

1. **Estatísticas Gerais**
   - Total de importações
   - Valor total investido
   - Lucro total
   - Margem média

2. **Rentabilidade por Modelo**
   - Lucro por modelo de iPhone
   - Margem por modelo
   - Quantidade vendida

3. **Análise de Status**
   - Distribuição por status
   - Tempo médio por status
   - Gráficos de pipeline

## 🔐 Segurança

- ✅ Autenticação obrigatória
- ✅ Controle de acesso por roles
- ✅ Validação de dados
- ✅ Proteção CSRF
- ✅ SQL Injection protection
- ✅ XSS protection

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Julio Cesar Portela**
- GitHub: [@juliocesarportela](https://github.com/juliocesarportela)
- LinkedIn: [Julio Cesar Portela](https://linkedin.com/in/juliocesarportela)

## 🙏 Agradecimentos

- Django Community
- Tailwind CSS Team
- Supabase Team
- Vercel Team

---

⭐ **Se este projeto te ajudou, deixe uma estrela!**
