# SESSION - Contexto Atual da Sessão

> **Sessão Ativa:** 2026-02-05  
> **Status:** ✅ Sistema estável - VIVA e contratos operacionais  
> **Branch:** main

---

## Estado Atual do Sistema

Funcionalidades principais
- Contratos com template Bacen
- Criação, edição e visualização institucional
- PDF via impressão do navegador
- Clientes e agenda funcionando
- WhatsApp integrado via Evolution API
- VIVA chat interno em `/viva`
- Conversas WhatsApp em `/whatsapp/conversas`

VIVA (modelos)
- Chat: GLM-4.7
- Visão: GLM-4.6V
- Imagem: GLM-Image
- Áudio: GLM-ASR-2512 (botão não operacional)
- Vídeo: CogVideoX-3

---

## Rotas Importantes

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Docs API: http://localhost:8000/docs
- VIVA: http://localhost:3000/viva

---

## Observações

- PDF é gerado no frontend com `window.print()`
- Chat interno usa OpenRouter quando configurado, senão modo local
- WhatsApp usa webhook para alimentar conversas no banco
- Roteiro de deploy Ubuntu 100% Docker documentado em `docs/DEPLOY_UBUNTU_DOCKER.md`

## Ajustes desta sessão

- Persona simples da VIVA adicionada ao prompt principal (contexto de servidor, empresas FC/Rezeta e capacidades de imagem/áudio/vídeo)
- Prompts secundários continuam em `frontend/src/app/viva/PROMPTS` para modos específicos
- Roteiro de deploy 100% Docker criado com etapas de produção

---

## Plano de Etapas (Ubuntu)

- Etapa 1: Roteiro de deploy 100% Docker (concluída)
- Etapa 2: WhatsApp funcional e integrado ao backend (pendente)
- Etapa 3: Protocolo final com DNS, SSL e hardening (pendente)

---

*Atualizado em: 2026-02-05*
