# VIVA e VIVIANE — Redesign de Personas e Orquestração

**Protocolo:** GODMOD (docs/PROMPTS/GODMOD.md)  
**Data:** 21 de fevereiro de 2026  
**Objetivo:** Redesenhar os agentes VIVA e VIVIANE com conhecimento compartilhado do SaaS e fluxo de orquestração (VIVA → VIVIANE para WhatsApp).

---

## 1. Formato sugerido (pré-execução)

### 1.1 Ordem de skills

| # | Skill | Saída esperada |
|---|-------|----------------|
| 1 | domain-analysis | Mapa de bounded contexts, protocolo VIVA↔VIVIANE |
| 2 | domain-identification-grouping | Matriz de capacidades por domínio |
| 3 | component-common-domain-detection | Referência compartilhada (o que ambos precisam saber) |
| 4 | skill-creator | Template de AGENT.md |
| 5 | subagent-creator | Protocolo de handoff e delegação |
| 6 | docs-writer | Redação final dos dois AGENT.md |

### 1.2 Estrutura do documento

- **Fase 1–3:** Análise técnica (read-only, sem aprovação).
- **Fase 4–5:** Estrutura e protocolo (read-only até gate).
- **Fase 6:** Redação final (requer "APROVADO" para editar AGENT.md).

### 1.3 Gate de persona (CHAMADA LUCAS)

Antes de redigir a seção de persona nos AGENT.md, o agente DEVE chamar Lucas para:

- Definir o que VIVA deve saber sobre o SaaS.
- Definir o que VIVIANE deve saber sobre o SaaS.
- Definir o que cada uma sabe sobre a outra.
- Validar fluxos: "agendar reunião + enviar WhatsApp aos participantes".

**Local do gate:** Após skill 3 (component-common-domain-detection), antes de skill 4 (skill-creator).

---

## 2. Regras GODMOD aplicadas

- Comandos de leitura e diagnóstico: executados livremente.
- Edição de `backend/COFRE/persona-skills/*/AGENT.md`: requer "APROVADO".
- Branch: `main` única.
- Documentação: atualizar `docs/SESSION.md` e `docs/STATUS.md` em rodada relevante.

---

## 3. Execução por skill

### Skill 1: domain-analysis

**Status:** Em execução.

**Processo (domain-analysis):**
- Fase 1: Extrair conceitos (Entities, Services, Use Cases, Controllers).
- Fase 2: Agrupar por linguagem ubíqua.
- Fase 3: Identificar subdomínios (Core, Supporting, Generic).
- Fase 4: Avaliar coesão.
- Fase 5: Mapear bounded contexts.
- Fase 6: Definir integração VIVA↔VIVIANE.

### Resultado Skill 1: domain-analysis

#### Fase 1: Conceitos extraídos

| Tipo | Conceitos |
|------|-----------|
| **Entities** | Cliente, Contrato, Agenda (compromisso), Campanha, Sessão VIVA, Handoff Task |
| **Services** | ClienteService, ContratoService, AgendaService, WhatsAppService, VivaChatOrchestratorService, VivaDomainQueryRouterService, VivaHandoffService, EvolutionWebhookService |
| **Use Cases** | Consultar clientes/contratos/agenda, criar campanha, agendar, enviar WhatsApp, handoff VIVA→VIVIANE |

#### Fase 2: Linguagem ubíqua por domínio

| Domínio | Termos |
|---------|--------|
| Contratos | contrato, template, modelo, emitido, cliente |
| Clientes | cliente, CPF, CNPJ, contratos do cliente |
| Agenda | compromisso, reunião, data, horário, participantes |
| Campanhas | campanha, briefing, CTA, FC, Rezeta |
| WhatsApp | mensagem, conversa, handoff, Viviane, Evolution |
| VIVA | orquestrador, consulta, execução, rota real |

#### Fase 3: Subdomínios e classificação

| Subdomínio | Tipo | Justificativa |
|------------|------|---------------|
| VIVA (orquestrador interno) | Core | Diferencial do SaaS, lógica complexa |
| VIVIANE (WhatsApp comercial) | Core | Atendimento externo, persona Rezeta |
| Contratos | Supporting | Específico do negócio |
| Clientes | Supporting | Específico do negócio |
| Agenda | Supporting | Específico do negócio |
| Campanhas | Supporting | Específico do negócio |
| WhatsApp (infra) | Generic | Evolution API, canal padrão |

