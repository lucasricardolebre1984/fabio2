# STATUS DO PROJETO - FC Soluções Financeiras

**Data:** 2026-02-06  
**Sessão:** Mapeamento e documentação completa  
**Status:** ⚠️ FUNCIONANDO COM LIMITAÇÕES EM IMAGENS

---

## Objetivo Atual

Etapa 1 concluída: roteiro de deploy 100% Docker no Ubuntu.  
Próxima etapa: ativar WhatsApp funcional no backend.

---

## Funcionalidades Operacionais

- Contratos com template Bacen
- Criação e edição de contratos
- Cálculo de valores por extenso
- Visualização institucional
- PDF via browser print
- Gestão de clientes
- Agenda de compromissos
- Integração WhatsApp (Evolution API)
- Chat IA VIVA interno (`/viva`)
- Conversas WhatsApp (`/whatsapp/conversas`)

---

## VIVA - Estado Atual

- Chat: OK
- Visão: OK (upload + prompt)
- Imagem: gera fundo, mas não respeita paleta/brief; arte final ainda parcial
- Áudio: NÃO funciona (botão)
- Upload de imagem: falha com PNG (MIME incorreto)

---

## Portas Padrão

- Frontend: 3000
- Backend: 8000
- PostgreSQL: 5432
- Redis: 6379
- Evolution API: 8080

---

## Etapas de Deploy (Ubuntu)

- Etapa 1: Roteiro de deploy 100% Docker (concluída)
- Etapa 2: WhatsApp funcional e integrado (pendente)
- Etapa 3: Protocolo final com DNS, SSL e hardening (pendente)

---

## Documentação Atualizada

- `docs/ARCHITECTURE/OVERVIEW.md`
- `docs/ARCHITECTURE.md`
- `docs/CONTEXT.md`
- `docs/API.md`
- `docs/INTEGRACAO_WHATSAPP_VIVA.md`
- `docs/MUDANCAS_WHATSAPP_VIVA.md`
- `docs/MANUAL_DO_CLIENTE.md`
- `docs/RUNBOOK.md`
- `docs/FOUNDATION.md`
- `docs/BUGSREPORT.md`
- `docs/DEPLOY_UBUNTU_DOCKER.md`

---

*Atualizado em: 2026-02-05*
