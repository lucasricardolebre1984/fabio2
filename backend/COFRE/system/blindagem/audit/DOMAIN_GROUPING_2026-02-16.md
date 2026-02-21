# Domain Identification and Grouping - SaaS FC Solucoes Financeiras

Data: 2026-02-16
Metodo: skill `domain-identification-grouping`
Escopo analisado: `backend/app`, `frontend/src/app`, `backend/COFRE`

## Resultado executivo

Mapeamento completo atualizado da stack:

- API backend: 16 arquivos de rota com 79 endpoints.
- Frontend App Router: 14 paginas.
- Modelos principais: 7 tabelas ORM.
- Tabelas runtime (servicos): chat, campanhas, handoff, google calendar, memoria vetorial e registros COFRE.
- COFRE: fonte canonica de persona/skills/memoria com ancora strict ativa.

Dominios logicos consolidados (9):

1. Identidade e Acesso
2. Contratos
3. Clientes (CRM)
4. Agenda e Google Calendar
5. Campanhas e Midia IA
6. VIVA Core (chat/orquestracao)
7. WhatsApp Operacional
8. COFRE (persona/skills/memoria)
9. Plataforma Compartilhada (config/db/providers)

## Inventario de dominios por camada

### 1) Identidade e Acesso

- Frontend:
  - `/` (login): `frontend/src/app/page.tsx`
- Backend:
  - prefixo: `/api/v1/auth/*`
  - arquivo: `backend/app/api/v1/auth.py`
  - model: `backend/app/models/user.py` (`users`)

### 2) Contratos

- Frontend:
  - `/contratos`
  - `/contratos/lista`
  - `/contratos/novo`
  - `/contratos/[id]`
  - `/contratos/[id]/editar`
- Backend:
  - prefixo: `/api/v1/contratos/*`
  - arquivo: `backend/app/api/v1/contratos.py`
  - servicos: `contrato_service.py`, `contrato_template_loader.py`, `pdf_service_playwright.py`
  - models: `contratos`, `contrato_templates`

### 3) Clientes (CRM)

- Frontend:
  - `/clientes`
- Backend:
  - prefixo: `/api/v1/clientes/*`
  - arquivo: `backend/app/api/v1/clientes.py`
  - servico: `cliente_service.py`
  - model: `clientes`

### 4) Agenda e Google Calendar

- Frontend:
  - `/agenda`
- Backend:
  - prefixos: `/api/v1/agenda/*`, `/api/v1/google-calendar/*`
  - arquivos: `agenda.py`, `google_calendar.py`
  - servicos: `agenda_service.py`, `google_calendar_service.py`
  - model: `agenda`
  - tabelas runtime: `google_calendar_connections`, `google_calendar_event_links`

### 5) Campanhas e Midia IA

- Frontend:
  - `/campanhas`
- Backend:
  - prefixos: `/api/v1/viva/campanhas*`, `/api/v1/viva/image/*`, `/api/v1/viva/vision*`, `/api/v1/viva/video/*`
  - arquivos: `viva_campaign_routes.py`, `viva_media_routes.py`
  - servicos: `viva_campaign_repository_service.py`, `openai_service.py`
  - tabela runtime: `viva_campanhas`

### 6) VIVA Core (chat/orquestracao)

- Frontend:
  - `/viva`
- Backend:
  - prefixos: `/api/v1/viva/chat*`, `/api/v1/viva/modules/status`, `/api/v1/viva/persona/status`, `/api/v1/viva/capabilities`
  - arquivos: `viva.py`, `viva_core.py`, `viva_chat_session_routes.py`, `viva_modules_routes.py`, `viva_capabilities_routes.py`
  - servicos: `viva_chat_orchestrator_service.py`, `viva_domain_query_router_service.py`, `viva_agenda_nlu_service.py`, `viva_agent_profile_service.py`, `viva_concierge_service.py`
  - tabelas runtime: `viva_chat_sessions`, `viva_chat_messages`

### 7) WhatsApp Operacional

- Frontend:
  - `/whatsapp`
  - `/whatsapp/conversas`
- Backend:
  - prefixos: `/api/v1/whatsapp/*`, `/api/v1/whatsapp-chat/*`, `/api/v1/webhook/evolution`
  - arquivos: `whatsapp.py`, `whatsapp_chat.py`, `webhook.py`
  - servicos: `whatsapp_service.py`, `evolution_webhook_service.py`, `viva_ia_service.py`
  - models: `whatsapp_conversas`, `whatsapp_mensagens`

### 8) COFRE (persona/skills/memoria)

- Estrutura:
  - `backend/COFRE/persona-skills/viva/AGENT.md`
  - `backend/COFRE/persona-skills/*.md|*.txt`
  - `backend/COFRE/memories/*`
  - `backend/COFRE/system/endpoints_manifest.json`
- Backend:
  - prefixo: `/api/v1/cofre/*`
  - arquivo: `cofre_memory_routes.py`
  - servicos: `cofre_memory_service.py`, `cofre_manifest_service.py`, `cofre_schema_service.py`, `viva_memory_service.py`
  - tabelas runtime: `cofre_persona_registry`, `cofre_skill_registry`, `cofre_memory_registry`, `cofre_manifest_registry`, `viva_memory_vectors`

### 9) Plataforma Compartilhada

- `backend/app/config.py`
- `backend/app/db/*`
- provedores: `openai_service.py`, `minimax_tts_service.py`, `deepseek_service.py`, `viva_local_service.py`
- bootstrap: `backend/app/main.py` (cofre bootstrap + memory storage check + worker handoff)

## Mapa Menu -> Front -> API -> Dados -> COFRE

