-- Migration: historico de campanhas geradas pela VIVA (chat interno)
CREATE TABLE IF NOT EXISTS viva_campanhas (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    modo VARCHAR(32) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    briefing TEXT,
    mensagem_original TEXT,
    image_url TEXT NOT NULL,
    overlay_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_viva_campanhas_created_at
    ON viva_campanhas(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_viva_campanhas_user_id
    ON viva_campanhas(user_id);

CREATE INDEX IF NOT EXISTS idx_viva_campanhas_modo
    ON viva_campanhas(modo);
