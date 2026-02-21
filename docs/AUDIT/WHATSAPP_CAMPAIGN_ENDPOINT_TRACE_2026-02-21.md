# WHATSAPP_CAMPAIGN_ENDPOINT_TRACE_2026-02-21

## Objetivo
Mapeamento rastreavel dos endpoints de WhatsApp e Campanhas para diagnostico de perda de contexto e visibilidade no SaaS.

## WhatsApp - fluxo principal

1. Evolution webhook (entrada)
- Endpoint: `POST /api/v1/webhook/evolution`
- Handler: `backend/app/api/v1/webhook.py`
- Service: `backend/app/services/evolution_webhook_service.py`
- Regras criticas:
  - ignora outbound `fromMe=true`;
  - prioriza inbound em lote `data.messages[]`.

2. Status de conexao
- Endpoint: `GET /api/v1/whatsapp/status`
- Handler: `backend/app/api/v1/whatsapp.py`
- Service: `backend/app/services/whatsapp_service.py`

2.1 Resolucao `@lid` (entrega outbound)
- Service: `backend/app/services/whatsapp_service.py` (`_resolve_lid_number`)
- Fontes de candidato (em ordem de seguranca):
  - `context_preferred_number` plausivel;
  - `remoteJidAlt` e metadados equivalentes;
  - match unico por `profilePicUrl`;
  - similaridade de nome + proximidade temporal de chats (`findChats`).
- Regra de verdade:
  - nenhum candidato e usado sem validacao em `POST /chat/whatsappNumbers/{instance}`.
- Evidencia:
  - `backend/COFRE/system/blindagem/audit/WHATSAPP_LID_RESOLUTION_HARDENING_2026-02-21.md`.

3. CRM de conversas
- Endpoints:
  - `GET /api/v1/whatsapp-chat/status`
  - `GET /api/v1/whatsapp-chat/conversas?status=ativa|aguardando|arquivada`
  - `GET /api/v1/whatsapp-chat/conversas/{id}/mensagens`
- Handler: `backend/app/api/v1/whatsapp_chat.py`
- Front:
  - `frontend/src/app/whatsapp/conversas/page.tsx`
  - `frontend/src/app/(dashboard)/whatsapp/page.tsx`
- Regras criticas:
  - fallback visual para `arquivada` quando nao ha conversa aberta.

4. Persistencia
- Tabelas:
  - `whatsapp_conversas`
  - `whatsapp_mensagens`
- Models:
  - `backend/app/models/whatsapp_conversa.py`
- Espelho COFRE:
  - `backend/COFRE/memories/whatsapp_conversas/`
  - `backend/COFRE/memories/whatsapp_mensagens/`

## Campanhas - fluxo principal

1. Chat interno VIVA
- Endpoints:
  - `POST /api/v1/viva/chat`
  - `POST /api/v1/viva/chat/stream`
- Service:
  - `backend/app/services/viva_chat_orchestrator_service.py`
  - `backend/app/services/viva_chat_domain_service.py`
- Regras criticas:
  - follow-up de CTA em campanha pendente pode destravar geracao real;
  - guard de agenda nao deve atuar fora de operacao de agenda;
  - bloqueio de resposta textual fake de "campanha criada".

2. Historico de campanhas
- Endpoints:
  - `GET /api/v1/viva/campanhas`
  - `GET /api/v1/viva/campanhas/{id}`
  - `DELETE /api/v1/viva/campanhas/{id}`
- Service:
  - `backend/app/services/viva_campaign_repository_service.py`

3. Persistencia
- Tabela: `viva_campanhas`
- Espelho COFRE:
  - `backend/COFRE/memories/viva_campanhas/`

## Validacoes operacionais recomendadas

1. WhatsApp
- Confirmar status:
  - `GET /api/v1/whatsapp/status`
  - `GET /api/v1/whatsapp-chat/status`
- Confirmar ingestao:
  - logs backend com `POST /api/v1/webhook/evolution`.
- Confirmar resolucao `@lid`:
  - testes: `backend/tests/test_whatsapp_lid_resolution.py`.
  - resultado homologado da rodada: `33 passed` (suite alvo WhatsApp + campanha).

2. Campanhas
- Rodar conversa de briefing com CTA de follow-up.
- Confirmar persistencia real em:
  - `GET /api/v1/viva/campanhas`
  - UI `/campanhas`.
