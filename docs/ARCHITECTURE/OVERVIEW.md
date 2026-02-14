# ARQUITETURA - Visao Geral

> **Projeto:** FC Solucoes Financeiras SaaS  
> **Versao:** 1.2.0  
> **Data:** 2026-02-13

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
- Montagem das mensagens do chat: `backend/app/services/viva_chat_domain_service.py` (`_build_viva_concierge_messages`).
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
- `backend/app/services/viva_chat_session_service.py` (sessao/snapshot/contexto);
- `backend/app/services/viva_chat_orchestrator_service.py` (orquestracao principal);
- `frontend/src/app/viva/page.tsx` (envio de mensagem e `session_id`).

Status:
- memoria de sessao e continuidade operacional ativas;
- memoria media em Redis ativa por sessao;
- memoria longa vetorial ativa em pgvector (`viva_memory_vectors`) com fallback local de embeddings quando OpenAI falhar por quota/rede;
- para operacao institucional, RAG fica **indisponivel para homologacao semantica premium** enquanto depender de fallback local sem rodada de qualidade dedicada.

Referencia institucional desta rodada:
- `docs/ARCHITECTURE/VIVA_ORQUESTRADOR_SKILLS_BLUEPRINT.md`

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

Handoff VIVA -> Viviane
1. Fabio agenda via chat interno VIVA;
2. VIVA cria tarefa de handoff para aviso WhatsApp;
3. motor de handoff processa tarefas vencidas e registra status (`pending/sent/failed`).
4. processamento automatico ocorre no lifespan da API (loop periodico).

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
- PostgreSQL 15 + pgvector
- Redis 7
- Evolution API

---

## Direcao de Memoria/RAG

Decisao vigente:
- piloto em `pgvector` no proprio PostgreSQL (DECISAO-025);
- trilha de escala para Qdrant em fase posterior, se volume/latencia exigirem.

Implementacao atual (DECISAO-031):
- curta: snapshot de chat;
- media: Redis por sessao;
- longa: busca semantica vetorial com embeddings OpenAI + fallback local controlado.

Critico para comercializacao:
- status de qualidade semantica deve ser homologado antes de vender modulo de memoria como diferencial.
- sem essa homologacao, modulo de memoria deve ser vendido como "contexto assistido" e nao como "RAG premium garantido".

---

## Orquestrador + Skills (arquitetura alvo comercial)

Componente central:
- `viva_orchestrator` como ponto unico de roteamento por intencao.

Contrato minimo de skill:
- `skill_id`
- `trigger_intents`
- `input_schema`
- `output_schema`
- `safety_rules`
- `observability_keys`

Skill obrigatoria de campanhas:
- `generate_campanha_neutra` (fonte canonica em `agents/skillconteudo.txt`).

---

## Divisao em Modulos de Produto (pre-config para novas vendas)

1. `core_saas`: auth, clientes, contratos, agenda, permissao, billing.
2. `modulo_viva`: chat interno, orquestrador, memoria curta/media/longa.
3. `modulo_viviane`: atendimento externo WhatsApp e handoff operacional.
4. `modulo_campanhas`: planner criativo + geracao de imagem + historico de criativos.
5. `modulo_memoria`: base semantica, indexacao, metricas e governanca de retention.

Regra de produto:
- VIVA e Viviane permanecem separadas por dominio;
- uma pode saber da outra via handoff estruturado, sem mistura de persona.

---

## Fala Continua e Avatar (estado atual)

Estado implementado em `frontend/src/app/viva/page.tsx`:
- escuta continua: `SpeechRecognition/webkitSpeechRecognition` do browser;
- voz de resposta: `window.speechSynthesis`;
- transcricao OpenAI (`/api/v1/viva/audio/transcribe`) apenas para audio anexado/manual.

Risco:
- qualidade de voz e estabilidade variam por SO/browser;
- nao ha pipeline realtime dedicado de voz com identidade vocal institucional fixa.

Pendencias abertas:
- trocar avatar para o asset oficial enviado pelo cliente;
- selecionar voz oficial e padronizar provider;
- validar stack de fala ao vivo para reduzir dependencia da engine nativa do navegador.

---

## Rotas Frontend (resumo)

- `/` login
- `/viva` chat interno VIVA
- `/contratos`, `/contratos/novo`, `/contratos/lista`, `/contratos/[id]`, `/contratos/[id]/editar`
- `/clientes`
- `/agenda`
- `/whatsapp`, `/whatsapp/conversas`

## Rotas Backend VIVA (novas de orquestracao)

- `/api/v1/viva/capabilities`
- `/api/v1/viva/handoff/schedule`
- `/api/v1/viva/handoff`
- `/api/v1/viva/handoff/process-due`
- `/api/v1/viva/memory/status`
- `/api/v1/viva/memory/search`
- `/api/v1/viva/memory/reindex`
- `/api/v1/viva/chat/sessions`

---

*Documento atualizado em: 2026-02-13*
