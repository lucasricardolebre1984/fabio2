# STATUS DO PROJETO - FC Soluções Financeiras

**Data:** 2026-02-07  
**Sessão:** Diagnóstico WhatsApp/Evolution + proposta de aplicação  
**Status:** ⚠️ Sistema operacional com pendências críticas no módulo WhatsApp

---

## Objetivo Atual

Etapa 1 concluída: roteiro de deploy 100% Docker no Ubuntu.  
Etapa 2 em execução: estabilizar integração WhatsApp (Evolution) no backend e conectar fluxo completo no frontend.

---

## Funcionalidades Operacionais

- Contratos com template Bacen
- Criação e edição de contratos
- Cálculo de valores por extenso
- Visualização institucional
- PDF via browser print
- Gestão de clientes
- Agenda de compromissos
- Chat IA VIVA interno (`/viva`)
- Módulo WhatsApp com estrutura de APIs e telas já criado

---

## VIVA - Estado Atual

- Chat: OK
- Visão: OK (upload + prompt)
- Imagem: gera fundo, mas ainda com inconsistência de paleta/brief
- Áudio: NÃO funciona (botão)
- Upload de imagem: falha com PNG (MIME incorreto)

---

## WhatsApp - Diagnóstico 2026-02-07

- Evolution API em `localhost:8080` está online e com instância ativa `Teste` (estado `open`).
- Backend está com parâmetros divergentes no runtime (chave/instância), causando falso desconectado em `/api/v1/whatsapp/status`.
- Payload atual de envio (`sendText`/`sendMedia`) no backend está defasado frente ao schema da Evolution v1.8.
- Webhook recebe eventos, mas o envio real da resposta da VIVA ao WhatsApp ainda está pendente (TODO).
- Rotas `/api/v1/whatsapp-chat/*` estão com erro 500 por incompatibilidade de modelagem (enum no ORM vs varchar no banco).
- Frontend `/whatsapp` ainda está em placeholder e `/whatsapp/conversas` usa token incorreto + URL hardcoded.

---

## Proposta de Aplicação (Etapa 2)

1. Alinhar ambiente Evolution/Backend
   - Padronizar `EVOLUTION_API_KEY`, `WA_INSTANCE_NAME` e webhook da instância.
2. Corrigir serviço WhatsApp no backend
   - Ajustar parser de status e payloads `sendText`/`sendMedia` para contrato atual da Evolution.
3. Corrigir API de conversas
   - Eliminar erro 500 em `/whatsapp-chat/*` ajustando mapeamento ORM/schema.
4. Ligar frontend ao backend
   - Implementar painel `/whatsapp` (status, conectar, desconectar, QR).
   - Migrar `/whatsapp/conversas` para client `api` com `access_token` e base URL via env.
5. Validar ponta a ponta
   - Mensagem de entrada -> webhook -> resposta VIVA -> envio real WhatsApp -> histórico no frontend.

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
- Etapa 2: WhatsApp funcional e integrado (em execução)
- Etapa 3: Protocolo final com DNS, SSL e hardening (pendente)

---

## Documentação Atualizada

- `docs/INTEGRACAO_WHATSAPP_VIVA.md`
- `docs/STATUS.md`
- `docs/SESSION.md`
- `docs/DECISIONS.md`
- `docs/BUGSREPORT.md`

---

*Atualizado em: 2026-02-07*