#### Fase 4: Bounded contexts sugeridos

| Contexto | Contém | Linguagem |
|----------|--------|-----------|
| **VIVAContext** | Chat interno, agenda, clientes, contratos, campanhas, acionar VIVIANE | "Consultar", "criar", "listar", "agendar", "enviar por WhatsApp" |
| **VIVIANEContext** | WhatsApp, comercial, handoff humano | "Atender", "responder", "transferir", "próximo passo" |
| **Shared** | Agenda, clientes, contratos (dados para mensagem) | "Participante", "reunião", "cliente", "contrato" |

#### Fase 5: Integração VIVA↔VIVIANE

**Padrão:** Customer/Supplier — VIVA (upstream) solicita; VIVIANE (downstream) executa.

**Canal técnico:** `VivaHandoffService.schedule_task()` — agenda evento, cliente_numero, mensagem, scheduled_for.

**Fluxo alvo:**
1. Usuário pede à VIVA: "Agende reunião amanhã 14h e avise os participantes por WhatsApp."
2. VIVA cria compromisso em `POST /api/v1/agenda`.
3. VIVA chama `VivaHandoffService.schedule_task()` com participantes e mensagem.
4. VIVIANE (via job/cron ou webhook) envia WhatsApp aos participantes.

**Regra:** VIVA conhece VIVIANE como "canal de envio WhatsApp". VIVIANE conhece VIVA como "origem de tarefas agendadas" (quando aplicável).

---

### Resultado Skill 2: domain-identification-grouping

#### Matriz de capacidades por domínio

| Domínio | VIVA | VIVIANE |
|---------|------|---------|
| **Agenda** | Criar, listar, consultar, abrir compromisso | Conhecer (participantes, data/hora) para mensagens |
| **Clientes** | Listar, abrir, consultar contratos do cliente | Conhecer (nome, contato) para mensagens |
| **Contratos** | Listar modelos, listar emitidos, abrir por cliente | Conhecer (tipo, número) para contexto comercial |
| **Campanhas** | Criar, listar, excluir (FC/Rezeta) | — |
| **WhatsApp** | Acionar VIVIANE (handoff task) | Enviar, responder, handoff humano |
| **Orquestração** | Rotear consultas, executar rotas reais | Receber tarefas da VIVA, executar envio |

#### Agrupamento de componentes por domínio

| Domínio | Componentes/Services |
|---------|----------------------|
| Agenda | AgendaService, VivaAgendaNluService, GoogleCalendarService |
| Clientes | ClienteService, intents/clientes |
| Contratos | ContratoService, intents/contratos |
| Campanhas | VivaCampaignRepositoryService, intents/campanhas |
| WhatsApp | WhatsAppService, EvolutionWebhookService |
| Handoff VIVA→VIVIANE | VivaHandoffService |

### Skill 2: domain-identification-grouping

**Status:** Concluído.

---

### Resultado Skill 3: component-common-domain-detection

#### Conhecimento compartilhado (ambos precisam saber)

| Conceito | VIVA usa para | VIVIANE usa para |
|----------|---------------|------------------|
| **Agenda** | Criar/listar compromissos | Contexto de "reunião X no dia Y" em mensagem |
| **Cliente** | Consultar, vincular | Destinatário, nome na mensagem |
| **Contrato** | Listar, abrir | Contexto comercial quando relevante |
| **Participante** | Extrair da agenda para handoff | Destinatário do WhatsApp |

#### Referência compartilhada sugerida

Arquivo: `backend/COFRE/persona-skills/references/saas-domains.md`

Conteúdo mínimo:
- Estrutura de agenda (compromisso, data, horário, participantes).
- Estrutura de cliente (nome, telefone, CPF/CNPJ).
- Estrutura de contrato (tipo, número, cliente).
- Fluxo handoff: VIVA agenda → VIVIANE envia.

### Skill 3: component-common-domain-detection

**Status:** Concluído.

---

