# ARQUITETURA - Resumo Executivo

> **Projeto:** FC Soluções Financeiras SaaS  
> **Versão:** 1.0.0  
> **Data:** 2026-02-05

---

## Objetivo

Centralizar a operação de contratos, clientes e agenda da FC Soluções Financeiras em um único sistema web, com geração de PDF e atendimento automatizado via VIVA.

---

## Stack

- Frontend: Next.js 14 + Tailwind + shadcn/ui
- Backend: FastAPI + SQLAlchemy
- Banco: PostgreSQL 15
- Cache/Fila: Redis 7
- WhatsApp: Evolution API
- IA VIVA: Z.AI (modelo principal), OpenRouter e modo local como fallback

---

## Componentes

Frontend
- App Router com rotas de contratos, clientes, agenda, WhatsApp e VIVA

Backend
- API REST em `/api/v1`
- Serviços internos para regras de negócio

Dados
- Modelos principais: `users`, `clientes`, `contratos`, `agenda`, `whatsapp_conversas`, `whatsapp_mensagens`

---

## Fluxos-Chave

- Contrato: template → formulário → cálculo automático → preview → PDF (browser print)
- VIVA chat: mensagens internas no `/viva` com prompts laterais
- WhatsApp: webhook → processamento → resposta VIVA → painel de conversas

---

## Referências

- Arquitetura completa: `docs/ARCHITECTURE/OVERVIEW.md`
- API detalhada: `docs/API.md`
- Integração VIVA: `docs/INTEGRACAO_WHATSAPP_VIVA.md`

---

*Documento atualizado em: 2026-02-05*

---

## Camada de conhecimento operacional da Viviane (V1)

A operacao WhatsApp da Rezeta utiliza base versionada de regras em arquivos para
permitir manutencao continua sem alterar fluxo de atendimento inteiro.

Fontes oficiais:
- `frontend/src/app/viva/REGRAS/Descrição_Detalhada_dos_Serviços_Rezeta_Brasil.md`
- `frontend/src/app/viva/REGRAS/Tabela Precços IA.xlsx`
- `frontend/src/app/viva/REGRAS/tabela_precos_ia_01_planilha1.csv`

Essa camada define:
- linguagem e postura comercial da Viviane;
- portfolio e contexto institucional da Rezeta;
- tabela base de oferta com margem operacional.
