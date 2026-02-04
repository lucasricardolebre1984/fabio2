-- Migration: Criar tabela de tracking de custos de imagens
CREATE TABLE IF NOT EXISTS imagens_custos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    imagem_id UUID REFERENCES imagens(id) ON DELETE SET NULL,
    modelo VARCHAR(50) NOT NULL DEFAULT 'glm-image',
    provider VARCHAR(50) NOT NULL DEFAULT 'zai',
    custo_usd NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    custo_brl NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    taxa_cambio NUMERIC(10, 6),
    dimensoes VARCHAR(20),
    formato VARCHAR(10),
    tempo_geracao_ms INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'pendente',
    erro_mensagem TEXT,
    prompt_original TEXT,
    prompt_enhanced TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_imagens_custos_imagem_id ON imagens_custos(imagem_id);
CREATE INDEX IF NOT EXISTS idx_imagens_custos_status ON imagens_custos(status);
CREATE INDEX IF NOT EXISTS idx_imagens_custos_created_at ON imagens_custos(created_at);
