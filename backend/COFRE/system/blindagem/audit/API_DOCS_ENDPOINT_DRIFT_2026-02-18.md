# Auditoria - Drift de Endpoints (docs vs runtime)

Data: 2026-02-18  
Escopo: `docs/API.md` vs rotas reais do FastAPI (runtime)  
Evidencia de runtime: `docs/AUDIT/runtime-fastapi-routes.json`

## Objetivo

Eliminar endpoints "fora de contexto" (documentados mas inexistentes) e documentar endpoints reais que nao estavam no contrato oficial.

## Metodo

1. Extracao das rotas em runtime via introspeccao de `app.routes`.
2. Parse de headings do `docs/API.md` (linhas `### METHOD /path`) assumindo base `/api/v1` para rotas versionadas.
3. Comparacao por conjunto (metodo + path).

## Resultados (deltas)

### A) Endpoints presentes em `docs/API.md` mas ausentes no runtime

Esses endpoints estavam documentados como parte do dominio VIVA/memoria, mas nao existem mais no backend atual:

- `GET /api/v1/viva/memory/status`
- `GET /api/v1/viva/memory/search`
- `POST /api/v1/viva/memory/reindex`

Decisao: estes endpoints sao substituidos pelo dominio COFRE (fonte unica de memoria/registro).

### B) Endpoints presentes no runtime mas ausentes em `docs/API.md`

Esses endpoints existem no backend e precisam constar no contrato:

COFRE (memoria e sistema):
- `GET /api/v1/cofre/system/manifest`
- `GET /api/v1/cofre/system/schema-status`
- `GET /api/v1/cofre/memories/status`
- `GET /api/v1/cofre/memories/tables`
- `GET /api/v1/cofre/memories/{table_name}/tail`
- `POST /api/v1/cofre/memories/sync-db-tables`

VIVA (expansoes oficiais):
- `GET /api/v1/viva/persona/status`
- `GET /api/v1/viva/tts/status`
- `POST /api/v1/viva/chat/stream`

Campanhas (operacao/limpeza):
- `DELETE /api/v1/viva/campanhas/{campanha_id}`
- `POST /api/v1/viva/campanhas/reset-all`
- `POST /api/v1/viva/campanhas/reset-patterns`

Sistema (nao versionado):
- `GET /health` (healthcheck root)
- `GET /docs`, `GET /openapi.json`, `GET /redoc` (quando `DEBUG=true`)

## Correcoes aplicadas nesta rodada

1. `docs/API.md` atualizado:
   - base URL agora diferencia:
     - rotas versionadas: `/api/v1/*`
     - rotas de sistema: `/health`, `/docs`, `/openapi.json`, `/redoc`, `/`
   - memoria VIVA foi removida do contrato e substituida por endpoints COFRE.
   - endpoints reais ausentes foram adicionados (COFRE + VIVA stream/persona/tts + resets campanhas).
   - exemplo de senha `1234` removido (nao publicar credencial dev em doc institucional).

2. Backend recebeu alias de compatibilidade:
   - `GET /api/v1/health` agora responde igual a `GET /health` (para ferramentas e para manter consistencia com base URL).

## Proximo passo recomendado

- Congelar o contrato de endpoints canonicamente em `docs/API.md`.
- Quando remover/renomear endpoint no backend:
  - atualizar `docs/API.md`
  - adicionar nota de deprecacao por 1 rodada em `docs/SESSION.md`
  - registrar bug/decisao se houver impacto em front/automacoes.
