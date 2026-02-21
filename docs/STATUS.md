# STATUS do projeto - FC Solucoes Financeiras

Data: 2026-02-21
Status geral: operacional em ambiente local e stack prod-like, com WhatsApp/VIVA/Viviane funcionais e layout de contratos estabilizado para homologacao final; documentacao institucional normalizada (FOUNDATION + caminhos COFRE), drift operacional do Ubuntu limpo e persistindo como pendencia principal a intermitencia especifica no fluxo WhatsApp.

## Fonte de verdade ativa

- Persona canonica VIVA: `backend/COFRE/persona-skills/viva/AGENT.md`
- Persona canonica VIVIANE: `backend/COFRE/persona-skills/viviane/AGENT.md`
- Limite de escopo: VIVA = orquestrador interno; atendimento comercial humano externo = VIVIANE.
- Referencia compartilhada de dominios: `backend/COFRE/persona-skills/references/saas-domains.md`
- Base comercial Rezeta (Viviane): `backend/COFRE/persona-skills/references/rezeta-servicos.md`
- Catalogo de endpoints para execucao da Viviane: `backend/COFRE/persona-skills/references/saas-endpoints-catalog.md`
- Principios de conversa natural da Viviane: `backend/COFRE/persona-skills/references/conversation-principles.md`
- Logica ODT operacional da VIVA: `backend/COFRE/persona-skills/references/viva-odt-logic.md`
- Memorias canonicas: `backend/COFRE/memories/<tabela>/`
- Protocolo: `docs/COFRE_RAG_PROTOCOL.md`

## Estado dos modulos

- Contratos: operacional e layout institucional ajustado (logo proporcional sem ampliar faixa azul)
- Clientes: operacional
- Agenda: operacional no modulo web, com ajuste de saudacao da VIVA em validacao (BUG-104)
- Campanhas: operacional com persistencia, ainda com pendencia de aderencia semantica (BUG-015/BUG-099)
- WhatsApp: operacional
- VIVA: operacional com inconsistencias de orquestracao (BUG-104, BUG-107) e correcao de contratos em validacao (BUG-105, BUG-106)

## Veredito gate a gate (auditoria vigente)

- Gate 1 Seguranca: Parcial
- Gate 2 Streaming VIVA: Parcial
- Gate 3 Frontend Performance: Parcial
- Gate 4 UX VIVA: Parcial
- Gate 5 Voz/TTS: Parcial
- Gate 6 Google Calendar: Parcial
- Gate 7 Testes: Nao concluido
- Gate 8 Build/Deploy: Parcial (stack prod-like validada; pendente go-live EC2 com dominio/SSL)
- Gate 9 Documentacao/Rollback final: Consolidado para rodada de contratos/logo

## Pendencias criticas abertas

- BUG-133: WhatsApp/SaaS com intermitencia de exibicao/resposta em homologacao (em validacao com evidencias de pipeline ativo)
- BUG-134: regressao de loop de handoff da Viviane no WhatsApp (corrigido local, pendente validacao Ubuntu)
- BUG-099: latencia alta no chat interno da VIVA
- BUG-104: em validacao apos ajuste de consulta de agenda (`liste`/`lite agenda`) e estabilizacao de saudacao
- BUG-105: em validacao apos ajuste de roteamento de contratos (modelos vs emitidos por cliente)
- BUG-106: em validacao apos ajuste de confirmacoes curtas
- BUG-107: drift de memoria/persona fora da ancora canonica
- BUG-116: vulnerabilidades criticas/altas no frontend (`next`, `axios`)
- BUG-117: `npm run type-check` quebrando por dependencia de `.next/types`
- BUG-118: suite backend com falhas em auth/contratos/viva (`pytest`)
- BUG-120: CORS amplo no backend (`allow_methods=*`, `allow_headers=*`)

## Evidencias desta rodada

