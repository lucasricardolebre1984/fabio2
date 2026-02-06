# SESSION - Contexto Atual da Sessão

> **Sessão Ativa:** 2026-02-06  
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
- Erro ativo: `StackOverflowError` na geração de imagens com prompt extra longo (REZETA/FC)
- Erro ativo: upload de imagem falha com PNG (MIME assumido como JPEG)
- Erro ativo: fundo da imagem não respeita paleta/brief do prompt (BUG-015)
- Erro ativo: arte final perde partes do texto (overlay truncado) (BUG-016)

## Ajustes desta sessão

- Persona simples da VIVA adicionada ao prompt principal (contexto de servidor, empresas FC/Rezeta e capacidades de imagem/áudio/vídeo)
- Prompts secundários continuam em `frontend/src/app/viva/PROMPTS` para modos específicos
- Roteiro de deploy 100% Docker criado com etapas de produção
- Roteamento de intenção de imagem no backend (`/viva/chat`) com retorno de mídia estruturada
- Prompts laterais enviados como `prompt_extra` para o backend
- Geração de fundo sem texto + overlay no front (arte final), ainda com perdas de conteúdo e paleta

---

## Protocolo GODMOD aplicado nesta sessão

Fluxo aplicado
- Mapeamento completo do frontend `/viva` e backend `/api/v1/viva/*`
- Diagnóstico com causa-raiz (prompt longo + overlay parcial)
- Arquitetura de correção definida para FC e Rezeta
- Registro formal em `STATUS` e `DECISIONS`
- Rollback obrigatório documentado

Critério institucional da sessão
- Nenhuma entrega sem plano de rollback
- Toda comunicação e evidência em pt-BR

---

## Plano de Etapas (Ubuntu)

- Etapa 1: Roteiro de deploy 100% Docker (concluída)
- Etapa 2: WhatsApp funcional e integrado ao backend (pendente)
- Etapa 3: Protocolo final com DNS, SSL e hardening (pendente)

---

*Atualizado em: 2026-02-06*
