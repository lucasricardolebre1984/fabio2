# VIVA Orquestrador + Skills Blueprint

Data: 2026-02-13
Status: aprovado para execucao por fases
Escopo: `/api/v1/viva/*`, campanhas, memoria, handoff VIVA->Viviane

---

## 1) Estado atual (as-is)

### 1.1 Fluxo ativo do chat
1. Front envia mensagem para `POST /api/v1/viva/chat`.
2. Orquestrador resolve modo e sessao.
3. Mensagem usuario e resposta IA sao persistidas em chat session.
4. Memoria media (Redis) e memoria longa (pgvector) tentam append.
5. Para campanha FC/REZETA, fluxo pode gerar imagem e salvar em `viva_campanhas`.

Arquivos centrais:
- `backend/app/api/v1/viva_core.py`
- `backend/app/services/viva_chat_orchestrator_service.py`
- `backend/app/services/viva_chat_domain_service.py`
- `backend/app/services/viva_memory_service.py`
- `frontend/src/app/viva/page.tsx`

### 1.2 Prompt principal em uso
- Prompt principal unico da VIVA interna: `backend/app/services/viva_concierge_service.py`.
- Injeccao de contexto de memoria no chat: `_build_viva_concierge_messages` em `backend/app/services/viva_chat_domain_service.py`.

Regra institucional:
- memoria conversacional deve usar apenas o prompt principal da VIVA.
- prompts legados nao entram como memoria contextual no fluxo principal.

### 1.3 Status real da memoria/RAG (runtime)
Evidencia desta rodada:
- `GET /api/v1/viva/memory/status` => `vector_enabled=true`, `redis_enabled=true`, `total_vectors=373`.
- `POST /api/v1/viva/memory/reindex?limit=200` => `processed=200`, `indexed=0`.
- `GET /api/v1/viva/memory/search?q=agenda&limit=3` => `items=[]`.

Conclusao:
- Memoria curta/media: operacional.
- Memoria longa semantica (RAG): indisponivel funcionalmente no estado atual.

---

## 2) Arquitetura alvo (to-be)

## 2.1 Um agente orquestrador
Nome: `viva_orchestrator`
Responsabilidade:
- receber intencao;
- rotear para skill correta;
- controlar estado de sessao;
- consolidar resposta final;
- registrar trilha auditavel.

## 2.2 Dois agentes de persona separados
- `viva_core_agent` (interno SaaS):
  - conhece empresa FC Solucoes Financeiras, modulos e processos internos.
  - fala com Fabio no chat interno.
- `viviane_handoff_agent` (externo WhatsApp):
  - executa contato operacional com cliente final.
  - nao assume papel da VIVA no chat interno.

Regra de fronteira:
- uma persona nao substitui a outra.
- compartilhamento apenas por handoff estruturado (`task`, `contexto`, `status`).

## 2.3 Contrato de skill routing
Cada skill deve expor:
- `skill_id`
- `trigger_intents`
- `input_schema`
- `output_schema`
- `safety_rules`
- `observability_keys`

---

## 3) Skill obrigatoria de campanha

Skill id: `skill_generate_campanha_ghd_copy`
Acao principal: `generate_campanha`

### 3.1 Quando acionar automaticamente
- usuario pedir campanha/post/banner/imagem criativa;
- usuario pedir "me de sugestao antes de gerar";
- usuario informar preferencia de elenco (mulher/homem/casal/grupo).

### 3.2 Contrato `generate_campanha`
Input minimo:
- `brand`: `FC` ou `REZETA`
- `objetivo`
- `publico`
- `tema`
- `oferta` (opcional)
- `cta` (opcional)
- `cast_preference` (opcional)
- `suggestion_only` (bool)

Output:
- `campaign_plan` (copy estruturada)
- `image_prompt` (quando houver geracao)
- `campaign_id` (quando salvar)
- `meta` (versao skill, origem, variacao)

Regras:
- obedecer contexto explicito do usuario;
- evitar repeticao visual obvia;
- nao impor estereotipo fixo de personagem;
- usar linguagem fluida (sem formulas proibidas).

Fonte base da skill:
- `C:/Users/Lucas/Desktop/skillconteudo.txt`

---

## 4) Governanca de prompt/memoria

Objetivo aprovado:
- manter apenas o prompt principal da VIVA como guia conversacional base;
- remover dependencia de prompts antigos na memoria.

Diretriz tecnica:
1. Prompt principal: `viva_concierge_service`.
2. Memoria contextual: apenas fatos de sessao e historico validado.
3. Prompts legados: somente referencia historica, fora do pipeline de memoria principal.

---

## 5) Skills do AGENTS que compensam no projeto

Selecao recomendada (uso imediato):
1. `coding-guidelines`: padrao seguro de implementacao/refactor.
2. `docs-writer`: manter docs institucionais sincronizados por entrega.
3. `playwright-skill`: validacao E2E real de `/viva`, `/campanhas`, `/agenda`.
4. `best-practices`: revisao de qualidade de frontend/backend.
5. `security-best-practices`: rodada de hardening quando houver mudancas de auth/dados sensiveis.
6. `gh-fix-ci`: diagnostico objetivo quando CI quebrar no GitHub.

Selecao opcional por demanda:
- `web-accessibility`
- `core-web-vitals`
- `seo`

Nao priorizar agora:
- skills de deploy cloud nao usadas no fluxo local atual.
- skills Nx (workspace atual nao e Nx).

---

## 6) Plano de execucao para reparar RAG com esse modelo

Fase 1 - Restaurar embeddings:
- validar credito/chave do provedor de embedding;
- adicionar telemetria explicita de erro em `append_long_memory`.

Fase 2 - Reindex confiavel:
- executar `memory/reindex` por lote;
- validar `indexed > 0`.

Fase 3 - Busca semantica:
- validar `memory/search` com hits reais por termos de sessao.

Fase 4 - Plug com orchestrator:
- usar resultado da busca apenas quando score minimo atingir threshold.

Criterio de aceite do RAG:
- `reindex` indexando consistentemente;
- `search` retornando itens relevantes;
- chat usando contexto recuperado sem alucinacao.

---

## 7) Checkpoint para pausa/retomada

Persistido nesta rodada:
- status tecnico real do RAG (indisponivel funcionalmente);
- blueprint alvo do orquestrador unico + personas separadas;
- contrato da skill `generate_campanha`;
- shortlist oficial de skills para uso no projeto.

Documento de referencia principal desta pauta:
- `docs/ARCHITECTURE/VIVA_ORQUESTRADOR_SKILLS_BLUEPRINT.md`
