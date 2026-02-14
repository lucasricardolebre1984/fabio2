# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview
SaaS de gestão de contratos para FC Soluções Financeiras, com backend FastAPI e frontend Next.js. Principais módulos de negócio: contratos (templates e renderização), clientes, agenda e integração WhatsApp (Evolution API).

## High-level architecture
- Backend em `backend/app` (FastAPI): rotas em `api/`, regras/serviços em `services/`, modelos SQLAlchemy em `models/`, schemas Pydantic em `schemas/`, infra/core em `core/` e `db/`.
- Frontend em `frontend/src` (Next.js App Router): páginas em `app/`, UI compartilhada em `components/`, utilitários em `lib/` e estado em `stores/`.
- Templates de contratos ficam em `contratos/templates/` (JSON).
- Documentação “fonte da verdade” no diretório `docs/` (arquitetura, decisões e playbooks).

## Common commands
### Quick start (Windows)
```powershell
.\setup-windows.ps1
```

### Local infra (Docker)
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

### Tests / lint
Não há comandos de testes ou lint documentados no README/AGENTS atuais. Verifique `package.json` no frontend e instruções em `SETUP.md` antes de executar testes ou lint.

## Important docs to read first
- `docs/ARCHITECTURE/OVERVIEW.md` (visão de arquitetura)
- `docs/DECISIONS.md` (decisões arquiteturais)
- `docs/FOUNDATION/UX_UI_STANDARDS.md` (design system)
- `docs/CONTRATOS/PLAYBOOK_MODELOS_MD.md` (processo oficial para novos modelos `.md`)
- `docs/BUGSREPORT.md` (bugs conhecidos e regra institucional)
- `docs/SESSION.md` (contexto de sessão)

## Operational rules from existing docs
- Regra institucional de bugs: registrar bug novo em `docs/BUGSREPORT.md` antes de corrigir e atualizar status na mesma entrega.
- Workarounds ativos em dev:
  - `backend/app/core/security_stub.py`: aceita senha `1234` para testes locais.
  - `backend/app/services/pdf_service_stub.py`: retorna JSON em vez de PDF (aguardando GTK+).
