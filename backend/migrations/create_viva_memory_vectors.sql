-- VIVA long-term memory vectors (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS viva_memory_vectors (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL,
    tipo VARCHAR(16) NOT NULL,
    modo VARCHAR(32),
    conteudo TEXT NOT NULL,
    meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_viva_memory_user_created
ON viva_memory_vectors(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_viva_memory_session_created
ON viva_memory_vectors(session_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_viva_memory_embedding_ivfflat
ON viva_memory_vectors USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
