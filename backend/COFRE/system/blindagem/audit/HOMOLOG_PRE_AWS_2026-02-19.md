# Homologacao Pre-AWS - Blindagem Final (2026-02-19)

## Skills acionadas nesta rodada
- coding-guidelines
- accessibility
- best-practices
- docs-writer
- playwright-skill (tentativa de smoke guiado; ambiente sem modulo local de runner)

## Provas tecnicas (gate de blindagem)

### 1) Backend - regressao critica
- Comando: `pytest backend/tests/test_viva_domain_intents.py backend/tests/test_whatsapp_lid_resolution.py -q`
- Resultado: `17 passed`.
- Cobertura chave: agenda NLU + resolucao WhatsApp `@lid`.

### 2) Frontend - consistencia de build
- Comando: `npm run type-check`
- Resultado: `OK`.
- Comando: `npm run build`
- Resultado: `OK` (Next 14.1.0, rotas geradas sem falha).
- Blindagem aplicada: `frontend/tsconfig.json` com `incremental=false` para eliminar quebra intermitente de `.next/types` stale.

### 3) Frontend - smoke de rotas
- Comando: `npm run smoke:routes`
- Resultado: todas as rotas principais `200`.
- Script adicionado: `frontend/scripts/smoke-routes.cjs`.
- Objetivo: detectar automaticamente erro de cache quebrado (`Cannot find module './*.js'`) no `next dev`.

### 4) Runtime operacional (Viviane/WhatsApp/COFRE)
- Prova API consolidada: `backend/COFRE/system/blindagem/audit/api-proof-2026-02-19.json`.
- Endpoints validados com `200`:
  - `/api/v1/auth/login`
  - `/api/v1/whatsapp/status`
  - `/api/v1/whatsapp-chat/status`
  - `/api/v1/viva/handoff`
  - `/api/v1/cofre/memories/status`
  - `/api/v1/viva/persona/status`
- Indicadores críticos observados:
  - WhatsApp conectado (`estado=open`).
  - Funil de conversas ativo (`whatsapp-chat/status`).
  - Handoff Viviane com itens enviados (`status=sent`).
  - Persona ancorada no COFRE (`strict_mode=true`, fallback inativo).

### 5) Acessibilidade (login)
- Resultado final login (`/`): score Lighthouse a11y `100`.
- Evidencia: `backend/COFRE/system/blindagem/audit/lighthouse-a11y-root-final.json`.

## Observacoes de estabilidade
- Aviso Docker Compose: atributo `version` obsoleto em `docker-compose.yml` (nao bloqueante).
- Lighthouse em Windows conclui auditoria e grava JSON, mas pode finalizar com erro de limpeza temporaria (`EPERM`), sem invalidar o arquivo final.

## Status para avancar AWS
- Estado atual: **Apto para pre-deploy AWS (staging)**.
- Recomendacao imediata antes do deploy final:
  1. Subir stack em staging Ubuntu.
  2. Rodar `smoke:routes` + checks API no staging.
  3. Validar webhook Evolution externo + handoff process-due em horario real.
