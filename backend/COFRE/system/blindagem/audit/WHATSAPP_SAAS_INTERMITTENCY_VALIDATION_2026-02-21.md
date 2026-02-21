# WHATSAPP_SAAS_INTERMITTENCY_VALIDATION_2026-02-21

Data: 2026-02-21
Gate: BUG-133 (P0)
Escopo: validar relato de conversa ausente/sem resposta no SaaS mesmo com WhatsApp conectado.

## Baseline e rollback

- baseline: `backend/COFRE/system/blindagem/rollback/rollback_bug133_whatsapp_saas_conversas_20260221_133021_baseline.txt`
- patch: `backend/COFRE/system/blindagem/rollback/rollback_bug133_whatsapp_saas_conversas_20260221_133021.patch`

## Evidencias coletadas

1. Status operacional da integracao:
- `GET /api/v1/whatsapp/status` retornou `conectado=true`, `estado=open`, webhook configurado.

2. Conversas visiveis por API:
- `GET /api/v1/whatsapp-chat/conversas?status=ativa&limit=100` retornou 2 conversas ativas.

3. Banco (Ubuntu):
- `whatsapp_conversas`: 2 ativas, 2 arquivadas.
- `whatsapp_mensagens`: trafego usuario + ia ate `2026-02-21 16:16:48`.

4. Logs:
- Evolution: eventos `messages.upsert` com destino `http://backend:8000/api/v1/webhook/evolution`.
- Backend: `POST /api/v1/webhook/evolution` com `200 OK` recorrente.

## Veredito desta rodada

- Nao houve reproducao continua de falha estrutural no pipeline inbound/outbound.
- Bug mantido como `Em validacao` por intermitencia reportada em homologacao.

## Proximo passo tecnico (para fechamento definitivo)

1. Capturar um caso com horario exato + numero do contato que nao respondeu.
2. Traçar o mesmo `message_id` fim-a-fim:
   - Evolution log -> backend webhook -> insert em `whatsapp_mensagens` -> tentativa outbound -> ack/status.
3. Se houver quebra, isolar em teste de regressao automatizado no backend.
