# ARQUITETURA - Visão Geral

> **Projeto:** FC Soluções Financeiras SaaS  
> **Versão:** 1.0.0  
> **Data:** 2026-02-05

---

## Visão Macro

```
Cliente (Browser)
  ↓ HTTPS
Frontend (Next.js 14)
  ↓ JSON/REST
Backend (FastAPI)
  ↓ SQL
PostgreSQL
  ↔ Redis (cache/filas)
  ↔ Evolution API (WhatsApp)
```

---

## Componentes Principais

Frontend
- Next.js 14 (App Router)
- UI institucional e módulo Chat IA VIVA
- Rotas protegidas com JWT

Backend
- FastAPI com rotas em `/api/v1`
- Serviços de contratos, clientes, agenda e WhatsApp
- Serviço VIVA (chat interno e integração WA)

Banco
- PostgreSQL 15
- Redis 7 (cache e filas)

Integrações
- Evolution API (WhatsApp)
- OpenAI / modo local (VIVA)

---

## Fluxos Principais

Contratos
1. Usuário cria contrato pelo frontend
2. Backend valida dados, calcula extenso e salva
3. Preview e geração de PDF via `window.print()` no frontend

PDF (Browser Print)
1. Frontend monta HTML do contrato
2. Abre nova janela e chama `window.print()`
3. Usuário salva como PDF

VIVA Chat (Web)
1. Usuário abre `/viva`
2. Envia mensagem e opcionalmente anexo
3. Backend usa OpenRouter ou modo local
4. Resposta aparece no chat

WhatsApp + VIVA
1. Cliente envia mensagem no WhatsApp
2. Evolution API chama webhook
3. Backend grava conversa e gera resposta
4. Resposta fica disponível no frontend de conversas

---

## Rotas do Frontend

- `/` login
- `/viva` chat interno VIVA
- `/contratos` menu de templates
- `/contratos/novo` criação
- `/contratos/lista` listagem
- `/contratos/[id]` visualização
- `/contratos/[id]/editar` edição
- `/clientes` cadastro e histórico
- `/agenda` compromissos
- `/whatsapp` painel WhatsApp
- `/whatsapp/conversas` chat WhatsApp (VIVA)
- `/chat` redireciona para conversas WhatsApp

---

## Serviços Internos (Backend)

- `contrato_service.py` geração e regras de contratos
- `cliente_service.py` cadastro e histórico
- `agenda_service.py` compromissos
- `whatsapp_service.py` integração Evolution API
- `evolution_webhook_service.py` processamento webhook
- `viva_ia_service.py` VIVA para WhatsApp
- `viva_local_service.py` VIVA local (sem API)
- `openai_service.py` provedor OpenAI institucional
- `viva_model_service.py` roteamento padrao da VIVA

---

## Templates de Contrato

Pasta: `contratos/templates`
- `bacen.json`
- `bacen-v2.json`

Os templates definem campos, seções e cláusulas do contrato.

---

## Observações Operacionais

- Autenticação por JWT
- PDF oficial via impressão no navegador
- VIVA chat com menu lateral de prompts
- Áudio no chat VIVA marcado como não operacional

---

*Documento atualizado em: 2026-02-05*
