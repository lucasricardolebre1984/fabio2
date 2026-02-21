# SaaS Domains - Shared Reference (VIVA + VIVIANE)

Data: 2026-02-21
Fonte: `docs/AUDIT/CONTEXT_SOURCE_OF_TRUTH_2026-02-21.md`

## 1) Objetivo

Este arquivo define o conhecimento compartilhado minimo para:
- VIVA (orquestrador interno do SaaS)
- VIVIANE (atendimento comercial no WhatsApp)

## 2) Dominios do SaaS

### Agenda
- Entidade: compromisso
- Campos-chave: titulo, data_inicio, participantes, descricao
- Rotas:
  - `POST /api/v1/agenda`
  - `GET /api/v1/agenda`
  - `PATCH /api/v1/agenda/{evento_id}/concluir`

### Clientes
- Entidade: cliente
- Campos-chave: nome, telefone, CPF/CNPJ
- Rotas:
  - `GET /api/v1/clientes`
  - `GET /api/v1/clientes/{cliente_id}`
  - `GET /api/v1/clientes/{cliente_id}/contratos`

### Contratos
- Entidades: contrato emitido, template de contrato
- Campos-chave: numero, tipo/template, cliente, status
- Rotas:
  - `GET /api/v1/contratos`
  - `GET /api/v1/contratos/templates`

### Campanhas
- Entidade: campanha
- Campos-chave: marca (FC/Rezeta), tema, CTA, status
- Rotas:
  - `POST /api/v1/viva/campanhas`
  - `GET /api/v1/viva/campanhas`
  - `DELETE /api/v1/viva/campanhas/{campanha_id}`

### WhatsApp / Handoff VIVA -> VIVIANE
- Entidade: tarefa de handoff
- Campos-chave: `agenda_event_id`, `cliente_nome`, `cliente_numero`, `mensagem`, `scheduled_for`
- Rotas:
  - `POST /api/v1/viva/handoff/schedule`
  - `GET /api/v1/viva/handoff`
  - `POST /api/v1/viva/handoff/process-due`

## 3) Fluxo institucional "Agendar + WhatsApp"

1. Usuario pede para VIVA agendar compromisso e avisar participantes no WhatsApp.
2. VIVA cria compromisso real em `POST /api/v1/agenda`.
3. VIVA prepara o texto do aviso (mensagem do usuario ou template institucional).
4. VIVA agenda handoff para VIVIANE (`schedule_task` / `POST /api/v1/viva/handoff/schedule`).
5. VIVIANE executa envio quando a tarefa vence.
6. Status da tarefa fica auditavel (`pending`, `sent`, `failed`).

## 4) Regras de integridade

- Nao confirmar "feito" sem execucao real de rota.
- Nao inventar numero de telefone, cliente, contrato ou status.
- Se faltar telefone/participantes para handoff, pedir apenas 1 dado objetivo.
- VIVA e VIVIANE devem usar linguagem coerente entre si (sem contradicao de contexto).
