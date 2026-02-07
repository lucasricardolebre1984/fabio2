# SESSION - contexto atual da sessao

Sessao ativa: 07/02/2026
Status: alinhamento fechado e V1.5 homologada localmente com cliente
Branch: main

## Resumo executivo
Nesta sessao, o cliente (Lebre + Fabio) fechou o pacote definitivo de
atendimento WhatsApp da Viviane para a Rezeta, com foco em atendimento humano,
conversao e controle de operacao.

## Definicoes aprovadas
- Modo B: VIVA conduz quase tudo.
- Persona: Viviane, consultora de negocios da Rezeta.
- Tom: hibrido (consultivo, direto, cordial, simples e acolhedor).
- Fluxo: objetivo -> perfil -> urgencia -> proximo passo.
- Politica P1 com fallback P2 em conversa formal.
- SLA 24/7 com callback em ate 15 minutos.
- 3 tentativas maximas sem resposta antes de encerrar.
- Coleta minima obrigatoria: nome, telefone, servico, cidade e urgencia.

## Regras comerciais
- Diagnostico 360 como primeira recomendacao.
- Venda direta sem 360 para servicos simples:
  - Limpa Nome
  - Aumento de Score
  - Aumento de Rating
- Oferta inicial com +15% sobre tabela de referencia.
- Negociacao de valor final somente atendimento humano.
- Motivo financeiro no nao fechamento deve ser registrado para follow-up.

## Fontes consolidadas na sessao
- `frontend/src/app/viva/REGRAS/Descrição_Detalhada_dos_Serviços_Rezeta_Brasil.md`
- `frontend/src/app/viva/REGRAS/Tabela Precços IA.xlsx`
- `frontend/src/app/viva/REGRAS/tabela_precos_ia_01_planilha1.csv`

## Gate institucional atual
V1 tecnica aplicada com base de conhecimento carregada em container. Proximo
passo e evoluir para melhorias incrementais sem quebrar o fluxo homologado.

## Atualizacao tecnica do fim da sessao
- VIVA migrada para OpenAI como provedor principal e unico no runtime.
- Chat/Audio/Imagem/Visao ativos via OpenAI.
- `zai_service.py` removido do backend ativo para eliminar conflito.
- Governanca Evolution consolidada:
  - instancia oficial `fc-solucoes`
  - webhook unico para backend
  - eventos ativos `MESSAGES_UPSERT` e `CONNECTION_UPDATE`
  - integracoes nativas do Evolution desativadas para evitar dupla automacao.

---

Atualizado em: 07/02/2026
