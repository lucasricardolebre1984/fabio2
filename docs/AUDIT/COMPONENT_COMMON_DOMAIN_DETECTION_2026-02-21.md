# COMPONENT_COMMON_DOMAIN_DETECTION_2026-02-21

## Escopo
Analise de dominio comum (duplicacao funcional) nos modulos afetados por regressao de WhatsApp e Campanhas.

## Componentes analisados
- `backend/app/services/evolution_webhook_service.py`
- `backend/app/services/whatsapp_service.py`
- `backend/app/services/viva_chat_orchestrator_service.py`
- `backend/app/services/viva_chat_domain_service.py`
- `backend/app/services/viva_chat_runtime_helpers_service.py`
- `backend/app/services/viva_domain_query_router_service.py`
- `frontend/src/app/(dashboard)/whatsapp/page.tsx`
- `frontend/src/app/whatsapp/conversas/page.tsx`

## Funcionalidades comuns detectadas

1. Classificacao de intencao conversacional
- Componentes:
  - `viva_chat_orchestrator_service`
  - `viva_domain_query_router_service`
  - `assistant/intents/*`
- Observacao:
  - ja existe consolidacao parcial em `assistant/intents/*`;
  - risco residual de drift quando guardas extras sao implementadas direto no orquestrador.

2. Guardas anti-resposta falsa (truth guards)
- Componentes:
  - `viva_chat_orchestrator_service`
  - `viva_chat_runtime_helpers_service`
- Observacao:
  - camada dupla e desejavel (orquestracao + sanitizacao de runtime);
  - recomendacao: manter regra de negocio no orquestrador e usar runtime apenas como rede de seguranca textual.

3. Carregamento de conversas WhatsApp no frontend
- Componentes:
  - `frontend/src/app/(dashboard)/whatsapp/page.tsx`
  - `frontend/src/app/whatsapp/conversas/page.tsx`
- Observacao:
  - ambos fazem combinacao `ativa/aguardando` com fallback `arquivada`;
  - oportunidade futura: extrair hook comum (`useWhatsappConversations`) para reduzir duplicacao.

## Consolidacoes aplicadas nesta rodada
- `is_campaign_count_intent` endurecida para evitar falso positivo em briefing de campanha.
- Follow-up de campanha pendente consolidado em helper dedicado no orquestrador.
- Sanitizacao de "campanha criada" sem execucao real centralizada em runtime helper.
- Parser de lote WhatsApp no webhook priorizando inbound real (`fromMe=false`).

## Risco residual
- Ainda ha pontos de regra de dominio dispersos entre:
  - `viva_chat_domain_service` (NLU + prompt),
  - `viva_chat_orchestrator_service` (execucao),
  - `viva_domain_query_router_service` (consultas de dominio).
- Recomendacao: evoluir para "Domain Policy Layer" unica para regras de decisao (sem misturar com montagem de prompt).
