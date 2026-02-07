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

---

## Ciclo 2026-02-07 - pacote definitivo aprovado com cliente

- Definido modo de operacao B para atendimento comercial.
- Persona oficial definida: Viviane, consultora de negocios da Rezeta.
- Politica de resposta P1/P2 fechada com tom hibrido.
- SLA 24/7 com callback em ate 15 minutos aprovado.
- Coleta minima de lead padronizada (nome, telefone, servico, cidade, urgencia).
- Politica comercial fechada:
  - Diagnostico 360 como recomendacao inicial.
  - Venda direta para Limpa Nome, Score e Rating.
  - Oferta inicial com margem de 15%.
  - Negociacao final apenas no atendimento humano.
- Base de conhecimento publicada em:
  - `frontend/src/app/viva/REGRAS/Descrição_Detalhada_dos_Serviços_Rezeta_Brasil.md`
  - `frontend/src/app/viva/REGRAS/tabela_precos_ia_01_planilha1.csv`

Status do ciclo: documentacao concluida, aguardando execucao tecnica da V1.