- Matriz menu -> API -> banco -> COFRE: `backend/COFRE/system/blindagem/audit/menu-endpoint-matrix.md`
- Auditoria documental: `backend/COFRE/system/blindagem/audit/DOCS_AUDIT_2026-02-16.md`
- Auditoria de qualidade web: `backend/COFRE/system/blindagem/audit/WEB_QUALITY_AUDIT_2026-02-16.md`
- Indice de blindagem e rollback: `backend/COFRE/system/blindagem/BLINDAGEM_INDEX.md`
- Refatoracao de dominio aplicada no orquestrador:
  - `backend/app/services/viva_domain_query_router_service.py`
  - consultas de contratos/clientes/campanhas/servicos extraidas do `viva_chat_orchestrator_service.py`
- Ajuste final do layout de contratos (logo):
  - `docs/CONTRATOS_LAYOUT_LOGO_MANUAL_AGENTES.md`
  - `backend/COFRE/system/blindagem/audit/CONTRATOS_LOGO_LAYOUT_2026-02-20.md`
  - `backend/COFRE/system/blindagem/rollback/rollback_contratos_logo_layout_20260220_131317_pre_fix_baseline.txt`
  - `backend/COFRE/system/blindagem/rollback/rollback_contratos_logo_layout_20260220_131317.patch`
- Hardening de deploy AWS/producao:
  - `docs/AWS_EC2_GO_LIVE_1PAGINA_2026-02-20.md`
  - `backend/COFRE/system/blindagem/rollback/rollback_pre_aws_go_live_20260220_144959_baseline.txt`
  - `backend/COFRE/system/blindagem/rollback/rollback_pre_aws_go_live_20260220_144959.patch`
  - `backend/COFRE/system/blindagem/rollback/rollback_aws_prod_hardening_20260220_153717_baseline.txt`
  - `backend/COFRE/system/blindagem/rollback/rollback_aws_prod_hardening_20260220_153717.patch`
- Fix de build Linux/EC2 (frontend):
  - Causa raiz: regra `lib/` no `.gitignore` ignorava `frontend/src/lib/api.ts`, `frontend/src/lib/utils.ts` e `frontend/src/lib/constants.ts`.
  - Correcao: excecao explicita no `.gitignore` para `frontend/src/lib/**` e versionamento desses arquivos.
- Fix de endpoint frontend em producao (HTTPS):
  - Causa raiz: `NEXT_PUBLIC_API_URL` nao era passado no build Docker do frontend e o bundle caia em fallback local.
  - Correcao: `ARG/ENV NEXT_PUBLIC_API_URL` no `frontend/Dockerfile`, `build.args` no `docker-compose.prod.yml` e `docker-compose-prod.yml`, e mensagem de erro de login sem `localhost` fixo.
- Fix de regras/precos Viviane em producao:
  - Causa raiz: backend em container sem acesso aos arquivos de regras/precos (`/app/viva_rules`).
  - Correcao: mount read-only de `./frontend/src/app/viva/REGRAS` para `/app/viva_rules` e `VIVA_RULES_DIR=/app/viva_rules` no backend (compose prod).
- Fix de variaveis de IA/Voz/Google em producao:
  - Causa raiz: `docker-compose.prod.yml` publicava so subconjunto de variaveis no backend, deixando `OPENAI_API_MODEL`, `GOOGLE_*` e `MINIMAX_*` ausentes no runtime.
  - Correcao: pass-through completo das variaveis de IA, Google Calendar/Gmail e MiniMax no backend dos arquivos `docker-compose.prod.yml` e `docker-compose-prod.yml`.
- Fix de autenticacao da Evolution em producao:
  - Causa raiz: compose prod da Evolution sem `AUTHENTICATION_API_KEY`, gerando chave nao padronizada entre backend e Evolution.
  - Correcao: alinhamento com stack local (`AUTHENTICATION_API_KEY=${EVOLUTION_API_KEY}` + flags de websocket/cache).
