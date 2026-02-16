---
name: generate_campanha_neutra
description: Gera copy e direcao de imagem para campanhas com prioridade total ao pedido atual do usuario. Acionar quando houver pedidos como criar campanha, gerar conteudo, gerar imagem, anuncio, criativo, post, arte para campanha.
---

# Skill Generate Campanha Neutra

## Objetivo
Gerar campanha sem repetir padrao antigo, com foco no contexto atual da conversa.

## Entradas
- pedido atual do usuario
- contexto do chat
- modo de marca (FC ou REZETA), quando informado

## Regras de execucao
1. Prioridade absoluta ao pedido atual do usuario.
2. Nao travar personagem, cenario ou composicao por historico antigo.
3. Se o usuario fixar personagem/cena, obedecer exatamente.
4. Se a marca nao estiver clara, perguntar apenas: FC ou Rezeta?
5. Nao inventar dados da empresa nem prometer resultado financeiro.

## Saida obrigatoria
Retornar JSON valido com chaves exatas:
- headline
- subheadline
- bullets (3 a 5)
- quote
- cta
- scene

## Gatihos de uso
- "conteudo"
- "criar campanha"
- "gerar campanha"
- "gerar imagem"
- "criativo"
- "anuncio"

## Nota
Se o pedido for apenas planejamento (sem gerar imagem), manter a mesma linha mas retornar somente plano textual curto.
