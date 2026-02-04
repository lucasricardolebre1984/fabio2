# 🤖 INTEGRAÇÃO WHATSAPP + IA VIVA

> **Data:** 2026-02-04  
> **Versão:** 1.0.0  
> **Status:** ✅ Implementado

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
                              │   Envia resposta        │
                              │   Evolution API         │
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
Recebe eventos do Evolution API (mensagens, status).

### API de Chat (Frontend)
```
GET  /api/v1/whatsapp-chat/conversas           # Lista conversas
GET  /api/v1/whatsapp-chat/conversas/{id}      # Detalhes conversa
GET  /api/v1/whatsapp-chat/conversas/{id}/mensagens  # Mensagens
POST /api/v1/whatsapp-chat/conversas/{id}/arquivar   # Arquivar
GET  /api/v1/whatsapp-chat/status              # Estatísticas
```

---

## 🤖 PERSONALIDADE VIVA

### Contexto Base
```
Você é VIVA, a assistente virtual inteligente da FC Soluções Financeiras e RezetaBrasil.
```

### Características
- **Profissional, calorosa e eficiente**
- Conhece profundamente os serviços das empresas
- Fala de forma natural, como uma concierge experiente
- Oferece ajuda antes de direcionar

### Empresas
| Empresa | Foco | Tom | Cores |
|---------|------|-----|-------|
| FC Soluções | PJ, empresarial | Profissional, corporativo | Azul |
| RezetaBrasil | PF, crédito pessoal | Acessível, promocional | Verde |

### Serviços
1. Informações sobre produtos/serviços
2. Agendar reuniões/consultas
3. Enviar contratos/documentos
4. Gerar imagens de campanha
5. Responder dúvidas frequentes
6. Direcionar para atendimento humano

---

## ⚙️ CONFIGURAÇÃO

### 1. Configurar Webhook no Evolution Manager

Acesse: http://localhost:8080/manager/Teste

**Configurações → Webhook:**
```
URL: http://host.docker.internal:8000/api/v1/webhook/evolution
Eventos: messages.upsert, connection.update
```

> **Nota:** Use `host.docker.internal` se o Evolution estiver no Docker e o backend rodando local.

### 2. Variáveis de Ambiente (.env)
```bash
# Já configurado
ZAI_API_KEY=a3d9a1dee82f4291884ad714ccda54a0.25dP5AZf6QxC1Nmw
ZAI_MODEL=glm-4
```

### 3. Executar Migration
```bash
cd backend/migrations
psql -U fabio2_user -d fabio2 -f create_whatsapp_chat.sql
```

Ou via Docker:
```bash
docker exec -i fabio2-postgres psql -U fabio2_user -d fabio2 < backend/migrations/create_whatsapp_chat.sql
```

---

## 🚀 FLUXO DE FUNCIONAMENTO

### 1. Cliente envia mensagem
```
Cliente → WhatsApp → Evolution API → Webhook (POST /webhook/evolution)
```

### 2. Backend processa
```
WebhookService:
  1. Extrai número e texto
  2. Busca/cria conversa no DB
  3. Salva mensagem do usuário
  4. Chama VivaIAService
```

### 3. IA responde
```
VivaIAService:
  1. Busca histórico (últimas 10 msgs)
  2. Monta contexto com system prompt
  3. Chama GLM-4
  4. Retorna resposta
```

### 4. Envia resposta
```
EvolutionService:
  1. Envia mensagem via Evolution API
  2. Salva no DB
  3. Atualiza timestamp
```

---

## 🎨 FRONTEND

### Nova Página
```
URL: http://localhost:3000/whatsapp/conversas
```

### Features
- ✅ Lista de conversas ativas
- ✅ Preview das mensagens em tempo real
- ✅ Interface tipo WhatsApp Web
- ✅ Distinção visual: Cliente (branco) vs VIVA (azul)
- ✅ Estatísticas (conversas ativas, mensagens hoje)
- ✅ Arquivar conversas
- ✅ Atualização automática (10s)

---

## 📁 ARQUIVOS CRIADOS/ALTERADOS

### Backend
```
backend/app/models/whatsapp_conversa.py      # Novo
backend/app/services/viva_ia_service.py      # Novo
backend/app/services/evolution_webhook_service.py  # Novo
backend/app/api/v1/webhook.py                # Novo
backend/app/api/v1/whatsapp_chat.py          # Novo
backend/app/schemas/whatsapp_chat.py         # Novo
backend/app/models/__init__.py               # Atualizado
backend/app/api/router.py                    # Atualizado
backend/migrations/create_whatsapp_chat.sql  # Novo
```

### Frontend
```
frontend/src/app/whatsapp/conversas/page.tsx # Novo
frontend/src/components/layout/Sidebar.tsx    # Atualizado
```

---

## 🧪 TESTE

### 1. Enviar mensagem de teste (curl)
```bash
curl -X POST http://localhost:8000/api/v1/webhook/evolution \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": {"instanceName": "Teste"},
    "data": {
      "message": {
        "key": {"remoteJid": "5511999999999@s.whatsapp.net", "id": "test123"},
        "conversation": "Olá, gostaria de saber sobre crédito"
      }
    }
  }'
```

### 2. Verificar no frontend
```
Acesse: http://localhost:3000/whatsapp/conversas
```

### 3. Testar com WhatsApp real
1. Conecte seu WhatsApp no Evolution Manager
2. Envie mensagem para o número conectado
3. A VIVA deve responder automaticamente!

---

## 🔮 PRÓXIMOS PASSOS

- [ ] Enviar mensagem manual pelo frontend
- [ ] Upload de imagem no chat
- [ ] Integração com agenda (marcar reuniões)
- [ ] Integração com contratos (enviar documentos)
- [ ] Treinar VIVA com mais contexto específico
- [ ] Dashboard de métricas de atendimento

---

*Documentação criada por Automania-AI*  
*Data: 2026-02-04*