- Fix de stream OpenAI para modelos com parametros restritos:
  - Causa raiz: `chat_stream` enviava `temperature` customizada para modelos que aceitam apenas valor padrao.
  - Correcao: fallback automatico no stream para reenviar sem `temperature/max_completion_tokens` ao receber `400/422 unsupported_value`.
- Fix de persistencia do chat VIVA (stream + non-stream):
  - Causa raiz: mensagens `ia` eram inseridas no banco, mas nao eram commitadas (e no streaming o `done` era emitido antes de persistir).
  - Correcao: commit explicito apos `append_chat_message`/memoria e `done` somente apos persistencia.
- Fix de coerencia de agenda na VIVA (consulta/criacao):
  - Causa raiz: frases comuns (`o que tem na agenda`, `crie ... daqui meia hora`) podiam escapar da rota deterministica de agenda e cair em resposta livre.
  - Correcao: ampliacao do NLU para capturar consulta de agenda (`hoje/ontem/data explicita`) e criacao relativa com `daqui meia hora`.
- Fix de paridade entre `/viva/chat` e `/viva/chat/stream`:
  - Causa raiz: stream seguia caminho tecnico separado e podia responder agenda sem executar rota real.
  - Correcao: `handle_chat_with_viva_stream` passou a delegar para o fluxo canonico `handle_chat_with_viva` e emitir SSE com `content` + `done`.
  - Evidencia: `backend/COFRE/system/blindagem/audit/VIVA_STREAM_CANONICAL_ORCHESTRATION_2026-02-21.md`.
- Fix de follow-up deterministico em clientes/contratos (anti-invencao):
  - Causa raiz: follow-ups curtos (`para Lucas`, `quero`, `com numero`, `clientes cadastrados`) podiam escapar do roteador de dominio e cair no modelo livre.
  - Correcao: roteador de dominio com continuidade por contexto, intents ampliadas e contagem direta de clientes.
  - Evidencia: `backend/COFRE/system/blindagem/audit/VIVA_DOMAIN_FOLLOWUP_TRUTH_GUARD_2026-02-21.md`.
- Fix de templates de contratos no deploy AWS:
  - Causa raiz: backend em container sem acesso a `./contratos/templates`, caindo no fallback sem clausulas (`CLÁUSULAS NÃO CADASTRADAS`).
  - Correcao: mount read-only de `./contratos` para `/app/contratos` no backend em `docker-compose.prod.yml` e `docker-compose-prod.yml`.
- Hotfix de resiliencia da IA VIVA em producao (stream/chat OpenAI):
  - Causa raiz: `chat_stream` devolvia erros OpenAI como conteudo normal (sem acionar fallback do frontend), e alguns modelos (`gpt-5*`) recusam `temperature` customizada.
  - Correcao: detecao de suporte a parametros opcionais por modelo, fallback automatico stream -> chat nao-streaming no backend e sinalizacao de erro SSE quando chunk vier com erro.
- Hotfix de entrega WhatsApp para eventos `@lid`:
  - Causa raiz: envio podia tentar destino `@lid` sem numero real resolvido, gerando falso sucesso/pendencia sem entrega no celular.
  - Correcao: bloqueio de envio direto para `@lid` sem resolucao (`erro_codigo=lid_unresolved`), enriquecimento do contexto com telefone de `sender` no payload do evento, priorizacao de numero resolvido no envio e flush da fila pendente.
