# ARQUITETURA - Resumo Executivo

Projeto: FC Solucoes Financeiras SaaS
Versao documental: 2.0
Data de revisao: 2026-02-16

## Objetivo

Centralizar contratos, clientes, agenda, campanhas e atendimento assistido por IA em um unico SaaS, com governanca de memoria institucional no COFRE.

## Stack

- Frontend: Next.js 14
- Backend: FastAPI
- Banco: PostgreSQL
- Cache: Redis
- WhatsApp: Evolution API
- IA: OpenAI

## Fonte tecnica principal

- Arquitetura completa: `docs/ARCHITECTURE/OVERVIEW.md`
- Contrato de API: `docs/API.md`
- Protocolo COFRE: `docs/COFRE_RAG_PROTOCOL.md`

## Regras de produto

- VIVA (interna) e operacao WhatsApp (externa) seguem dominio separado.
- Persona e skills sao mantidas no COFRE.
- Memoria operacional deve ser auditavel e sincronizada com eventos reais.

Atualizado em: 2026-02-16
