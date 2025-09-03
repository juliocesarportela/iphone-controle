-- =====================================================
-- SCRIPT SQL PARA CRIAÇÃO DAS TABELAS NO SUPABASE
-- Sistema de Gestão de Importações de iPhone
-- =====================================================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. TABELA DE USUÁRIOS (core_user)
-- =====================================================
CREATE TABLE IF NOT EXISTS core_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMPTZ,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    role VARCHAR(10) NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para a tabela de usuários
CREATE INDEX IF NOT EXISTS core_user_username_idx ON core_user(username);
CREATE INDEX IF NOT EXISTS core_user_email_idx ON core_user(email);
CREATE INDEX IF NOT EXISTS core_user_role_idx ON core_user(role);

-- =====================================================
-- 2. TABELA DE GRUPOS DE USUÁRIOS (auth_group)
-- =====================================================
CREATE TABLE IF NOT EXISTS auth_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

-- =====================================================
-- 3. TABELA DE PERMISSÕES (auth_permission)
-- =====================================================
CREATE TABLE IF NOT EXISTS auth_permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INTEGER NOT NULL,
    codename VARCHAR(100) NOT NULL
);

-- =====================================================
-- 4. TABELA DE RELACIONAMENTO USUÁRIO-GRUPOS (core_user_groups)
-- =====================================================
CREATE TABLE IF NOT EXISTS core_user_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES core_user(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,
    UNIQUE(user_id, group_id)
);

-- =====================================================
-- 5. TABELA DE RELACIONAMENTO USUÁRIO-PERMISSÕES (core_user_user_permissions)
-- =====================================================
CREATE TABLE IF NOT EXISTS core_user_user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES core_user(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
    UNIQUE(user_id, permission_id)
);

