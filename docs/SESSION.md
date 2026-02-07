# SESSION - Contexto Atual da Sessão

> **Sessão Ativa:** 2026-02-07  
> **Status:** ⚠️ Diagnóstico concluído, execução técnica WhatsApp pendente  
> **Branch:** main

---

## Estado Atual do Sistema

Funcionalidades principais
- Contratos com template Bacen
- Criação, edição e visualização institucional
- PDF via impressão do navegador
- Clientes e agenda funcionando
- VIVA chat interno em `/viva`
- Módulo WhatsApp com backend/frontend parcialmente conectado

VIVA (modelos)
- Chat: GLM-4.7
- Visão: GLM-4.6V
- Imagem: GLM-Image
- Áudio: GLM-ASR-2512 (botão não operacional)
- Vídeo: CogVideoX-3

---

## Evidências Técnicas da Sessão

- `localhost:8080` ativo com Evolution e instância `Teste` em estado `open`.
- `/api/v1/whatsapp/status` no backend reporta desconectado por divergência de instância/chave.
- `/api/v1/whatsapp-chat/*` retorna erro 500 no estado atual.
- Webhook `/api/v1/webhook/evolution` responde health, porém envio real da resposta da VIVA ao WhatsApp ainda não foi implementado.
- Frontend `/whatsapp` está em placeholder e `/whatsapp/conversas` usa token/key incompatível com login atual.

---

## Proposta Registrada para Execução

1. Alinhar configuração Evolution/Backend (`EVOLUTION_API_KEY`, `WA_INSTANCE_NAME`, webhook).
2. Corrigir `whatsapp_service.py` para contrato atual da Evolution v1.8.
3. Corrigir erro 500 de `whatsapp-chat` (modelagem ORM x schema).
4. Ligar frontend WhatsApp aos endpoints reais com autenticação correta.
5. Validar fluxo ponta a ponta com evidências de envio/recebimento.

---

## Bugs Abertos nesta Sessão

- BUG-017: erro 500 em `/whatsapp-chat/*`
- BUG-018: divergência de instância/chave Evolution
- BUG-019: token incorreto e URL hardcoded no frontend WhatsApp
- BUG-020: webhook sem envio real de resposta ao WhatsApp

---

## Plano de Etapas (Ubuntu)

- Etapa 1: Roteiro de deploy 100% Docker (concluída)
- Etapa 2: WhatsApp funcional e integrado ao backend/frontend (em execução)
- Etapa 3: Protocolo final com DNS, SSL e hardening (pendente)

---

*Atualizado em: 2026-02-07*