## 4. GATE: CHAMADA LUCAS (persona) - RESOLVIDO

Gate resolvido com base no anexo validado como fonte da verdade:
- `docs/AUDIT/CONTEXT_SOURCE_OF_TRUTH_2026-02-21.md`

### 4.1 O que a VIVA deve saber

- [x] Escopo de persona:
  - sem novo insumo de atendimento comercial; VIVA permanece orquestrador interno.
- [x] Sobre o SaaS:
  - operar agenda, clientes, contratos e campanhas por rotas reais.
- [x] Sobre a VIVIANE:
  - VIVIANE e subagente/comercial de WhatsApp para execucao de disparos.
- [x] Sobre agenda/clientes/contratos/campanhas:
  - conhecimento de dominios compartilhados para responder e executar sem invencao.
- [x] Fluxos que pode acionar:
  - agendar compromisso;
  - listar/consultar dados do SaaS;
  - criar/listar campanhas;
  - agendar handoff WhatsApp para VIVIANE.

### 4.2 O que a VIVIANE deve saber

- [x] Sobre o SaaS:
  - visao geral de modulos e contexto operacional do cliente.
- [x] Sobre a VIVA:
  - VIVA e origem de tarefas agendadas para WhatsApp.
- [x] Sobre agenda/clientes/contratos:
  - usar dados como contexto de mensagem comercial (data, nome, compromisso, contrato).
- [x] Quando recebe tarefas da VIVA:
  - executar envio e reportar resultado objetivo (sent/failed), sem loop.

### 4.3 Fluxo "agendar + WhatsApp"

- [x] VIVA cria:
  - compromisso real na agenda (`POST /api/v1/agenda`) e handoff task.
- [x] VIVIANE envia:
  - mensagem de lembrete/comercial no WhatsApp para participantes.
- [x] Texto da mensagem:
  - prioridade para texto do usuario; fallback para template institucional da VIVA.

---

## 5. Resultado Skill 4: skill-creator

**Status:** Concluido.

Template aplicado para os dois AGENTs:
- Identidade
- Escopo de atuacao
- Dominios e rotas de verdade
- Fluxos operacionais passo a passo
- Regras de resposta/conduta
- Referencias compartilhadas
- Governanca

Arquivos impactados:
- `backend/COFRE/persona-skills/viva/AGENT.md`
- `backend/COFRE/persona-skills/viviane/AGENT.md`

---

## 6. Resultado Skill 5: subagent-creator

**Status:** Concluido.

Protocolo de delegacao consolidado:
1. VIVA recebe pedido de agendamento + WhatsApp.
2. VIVA cria compromisso no SaaS.
3. VIVA agenda handoff para VIVIANE com dados minimos.
4. VIVIANE executa envio quando devido.
5. Status fica auditavel (`pending`, `sent`, `failed`).

Referencia compartilhada criada:
- `backend/COFRE/persona-skills/references/saas-domains.md`

---

## 7. Resultado Skill 6: docs-writer

**Status:** Concluido.

Documentos finais de persona redigidos:
- `backend/COFRE/persona-skills/viva/AGENT.md` (VIVA v4.1)
- `backend/COFRE/persona-skills/viviane/AGENT.md` (VIVIANE v5.2)
- `backend/COFRE/persona-skills/references/rezeta-servicos.md` (base de conhecimento comercial)

Criterios aplicados:
- Linguagem direta
- Passos operacionais claros
- Limite de perguntas de complemento
- Regras anti-loop e anti-invencao
- Coerencia VIVA <-> VIVIANE

---

## 8. Status final da trilha de skills

| # | Skill | Status | Saida |
|---|-------|--------|-------|
| 1 | domain-analysis | Concluido | Bounded contexts + integracao |
| 2 | domain-identification-grouping | Concluido | Matriz de capacidades |
| 3 | component-common-domain-detection | Concluido | Conhecimento compartilhado |
| 4 | skill-creator | Concluido | Estrutura final dos AGENT.md |
| 5 | subagent-creator | Concluido | Protocolo de handoff VIVA->VIVIANE |
| 6 | docs-writer | Concluido | Redacao final de personas e referencias |

Veredito: redesign concluido com gate de persona fechado e fonte de contexto versionada.
