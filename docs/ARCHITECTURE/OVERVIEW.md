# ARQUITETURA - Visao Geral

> **Projeto:** FC Solucoes Financeiras SaaS  
> **Versao:** 1.1.0  
> **Data:** 2026-02-10

---

## Visao Macro

```
Cliente (Browser)
  -> HTTPS
Frontend (Next.js 14)
  -> JSON/REST
Backend (FastAPI)
  -> SQL
PostgreSQL
  <-> Redis (cache/filas)
  <-> Evolution API (WhatsApp)
```

---

## Dominios de Persona (oficial)

- VIVA: concierge interna do Fabio no SaaS (`/viva`, `/api/v1/viva/*`).
- Viviane: secretaria humana/comercial no atendimento externo WhatsApp (webhook + conversas).

Regra de arquitetura:
- persona interna e externa sao separadas por dominio de rota e contexto de negocio;
- nao compartilhar cadeia de prompts file-based entre os dois dominios.

---

## Prompt Mestre (fonte ativa)

- Prompt mestre da VIVA interna: `backend/app/services/viva_concierge_service.py`.
- Montagem das mensagens do chat: `backend/app/api/v1/viva.py` (`_build_viva_concierge_messages`).
- Frontend nao injeta mais prompt por arquivo no payload de chat.

Observacao:
- `docs/PROMPTS/GODMOD.md` e `docs/PROMPTS/PROJETISTA.md` permanecem como documentacao/protocolo, nao como prompt runtime do chat interno.

---

## Memoria Atual (runtime)

Fluxo atual do chat VIVA:
1. frontend envia mensagem para `/api/v1/viva/chat`;
2. backend persiste mensagem;
3. backend recarrega snapshot da sessao no banco;
4. contexto efetivo e reconstruido server-side;
5. modelo responde com base no contexto reconstruido.

Arquivos-chave:
- `backend/app/api/v1/viva.py` (sessao, snapshot, reconstrucao de contexto);
- `frontend/src/app/viva/page.tsx` (envio de mensagem e `session_id`).

Status:
- memoria de sessao e continuidade operacional estao ativas;
- camada vetorial RAG de longo prazo ainda pendente (BUG-058 ativo).

---

## Fluxos Principais

Contratos
1. usuario cria contrato no frontend;
2. backend valida e persiste;
3. visualizacao/edicao no dashboard.

Agenda + VIVA
1. usuario conversa com VIVA no `/viva`;
2. backend detecta intencao de agenda (consulta/criacao/conclusao);
3. backend opera na agenda real por usuario e responde no chat.

WhatsApp
1. mensagem chega via Evolution API;
2. webhook processa e gera resposta no dominio comercial (Viviane);
3. conversa e refletida no painel de conversas.

---

## Stack e Servicos

Frontend
- Next.js 14 (App Router)
- Tailwind + shadcn/ui
- JWT no cliente

Backend
- FastAPI (`/api/v1`)
- servicos de contratos, clientes, agenda, WhatsApp e VIVA
- OpenAI institucional + fallback local da VIVA

Banco/Infra
- PostgreSQL 15
- Redis 7
- Evolution API

---

## Direcao de Memoria/RAG

Decisao vigente:
- piloto em `pgvector` no proprio PostgreSQL (DECISAO-025);
- trilha de escala para Qdrant em fase posterior, se volume/latencia exigirem.

---

## Rotas Frontend (resumo)

- `/` login
- `/viva` chat interno VIVA
- `/contratos`, `/contratos/novo`, `/contratos/lista`, `/contratos/[id]`, `/contratos/[id]/editar`
- `/clientes`
- `/agenda`
- `/whatsapp`, `/whatsapp/conversas`

---

*Documento atualizado em: 2026-02-10*