-- =====================================================
-- 6. TABELA DE CONFIGURAÇÕES PADRÃO (core_configuracaopadrao)
-- =====================================================
CREATE TABLE IF NOT EXISTS core_configuracaopadrao (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES core_user(id) ON DELETE CASCADE,
    cambio_usdt_padrao DECIMAL(10,4) NOT NULL DEFAULT 5.5600,
    frete_py_padrao DECIMAL(10,2) NOT NULL DEFAULT 7.50,
    taxa_adm_padrao DECIMAL(10,2) NOT NULL DEFAULT 1.90,
    frete_eua_padrao DECIMAL(10,2) NOT NULL DEFAULT 1.93,
    pol_eua_padrao DECIMAL(10,2) NOT NULL DEFAULT 10.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índice para configurações
CREATE INDEX IF NOT EXISTS core_configuracaopadrao_user_idx ON core_configuracaopadrao(user_id);

-- =====================================================
-- 7. TABELA DE IMPORTAÇÕES (core_importacao)
-- =====================================================
CREATE TABLE IF NOT EXISTS core_importacao (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES core_user(id) ON DELETE CASCADE,
    
    -- Informações básicas do produto
    modelo VARCHAR(50) NOT NULL,
    capacidade_gb INTEGER NOT NULL CHECK (capacidade_gb >= 64),
    grade VARCHAR(2) NOT NULL CHECK (grade IN ('A+', 'A', 'B+', 'B', 'C')),
    quantidade INTEGER NOT NULL CHECK (quantidade >= 1),
    
    -- Custos EUA (baseados na planilha)
    valor_eua_unitario DECIMAL(10,2) NOT NULL,
    taxa_adm_percentual DECIMAL(5,3) NOT NULL DEFAULT 0.005,
    taxa_adm_fixa DECIMAL(10,2) NOT NULL DEFAULT 1.90,
    frete_eua DECIMAL(10,2) NOT NULL DEFAULT 1.93,
    pol_eua DECIMAL(10,2) NOT NULL DEFAULT 10.00,
    
    -- Câmbio e frete Paraguay
    cambio_usdt DECIMAL(10,4) NOT NULL DEFAULT 5.5600,
    frete_py_usd_kg DECIMAL(10,2) NOT NULL DEFAULT 7.50,
    kg_py_usd DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    
    -- Status e datas
    data_importacao DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(15) NOT NULL DEFAULT 'planejado' CHECK (status IN ('planejado', 'em_transito', 'recebido', 'vendido')),
    
    -- Venda (opcional)
    preco_venda_unitario DECIMAL(10,2),
    data_venda DATE,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para importações
CREATE INDEX IF NOT EXISTS core_importacao_user_idx ON core_importacao(user_id);
CREATE INDEX IF NOT EXISTS core_importacao_modelo_idx ON core_importacao(modelo);
CREATE INDEX IF NOT EXISTS core_importacao_status_idx ON core_importacao(status);
CREATE INDEX IF NOT EXISTS core_importacao_grade_idx ON core_importacao(grade);
CREATE INDEX IF NOT EXISTS core_importacao_data_importacao_idx ON core_importacao(data_importacao);
CREATE INDEX IF NOT EXISTS core_importacao_data_venda_idx ON core_importacao(data_venda);

-- =====================================================
-- 8. TABELA DE HISTÓRICO DE PREÇOS (core_historicopreco)
-- =====================================================
CREATE TABLE IF NOT EXISTS core_historicopreco (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES core_user(id) ON DELETE CASCADE,
    modelo VARCHAR(50) NOT NULL,
    capacidade_gb INTEGER NOT NULL,
    grade VARCHAR(2) NOT NULL CHECK (grade IN ('A+', 'A', 'B+', 'B', 'C')),
    preco_eua DECIMAL(10,2) NOT NULL,
    preco_venda_brl DECIMAL(10,2),
    data_registro DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para histórico de preços
CREATE INDEX IF NOT EXISTS core_historicopreco_user_idx ON core_historicopreco(user_id);
CREATE INDEX IF NOT EXISTS core_historicopreco_modelo_idx ON core_historicopreco(modelo);
CREATE INDEX IF NOT EXISTS core_historicopreco_data_registro_idx ON core_historicopreco(data_registro);

-- =====================================================
-- 9. TABELAS DO DJANGO ADMIN E SESSÕES
-- =====================================================

-- Tabela de tipos de conteúdo do Django
CREATE TABLE IF NOT EXISTS django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE(app_label, model)
);

-- Tabela de sessões do Django
CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMPTZ NOT NULL
);

-- Índice para sessões
CREATE INDEX IF NOT EXISTS django_session_expire_date_idx ON django_session(expire_date);

-- Tabela de migrações do Django
CREATE TABLE IF NOT EXISTS django_migrations (
    id SERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================
-- 10. TRIGGERS PARA UPDATED_AT
-- =====================================================

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar updated_at
CREATE TRIGGER update_core_configuracaopadrao_updated_at 
    BEFORE UPDATE ON core_configuracaopadrao 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_core_importacao_updated_at 
    BEFORE UPDATE ON core_importacao 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 11. INSERIR DADOS INICIAIS
-- =====================================================

-- Inserir tipos de conteúdo básicos
INSERT INTO django_content_type (app_label, model) VALUES 
    ('core', 'user'),
    ('core', 'configuracaopadrao'),
    ('core', 'importacao'),
    ('core', 'historicopreco'),
    ('auth', 'group'),
    ('auth', 'permission')
ON CONFLICT (app_label, model) DO NOTHING;

-- Inserir permissões básicas
INSERT INTO auth_permission (name, content_type_id, codename) VALUES 
    ('Can add user', (SELECT id FROM django_content_type WHERE app_label='core' AND model='user'), 'add_user'),
    ('Can change user', (SELECT id FROM django_content_type WHERE app_label='core' AND model='user'), 'change_user'),
    ('Can delete user', (SELECT id FROM django_content_type WHERE app_label='core' AND model='user'), 'delete_user'),
    ('Can view user', (SELECT id FROM django_content_type WHERE app_label='core' AND model='user'), 'view_user'),
    ('Can add importacao', (SELECT id FROM django_content_type WHERE app_label='core' AND model='importacao'), 'add_importacao'),
    ('Can change importacao', (SELECT id FROM django_content_type WHERE app_label='core' AND model='importacao'), 'change_importacao'),
    ('Can delete importacao', (SELECT id FROM django_content_type WHERE app_label='core' AND model='importacao'), 'delete_importacao'),
    ('Can view importacao', (SELECT id FROM django_content_type WHERE app_label='core' AND model='importacao'), 'view_importacao')
ON CONFLICT DO NOTHING;

-- =====================================================
-- 12. POLÍTICAS DE SEGURANÇA RLS (ROW LEVEL SECURITY)
-- =====================================================

-- Habilitar RLS nas tabelas principais
ALTER TABLE core_configuracaopadrao ENABLE ROW LEVEL SECURITY;
ALTER TABLE core_importacao ENABLE ROW LEVEL SECURITY;
ALTER TABLE core_historicopreco ENABLE ROW LEVEL SECURITY;

-- Política para configurações: usuários só veem suas próprias configurações
CREATE POLICY "Users can view own configurations" ON core_configuracaopadrao
    FOR ALL USING (auth.uid()::text = user_id::text);

-- Política para importações: usuários só veem suas próprias importações
CREATE POLICY "Users can view own imports" ON core_importacao
    FOR ALL USING (auth.uid()::text = user_id::text);

-- Política para histórico: usuários só veem seu próprio histórico
CREATE POLICY "Users can view own price history" ON core_historicopreco
    FOR ALL USING (auth.uid()::text = user_id::text);

-- =====================================================
-- 13. COMENTÁRIOS NAS TABELAS
-- =====================================================

COMMENT ON TABLE core_user IS 'Tabela de usuários do sistema com roles personalizados';
COMMENT ON TABLE core_configuracaopadrao IS 'Configurações padrão por usuário para importações';
COMMENT ON TABLE core_importacao IS 'Tabela principal de importações de iPhone com cálculos automáticos';
COMMENT ON TABLE core_historicopreco IS 'Histórico de preços para análise de tendências';

-- Comentários em colunas importantes
COMMENT ON COLUMN core_importacao.valor_eua_unitario IS 'Valor unitário nos EUA em USD';
COMMENT ON COLUMN core_importacao.cambio_usdt IS 'Taxa de câmbio USDT para BRL';
COMMENT ON COLUMN core_importacao.frete_py_usd_kg IS 'Frete Paraguay por kg em USD';

-- =====================================================
-- FIM DO SCRIPT
-- =====================================================

-- Verificar se todas as tabelas foram criadas
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename LIKE 'core_%' 
    OR tablename LIKE 'django_%'
    OR tablename LIKE 'auth_%'
ORDER BY tablename;
