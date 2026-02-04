# 🤖 INTEGRAÇÃO WHATSAPP + IA VIVA

> **Data:** 2026-02-04  
> **Versão:** 1.0.0  
> **Status:** ✅ IMPLEMENTADO E TESTADO

---

## 🎯 VISÃO GERAL

Integração completa entre:
- **WhatsApp** (via Evolution API)
- **Frontend** (Next.js)
- **IA VIVA** (GLM-4 Z.AI)

A VIVA é a assistente virtual que atende automaticamente os clientes no WhatsApp, com personalidade profissional da FC Soluções Financeiras e RezetaBrasil.

---

## 🏗️ ARQUITETURA

```
┌─────────────────┐     HTTP      ┌──────────────────┐
│  Evolution API  │ ─────────────▶│   Webhook        │
│  (localhost:8080)│               │  /api/v1/webhook │
└─────────────────┘               └────────┬─────────┘
                                           │
                              ┌────────────▼────────────┐
                              │  EvolutionWebhookService │
                              └────────────┬────────────┘
                                           │
                              ┌────────────▼────────────┐
                              │    VivaIAService        │
                              │    (GLM-4)              │
                              └────────────┬────────────┘
                                           │
                              ┌────────────▼────────────┐
                              │   Salva no PostgreSQL   │
                              └────────────┬────────────┘
                                           │
                              ┌────────────▼────────────┐
                              │   Frontend React        │
                              │   /whatsapp/conversas   │
                              └─────────────────────────┘
```

---

## 📊 BANCO DE DADOS

### Tabelas Criadas

#### `whatsapp_conversas`
```sql
- id (UUID PK)
- numero_telefone (VARCHAR 20)
- nome_contato (VARCHAR 200)
- instance_name (VARCHAR 100)
- status (ativa|arquivada|aguardando)
- contexto_ia (JSONB)
- ultima_mensagem_em (TIMESTAMP)
- created_at, updated_at
```

#### `whatsapp_mensagens`
```sql
- id (UUID PK)
- conversa_id (UUID FK)
- tipo_origem (usuario|ia|sistema)
- conteudo (TEXT)
- message_id (VARCHAR 100)
- tipo_midia, url_midia
- lida, enviada
- created_at
```

---

## 🔌 ENDPOINTS

### Webhook (Evolution → Backend)
```
POST /api/v1/webhook/evolution
```

### API de Chat (Frontend)
```
GET  /api/v1/whatsapp-chat/conversas
GET  /api/v1/whatsapp-chat/conversas/{id}
GET  /api/v1/whatsapp-chat/conversas/{id}/mensagens
POST /api/v1/whatsapp-chat/conversas/{id}/arquivar
GET  /api/v1/whatsapp-chat/status
```

---

## 🤖 PERSONALIDADE VIVA

### Contexto Base
Você é VIVA, assistente virtual inteligente da FC Soluções Financeiras e RezetaBrasil.

### Características
- **Profissional, calorosa e eficiente**
- Conhece profundamente os serviços das empresas
- Fala de forma natural, como uma concierge experiente

### Empresas
| Empresa | Foco | Tom | Cores |
|---------|------|-----|-------|
| FC Soluções | PJ, empresarial | Profissional | Azul |
| RezetaBrasil | PF, crédito pessoal | Acessível | Verde |

---

## 🚀 COMO FUNCIONA

1. Cliente envia mensagem no WhatsApp
2. Evolution API chama webhook do backend
3. Backend salva mensagem no banco
4. VIVA (GLM-4) processa e gera resposta
5. Resposta é salva e exibida no frontend
6. (Opcional) Enviar resposta de volta ao WhatsApp

---

*Documentação completa disponível em docs/MUDANCAS_WHATSAPP_VIVA.md*
