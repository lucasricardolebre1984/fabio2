# Domain Identification and Grouping - SaaS FC Solucoes Financeiras

Data: 2026-02-16
Metodo: skill `domain-identification-grouping`
Escopo analisado: `backend/app`, `frontend/src/app`, `backend/COFRE`

## Resultado executivo

A base atual se organiza em 9 dominios logicos claros para evolucao service-based:

1. Identidade e Acesso
2. Contratos
3. Clientes (CRM)
4. Agenda e Calendar Sync
5. Campanhas e Midia
6. VIVA Core (orquestracao conversacional)
7. WhatsApp Operacional
8. COFRE (persona/skills/memoria)
9. Plataforma Compartilhada (infra/providers)

## Mapa de dominios -> componentes

### 1) Identidade e Acesso

- Backend:
  - `backend/app/api/v1/auth.py`
  - `backend/app/models/user.py`
  - `backend/app/core/security_stub.py` (dev-only workaround)
- Frontend:
  - login em `frontend/src/app/page.tsx`
  - auth client em `frontend/src/lib/api.ts`

Responsabilidade:
- autenticacao JWT, sessao de operador e protecao de rotas.

### 2) Contratos

- Backend:
  - `backend/app/api/v1/contratos.py`
  - `backend/app/services/contrato_service.py`
  - `backend/app/services/contrato_template_loader.py`
  - `backend/app/services/pdf_service_playwright.py`
  - `backend/app/models/contrato.py`
  - `backend/app/models/contrato_template.py`
- Frontend:
  - `frontend/src/app/(dashboard)/contratos/*`

Responsabilidade:
- templates, criacao, listagem, edicao, PDF e ciclo de contrato emitido.

### 3) Clientes (CRM)

- Backend:
  - `backend/app/api/v1/clientes.py`
  - `backend/app/services/cliente_service.py`
  - `backend/app/models/cliente.py`
- Frontend:
  - `frontend/src/app/(dashboard)/clientes/page.tsx`

Responsabilidade:
- cadastro de clientes, deduplicacao e relacionamento cliente<->contrato.

### 4) Agenda e Calendar Sync

- Backend:
  - `backend/app/api/v1/agenda.py`
  - `backend/app/api/v1/google_calendar.py`
  - `backend/app/services/agenda_service.py`
  - `backend/app/services/google_calendar_service.py`
  - `backend/app/models/agenda.py`
- Frontend:
  - `frontend/src/app/(dashboard)/agenda/page.tsx`

Responsabilidade:
- compromissos internos do SaaS e sincronizacao opcional com Google Calendar.

### 5) Campanhas e Midia

- Backend:
  - `backend/app/api/v1/viva_campaign_routes.py`
  - `backend/app/services/viva_campaign_repository_service.py`
  - `backend/app/services/openai_service.py` (image)
- Frontend:
  - `frontend/src/app/(dashboard)/campanhas/page.tsx`

Responsabilidade:
- geracao/listagem/exclusao de campanhas e ativos de midia.

### 6) VIVA Core (orquestracao conversacional)

- Backend:
  - `backend/app/api/v1/viva.py`
  - `backend/app/services/viva_chat_orchestrator_service.py`
  - `backend/app/services/viva_chat_session_service.py`
  - `backend/app/services/viva_agenda_nlu_service.py`
  - `backend/app/services/viva_concierge_service.py`
  - `backend/app/services/viva_agent_profile_service.py`
- Frontend:
  - `frontend/src/app/viva/page.tsx`

Responsabilidade:
- roteamento de intencao, execucao por skill/rota real e resposta da assistente.

### 7) WhatsApp Operacional

- Backend:
  - `backend/app/api/v1/whatsapp.py`
  - `backend/app/api/v1/whatsapp_chat.py`
  - `backend/app/api/v1/webhook.py`
  - `backend/app/services/whatsapp_service.py`
  - `backend/app/services/evolution_webhook_service.py`
  - `backend/app/models/whatsapp_conversa.py`

Responsabilidade:
- conexao Evolution, webhooks, historico e operacao de atendimento externo.

### 8) COFRE (persona/skills/memoria)

- Backend:
  - `backend/app/api/v1/cofre_memory_routes.py`
  - `backend/app/services/cofre_memory_service.py`
  - `backend/app/services/cofre_manifest_service.py`
  - `backend/app/services/cofre_schema_service.py`
  - `backend/app/services/viva_memory_service.py`
- Artefatos:
  - `backend/COFRE/persona-skills/*`
  - `backend/COFRE/memories/*`

Responsabilidade:
- fonte de verdade de persona, skills e memoria auditavel.

### 9) Plataforma Compartilhada (infra/providers)

- Backend:
  - `backend/app/config.py`
  - `backend/app/db/*`
  - `backend/app/services/viva_model_service.py`
  - `backend/app/services/openai_service.py`
  - `backend/app/services/minimax_tts_service.py`

Responsabilidade:
- configuracao, persistencia, provedores e suporte transversal.

## Fronteiras recomendadas (DDD-lite)

- `contracts-domain`: Contratos + templates + PDF
- `crm-domain`: Clientes
- `agenda-domain`: Agenda + Google Sync
- `campaign-domain`: Campanhas/midia
- `assistant-domain`: VIVA orquestrador/NLU/chat
- `messaging-domain`: WhatsApp externo
- `knowledge-domain`: COFRE/memoria/persona
- `platform-domain`: auth/infra/providers

## Inconsistencias detectadas

1. VIVA Core ainda concentra logica de varios dominios no mesmo orquestrador.
2. Agenda depende de NLU textual com alto custo de variação linguistica.
3. Contratos (modelos vs emitidos) ainda exigem padronizacao semantica adicional em prompts para evitar ambiguidade.

## Plano de refatoracao por namespace (incremental)

### Estado atual (exemplo)
- `app/services/viva_chat_orchestrator_service.py` mistura agenda, contratos, clientes, campanhas.

### Estado alvo
- `app/domains/assistant/orchestrator.py`
- `app/domains/agenda/application/query_service.py`
- `app/domains/contracts/application/query_service.py`
- `app/domains/campaigns/application/query_service.py`
- `app/domains/crm/application/query_service.py`

## Prioridade sugerida

1. Extrair query handlers de Agenda/Contratos do orquestrador VIVA.
2. Consolidar contrato semantico de intents por dominio (agenda, contratos, clientes, campanhas).
3. Publicar suite de testes por dominio (assistant-domain first).

## Veredito

O sistema ja possui fronteiras de negocio suficientes para operar com arquitetura por dominios.
A principal melhoria restante e reduzir o acoplamento da VIVA Core para cada dominio responder por suas proprias regras e consultas.
