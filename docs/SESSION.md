# SESSION - contexto atual da sessao

Sessao ativa: 09/02/2026
Status: V1.7 local com fluxo de clientes/contratos saneado (unicidade CPF/CNPJ)
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

## Atualizacao tecnica (2026-02-09 - clientes/contratos)
- Rollback snapshot criado antes do fix:
  - `rollback-20260209-clientes-unicos-pre-fix`
- Correcao do bug de fechamento de contrato por duplicidade de cliente:
  - causa raiz: `MultipleResultsFound` em `POST /api/v1/contratos` quando havia
    mais de um cliente para o mesmo CPF/CNPJ normalizado.
- Backend:
  - `ClienteService.get_by_documento` passou a selecionar cliente canonico de
    forma deterministica (sem `scalar_one_or_none` em base legada duplicada);
  - novo saneamento institucional:
    - `POST /api/v1/clientes/deduplicar-documentos` (admin),
    - relink de contratos/agenda para cliente canonico,
    - remocao de duplicados.
  - `ContratoService.create` passou a reutilizar busca canonica de cliente.
- Frontend:
  - `/clientes` com acoes de editar/excluir;
  - botao para saneamento de duplicados CPF/CNPJ;
  - `/contratos/novo` busca cliente por documento e preenche dados automaticamente.

## Validacao read-only adicional (2026-02-09)
- `GET /api/v1/clientes/documento/334.292.588-47`: `200`.
- `POST /api/v1/contratos` com CPF historicamente duplicado: `201`.
- `POST /api/v1/clientes` com mesmo CPF: `409` (bloqueio correto).
- `POST /api/v1/clientes/deduplicar-documentos`: `200`.
- Consulta SQL de duplicidade normalizada em `clientes`: `0` linhas duplicadas.
- Correcao adicional de metricas:
  - `total_contratos` agora atualiza no delete de contrato;
  - `POST /api/v1/clientes/sincronizar-contratos` passou a recalcular metricas de todos os clientes (`clientes_recalculados`).

---

Atualizado em: 09/02/2026

## Atualizacao tecnica (2026-02-09 - layout contratos + CADIN)
- Rollback snapshot criado antes desta fase:
  - `rollback-20260209-layout-cadin-pre`
- Correcao institucional de branding em contratos:
  - logo oficial `logo2.png` aplicada no preview de contrato;
  - logo oficial aplicada na geracao PDF frontend (`frontend/src/lib/pdf.ts`);
  - logo oficial aplicada na geracao PDF backend (Playwright).
- Inclusao do novo contrato CADIN PF/PJ:
  - template `contratos/templates/cadin.json` criado com base em `contratos/cadinpfpjmodelo.docx`;
  - menu de contratos passou a exibir card ativo de CADIN;
  - `/contratos/novo` passou a aceitar `?template=cadin` e enviar `template_id` correto;
  - visualizacao `/contratos/[id]` com subtitulo e clausulas base para CADIN.


## Atualizacao tecnica (2026-02-09 - logo transparente + CADIN canonico)
- Rollback local do estado atual registrado em `docs/ROLLBACK/rollback-20260209-122338.patch`.
- Marca de contrato trocada para `logo2.png` (transparente) no preview e nos dois pipelines de PDF.
- Contrato CADIN alinhado ao `cadinpfpjmodelo.docx` com clausulas 1a-5a completas e acentuacao correta em:
  - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
  - `frontend/src/lib/pdf.ts`
  - `backend/app/services/pdf_service_playwright.py`
  - `contratos/templates/cadin.json`
- Documentacao atualizada para refletir logo oficial e conteudo juridico canonico do CADIN.

## Atualizacao tecnica (2026-02-09 - fix de acentuacao + escala de layout)
- Rollback local adicional criado antes do ajuste:
  - `docs/ROLLBACK/rollback-20260209-124435.patch`
- Correcao de texto corrompido (mojibake) no fluxo de contrato:
  - preview (`frontend/src/app/(dashboard)/contratos/[id]/page.tsx`)
  - PDF frontend (`frontend/src/lib/pdf.ts`)
  - PDF backend (`backend/app/services/pdf_service_playwright.py`)
- Ajuste leve de tamanho do layout para melhorar legibilidade no preview e no PDF.

## Atualizacao tecnica (2026-02-09 - fix pontual local_assinatura legado)
- Rollback local adicional criado antes deste ajuste:
  - `docs/ROLLBACK/rollback-20260209-131517.patch`
- Correcao pontual para valor legado em `local_assinatura`:
  - preview (`frontend/src/app/(dashboard)/contratos/[id]/page.tsx`)
  - PDF frontend (`frontend/src/lib/pdf.ts`)
  - PDF backend (`backend/app/services/pdf_service_playwright.py`)
- Correcao preventiva na origem do dado:
  - default de `local_assinatura` em `frontend/src/app/(dashboard)/contratos/novo/page.tsx` para `Ribeirao Preto/SP`.
- Resultado: assinatura final nao exibe mais `Ribeirao` corrompido quando o registro vem com encoding legado.

## Atualizacao tecnica (2026-02-09 - contratos menu + historico clientes)
- Rollback local adicional criado antes desta rodada:
  - `docs/ROLLBACK/rollback-20260209-164001.patch`
  - `docs/ROLLBACK/rollback-20260209-164001-staged.patch`
  - `docs/ROLLBACK/rollback-20260209-164001-untracked.txt`
- Correcao de frontend em `/contratos`:
  - eliminacao de mojibake em descricoes de cards e bloco de acoes rapidas.
- Correcao de backend em `/api/v1/clientes`:
  - `total_contratos` passa a ser calculado por agregacao real da tabela `contratos`.
- Evolucao de UX em `/clientes`:
  - novo campo de historico por cliente (botao `Ver historico`) com lista de contratos vinculados.
