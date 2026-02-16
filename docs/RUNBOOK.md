# RUNBOOK - Operacao Local e Homologacao

Projeto: FC Solucoes Financeiras SaaS
Data de revisao: 2026-02-16

## Pre-requisitos

- Docker Desktop
- Python 3.11+
- Node.js 18+

## Subir infraestrutura local

```powershell
cd c:\projetos\fabio2
docker-compose -f docker-compose.local.yml up -d
```

Servicos esperados:
- PostgreSQL: `5432`
- Redis: `6379`
- Evolution API: `8080`

## Backend local

```powershell
cd c:\projetos\fabio2\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Frontend local

```powershell
cd c:\projetos\fabio2\frontend
npm run dev
```

Acesso:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- OpenAPI: `http://localhost:8000/docs`

## Verificacoes obrigatorias de rodada

1. Login no frontend
2. Menu `Clientes` carregando lista real
3. Menu `Contratos` carregando templates e lista
4. Menu `Agenda` com criacao e listagem
5. Menu `Campanhas` com listagem e exclusao
6. Menu `VIVA` respondendo sem erro de rota
7. Endpoint `GET /api/v1/cofre/memories/status` com `200`

## Governanca COFRE

- Persona e skills so em `backend/COFRE/persona-skills/`
- Memorias so em `backend/COFRE/memories/`
- Toda exclusao funcional deve refletir no COFRE

## Deploy institucional

- Alvo principal: Ubuntu AWS com Docker
- Guia principal: `docs/DEPLOY_UBUNTU_DOCKER.md`
- Vercel nao e alvo institucional desta operacao

## Troubleshooting rapido

Backend nao sobe:
- validar env em `backend/.env`
- validar containers de banco/redis

Frontend nao sobe:
- remover cache: `Remove-Item -Recurse -Force .next`
- reinstalar deps: `npm install`

VIVA sem dados reais:
- validar token JWT no frontend
- validar endpoints de modulo no backend
- validar registros em banco e espelho COFRE

Atualizado em: 2026-02-16
