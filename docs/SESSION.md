# SESSION - contexto da rodada atual

Data da rodada: 2026-02-21
Branch: main
Status: consolidacao final de homologacao local (WhatsApp/VIVA/Viviane) + ajuste cirurgico de layout de contratos com rollback institucional.

## Objetivo da rodada

- Validar e normalizar a pasta `docs` para refletir o estado real do SaaS.
- Separar documentacao ativa de documentacao legada.
- Reforcar COFRE como unica fonte institucional para persona, skills e memorias.

## Entregas desta rodada

- Criado indice canonico: `docs/README.md`
- Reescrito estado ativo: `docs/STATUS.md`
- Reescrita arquitetura ativa: `docs/ARCHITECTURE/OVERVIEW.md`
- Reescrito contexto do produto: `docs/CONTEXT.md`
- Reescrito runbook operacional: `docs/RUNBOOK.md`
- Criada auditoria documental: `docs/AUDIT/DOCS_AUDIT_2026-02-16.md`
- Criada auditoria de qualidade web: `docs/AUDIT/WEB_QUALITY_AUDIT_2026-02-16.md`
- Evidencia de Lighthouse login registrada em: `docs/AUDIT/lighthouse-login.json`
- Documentos legados removidos da estrutura ativa de `docs/`
- Correcao no chat VIVA para contratos:
  - modelos de contrato separados de contratos emitidos por cliente;
  - suporte a comando direto de continuidade (`listar`, `nomes`);
  - filtro por cliente em consulta de contratos emitidos.
- Correcao no NLU de agenda:
  - consulta passou a aceitar variacoes `liste agenda` e `lite agenda` na rota de agenda real.
- Refatoracao de estrutura por dominio:
  - criado `backend/app/services/viva_domain_query_router_service.py`;
  - orquestrador VIVA passou a delegar consultas de contratos/clientes/campanhas/servicos para esse router.
- Ajuste final de logo em contratos sem ampliar faixa azul:
  - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
  - `frontend/public/logo2-tight.png`
  - `frontend/src/lib/pdf.ts`
  - `backend/app/services/pdf_service_playwright.py`
  - `contratos/logo2-tight.png`
- Documentacao operacional para agentes:
  - `docs/CONTRATOS_LAYOUT_LOGO_MANUAL_AGENTES.md`
- Blindagem/rollback da rodada:
  - `backend/COFRE/system/blindagem/audit/CONTRATOS_LOGO_LAYOUT_2026-02-20.md`
  - `backend/COFRE/system/blindagem/rollback/rollback_contratos_logo_layout_20260220_131317_pre_fix_baseline.txt`
  - `backend/COFRE/system/blindagem/rollback/rollback_contratos_logo_layout_20260220_131317.patch`
- Correcao de paridade canonica no chat stream:
  - `backend/app/services/viva_chat_orchestrator_service.py`
  - `backend/tests/test_viva_chat.py` (teste `test_viva_chat_stream_delegates_to_canonical_flow`)
  - `backend/COFRE/system/blindagem/audit/VIVA_STREAM_CANONICAL_ORCHESTRATION_2026-02-21.md`
  - `docs/BUGSREPORT.md` (BUG-127)
- Correcao de follow-up deterministico em dominio clientes/contratos:
  - `backend/app/services/viva_domain_query_router_service.py`
  - `backend/app/services/assistant/intents/clientes.py`
  - `backend/app/services/assistant/intents/contratos.py`
  - `backend/tests/test_viva_domain_intents.py`
  - `backend/COFRE/system/blindagem/audit/VIVA_DOMAIN_FOLLOWUP_TRUTH_GUARD_2026-02-21.md`
  - `docs/BUGSREPORT.md` (BUG-128)
- Correcao de central WhatsApp + blindagem de erro outbound:
  - `frontend/src/app/whatsapp/conversas/page.tsx`
  - `backend/app/services/evolution_webhook_service.py`
  - `docker-compose.prod.yml`
  - `docker-compose-prod.yml`
  - `docs/BUGSREPORT.md` (BUG-129)

## Novos bugs abertos nesta auditoria

- BUG-116: vulnerabilidades criticas/altas no frontend (`next`, `axios`)
- BUG-117: `npm run type-check` quebrando por dependencia de `.next/types`
- BUG-118: suite backend falhando em auth/contratos/viva
- BUG-119: `security_stub` ativo no fluxo real de autenticacao
- BUG-120: CORS amplo no backend (`allow_methods=*`, `allow_headers=*`)

## Regra de historico

O historico tecnico antigo permanece preservado em arquivos de rollback e em documentos no VAULT.
Este arquivo passa a registrar apenas o contexto corrente de sessao.

Atualizado em: 2026-02-21
