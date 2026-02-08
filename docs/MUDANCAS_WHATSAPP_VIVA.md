# 📋 Mudanças: Integração WhatsApp + IA VIVA

> **Data:** 2026-02-08  
> **Branch:** main  
> **Status:** Em uso local

---

## Resumo do Ciclo Atual

- Chat interno VIVA publicado em `/viva`
- Menu lateral com prompts específicos
- Integração WhatsApp com histórico de conversas
- Modelos OpenAI definidos para chat, visao, imagem e audio

---

## Novas Funcionalidades

Chat IA VIVA (Web)
- UI estilo chat com anexos
- Prompts laterais: Landing Pages, Logos & Brand, Imagens FC, Imagens Rezeta
- Upload de imagem para análise
- Upload de áudio:
  - WhatsApp/webhook: ativo (transcricao)
  - chat interno `/viva`: botao ainda pendente (`BUG-012`)

WhatsApp
- Webhook para Evolution API
- Tabelas de conversas e mensagens
- Painel `/whatsapp/conversas`

---

## Modelos OpenAI (Oficiais)

- Chat: gpt-5-mini
- Visao: gpt-4o-mini
- Imagem: gpt-image-1
- Audio: gpt-4o-mini-transcribe

---

## Status Atual

- Chat: OK
- Visão: OK
- Imagem: OK
- Audio: parcial
  - webhook e endpoint: OK
  - botao do chat interno: pendente

---

## Observações Técnicas

- Chat interno e WhatsApp usam OpenAI como provedor institucional
- Modo local permanece como contingencia
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

## Ciclo 2026-02-07 (tarde) - migracao completa para OpenAI

- Removido `zai_service.py` do runtime.
- `VivaIAService` e webhook de audio roteados para OpenAI.
- `/api/v1/viva/chat` migrado para OpenAI no fluxo principal.
- `/api/v1/viva/image/generate` migrado para OpenAI Images.
- Corrigido bug de imagem (`Unknown parameter: response_format`).
- Corrigido bug de chave OpenAI vazia por override no compose.

Status do ciclo: OpenAI ativo e backend saudável.

## Ciclo 2026-02-08 (madrugada) - estabilizacao de PDF de contratos

- Corrigido `BUG-026` no backend:
  - fallback de renderizacao `Playwright -> WeasyPrint`;
  - pin de dependencia `pydyf==0.10.0` para compatibilidade com WeasyPrint.
- Validado endpoint:
  - `GET /api/v1/contratos/{id}/pdf` retornando `200` com `application/pdf`.
- Documentacao institucional alinhada (`STATUS`, `SESSION`, `DECISIONS`, `BUGSREPORT`, `MANUAL`).
