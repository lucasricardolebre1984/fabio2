# Integração WhatsApp + IA VIVA

> **Data:** 2026-02-07  
> **Versão:** 1.2.0  
> **Status:** ⚠️ Parcial - estabilização em execução

---

## Visão Geral

Integração entre:
- WhatsApp (Evolution API)
- Backend (FastAPI)
- Frontend (Next.js)
- IA VIVA (Z.AI / OpenRouter / modo local)

A VIVA atende clientes via WhatsApp e também opera como chat interno no frontend (`/viva`).

---

## Arquitetura

```text
WhatsApp -> Evolution API -> Webhook (/api/v1/webhook/evolution)
                         -> EvolutionWebhookService
                         -> VivaIAService
                         -> PostgreSQL (logs/historico)
                         -> Frontend /whatsapp/conversas
```

Chat interno (web)
```text
Frontend /viva -> API /api/v1/viva/* -> VIVA (Z.AI/OpenRouter/local)
```

---

## Endpoints

Webhook (Evolution)
- POST `/api/v1/webhook/evolution`
- GET `/api/v1/webhook/evolution`

WhatsApp (Conexão/Envio)
- GET `/api/v1/whatsapp/status`
- POST `/api/v1/whatsapp/conectar`
- POST `/api/v1/whatsapp/desconectar`
- POST `/api/v1/whatsapp/enviar-texto`
- POST `/api/v1/whatsapp/enviar-arquivo`

Chat WhatsApp (Frontend)
- GET `/api/v1/whatsapp-chat/conversas`
- GET `/api/v1/whatsapp-chat/conversas/{id}`
- GET `/api/v1/whatsapp-chat/conversas/{id}/mensagens`
- POST `/api/v1/whatsapp-chat/conversas/{id}/arquivar`
- GET `/api/v1/whatsapp-chat/status`

Chat VIVA (Interno)
- POST `/api/v1/viva/chat`
- POST `/api/v1/viva/vision`
- POST `/api/v1/viva/vision/upload`
- POST `/api/v1/viva/audio/transcribe`
- POST `/api/v1/viva/image/generate`
- GET `/api/v1/viva/status`

---

## Diagnóstico Atual (2026-02-07)

- Evolution API está ativa em `http://localhost:8080`.
- Instância ativa detectada: `Teste` (estado `open`).
- Backend reporta desconectado em `/whatsapp/status` quando há divergência entre `WA_INSTANCE_NAME`/`EVOLUTION_API_KEY` e runtime da Evolution.
- Serviço backend de envio está defasado em relação ao contrato atual da Evolution v1.8.
- Webhook ainda não envia de fato a resposta da VIVA para o WhatsApp (somente persiste no banco).
- Endpoints `/whatsapp-chat/*` com erro 500 no estado atual.
- Frontend `/whatsapp` está em placeholder e `/whatsapp/conversas` tem inconsistência de token/base URL.

---

## Plano de Aplicação

1. Alinhamento de configuração
   - Padronizar `EVOLUTION_API_KEY`, `WA_INSTANCE_NAME` e webhook da instância.
2. Correção do backend WhatsApp
   - Ajustar leitura de status e payloads de envio para Evolution v1.8.
3. Correção de persistência/conversas
   - Resolver incompatibilidade ORM/schema que gera erro 500.
4. Conexão do frontend
   - Implementar painel real de conexão WhatsApp (`/whatsapp`).
   - Ajustar `/whatsapp/conversas` para API client padrão e `access_token`.
5. Validação ponta a ponta
   - Entrada no WhatsApp -> webhook -> resposta VIVA -> envio real -> histórico no frontend.

---

## Persistência

Tabelas principais
- `whatsapp_conversas`
- `whatsapp_mensagens`

---

## Referências

- `docs/STATUS.md`
- `docs/SESSION.md`
- `docs/DECISIONS.md`
- `docs/BUGSREPORT.md`

---

*Documento atualizado em: 2026-02-07*
