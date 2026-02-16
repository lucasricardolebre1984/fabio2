---
name: interpretar_contratos
description: Interpreta clausulas e contratos com linguagem clara, destacando riscos, obrigacoes, prazos e pendencias. Acionar quando houver pedido para analisar contrato, clausula, aditivo, multa, garantia, vigencia ou assinatura.
---

# Skill Interpretar Contratos

## Objetivo
Explicar contratos de forma pratica para operacao comercial e juridica basica.

## Entradas
- texto integral ou parcial do contrato
- pergunta especifica do usuario

## Fluxo
1. Identificar tipo do documento (contrato, aditivo, proposta, termo).
2. Extrair pontos criticos:
- partes
- objeto
- vigencia
- valores
- reajuste
- multa
- rescisao
- garantias
- obrigacoes das partes
3. Responder em linguagem simples, sem juridiqus desnecessario.
4. Se faltar trecho essencial, pedir somente o trecho faltante.

## Saida padrao
- Resumo executivo (curto)
- Riscos principais
- Acoes recomendadas
- Pendencias para assinatura/execucao

## Limites
- Nao substituir advogado.
- Nao inventar clausula ausente no texto.
