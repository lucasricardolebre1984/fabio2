-- Migration: Criacao das tabelas de Chat WhatsApp
-- Data: 2026-02-04
-- Descricao: Tabelas para armazenar conversas e mensagens do WhatsApp com IA VIVA

-- Tabela de Conversas
CREATE TABLE IF NOT EXISTS whatsapp_conversas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_telefone VARCHAR(20) NOT NULL,
    nome_contato VARCHAR(200),
    instance_name VARCHAR(100) NOT NULL DEFAULT 'Teste',
    status VARCHAR(20) NOT NULL DEFAULT 'ativa' CHECK (status IN ('ativa', 'arquivada', 'aguardando')),
    contexto_ia JSONB DEFAULT '{}',
    ultima_mensagem_em TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indices para conversas
CREATE INDEX IF NOT EXISTS idx_whatsapp_conversas_numero ON whatsapp_conversas(numero_telefone);
CREATE INDEX IF NOT EXISTS idx_whatsapp_conversas_status ON whatsapp_conversas(status);
CREATE INDEX IF NOT EXISTS idx_whatsapp_conversas_instance ON whatsapp_conversas(instance_name);
CREATE INDEX IF NOT EXISTS idx_whatsapp_conversas_ultima_msg ON whatsapp_conversas(ultima_mensagem_em DESC);

-- Tabela de Mensagens
CREATE TABLE IF NOT EXISTS whatsapp_mensagens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversa_id UUID NOT NULL REFERENCES whatsapp_conversas(id) ON DELETE CASCADE,
    tipo_origem VARCHAR(20) NOT NULL CHECK (tipo_origem IN ('usuario', 'ia', 'sistema')),
    conteudo TEXT NOT NULL,
    message_id VARCHAR(100),
    tipo_midia VARCHAR(50),
    url_midia VARCHAR(500),
    lida BOOLEAN DEFAULT FALSE,
    enviada BOOLEAN DEFAULT TRUE,
    erro TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indices para mensagens
CREATE INDEX IF NOT EXISTS idx_whatsapp_mensagens_conversa ON whatsapp_mensagens(conversa_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_mensagens_created ON whatsapp_mensagens(created_at DESC);

-- Comentarios
COMMENT ON TABLE whatsapp_conversas IS 'Conversas ativas do WhatsApp com clientes';
COMMENT ON TABLE whatsapp_mensagens IS 'Mensagens individuais das conversas WhatsApp';
COMMENT ON COLUMN whatsapp_conversas.contexto_ia IS 'Contexto da conversa para a IA VIVA';
COMMENT ON COLUMN whatsapp_mensagens.tipo_origem IS 'Quem enviou: usuario, ia (VIVA) ou sistema';

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_whatsapp_conversas_updated_at ON whatsapp_conversas;
CREATE TRIGGER update_whatsapp_conversas_updated_at
    BEFORE UPDATE ON whatsapp_conversas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