- Blindagem de runtime para IA/WhatsApp em producao (EC2):
  - Causa raiz 1: webhook Evolution ausente (`webhook/find = null`) mesmo com instancia `open`, impedindo ingestao de mensagens no backend.
  - Causa raiz 2: `ensure_chat_tables()` executava DDL por request, gerando lock em relacao e saturacao da pool (`QueuePool timeout`) no `/api/v1/viva/chat/stream`.
  - Correcao:
    - auto-healing de webhook em `whatsapp_service` (`/webhook/find` -> `/webhook/set`) com fallback institucional `http://backend:8000/api/v1/webhook/evolution`.
    - padronizacao `byEvents=false` para evitar rotas inexistentes (`/webhook/evolution/<evento>`) e garantir ingestao no endpoint unico implementado.
    - guarda de inicializacao em `ensure_chat_tables()` com lock assíncrono e flag de execucao unica por processo.
  - Evidencia: `backend/COFRE/system/blindagem/audit/WHATSAPP_WEBHOOK_DB_POOL_GUARD_2026-02-21.md`.
- Fix de visibilidade da central WhatsApp + sanitizacao de erro tecnico:
  - Causa raiz 1: `/whatsapp/conversas` carregava apenas `status=ativa` e podia parecer vazia com dados arquivados.
  - Causa raiz 2: erro tecnico de provedor (`OPENAI_API_KEY`) podia vazar no texto enviado ao cliente.
  - Correcao:
    - fallback de listagem na central para `arquivada` quando nao houver `ativa/aguardando`;
    - sanitizacao de resposta tecnica no webhook antes do envio outbound;
  - default local de `WA_INSTANCE_NAME=fc-solucoes-local` para reduzir colisao local x producao quando env nao definido.
- Fix de verdade operacional no webhook WhatsApp (anti-loop outbound):
  - `backend/app/services/evolution_webhook_service.py`
  - mensagens `fromMe=true` agora sao ignoradas no processamento inbound;
  - parser de lote `data.messages[]` agora prioriza mensagem inbound (`fromMe=false`), reduzindo loop/ruido de conversa.
- Hardening de resolucao `@lid` no envio outbound WhatsApp:
  - `backend/app/services/whatsapp_service.py`
  - match seguro por similaridade de nome + proximidade temporal de chat;
  - match por foto de perfil apenas quando unico;
  - validacao obrigatoria de candidato em `POST /chat/whatsappNumbers/{instance}` antes de enviar.
- Fix de contexto de campanha no chat VIVA:
  - `backend/app/services/assistant/intents/campanhas.py`
  - `backend/app/services/viva_chat_orchestrator_service.py`
  - `backend/app/services/viva_chat_runtime_helpers_service.py`
  - endurecimento de intent de contagem para evitar falso positivo em briefing;
  - guard de agenda aplicado apenas quando ha operacao de agenda;
  - follow-up de CTA em campanha pendente passa a destravar geracao real;
  - bloqueio de resposta textual "campanha criada/local salvo" sem execucao real.
- Evidencias de blindagem desta rodada:
  - `backend/COFRE/system/blindagem/audit/VIVA_CAMPAIGN_CONTEXT_TRUTH_GUARD_2026-02-21.md`
  - `backend/COFRE/system/blindagem/audit/WHATSAPP_VISIBILITY_RUNTIME_GUARD_2026-02-21.md`
  - `backend/COFRE/system/blindagem/audit/WHATSAPP_LID_RESOLUTION_HARDENING_2026-02-21.md`
  - `backend/COFRE/system/blindagem/audit/WHATSAPP_SAAS_INTERMITTENCY_VALIDATION_2026-02-21.md`
  - `docs/AUDIT/WHATSAPP_CAMPAIGN_ENDPOINT_TRACE_2026-02-21.md`
  - `docs/AUDIT/COMPONENT_COMMON_DOMAIN_DETECTION_2026-02-21.md`
- Fechamento do redesign de personas VIVA/VIVIANE:
  - `docs/AUDIT/VIVA_VIVIANE_AGENTS_REDESIGN_2026-02-21.md`
  - `docs/AUDIT/CONTEXT_SOURCE_OF_TRUTH_2026-02-21.md`

## Diretriz de deploy institucional

- Alvo principal: Ubuntu AWS virgem (stack Docker)
- Nao usar Vercel como alvo institucional desta operacao

Atualizado em: 2026-02-21
