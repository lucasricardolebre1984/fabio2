# Deploy Vercel (Frontend + Backend)

## Objetivo
Publicar o projeto em modo "tudo Vercel" (frontend Next.js + backend FastAPI serverless) com rollback simples.

## Backend (FastAPI) no Vercel
### Arquivos adicionados
- `backend/api/index.py`
- `backend/vercel.json`

### Comportamento em ambiente Vercel
- Para evitar loop/background worker em ambiente serverless, o backend desativa o `handoff_worker()` quando a env var `VERCEL=1`.

### Criar projeto (Vercel UI)
1. Vercel -> Add New -> Project
2. Importar o repositório
3. **Root Directory**: `backend`
4. Deploy

### Variáveis de ambiente (mínimo)
- `OPENAI_API_KEY`
- `DATABASE_URL` (Postgres externo)
- `SECRET_KEY` (seu JWT/segurança)
- `CORS_ORIGINS` (inclua a URL do frontend Vercel)
- `VERCEL=1`

### Rotas
- Health: `/health`
- API: `/api/v1/...`

## Frontend (Next.js) no Vercel
1. Vercel -> Add New -> Project
2. Importar o repositório
3. **Root Directory**: `frontend`
4. Env var:
   - `NEXT_PUBLIC_API_URL` = `https://<backend-vercel-domain>/api/v1`
5. Deploy

## Rollback (voltar ao modo anterior)
1. Remover arquivos:
   - `backend/vercel.json`
   - `backend/api/index.py`
2. Reverter alteração em `backend/app/main.py`:
   - remover lógica `is_vercel = os.getenv("VERCEL") == "1"`
   - voltar a iniciar sempre o `handoff_worker()` no `lifespan`

Observação: rollback não altera banco/infra, apenas o suporte a serverless no Vercel.
