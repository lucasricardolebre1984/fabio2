# AGENTS.md

This file provides guidance to coding agents working in this repository.

## Overview
SaaS de gestao de contratos para FC Solucoes Financeiras, com backend FastAPI e frontend Next.js.
Modulos principais: contratos, clientes, agenda, campanhas e integracao WhatsApp (Evolution API).

## Arquitetura
- Backend: `backend/app`
- Frontend: `frontend/src`
- Templates de contratos: `contratos/templates`
- Documentacao oficial: `docs/`

## Regra de ouro (COFRE)
Fonte unica para VIVA:
- Persona: `backend/COFRE/persona-skills/AGENT.md`
- Skills: `backend/COFRE/persona-skills/*.md`
- Memorias auditaveis: `backend/COFRE/memories/<nome_tabela>/`

Toda acao de delete funcional (UI/API) deve refletir delete no COFRE quando aplicavel.

## Comandos comuns
### Setup rapido (Windows)
```powershell
.\setup-windows.ps1
```

### Infra local
```powershell
docker-compose -f docker-compose.local.yml up -d
```

### Backend
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

### Frontend
```powershell
cd frontend
npm run dev
```

## Regras operacionais
- Registrar bug novo em `docs/BUGSREPORT.md` antes de corrigir.
- Atualizar status do bug na mesma entrega.
- Nao manter regras de persona em caminhos paralelos fora do COFRE.
