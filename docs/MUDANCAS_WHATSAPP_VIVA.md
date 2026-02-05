# 📋 Mudanças: Integração WhatsApp + IA VIVA

> **Data:** 2026-02-05  
> **Branch:** main  
> **Status:** Em uso local

---

## Resumo do Ciclo Atual

- Chat interno VIVA publicado em `/viva`
- Menu lateral com prompts específicos
- Integração WhatsApp com histórico de conversas
- Modelos Z.AI definidos para chat, visão, imagem, áudio e vídeo

---

## Novas Funcionalidades

Chat IA VIVA (Web)
- UI estilo chat com anexos
- Prompts laterais: Landing Pages, Logos & Brand, Imagens FC, Imagens Rezeta
- Upload de imagem para análise
- Upload de áudio (botão presente, operação pendente)

WhatsApp
- Webhook para Evolution API
- Tabelas de conversas e mensagens
- Painel `/whatsapp/conversas`

---

## Modelos Z.AI (Oficiais)

- Chat: GLM-4.7
- Visão: GLM-4.6V
- Imagem: GLM-Image
- Áudio: GLM-ASR-2512
- Vídeo: CogVideoX-3

---

## Status Atual

- Chat: OK
- Visão: OK
- Imagem: OK
- Áudio: NÃO funciona (botão)

---

## Observações Técnicas

- Chat interno usa OpenRouter quando há chave configurada
- Sem OpenRouter, VIVA opera em modo local com templates
- WhatsApp utiliza VivaIAService para respostas automáticas

---

*Documento atualizado em: 2026-02-05*
