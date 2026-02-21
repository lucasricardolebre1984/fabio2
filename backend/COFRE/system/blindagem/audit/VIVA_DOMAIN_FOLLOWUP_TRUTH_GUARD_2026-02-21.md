# VIVA Domain Follow-up Truth Guard (2026-02-21)

## Escopo
- Fluxo de consultas de clientes/contratos no chat VIVA.
- Inbound de webhook Evolution para WhatsApp.

## Problema observado
- Follow-up curto (`para Lucas`, `quero`, `com numero`, `clientes cadastrados`) escapava do roteador deterministico e podia cair em resposta livre do modelo.
- Resultado: contratos inventados e perguntas de exportacao fora de contexto.
- Em WhatsApp, payloads no formato `data.messages[]` podiam ser ignorados na extracao da mensagem.

## Causa raiz
1. Extracao de nome de cliente em contratos nao aceitava `para <nome>`.
2. Confirmacoes curtas nao eram reconhecidas como continuidade canonica.
3. Faltava fallback de contexto para cliente no fluxo de contratos por cliente.
4. Intents de clientes nao cobriam variacoes comuns (`clientes na base`, `clientes cadastrados`).
5. Extrator de webhook nao cobria o formato `messages[]`.

## Correcao aplicada
- `backend/app/services/assistant/intents/contratos.py`
  - suporte a `para/pro/pra <nome>`.
- `backend/app/services/viva_domain_query_router_service.py`
  - confirmacoes curtas ampliadas;
  - resolucao de cliente por contexto recente;
  - follow-up pendente de nome de cliente;
  - contagem direta de clientes.
- `backend/app/services/assistant/intents/clientes.py`
  - intents ampliadas para `cadastrados`/`base`.
- `backend/app/services/evolution_webhook_service.py`
  - parse de `data.messages[]`.
- `backend/app/services/whatsapp_service.py`
  - valida eventos minimos do webhook antes de marcar configuracao como pronta.

## Testes de regressao
- `backend/tests/test_viva_domain_intents.py`
  - follow-up `para Lucas` apos prompt pendente de cliente;
  - follow-up `com numero` com cliente inferido por contexto;
  - contagem de clientes.
- `backend/tests/test_evolution_webhook_lid_resolution.py`
  - parse de `messages[]`.
- `backend/tests/test_whatsapp_lid_resolution.py`
  - validacao de eventos minimos de webhook.

## Resultado esperado
- Consultas de contratos/clientes voltam a responder com fonte real do sistema sem inventar itens.
- Fluxo de pergunta direta permanece direto no chat, sem desvio para exportacao nao solicitada.
- Webhook inbound fica resiliente a formato comum de payload da Evolution.
