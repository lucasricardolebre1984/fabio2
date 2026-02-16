# CONTEXTO DO PROJETO

Projeto: FC Solucoes Financeiras SaaS
Data de revisao: 2026-02-16

## Problema de negocio

A operacao precisa de um sistema unico para contratos, clientes, agenda, campanhas e atendimento assistido por IA, com trilha auditavel de memoria institucional.

## Objetivo institucional

- Centralizar operacao comercial e administrativa em um unico SaaS.
- Garantir consistencia entre frontend, backend, banco e memoria COFRE.
- Tornar a VIVA uma assistente operacional alinhada a persona oficial, sem orquestracao artificial excessiva.

## Escopo ativo

- Contratos (templates, criacao, listagem, PDF)
- Clientes (cadastro, historico, relacao com contratos)
- Agenda (compromissos e sincronizacao Google Calendar)
- Campanhas (geracao, listagem, exclusao sincronizada com COFRE)
- WhatsApp (status e conversas)
- VIVA (chat interno com memoria e skills canonicas)

## Fonte de verdade semantica

- Persona: `backend/COFRE/persona-skills/AGENT.md`
- Skills: `backend/COFRE/persona-skills/*.md`
- Memorias: `backend/COFRE/memories/<tabela>/`

## Publico operacional

- Fabio (administrador)
- Operadores internos
- Parceiros comerciais autorizados

## Criterios de sucesso

- Fluxos de menu refletem dados reais do SaaS (sem resposta ficticia).
- Acao no front tem reflexo em banco e COFRE.
- VIVA executa ordem direta com baixa friccao e sem loops de confirmacao.
- Documentacao ativa acompanha o estado real de runtime.

Atualizado em: 2026-02-16
