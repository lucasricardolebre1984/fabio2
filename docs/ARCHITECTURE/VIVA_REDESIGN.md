# VIVA Redesign (Server-First, Fluida, Sem Rigidez)

**Data:** 2026-02-10  
**Status:** Aprovado para execucao em 3 etapas  
**Escopo:** Chat interno VIVA, agenda inteligente, campanhas, handoff para Viviane (WhatsApp)

---

## 1. Objetivo

Transformar a VIVA em uma assistente operacional fluida e inteligente, sem exigir formato textual rigido, com memoria contextual de curto e longo prazo, e com orquestracao do fluxo:

`Fabio -> VIVA -> Viviane -> Fabio`

---

## 2. Problema Atual (resumo executivo)

- `backend/app/api/v1/viva.py` esta monolitico e concentra multiplos dominios.
- Parte do fluxo de agenda ainda cai em fallback prescritivo.
- Nao existe handoff operacional fechado para aviso programado ao cliente via persona Viviane.
- Memoria longa sem camada vetorial moderna para recuperar contexto com filtro.

---

## 3. Arquitetura Alvo

### 3.1 Separacao por camadas

- `router`: apenas contrato HTTP.
- `orchestrator`: decide intencao, proximo passo, e resposta.
- `services/agenda`: criar, listar, concluir, reagendar, lembrar.
- `services/campaigns`: briefing, copy, imagem, persistencia.
- `services/capabilities`: catalogo do que a VIVA pode fazer no SaaS.
- `services/handoff`: cria e executa tarefas VIVA -> Viviane.
- `services/memory`: sessao curta + memoria longa vetorial.

### 3.2 Memoria (curta + longa)

- Curta (operacional): estado da sessao por usuario (janela de trabalho).
- Longa (RAG): `pgvector` no Postgres do projeto.
- Filtros obrigatorios:
  - `empresa` (`FC`, `REZETA`)
  - `modulo` (`agenda`, `campanhas`, `clientes`, `contratos`, `whatsapp`)
  - `user_id`
  - `tipo_contexto` (`regra`, `historico`, `preferencia`, `resultado`)
  - `canal` (`viva_interna`, `whatsapp_viviane`)

---

## 4. Endpoints Necessarios (contrato minimo)

### 4.1 VIVA Core

- `POST /api/v1/viva/chat`
  - entrada: `mensagem`, `session_id`, `modo`, anexos/referencias opcionais
  - saida: `resposta`, `acoes_sugeridas`, `midia`, `session_id`, `meta`
- `GET /api/v1/viva/chat/snapshot`
  - recuperar historico de sessao.
- `POST /api/v1/viva/chat/session/new`
  - iniciar nova sessao sem perder historico.
- `GET /api/v1/viva/status`
  - status de modelos/configuracao.

### 4.2 Agenda Fluida

- `POST /api/v1/viva/agenda/interpret`
  - converte linguagem natural em intencao estruturada.
- `POST /api/v1/viva/agenda/execute`
  - executa intencao validada (criar/listar/concluir/reagendar).
- `GET /api/v1/agenda`
  - fonte oficial de compromissos por usuario.
- `POST /api/v1/agenda`
  - cria compromisso.
- `PATCH /api/v1/agenda/{id}/concluir`
  - conclui compromisso.

### 4.3 Campanhas

- `POST /api/v1/viva/campaigns/plan`
  - retorna 2-3 caminhos criativos curtos.
- `POST /api/v1/viva/campaigns/generate`
  - gera imagem/copy final.
- `GET /api/v1/viva/campanhas`
  - historico.
- `POST /api/v1/viva/campanhas`
  - persistencia do resultado.

### 4.4 Handoff VIVA -> Viviane

- `POST /api/v1/viva/handoff/schedule`
  - cria tarefa de aviso no horario.
- `POST /api/v1/viva/handoff/execute/{task_id}`
  - executa disparo para WhatsApp.
- `GET /api/v1/viva/handoff/{task_id}`
  - status (`pending`, `sent`, `failed`, `acknowledged`).

### 4.5 Memoria Longa (RAG)

- `POST /api/v1/viva/memory/upsert`
- `POST /api/v1/viva/memory/search`
- `POST /api/v1/viva/memory/feedback`

---

## 5. Regras Conversacionais Alvo

- Nunca exigir frase identica para funcionar.
- Se faltar dado critico: uma pergunta curta e contextual.
- Para agenda: primeiro interpretar intencao, depois confirmar acao.
- Para campanhas: no maximo 3 gates curtos; com comando direto, gerar.
- Confirmar resultado de forma objetiva (o que foi feito, quando, para quem).

---

## 6. Fluxo Operacional de Secretaria

1. Fabio pede para VIVA: "Agende e avise cliente X amanha 10h no WhatsApp".
2. VIVA interpreta e cria compromisso + tarefa de handoff.
3. No horario, Viviane envia mensagem WhatsApp (template/contexto correto).
4. VIVA registra entrega e responde ao Fabio com status.

---

## 7. Plano de Execucao em 3 Etapas

### Etapa 1 (documentacao + baseline)

- Registrar bugs estruturais.
- Publicar este blueprint tecnico.
- Criar commit de seguranca antes da refatoracao pesada.

### Etapa 2 (desmonte do monolito + agenda fluida)

- Extrair dominios de `viva.py` para servicos.
- Trocar fallback rigido por follow-up contextual de agenda.
- Preservar contratos HTTP existentes para nao quebrar frontend.

### Etapa 3 (handoff e memoria longa)

- Implementar orquestracao completa VIVA -> Viviane.
- Adicionar `pgvector` com filtros contextuais.
- Validar fluxo ponta a ponta com evidencias.

---

## 8. Criterios de Aceite

- VIVA agenda com linguagem natural sem exigir template fixo.
- VIVA cria handoff para Viviane e registra status de envio.
- Campanhas geram com aderencia ao contexto de marca e tema.
- Historico/sessao continua apos refresh da tela.
- Sem regressao nas rotas atuais `/viva`, `/agenda`, `/campanhas`, `/whatsapp`.
