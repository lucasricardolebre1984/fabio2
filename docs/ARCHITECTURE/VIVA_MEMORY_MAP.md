# VIVA Memory Map (Sem Viviane)

Este documento mapeia **todos os pontos do sistema que guardam "memoria" da VIVA** (runtime e configuracao) e como zerar, sem tocar na Viviane (WhatsApp).

## 1) O que e "memoria" neste SaaS

1. **Contrato canonico (nao-runtime):**
   - `agents/AGENT.md`: identidade/empresa/regras base do agente (unico).
   - `agents/skillconteudo.txt`: skill neutra de campanha (brief -> campanha).
   - Isto nao e "memoria aprendida"; e o que a VIVA *sempre* deve saber (empresa e regras).

2. **Memoria runtime (persistente):**
   - Postgres (tabelas) para chat, campanhas e vetores.
   - Storage local (imagens/campanhas geradas).

3. **Memoria runtime (cache):**
   - Redis (memoria media por sessao).

4. **Memoria do cliente (browser):**
   - `localStorage`: tokens (nao e memoria de IA).

## 2) Onde a VIVA realmente persiste coisas (pontos de armazenamento)

### 2.1 Postgres (persistente)

Tabelas principais:
- `viva_chat_sessions`: sessoes do chat (lista no dropdown do front).
- `viva_chat_messages`: historico de mensagens por sessao.
- `viva_memory_vectors`: memoria longa (RAG/pgvector).
- `viva_campanhas`: registros de campanhas geradas/salvas.

DDL/migrations relacionadas:
- `backend/migrations/create_viva_memory_vectors.sql`
- `backend/migrations/create_viva_campanhas.sql`

Camadas de codigo relacionadas:
- `backend/app/services/viva_chat_repository_service.py` (chat sessions/messages)
- `backend/app/services/viva_campaign_repository_service.py` (campanhas)
- `backend/app/services/viva_memory_service.py` (memoria longa + reindex/search)

### 2.2 Redis (cache de memoria media por sessao)

Chave principal:
- `viva:memory:session:{session_id}:medium`

Codigo:
- `backend/app/services/viva_memory_service.py`

### 2.3 Storage local (assets gerados)

Diretorios:
- `backend/storage/imagens/` (imagens geradas)
- `backend/storage/campanhas/` (arte final / overlays / derivados)

Observacao:
- `backend/storage/logos/` e logo/brand assets (nao e memoria conversacional, mas e asset persistente).

### 2.4 Prompts/config que viravam "memoria por acidente"

Arquivos que historicamente tinham prompts longos/menu/roteiro e causavam "falação" no fallback:
- `backend/app/services/viva_local_service.py` (fallback sem provedor remoto)
- `backend/app/services/deepseek_service.py` (provedor alternativo)

Contrato atual (fonte canonica):
- `backend/app/services/viva_agent_profile_service.py` (carrega `agents/AGENT.md` e `agents/skillconteudo.txt`)

## 3) Como zerar tudo (reset total de memoria da VIVA)

### 3.1 Reset runtime (recomendado para "zerar resquicios")

1. Postgres: truncar tabelas VIVA
2. Redis: apagar chaves `viva:memory:session:*`
3. Storage: limpar `backend/storage/imagens/*` e `backend/storage/campanhas/*`

Resultado esperado:
- UI do chat reabre "limpa" (sem sessoes antigas)
- RAG volta com `total_vectors=0` ate reindex/uso
- Campanhas antigas somem do historico do modulo Campanhas IA

### 3.2 Reset nuclear (quando quer um ambiente 100% novo)

Opcional:
- remover volumes do Postgres/Redis no Docker e subir novamente.

Isso apaga qualquer dado de outros modulos tambem, entao so usar com cuidado.

## 4) O que NAO zerar (para nao quebrar a identidade)

Manter:
- `agents/AGENT.md` (empresa + regras base)
- `agents/skillconteudo.txt` (skill neutra de campanha)
- codigo de skills/orquestracao

## 5) Viviane (fora do escopo)

Este mapa **nao inclui** memoria/rotas de WhatsApp/Viviane.
Qualquer limpeza de memoria da Viviane deve ser tratada em plano separado.