| Menu SaaS | Front route | API principal | Tabelas | Espelho COFRE |
|---|---|---|---|---|
| Login | `/` | `/api/v1/auth/*` | `users` | n/a |
| Contratos | `/contratos*` | `/api/v1/contratos/*` | `contratos`, `contrato_templates` | indireto por memoria/chat |
| Clientes | `/clientes` | `/api/v1/clientes/*` | `clientes` | indireto por memoria/chat |
| Agenda | `/agenda` | `/api/v1/agenda/*`, `/api/v1/google-calendar/*` | `agenda`, `google_calendar_*` | indireto por memoria/chat |
| Campanhas | `/campanhas` | `/api/v1/viva/campanhas*` | `viva_campanhas` | `memories/viva_campanhas/*` |
| VIVA | `/viva` | `/api/v1/viva/chat*` | `viva_chat_*`, `viva_memory_vectors` | `memories/viva_chat_*`, `redis_viva_memory_medium` |
| WhatsApp | `/whatsapp*` | `/api/v1/whatsapp*`, `/api/v1/webhook/evolution` | `whatsapp_conversas`, `whatsapp_mensagens`, `viva_handoff_tasks` | `memories/viva_handoff_tasks/*` |

## Inconsistencias detectadas (estado atual)

1. `assistant-domain` ainda e chamado a partir do `viva_chat_orchestrator_service.py`, mas o roteamento semantico principal ja foi extraido para `viva_domain_query_router_service.py`.
2. Consultas de cliente em linguagem natural estao cobertas por handler dedicado com match aproximado (nome parcial/ruidoso).
3. Pedidos de "prova por print/OCR" agora passam por guarda anti-alucinacao e nao caem mais em resposta inventada de anexo.
4. Dominio de contratos agora separa melhor modelos vs emitidos e usa `cliente_id` para contratos por cliente; risco residual e apenas variacao extrema de texto.

## Plano de alinhamento de dominio (incremental)

1. Criar handler de cliente detalhe no `viva_domain_query_router_service.py`.
2. Criar guarda de nao alucinacao visual para pedidos sobre print/OCR sem pipeline oficial.
3. Extrair intents por pacote de dominio:
   - `assistant/intents/clientes.py`
   - `assistant/intents/contratos.py`
   - `assistant/intents/agenda.py`
   - `assistant/intents/campanhas.py`
4. Adicionar testes de regressao por intent critica (chat -> dominio -> resposta).

## Veredito

Arquitetura por dominios esta bem definida e operavel.
O principal risco residual deixou de ser estrutural e passou a ser apenas ajuste fino de linguagem natural em casos muito ambiguos.

## Progresso aplicado ate esta rodada

- Domain router ja separa consultas de contratos, clientes, campanhas e servicos.
- Ancora de persona/COFRE hardenizada:
  - `VIVA_AGENT_STRICT=true`;
  - `GET /api/v1/viva/persona/status`;
  - hash da persona em `GET /api/v1/viva/modules/status`.
- COFRE consolidado como fonte unica:
  - `backend/COFRE/persona-skills/*`
  - `backend/COFRE/memories/*`
  - `backend/COFRE/system/endpoints_manifest.json`.

## Atualizacao aplicada (rodada coding-guidelines)

Itens executados em sequencia conforme plano:

1. Handler de cliente detalhe implementado:
   - arquivo: `backend/app/services/viva_domain_query_router_service.py`
   - comandos naturais cobertos:
     - `entre no cadastro do cliente <nome>`
     - `abrir cadastro do cliente <nome>`
     - `dados do cliente <nome>`
   - retorno agora usa dados reais de `clientes` (nome, documento, telefone, email, cidade/UF, endereco, observacoes, contratos vinculados).

2. Guarda anti-alucinacao para print/OCR sem pipeline oficial:
   - arquivo: `backend/app/services/viva_domain_query_router_service.py`
   - quando houver pedido de "prova por print/anexo", resposta curta orienta a consultar fonte de verdade no cadastro do sistema.

3. Intents extraidas por pacote de dominio:
   - `backend/app/services/assistant/intents/clientes.py`
   - `backend/app/services/assistant/intents/contratos.py`
   - `backend/app/services/assistant/intents/agenda.py`
   - `backend/app/services/assistant/intents/campanhas.py`
   - router passou a importar e usar os intents desses modulos.

4. Testes de regressao por intent critica:
   - novo arquivo: `backend/tests/test_viva_domain_intents.py`
   - cobertura:
     - detalhe de cliente por linguagem natural;
     - typo de modelos de contrato (`modolos`);
     - listagem de campanhas nao acionando geracao;
     - guarda visual anti-alucinacao;
     - resposta de detalhe de cliente com campos reais via router.

Validacao tecnica:
- `python -m py_compile` dos modulos alterados: OK.
- `python -m pytest tests/test_viva_domain_intents.py -q` (em `backend/`): `13 passed`.

## Atualizacao final da rodada (agenda + consistencia runtime)

- Ajuste aplicado em janela de agenda para reduzir inconsistencia de dia/horario:
  - `backend/app/services/viva_agenda_nlu_service.py`
    - parser e janela usando horario de Brasilia como base (`America/Sao_Paulo`).
  - `backend/app/services/agenda_service.py`
    - filtro de fim ajustado para `< fim` (evita incluir borda do dia seguinte).
- Rebuild do backend Docker executado para garantir runtime com o codigo novo.
- Integridade COFRE validada:
  - todas as tabelas `public` possuem pasta correspondente em `backend/COFRE/memories`;
  - extra esperado: `redis_viva_memory_medium` (cache/memoria curta).

