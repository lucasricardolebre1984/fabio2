# WHATSAPP_VISIBILITY_RUNTIME_GUARD_2026-02-21

## Contexto
- Painel `/whatsapp/conversas` podia ficar vazio com `mensagens_hoje > 0` quando nao havia conversa `ativa`.
- Respostas de erro tecnico de runtime (ex.: credencial OpenAI ausente) podiam vazar para o cliente no WhatsApp.

## Blindagem aplicada
1. UI central WhatsApp:
   - `frontend/src/app/whatsapp/conversas/page.tsx`
   - Estrategia de carga:
     - primeiro: `status=ativa` + `status=aguardando`
     - fallback: `status=arquivada` com aviso explicito.

2. Sanitizacao outbound no webhook:
   - `backend/app/services/evolution_webhook_service.py`
   - bloqueio de mensagens tecnicas de provedor antes de enviar ao cliente.

3. Isolamento padrao local x producao:
   - `docker-compose.prod.yml`
   - `docker-compose-prod.yml`
   - default `WA_INSTANCE_NAME` alterado para `fc-solucoes-local` quando env nao for fornecida.

## Validacao executada
- `next lint --file src/app/whatsapp/conversas/page.tsx` => OK
- `python -m py_compile backend/app/services/evolution_webhook_service.py backend/app/api/v1/whatsapp_chat.py` => OK
- EC2:
  - `GET /api/v1/whatsapp-chat/status` retorna `200`.
  - `GET /api/v1/whatsapp-chat/conversas?status=arquivada` retorna conversa existente.

## Rollback
```bash
git restore frontend/src/app/whatsapp/conversas/page.tsx
git restore backend/app/services/evolution_webhook_service.py
git restore docker-compose.prod.yml docker-compose-prod.yml
```
