# SESSION - contexto atual da sessao

Sessao ativa: 08/02/2026
Status: V1.6 homologada localmente com cliente apos estabilizacao de PDF
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

## Validacao read-only (2026-02-07)
- Confirmado: BUG-013, BUG-014, BUG-017 e BUG-019 sem regressao no fluxo atual.
- Novo achado: criacao de contrato quebra com `Template bacen nao encontrado` (`BUG-025`).
- Novo achado: geracao de PDF de contrato quebra com `ModuleNotFoundError: playwright` (`BUG-026`).
- Acao pendente: corrigir pipeline de templates/pdfs antes de nova rodada institucional de contratos.

## Atualizacao tecnica adicional (2026-02-07 - noite)
- `BUG-025` corrigido:
  - fallback de template (`bacen/serasa/protesto`) para ambiente sem seed;
  - geracao de numero de contrato passou a usar maior sequencial do ano (evita duplicidade).
- Cadastro de clientes reforcado:
  - contrato novo volta a vincular/criar cliente automaticamente;
  - endpoint `POST /api/v1/clientes/sincronizar-contratos` para recuperar contratos orfaos.
- Frontend entregue com minimo funcional:
  - `Clientes`: listagem real + cadastro manual + botao de sincronizacao.
  - `Agenda`: criacao/listagem/conclusao/exclusao de compromissos.
- VIVA (chat interno com Fabio) integrada com agenda:
  - comando suportado: `agendar TITULO | DD/MM/AAAA HH:MM | descricao opcional`;
  - cria evento real no backend e retorna confirmacao.
- `BUG-026` corrigido:
  - fallback robusto de geracao PDF no backend (Playwright -> WeasyPrint);
  - dependencia `pydyf` fixada para versao compativel (`0.10.0`);
  - validacao real da rota `GET /api/v1/contratos/{id}/pdf` com retorno `200`.

## Validacao read-only adicional (2026-02-08)
- `GET /health`: `200` (`healthy`).
- `GET /api/v1/whatsapp/status`: `200`.
- `GET /api/v1/whatsapp-chat/status`: `200`.
- `GET /api/v1/whatsapp-chat/conversas?limit=5`: `200`.
- `GET /api/v1/contratos/{id}/pdf`: `200` com `application/pdf`.

---

Atualizado em: 08/02/2026
