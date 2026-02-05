# 🤖 Integração WhatsApp + IA VIVA

> **Data:** 2026-02-05  
> **Versão:** 1.1.0  
> **Status:** ✅ Implementado e testado

---

## Visão Geral

Integração entre:
- WhatsApp (Evolution API)
- Backend (FastAPI)
- Frontend (Next.js)
- IA VIVA (Z.AI / OpenRouter / modo local)

A VIVA atende automaticamente clientes via WhatsApp e também opera como chat interno no frontend (`/viva`).

---

## Arquitetura

```
WhatsApp → Evolution API → Webhook (/api/v1/webhook/evolution)
                        ↓
             EvolutionWebhookService
                        ↓
                  VivaIAService
                        ↓
                 PostgreSQL (logs)
                        ↓
             Frontend /whatsapp/conversas
```

Chat interno (web)
```
Frontend /viva → API /api/v1/viva/* → VIVA (Z.AI/OpenRouter/local)
```

---

## Endpoints

Webhook (Evolution)
- POST `/api/v1/webhook/evolution`
- GET `/api/v1/webhook/evolution`

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

## Modelos Z.AI (Configuração Oficial)

- Chat: `GLM-4.7`
- Visão: `GLM-4.6V`
- Imagem: `GLM-Image`
- Áudio: `GLM-ASR-2512`
- Vídeo: `CogVideoX-3`

A configuração é feita via `.env` no backend. Não expor chaves em documentação.

---

## Status Operacional (Validação Manual)

- Chat: OK
- Visão: OK (upload + prompt)
- Imagem: OK (geração/edição)
- Áudio: NÃO funciona (botão)

---

## Persistência

Tabelas principais
- `whatsapp_conversas`
- `whatsapp_mensagens`

As conversas ficam registradas no banco e exibidas no painel `/whatsapp/conversas`.

---

## Observações

- O chat interno usa OpenRouter quando configurado, senão modo local.
- O WhatsApp usa `VivaIAService` para gerar respostas automáticas.
- O envio real de resposta ao WhatsApp deve ser ativado conforme evolução do fluxo.

---

*Documento atualizado em: 2026-02-05*
