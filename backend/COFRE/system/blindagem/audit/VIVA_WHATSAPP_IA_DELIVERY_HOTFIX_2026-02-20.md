# VIVA + WhatsApp Delivery Hotfix (2026-02-20)

## Escopo

- Stabilizar resposta da VIVA em `/api/v1/viva/chat/stream`.
- Evitar perda de entrega WhatsApp em eventos com `remoteJid=@lid`.
- Manter contratos/clientes/agenda intactos.

## Causa raiz consolidada

1. Stream VIVA retornava erros OpenAI como `content` normal.
- Resultado: frontend entendia stream como sucesso e nao executava fallback para `/api/v1/viva/chat`.

2. Modelos `gpt-5*` podem rejeitar `temperature` customizada no `chat/completions`.
- Resultado: erro 400 recorrente no stream (`unsupported_value`).

3. Entrega WhatsApp com `@lid` podia seguir sem numero real resolvido.
- Resultado: envio para destino nao entregavel, fila sem saneamento de origem.

## Correcoes aplicadas

### IA (OpenAI + stream)

- `backend/app/services/openai_service.py`
  - Adicionado `_supports_optional_chat_params()`.
  - Para modelos `gpt-5*`, nao envia parametros opcionais (`temperature`, `max_completion_tokens`) no `chat/completions`.
  - `chat_stream()` agora faz fallback backend para `chat()` (nao-streaming) quando stream falha.

- `backend/app/services/viva_chat_orchestrator_service.py`
  - Stream agora detecta chunk de erro (`erro`/`error`) e emite evento SSE `{ "error": ... }`.
  - Evita finalizar stream com resposta vazia.

### WhatsApp (Evolution / @lid)

- `backend/app/services/whatsapp_service.py`
  - Em `send_text()`, se destino permanece `@lid` sem resolucao real, bloqueia envio e retorna:
    - `sucesso=false`
    - `erro_codigo=lid_unresolved`

- `backend/app/services/evolution_webhook_service.py`
  - Adicionado `_extract_phone_from_event()` para captar numero real em campos `sender/participant` do evento.
  - `resolved_whatsapp_number` agora pode ser preenchido por `event_sender`.
  - Em envio de resposta:
    - se destino for `@lid` e existir numero resolvido, usa numero resolvido.
  - Em falha `lid_unresolved`, move para fila pendente com `needs_manual_bind=true`.
  - No flush da fila, substitui destino `@lid` por numero resolvido quando disponivel.

## Validacao recomendada na EC2

1. Rebuild/restart backend+nginx:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build backend nginx
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --no-deps --force-recreate nginx
```

2. Health:

```bash
curl -sS https://fabio.automaniaai.com.br/health
```

3. IA VIVA:

- Abrir `/viva`, enviar `oi`.
- Esperado: sem erro `Unsupported value: temperature ...` e sem bolha travada.

4. WhatsApp:

- Enviar mensagem do celular para a instância conectada.
- Esperado: conversa aparece em `/whatsapp/conversas` e resposta chega no celular.

## Arquivos alterados

- `backend/app/services/openai_service.py`
- `backend/app/services/viva_chat_orchestrator_service.py`
- `backend/app/services/whatsapp_service.py`
- `backend/app/services/evolution_webhook_service.py`

