# BLINDAGEM - Indice Canonico (COFRE)

Atualizado em: 2026-02-20

Este arquivo centraliza os artefatos institucionais de blindagem para homologacao.

## Auditorias
- `backend/COFRE/system/blindagem/audit/API_DOCS_ENDPOINT_DRIFT_2026-02-18.md`
- `backend/COFRE/system/blindagem/audit/DOCS_AUDIT_2026-02-16.md`
- `backend/COFRE/system/blindagem/audit/DOMAIN_GROUPING_2026-02-16.md`
- `backend/COFRE/system/blindagem/audit/lighthouse-agenda-route.json`
- `backend/COFRE/system/blindagem/audit/lighthouse-a11y-agenda.json`
- `backend/COFRE/system/blindagem/audit/lighthouse-a11y-root.json`
- `backend/COFRE/system/blindagem/audit/lighthouse-a11y-root-after.json`
- `backend/COFRE/system/blindagem/audit/lighthouse-a11y-root-final.json`
- `backend/COFRE/system/blindagem/audit/lighthouse-a11y-viva.json`
- `backend/COFRE/system/blindagem/audit/lighthouse-a11y-whatsapp.json`
- `backend/COFRE/system/blindagem/audit/lighthouse-a11y-whatsapp-conversas.json`
- `backend/COFRE/system/blindagem/audit/lighthouse-login.json`
- `backend/COFRE/system/blindagem/audit/menu-endpoint-matrix.json`
- `backend/COFRE/system/blindagem/audit/menu-endpoint-matrix.md`
- `backend/COFRE/system/blindagem/audit/runtime-fastapi-routes.json`
- `backend/COFRE/system/blindagem/audit/WEB_QUALITY_AUDIT_2026-02-16.md`
- `backend/COFRE/system/blindagem/audit/A11Y_VIVIANE_STATUS_2026-02-19.md`
- `backend/COFRE/system/blindagem/audit/api-proof-2026-02-19.json`
- `backend/COFRE/system/blindagem/audit/docker-compose.resolved.yml`
- `backend/COFRE/system/blindagem/audit/HOMOLOG_PRE_AWS_2026-02-19.md`
- `backend/COFRE/system/blindagem/audit/VIVIANE_HUMANIZATION_2026-02-19.md`
- `backend/COFRE/system/blindagem/audit/VIVIANE_PERSONA_NATURAL_PATCH_2026-02-19.md`
- `backend/COFRE/system/blindagem/audit/COFRE_DB_FOLDER_MAP_2026-02-20.md`
- `backend/COFRE/system/blindagem/audit/COFRE_MEMORY_STATUS_2026-02-20.md`
- `backend/COFRE/system/blindagem/audit/WHATSAPP_LID_DELIVERY_BUG_2026-02-20.md`
- `backend/COFRE/system/blindagem/audit/EVOLUTION_LID_FIX_2026-02-20.md`
- `backend/COFRE/system/blindagem/audit/PERSONA_VIVIANE_SCOPE_2026-02-20.md`

## Rollbacks
- `backend/COFRE/system/blindagem/rollback/rollback_gate2_cca7e3d.patch`
- `backend/COFRE/system/blindagem/rollback/rollback_gate_layout_viva_20260219_135831.patch`
- `backend/COFRE/system/blindagem/rollback/rollback_whatsapp_lid_guard_20260219_155732.patch`
- `backend/COFRE/system/blindagem/rollback/rollback_viviane_persona_natural_20260219_181200.patch`

## Regra
- Novos relatorios de auditoria devem entrar em `backend/COFRE/system/blindagem/audit/`.
- Novos patches de rollback devem entrar em `backend/COFRE/system/blindagem/rollback/`.
- Nao manter artefatos de blindagem fora do COFRE.
