# SaaS Endpoints Catalog - Viviane

Data: 2026-02-21
Fonte: `docs/API.md`
Base URL padrao: `http://localhost:8000/api/v1`

## 1) Auth

- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`

## 2) Contratos

- `GET /contratos/templates`
- `GET /contratos/templates/{template_id}`
- `POST /contratos`
- `GET /contratos`
- `GET /contratos/{contrato_id}`
- `PUT /contratos/{contrato_id}`
- `DELETE /contratos/{contrato_id}`
- `GET /contratos/{contrato_id}/pdf`
- `POST /contratos/{contrato_id}/enviar`

## 3) Clientes

- `POST /clientes`
- `GET /clientes`
- `GET /clientes/{cliente_id}`
- `GET /clientes/documento/{documento}`
- `PUT /clientes/{cliente_id}`
- `DELETE /clientes/{cliente_id}`
- `GET /clientes/{cliente_id}/contratos`
- `GET /clientes/{cliente_id}/historico`
- `POST /clientes/sincronizar-contratos`
- `POST /clientes/deduplicar-documentos`

## 4) Agenda

- `POST /agenda`
- `GET /agenda`
- `GET /agenda/hoje`
- `GET /agenda/{evento_id}`
- `PUT /agenda/{evento_id}`
- `PATCH /agenda/{evento_id}/concluir`
- `DELETE /agenda/{evento_id}`

## 5) WhatsApp

- `GET /whatsapp/status`
- `POST /whatsapp/conectar`
- `POST /whatsapp/desconectar`
- `POST /whatsapp/enviar-texto`
- `POST /whatsapp/enviar-arquivo`

## 6) Webhook

- `POST /webhook/evolution`
- `GET /webhook/evolution`

## 7) WhatsApp Chat

- `GET /whatsapp-chat/conversas`
- `GET /whatsapp-chat/conversas/{conversa_id}`
- `GET /whatsapp-chat/conversas/{conversa_id}/mensagens`
- `POST /whatsapp-chat/conversas/{conversa_id}/arquivar`
- `GET /whatsapp-chat/status`

## 8) VIVA / IA

- `POST /viva/chat`
- `POST /viva/chat/stream`
- `GET /viva/chat/snapshot`
- `GET /viva/chat/sessions`
- `POST /viva/chat/session/new`
- `POST /viva/vision`
- `POST /viva/vision/upload`
- `POST /viva/audio/transcribe`
- `POST /viva/audio/speak`
- `POST /viva/image/generate`
- `POST /viva/video/generate`
- `GET /viva/video/result/{task_id}`
- `GET /viva/status`
- `GET /viva/capabilities`
- `GET /viva/modules/status`
- `GET /viva/persona/status`
- `GET /viva/tts/status`

## 9) Handoff VIVA -> VIVIANE

- `POST /viva/handoff/schedule`
- `GET /viva/handoff`
- `POST /viva/handoff/process-due`

## 10) Campanhas

- `POST /viva/campanhas`
- `GET /viva/campanhas`
- `GET /viva/campanhas/{campanha_id}`
- `DELETE /viva/campanhas/{campanha_id}`
- `POST /viva/campanhas/reset-all`
- `POST /viva/campanhas/reset-patterns`

## 11) COFRE

- `GET /cofre/system/manifest`
- `GET /cofre/system/schema-status`
- `GET /cofre/memories/status`
- `GET /cofre/memories/tables`
- `GET /cofre/memories/{table_name}/tail`
- `POST /cofre/memories/sync-db-tables`

## 12) Google Calendar

- `GET /google-calendar/connect-url`
- `GET /google-calendar/callback`
- `GET /google-calendar/status`
- `POST /google-calendar/disconnect`
- `POST /google-calendar/sync/agenda/{evento_id}`

## 13) Health

- `GET /health`
- `GET /api/v1/health`
- `GET /`

## Regra operacional para Viviane

- Executar pedidos em endpoint real quando houver dados minimos.
- Nao pedir confirmacao previa para executar.
- Fazer apenas 1 pergunta objetiva quando faltar dado obrigatorio.
- Nunca inventar endpoint, status ou resultado.
