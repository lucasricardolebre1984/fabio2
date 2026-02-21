# WhatsApp Webhook + DB Pool Guard (2026-02-21)

## Escopo

- Restaurar entrega WhatsApp no SaaS quando instancia estiver conectada, mas sem eventos no backend.
- Eliminar falha intermitente da VIVA (`QueuePool timeout`) no `/api/v1/viva/chat/stream`.
- Preservar modulos ja homologados (contratos, clientes, agenda).

## Causa raiz consolidada

1. **Webhook Evolution ausente (`null`)**
- Instancia `fc-solucoes` estava `open`, mas sem configuracao de webhook.
- Resultado: mensagens recebidas/enviadas nao chegavam ao backend (`/api/v1/webhook/evolution`), logo conversas ficavam vazias no SaaS.

2. **DDL concorrente em runtime no chat VIVA**
- `ensure_chat_tables()` executava `CREATE TABLE/INDEX IF NOT EXISTS` a cada request.
- Em streaming concorrente, isso gerou lock em relacao e fila de conexoes (`sqlalchemy.exc.TimeoutError: QueuePool limit ...`).
- Resultado: IA travava/intermitia mesmo com OpenAI funcional.

## Correcoes aplicadas

### 1) Blindagem do bootstrap de tabelas VIVA

- `backend/app/services/viva_chat_session_service.py`
  - Adicionado lock assíncrono global e flag de inicializacao:
    - `_chat_tables_lock`
    - `_chat_tables_ready`
  - `ensure_chat_tables()` agora executa DDL **uma vez por processo**, com commit/rollback controlado.
  - Remove lock tempestivo por request e evita saturacao da pool.

### 2) Auto-healing de webhook Evolution

- `backend/app/services/whatsapp_service.py`
  - Adicionados eventos canonicos de webhook (`DEFAULT_WEBHOOK_EVENTS`).
  - Adicionada resolucao de URL alvo via `WEBHOOK_URL` ou fallback institucional:
    - `http://backend:8000/api/v1/webhook/evolution`
  - Novo `_ensure_instance_webhook()`:
    - valida webhook atual (`/webhook/find/{instance}`);
    - aplica webhook (`/webhook/set/{instance}`) se ausente/incorreto.
  - `get_status()` e `connect()` agora garantem webhook automaticamente quando a instancia estiver `open`.

## Validacao operacional executada

1. **Git/Deploy**
- Commit hotfix de IA/WhatsApp publicado e aplicado na EC2.

2. **Infra**
- `health` e `evolution` respondendo no dominio.

3. **Evolution**
- `fetchInstances` retorna `fc-solucoes` com `connectionStatus=open`.
- `webhook/find/fc-solucoes` passou de `null` para objeto valido com URL interna do backend.

4. **OpenAI**
- `chat()` e `chat_stream()` testados via backend container, ambos respondendo.

## Arquivos alterados

- `backend/app/services/viva_chat_session_service.py`
- `backend/app/services/whatsapp_service.py`

