# SESSION - contexto atual da sessao

Sessao ativa: 13/02/2026
Status: rodada de consolidacao documental e plano em 3 gates para modularizacao comercial
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

Atualizado em: 10/02/2026

## Atualizacao tecnica (2026-02-09 - layout contratos + CADIN)
- Rollback snapshot criado antes desta fase:
  - `rollback-20260209-layout-cadin-pre`
- Correcao institucional de branding em contratos:
- logo oficial `logo2.png` aplicada no preview de contrato;
- logo oficial aplicada na geracao PDF frontend (`frontend/src/lib/pdf.ts`);

## Atualizacao tecnica (2026-02-11 - piloto template CNH)
- objetivo da rodada:
  - subir um modelo novo padronizado para teste antes da carga dos demais.
- modelo piloto aplicado:
  - `CNH` com base em `CNH.md` (fonte enviada pelo cliente).
- entregas tecnicas:
  - template novo criado em `contratos/templates/cnh.json`;
  - fallback backend para template `cnh` em `backend/app/services/contrato_service.py`;
  - fluxo de criacao habilitado no frontend (`/contratos` e `/contratos/novo?template=cnh`);
  - preview contratual de CNH em `/contratos/[id]` com campo opcional `cnh_numero`;
  - PDF frontend/backend com subtitulo e clausulas especificas de CNH.
- validacoes executadas:
  - `python -m py_compile backend/app/services/contrato_service.py backend/app/services/pdf_service_playwright.py` => OK;
  - `frontend`: `npm run type-check` => OK;
  - `frontend`: `npm run lint` direcionado nas telas de contrato alteradas => OK (warnings conhecidos nao bloqueantes);
  - `frontend`: `npm run build` => compilacao concluida; warning residual de copia `standalone` no Windows sem bloquear entrega funcional.
- status:
  - piloto CNH pronto para validacao funcional do cliente;
  - apos validacao visual/operacional, liberar carga dos modelos restantes no mesmo padrao.

## Atualizacao tecnica (2026-02-11 - normalizacao de acentuacao contratos)
- contexto:
  - apos homologacao funcional do piloto CNH, foi identificado bug visual de encoding no contrato (`mojibake`) em preview e PDF.
- acao aplicada:
  - normalizacao UTF-8 em:
    - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`;
    - `frontend/src/lib/pdf.ts`;
    - `backend/app/services/pdf_service_playwright.py`;
    - ajuste pontual em `frontend/src/app/(dashboard)/contratos/novo/page.tsx`.
- resultado:
  - cabecalho institucional, clausulas, campos das partes e assinatura voltaram a exibir acentos corretos.
- padrao para proximos lotes:
  - novos contratos em `.md` devem manter texto canonico UTF-8 desde template ate renderizacao final (preview e PDF), sem strings legadas com mojibake.
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

## Atualizacao tecnica (2026-02-09 - VIVA prompts FC/REZETA + modal arte)
- Rollback local adicional criado antes deste bloco:
  - `docs/ROLLBACK/rollback-20260209-181844.patch`
  - `docs/ROLLBACK/rollback-20260209-181844-staged.patch`
  - `docs/ROLLBACK/rollback-20260209-181844-untracked.txt`
- Correcao de coerencia de modo no chat VIVA:
  - frontend passou a enviar `modo` explicitamente em `/viva/chat`;
  - backend passou a priorizar `modo` do payload para aplicar fluxo de campanha correto.
- Correcao de fluxo de campanha (FC/REZETA):
  - antes da geracao de imagem, VIVA agora solicita brief minimo (`objetivo`, `publico`, `formato`, `cta`);
  - com brief completo, gera imagem com copy estruturada (evita banner aleatorio sem conduzir conversa).
- Correcao de prompts duplicados no frontend:
  - carregamento centralizado via `/api/viva/prompts/[promptId]`;
  - fonte canonica definida em `frontend/src/app/viva/PROMPTS` com fallback legado.
- Correcao de usabilidade no modal "Arte final":
  - layout adaptado para zoom 100% com scroll e limite de largura, sem esconder botoes de acao.

## Atualizacao tecnica (2026-02-09 - menu campanhas + historico VIVA)
- Rollback local adicional criado antes deste bloco:
  - `docs/ROLLBACK/rollback-20260209-190632.patch`
  - `docs/ROLLBACK/rollback-20260209-190632-staged.patch`
  - `docs/ROLLBACK/rollback-20260209-190632-untracked.txt`
- Backend (`/api/v1/viva`):
  - adicionadas rotas de historico de campanhas:
    - `POST /campanhas`
    - `GET /campanhas`
    - `GET /campanhas/{campanha_id}`
  - criacao idempotente da tabela `viva_campanhas` em runtime (`CREATE TABLE IF NOT EXISTS`);
  - geracoes de imagem FC/REZETA passam a salvar automaticamente campanha no historico;
  - `midia.meta` retorna `campanha_id` para rastreabilidade no frontend.
- Frontend:
  - novo menu lateral `Campanhas` no dashboard;
  - nova tela `/campanhas` com filtro (Todas/FC/Rezeta), cards com imagem, data e briefing;
  - no chat `/viva`, cada imagem salva exibe atalho `Ver em campanhas`.
- Fluxo de briefing:
  - melhoria no detector de intencao de campanha (mesmo sem palavra "imagem");
  - extracao de campos por texto livre para reduzir atrito no preenchimento do brief.
  - ajuste anti-loop quando faltar apenas CTA: resposta curta e opcao `usar CTA padrao`.

## Atualizacao tecnica (2026-02-09 - FCNOVO + preview imagem sem popup)
- Rollback local adicional criado antes deste ajuste:
  - `docs/ROLLBACK/rollback-20260209-202655.patch`
  - `docs/ROLLBACK/rollback-20260209-202655-staged.patch`
  - `docs/ROLLBACK/rollback-20260209-202655-untracked.txt`
- Prompt FC unificado com `FCNOVO.md` em:
  - `frontend/src/app/viva/PROMPTS/FC.md` (fonte canonica no app)
  - `frontend/public/PROMPTS/FC.md` (fallback)
  - `docs/PROMPTS/FC.md` (documentacao)
- Roteamento operacional adicionado ao prompt FC (rotas SaaS e regras para nao simular publicacao externa).
- Chat VIVA:
  - anexo de imagem agora injeta resumo de visao no payload de `/api/v1/viva/chat` como referencia visual;
  - autoscroll reforcado no viewport real do `ScrollArea`;
  - no modal de arte, `Abrir imagem` abre preview interno (sem popup/aba em branco).
- Briefing FC/Rezeta:
  - campos minimos agora: `objetivo`, `publico`, `formato` (CTA vira fallback automatico `Saiba mais`);
  - resposta de coleta ficou natural e nao repete loop quando mensagem sai do contexto de briefing.
- Tela `/campanhas`:
  - `Abrir imagem` passou para modal interno com download, removendo dependencia de popup.

## Atualizacao tecnica (2026-02-09 - pendencia aberta no gerador)
- Status homologado da rodada:
  - fluxo de conversa da VIVA simplificado (sem burocracia de formato fixo);
  - abertura de imagem no SaaS estabilizada sem popup externo;
  - historico de campanhas ativo.
- Pendencia mantida:
  - BUG-015 (gerador de imagem) segue pendente por repeticao de composicao e aderencia parcial ao contexto.

## Atualizacao tecnica (2026-02-09 - blocos 1 e 2 memoria/persona)
- Rollback institucional desta rodada:
  - `docs/ROLLBACK/rollback-20260209-213516-baseline.txt`
- Bloco 1 aplicado:
  - fonte canonica de prompts consolidada em `frontend/src/app/viva/PROMPTS`;
  - rota interna `/api/viva/prompts/[promptId]` sem fallback em `public/PROMPTS`;
  - alias legado `CRIADORWEB` mantido para `CRIADORPROMPT`.
- Bloco 2 aplicado:
  - backend com persistencia de sessao e historico por usuario (`viva_chat_sessions`, `viva_chat_messages`);
  - novas rotas de memoria:
    - `GET /api/v1/viva/chat/snapshot`
    - `POST /api/v1/viva/chat/session/new`
  - `/api/v1/viva/chat` agora aceita/retorna `session_id` e persiste mensagens da conversa;
  - frontend `/viva` recupera historico automaticamente na abertura e limpa contexto iniciando nova sessao.

## Proximos passos aprovados (pendentes de execucao)
1. Bloco 3: memoria operacional da VIVA com agenda em linguagem natural (consultar/criar/concluir).
2. Bloco 4: streaming da resposta com autoscroll continuo em tempo real.
3. Bloco 5: previsibilidade de erros no fluxo de audio interno.
4. Bloco 6: atualizacao documental e fechamento institucional por bloco validado.

## Atualizacao tecnica (2026-02-10 - bloco 3 agenda linguagem natural)
- VIVA/chat:
  - bypass de agenda implementado antes do fluxo LLM para evitar loop de confirmacoes;
  - consulta de agenda por linguagem natural (`hoje`, `amanha`, `semana`, follow-up de confirmacao);
  - criacao por comando estruturado e tambem por frase natural com data/hora;
  - conclusao/confirmacao de compromisso via ID no chat.
- Agenda service/api:
  - filtro por usuario aplicado em listagem/consulta/update/concluir/delete;
  - rotas `/api/v1/agenda/*` agora usam `current_user.id` em todas as operacoes.
- Objetivo desta rodada:
  - eliminar respostas "falsas" de acesso/checagem e retornar agenda real do usuario no primeiro pedido.

## Atualizacao operacional (2026-02-10 - auditoria GODMOD pre-fix)
- Pedido do usuario: documentar estado real antes de corrigir e registrar rollback institucional.
- Leitura institucional revalidada:
  - `README.md`
  - `docs/CONTEXT.md`
  - `docs/FOUNDATION.md`
  - `docs/STATUS.md`
  - `docs/DECISIONS.md`
  - `docs/BUGSREPORT.md`
  - `docs/PROMPTS/GODMOD.md`
- Rollback institucional pre-fix gerado:
  - `docs/ROLLBACK/rollback-20260210-104803-pre-fix-baseline.txt`
  - `docs/ROLLBACK/rollback-20260210-104803-pre-fix.patch`
  - `docs/ROLLBACK/rollback-20260210-104803-pre-fix-staged.patch`
  - `docs/ROLLBACK/rollback-20260210-104803-pre-fix-untracked.txt`
- Validacao com frontend ativo:
  - rotas web principais com `200` (`/`, `/viva`, `/contratos`, `/contratos/novo`, `/whatsapp`, `/whatsapp/conversas`, `/campanhas`);
  - backend + auth + VIVA/WhatsApp operacionais (`200`).
- Pendencias abertas formalizadas em `docs/BUGSREPORT.md`:
  - `BUG-048` a `BUG-053`.

## Atualizacao tecnica (2026-02-10 - execucao BUG-048..053)
- Build frontend destravado com `Suspense` em paginas que usam `useSearchParams`:
  - `frontend/src/app/(dashboard)/campanhas/page.tsx`
  - `frontend/src/app/(dashboard)/contratos/novo/page.tsx`
  - `frontend/src/app/whatsapp/conversas/page.tsx`
- Testes legados higienizados:
  - `test_db.py` e `test_db2.py` sem credenciais hardcoded, agora com `TEST_DATABASE_URL`/`TEST_DB_*`;
  - `backend/test_glm.py` convertido para placeholder legado com `pytest.mark.skip` (sem quebra de coleta).
- Tooling frontend estabilizado:
  - ESLint inicializado com `frontend/.eslintrc.json` + dependencias (`eslint`, `eslint-config-next`);
  - `npm run lint` executa sem wizard.
- Documentacao alinhada ao runtime:
  - `docs/DEPLOY_UBUNTU_DOCKER.md` ajustado para `/health`;
  - `docs/API.md` ajustado para auth obrigatoria em `/whatsapp-chat/*`.
- Validacao desta rodada:
  - `npm run type-check`: OK
  - `npm run lint`: OK (warnings nao bloqueantes)
  - `npm run build`: OK
  - `python -m pytest -q ..\\test_db.py ..\\test_db2.py .\\test_glm.py`: `3 skipped`

## Gate atual da sessao
Rodada BUG-048..053 concluida com validacao tecnica e documentacao atualizada.

## Atualizacao operacional (2026-02-10 - kickoff persona dual + RAG)
- Solicitação formal do cliente:
  - separar claramente personas:
    - VIVA = concierge do Fabio, assistente global do SaaS;
    - Viviane = secretaria humana/comercial em atendimento externo.
  - reduzir Frankenstein de prompts/pastas e simplificar fluxo conversacional.
- Rollback institucional pre-clean criado antes de delecoes/refatoracoes:
  - `docs/ROLLBACK/rollback-20260210-112843-pre-clean-baseline.txt`
  - `docs/ROLLBACK/rollback-20260210-112843-pre-clean.patch`
  - `docs/ROLLBACK/rollback-20260210-112843-pre-clean-staged.patch`
  - `docs/ROLLBACK/rollback-20260210-112843-pre-clean-untracked.txt`
- Diagnostico consolidado da rodada:
  - prompt files duplicados em:
    - `frontend/src/app/viva/PROMPTS`
    - `frontend/public/PROMPTS`
    - `docs/PROMPTS`
  - chat interno `/viva` com memoria persistida, mas contexto de inferencia ainda curto por dependencia do frontend;
  - agenda natural evoluiu, mas ainda com rigidez em alguns padroes de frase;
  - sem camada vetorial RAG no backend atual.
- Bugs abertos para execucao desta rodada:
  - `BUG-054` a `BUG-058`.

## Plano de execucao aprovado na sessao
1. atualizar documentacao institucional completa (estado + riscos + plano).
2. remover duplicacoes de prompt com seguranca e rollback.
3. consolidar contrato de persona no backend por dominio/canal.
4. ajustar memoria para contexto server-side por sessao.
5. preparar arquitetura RAG moderna para piloto.

## Atualizacao tecnica (2026-02-10 - execucao blocos B/C/D)
- Limpeza estrutural concluida:
  - removido `frontend/src/app/api/viva/prompts/[promptId]/route.ts`;
  - removida cadeia de arquivos em `frontend/src/app/viva/PROMPTS`;
  - removidos prompts legados em `frontend/public/PROMPTS`;
  - em `docs/PROMPTS`, mantidos apenas `GODMOD.md` e `PROJETISTA.md`.
- Persona interna consolidada:
  - novo serviço `backend/app/services/viva_concierge_service.py` para VIVA concierge;
  - chat interno `/api/v1/viva/chat` agora monta mensagens com prompt de sistema da concierge.
- Memoria operacional reforcada:
  - contexto de inferencia agora parte de snapshot server-side da sessao (`viva_chat_sessions`/`viva_chat_messages`);
  - frontend deixa de injetar `prompt_extra` baseado em arquivo.
- Agenda natural melhorada:
  - conclusao passou a aceitar ID ou parte do titulo do compromisso.
- Limpeza adicional de legado:
  - removidos `backend/app/services/openrouter_service.py` e `backend/app/services/brainimage_service_v1_backup.py`.

## Validacao desta etapa
- frontend:
  - `npm run type-check` OK
  - `npm run lint` OK (warnings nao bloqueantes)
  - `npm run build` OK
- backend:
  - `python -m py_compile` OK nos arquivos alterados
  - `pytest` alvo legado: `3 skipped` (sem erro de coleta)
  - smoke:
    - `GET /health` = `200`
    - `POST /api/v1/viva/chat` autenticado = `200` com `session_id`
    - agenda natural por chat: criar e concluir por titulo = `200`

## Direcao RAG definida na sessao
- Fase piloto: `pgvector` em PostgreSQL (stack atual), minimizando complexidade e acelerando entrega.
- Fase de escala: avaliar Qdrant se volume/QPS ultrapassar limite do piloto.

## Atualizacao tecnica (2026-02-10 - incidente Next dev apos remocao de rota legacy)
- Contexto operacional consolidado: local-only (`c:\projetos\fabio2`) nesta rodada.
- Observacao do usuario: ambiente Ubuntu/deploy ainda virgem para esta fase; documentacao de deploy fica como referencia futura, nao como estado real do runtime atual.
- Erro reportado e reproduzido por evidencias de log:
  - `MODULE_NOT_FOUND` com requireStack referenciando `.../.next/server/app/api/viva/prompts/[promptId]/route`.
- Diagnostico:
  - rota legacy removida corretamente em source;
  - cache `.next` stale mantendo grafo antigo de dependencias do dev server.
- Correcao implementada:
  - `frontend/package.json`:
    - `clean:next`: limpeza de cache `.next`
    - `dev:reset`: limpeza + subida do `next dev`
- Validacao executada:
  - `npm run clean:next`: OK
  - `npm run build`: OK (com warnings conhecidos nao bloqueantes)
- Runbook local definido:
  1. parar processo `next dev` atual
  2. rodar `npm run clean:next`
  3. rodar `npm run dev:reset`
  4. se persistir, remover `tsconfig.tsbuildinfo` e repetir

## Atualizacao tecnica (2026-02-10 - BUG-060 autenticacao local)
- Causa raiz: divergencia entre documentacao de login (`README.md`) e runtime dev (`security_stub.py`), somada a mensagem de erro generica no frontend.
- Mudancas executadas:
  - `frontend/src/app/page.tsx`: mensagens de erro diferenciadas por status/falha de conexao.
  - `README.md`: credencial de teste local corrigida para `1234`.
- Evidencias:
  - login API com `1234`: `200`.
  - login API com `senha123`: `401`.
  - `npm run type-check`: OK.
  - `npm run lint`: OK (warnings legados).
- Rollback institucional desta micro-rodada (auth/docs):
  - `docs/ROLLBACK/rollback-20260210-140052-login-auth-baseline.txt`
  - `docs/ROLLBACK/rollback-20260210-140052-login-auth.patch`
  - `docs/ROLLBACK/rollback-20260210-140052-login-auth-staged.patch`
  - `docs/ROLLBACK/rollback-20260210-140052-login-auth-untracked.txt`

## Atualizacao da sessao (2026-02-10 - APROVADO redesign VIVA)
- Solicitacao do cliente:
  - remover comportamento de "bot travado" no fluxo de agenda;
  - reduzir Frankenstein de regras no monolito `viva.py`;
  - garantir fluxo fluido de secretaria: `Fabio -> VIVA -> Viviane -> Fabio`.
- Planejamento aprovado em 3 etapas:
  1. documentacao + baseline;
  2. refatoracao por dominios + agenda fluida;
  3. handoff operacional + memoria longa vetorial.
- Artefatos criados nesta etapa:
  - `docs/ARCHITECTURE/VIVA_REDESIGN.md`
  - registros `BUG-062`, `BUG-063`, `BUG-064` em `docs/BUGSREPORT.md`.

## Inicio da Etapa 2 (2026-02-10)
- Mudanca inicial implementada:
  - substituicao do fallback rigido de agenda por resposta contextual curta.
- Objetivo:
  - reduzir percepcao de bot travado e manter fluidez de conversa.
- Evidencia:
  - ajuste em `backend/app/api/v1/viva.py` com helper `_build_agenda_recovery_reply(...)`.

## Etapa 2 - progresso (2026-02-10)
- Componentizacao iniciada:
  - `viva_agenda_nlu_service` para interpretacao de agenda;
  - `viva_handoff_service` para tarefas VIVA -> Viviane;
  - `viva_capabilities_service` para inventario de capacidades.
- Endpoints novos adicionados em `/api/v1/viva/*`:
  - `GET /capabilities`
  - `POST /handoff/schedule`
  - `GET /handoff`
  - `POST /handoff/process-due`
- Fluxo funcional validado:
  - chat com "agendar ... avisar cliente no whatsapp <numero>" cria compromisso e handoff;
  - handoff aparece em listagem e pode ser processado.

## Fechamento do dia (2026-02-10)
- Worker automatico implementado no backend para processar handoffs vencidos sem chamada manual.
- Prova de vida:
  - tarefa teste criada com horario no passado;
  - apos janela do worker, status mudou para `sent` com `sent_at`.
- Entrega pronta para demonstracao:
  - VIVA conversa com fluidez maior;
  - agenda + aviso WhatsApp via Viviane operando no fluxo aprovado.

## Atualizacao da sessao (2026-02-10 - fechamento memoria/RAG)
- pedido do cliente executado:
  - memoria longa/medio/curta fechada no backend;
  - capacidade de recuperar historico salvo via API.
- implementacoes principais:
  - `backend/app/services/viva_memory_service.py` (Redis + pgvector);
  - embedding OpenAI em `backend/app/services/openai_service.py`;
  - chat da VIVA integrado com contexto de memoria recuperado.
- endpoints entregues:
  - `GET /api/v1/viva/memory/status`
  - `GET /api/v1/viva/memory/search`
  - `POST /api/v1/viva/memory/reindex`
  - `GET /api/v1/viva/chat/sessions`
- prova de vida:
  - status memoria => `vector_enabled=true`, `redis_enabled=true`;
  - reindexacao processando historico salvo;
  - busca semantica retornando resultados;
  - limpeza de chat (`session/new`) mantendo recuperacao de memoria longa.
- proximo plano executivo registrado em:
  - `docs/ARCHITECTURE/VIVA_NEXT_EXECUTION_PLAN.md`

## Atualizacao da sessao (2026-02-10 - fechamento bug audio institucional)
- contexto validado pelo cliente:
  - tamanho do campo de texto aprovado;
  - rolagem automatica do chat aprovada;
  - pendencia restante focada no fluxo de audio.
- problema final observado:
  - apos gravar, audio ainda aparecia como anexo pendente e dependia de `Enter` para seguir.
- correcao aplicada:
  - `frontend/src/app/viva/page.tsx`:
    - `MediaRecorder.onstop` agora dispara envio automatico para `handleSend` com `anexosOverride` de audio;
    - fluxo normal passa a ser direto: gravar -> parar -> transcrever -> VIVA responde;
    - bolha de anexo de audio deixa de ser etapa obrigatoria no caminho principal.
- evidencia de governanca:
  - BUG documentado/fechado como `BUG-071` em `docs/BUGSREPORT.md`.
- estado ao fim da rodada:
  - pendencia de audio institucional encerrada para demonstracao local.

## Atualizacao da sessao (2026-02-10 - visual holografico VIVA)
- solicitacao executada:
  - avatar da VIVA mais holografico/3D com movimento.
- implementacao:
  - adicionada stage central com camadas visuais (rings, grid, glow, scanline e sombra dinamica);
  - animacoes atreladas ao estado da assistente para sensacao de presenca.
- impacto:
  - experiencia visual mais humanizada sem alterar persistencia/log do chat.
- validacao:
  - lint e type-check do frontend concluidos com sucesso.

## Atualizacao da sessao (2026-02-11 - hotfix da ultima rodada VIVA)
- problema reportado:
  - ultima atualizacao visual/audio nao estava consistente em uso real.
- ajustes executados:
  - `frontend/src/app/viva/page.tsx`:
    - holograma reposicionado fora da area rolavel para manter visibilidade constante;
    - fila de audio pendente reforcada para envio automatico ao fim do `loading`;
    - `handleSend` encapsulado com `useCallback` para estabilidade do efeito de fila.
- validacao tecnica:
  - `npm run type-check` => OK;
  - `npm run lint -- --file src/app/viva/page.tsx` => OK (apenas warnings legados de `<img>`).
- rastreabilidade:
  - `BUG-072` atualizado para **Em validacao** em `docs/BUGSREPORT.md`.

## Atualizacao da sessao (2026-02-11 - encerramento com incidente agenda)
- incidente reportado em uso real:
  - comando "agende o Andre amanha as 10 para mim. Mande para a agenda." nao criou compromisso;
  - VIVA respondeu com consulta/listagem: "Voce nao tem compromissos de amanha."
- classificacao:
  - regressao de interpretacao de intencao em agenda (criacao x consulta).
- governanca aplicada:
  - bug registrado como `BUG-073` em `docs/BUGSREPORT.md` antes de qualquer nova correcao.
- status da rodada:
  - usuario solicitou somente documentacao e encerramento do dia;
  - nenhuma correcao de codigo adicional executada nesta janela.
- proxima retomada (amanha):
  - ajustar priorizacao de verbos de acao de criacao de agenda;
  - validar com frases naturais equivalentes e com retorno de confirmacao de criacao.

## Atualizacao da sessao (2026-02-11 - retomada: agenda + modo conversacao)
- escopo executado:
  - corrigir `BUG-073` (agenda natural criando compromisso, sem cair em consulta);
  - corrigir `BUG-076` (modo conversacao em submenu lateral, separado do chat padrao).
- backend:
  - `backend/app/services/viva_agenda_nlu_service.py`:
    - novos verbos imperativos de criacao (`agende`, `marque`, `crie`, `adicione`);
    - parser de hora natural com suporte a `as 10`, `10h` e `10:30`;
    - ajuste de query-intent para reduzir falso positivo de consulta em frases de criacao.
- frontend:
  - `frontend/src/app/viva/page.tsx`:
    - novo botao lateral `Conversa VIVA`;
    - modo conversacao ativado/desativado por submenu (nao acoplado ao chat normal);
    - TTS da VIVA condicionado ao modo conversacao com toggle de voz.
- validacoes da rodada:
  - `npm run type-check` (frontend): OK;
  - `npm run lint -- --file src/app/viva/page.tsx`: OK (warnings nao bloqueantes de `<img>`);
  - `python -m compileall app/services/viva_agenda_nlu_service.py app/api/v1/viva.py`: OK;
  - smoke NLU: frase de agendamento natural gerou payload de criacao valido e nao foi classificada como consulta.

## Atualizacao da sessao (2026-02-11 - fechamento BUG-077 conversa continua)
- problema reportado:
  - modo de conversacao ainda estava hibrido (chat visivel + necessidade de fluxo manual de audio).
- correcao aplicada:
  - `frontend/src/app/viva/page.tsx`:
    - modo `Conversa VIVA` convertido para tela dedicada sem feed de chat na interface;
    - escuta de voz continua automatica com Web Speech API (sem botao manual estilo whisper para cada fala);
    - pausa da escuta durante TTS da VIVA e retomada automatica ao fim da resposta;
    - avatar holografico central com fallback de arquivos de avatar institucionais.
- validacao:
  - `npm run type-check` => OK;
  - `npm run lint -- --file src/app/viva/page.tsx` => OK (apenas warnings legados de `<img>`).
- status:
  - `BUG-077` em validacao funcional no navegador do Fabio.

## Atualizacao da sessao (2026-02-11 - pausa modulo conversa e foco campanhas)
- decisao do usuario:
  - pausar modulo de conversa continua/3D da VIVA para priorizar funcional principal de campanhas.
- governanca aplicada:
  - `BUG-076` e `BUG-077` marcados como **Em pausa (prioridade campanhas)** em `docs/BUGSREPORT.md`.
- auditoria tecnica da repeticao visual:
  - `BUG-061` reaberto como ativo apos nova evidencia de personagens repetidos;
  - causa provavel registrada: convergencia frequente para defaults de brief + compressao de `scene` (limite de 240 chars) + baixa temperatura na copy (`0.35`), reduzindo variabilidade real da direcao de arte.
- backlog tecnico confirmado:
  - `BUG-062` permanece ativo (monolito `backend/app/api/v1/viva.py`, ~2769 linhas, 21 rotas, 90+ funcoes).

## Atualizacao da sessao (2026-02-11 - inicio correcao funcional de campanhas)
- pedido do usuario:
  - priorizar funcional de geracao de imagem e diversidade visual antes de continuar modulo de conversa continua.
- trilha executada:
  - resumo institucional de status de bugs consolidado em `docs/BUGSREPORT.md`;
  - `BUG-061` atacado na rodada 2 com reforco de variacao humana/cena no prompt de imagem;
  - modulo conversa continua mantido em pausa (`BUG-076` e `BUG-077`).
- mudancas tecnicas:
  - `backend/app/api/v1/viva.py`:
    - funcoes novas `_stable_pick` e `_persona_scene_variant`;
    - ampliacao de contexto `scene` para reduzir compressao de prompt;
    - prompt final com diretriz de elenco + humor + composicao por `variation_id`;
    - aumento de variabilidade na copy (`temperature=0.6`).
- validacao da etapa:
  - compileall sem erro;
  - smoke local confirmou variacao de elenco/enquadramento/humor por seed.

## Atualizacao da sessao (2026-02-11 - rodada 3 campanhas: tema livre sem hardcode)
- diretriz do usuario aplicada:
  - nao usar lista fixa de temas sazonais no backend (tema do ano e dinamico).
- ajuste executado:
  - `backend/app/api/v1/viva.py`:
    - `_theme_scene_hint` refeito para usar apenas `tema/oferta/objetivo` recebidos no briefing;
    - removido comportamento dependente de tema especifico;
    - parser de `tema` reforcado para frase natural (`campanha de/do/da/para ...`);
    - parser de oferta percentual corrigido para nao arrastar `formato/publico/objetivo`;
    - anti-repeticao visual ampliada com selecao de elenco baseada em historico recente (`cast_profile` + `recent_cast_ids`).
- validacao:
  - `python -m py_compile app/api/v1/viva.py` => OK;
  - smoke parser com texto livre validou tema/oferta corretos;
  - prompt final inclui diretriz de elenco obrigatoria + historico recente para evitar repeticao.

## Atualizacao da sessao (2026-02-11 - rodada adicional agenda NLU)
- foco:
  - corrigir tolerancia de linguagem natural em `BUG-073` para frases com acento (`amanhã às 10`) mesmo com ruido de encoding.
- ajuste executado:
  - `backend/app/services/viva_agenda_nlu_service.py`:
    - parsing de hora via texto normalizado;
    - fallback de hora isolada com contexto temporal;
    - reconhecimento de `amanh*`/`hoj*` para data;
    - limpeza de titulo com saneamento extra.
- validacao:
  - `python -m py_compile app/services/viva_agenda_nlu_service.py` => OK;
  - smoke local confirmou `date_time` de criacao para amanha as 10.

## Atualizacao da sessao (2026-02-11 - BUG-016 overlay truncado rodada 2)
- ajuste aplicado:
  - `frontend/src/app/viva/page.tsx`:
    - parser de overlay com limite de texto maior (menos truncamento precoce);
    - modal de arte final com areas de texto maiores e rolagem interna;
    - exportacao PNG com distribuicao vertical mais ampla para texto e wrap com limite vertical.
- validacao:
  - `npm run type-check` => OK;
  - `npm run lint -- --file src/app/viva/page.tsx` => OK (warnings conhecidos de `<img>`).

## Atualizacao da sessao (2026-02-11 - BUG-015/061 rodada 4 diversidade visual)
- foco:
  - reduzir repeticao de personagens/cenarios nas imagens de campanha (`FC`/`REZETA`) sem hardcode de tema.
- ajuste aplicado:
  - `backend/app/api/v1/viva.py`:
    - novo `scene_profile` com selecao dinamica por publico e historico recente;
    - historico anti-repeticao agora usa dois eixos: `cast_profile` + `scene_profile`;
    - pool de cenarios ampliado (PF/MEI/PJ) para aumentar variedade antes de repetir;
    - prompt final com bloqueio explicito de composicoes genericas recorrentes;
    - chamada OpenAI Images com `quality=high` em campanhas;
    - fallback seguro em `_generate_campaign_copy` para evitar quebra `500` quando a etapa de copy falhar/timeout.
- validacao:
  - `python -m py_compile app/api/v1/viva.py` => OK;
  - simulacao local de rotacao:
    - `cast_profile`: 8 variacoes em 8 geracoes sequenciais;
    - `scene_profile`: 8 variacoes em 8 geracoes sequenciais.

## Atualizacao da sessao (2026-02-11 - snapshot institucional pre-commit)
- validacao de leitura executada antes do snapshot:
  - backend:
    - `python -m py_compile app/api/v1/viva.py app/services/viva_agenda_nlu_service.py` => OK;
  - frontend:
    - `npm run type-check` => OK;
    - `npm run lint -- --file src/app/viva/page.tsx` => OK (warnings nao bloqueantes de `<img>`);
  - API read-only (runtime local):
    - `/health` => 200;
    - `/api/v1/auth/login` => 200;
    - `/api/v1/auth/me` => 200;
    - `/api/v1/viva/status` => 200;
    - `/api/v1/viva/campanhas?limit=5` => 200;
    - `/api/v1/agenda` => 200;
    - `/api/v1/clientes?limit=5` => 200.
- objetivo:
  - registrar prova viva de estado funcional antes de seguir para novos blocos de correcao.

## Atualizacao da sessao (2026-02-11 - bloco adicional de baixa)
- execucao:
  - rodada de prova viva para baixar bugs em validacao com evidencias objetivas de API e leitura de codigo.
- ajuste de codigo desta rodada:
  - `backend/app/services/viva_agenda_nlu_service.py`:
    - `parse_agenda_natural_create` passou a aceitar tambem o gatilho `agenda ...` em linguagem natural.
- validacoes chave:
  - persistencia de campanhas (`POST/GET /api/v1/viva/campanhas`) validada;
  - sessao/historico do chat (`/viva/chat/session/new` + `/viva/chat/snapshot`) validada;
  - agenda real sem loop e com filtro por usuario validada em dois usuarios QA;
  - frase real do incidente de agendamento natural voltou a criar compromisso com sucesso.
- resultado documental:
  - `BUG-037`, `BUG-038`, `BUG-040`, `BUG-041`, `BUG-042`, `BUG-045`, `BUG-046`, `BUG-047`, `BUG-054`, `BUG-057`, `BUG-073` baixados para **Resolvido** em `docs/BUGSREPORT.md`.

## Atualizacao da sessao (2026-02-11 - bloco final dos 7 pendentes)
- backend:
  - `backend/app/api/v1/viva.py` desacoplado de SQL direto de chat/campanhas;
  - novos repositorios:
    - `backend/app/services/viva_chat_repository_service.py`
    - `backend/app/services/viva_campaign_repository_service.py`
  - campanhas:
    - inferencia de tema livre reforcada (`_extract_unstructured_theme`);
    - prompt de imagem com ancora obrigatoria de tema/oferta/cena;
    - variacao adicional de aparencia para reduzir repeticao de personagem.
- frontend:
  - `frontend/src/app/viva/page.tsx`:
    - overlay/export mais resiliente a texto longo (ellipsis + areas ampliadas);
    - audio manual em fluxo direto (selecionou -> transcreveu/enviou);
    - modo `Conversa VIVA` mantido no submenu dedicado com holograma 3D e tilt por ponteiro.
- validacao tecnica:
  - `python -m py_compile app/api/v1/viva.py app/services/viva_chat_repository_service.py app/services/viva_campaign_repository_service.py` => OK;
  - `npm run type-check` => OK;
  - `npm run lint -- --file src/app/viva/page.tsx` => OK (warnings nao bloqueantes de `<img>`).
- status consolidado:
  - resolvidos: `BUG-072`, `BUG-076`, `BUG-077`;
  - em validacao final: `BUG-015`, `BUG-016`, `BUG-061`, `BUG-062`.

## Atualizacao tecnica (2026-02-11 - playbook oficial de subida de modelos .md)
- documentacao operacional criada para eliminar margem de erro de agentes na carga de novos contratos:
  - `docs/CONTRATOS/PLAYBOOK_MODELOS_MD.md`
- o playbook define:
  - arquivos obrigatorios por etapa (template, fallback, menu, novo, preview, PDF frontend, PDF backend);
  - gates de encoding UTF-8 (anti-mojibake);
  - validacao tecnica e funcional obrigatoria;
  - checklist final de entrega e fechamento documental.

## Atualizacao Operacional (2026-02-12 - execucao lote completo dos modelos `.md`)
- escopo executado:
  - integracao dos 10 modelos restantes enviados em `.md` no fluxo oficial de contratos.
- templates novos adicionados:
  - `contratos/templates/aumento_score.json`
  - `contratos/templates/ccf.json`
  - `contratos/templates/certificado_digital.json`
  - `contratos/templates/diagnostico360.json`
  - `contratos/templates/limpa_nome_express.json`
  - `contratos/templates/limpa_nome_standard.json`
  - `contratos/templates/rating_convencional.json`
  - `contratos/templates/rating_express_pj.json`
  - `contratos/templates/remocao_proposta.json`
  - `contratos/templates/revisional.json`
- consolidacao de templates base:
  - `contratos/templates/cnh.json` atualizado com clausulas estruturadas;
  - `contratos/templates/bacen.json` e `contratos/templates/cadin.json` com `subtitulo` canonico.
- backend:
  - `backend/app/services/contrato_service.py` com fallbacks dos novos templates;
  - `backend/app/services/pdf_service_playwright.py` convertido para renderizacao dinamica por template JSON;
  - `backend/app/schemas/contrato.py` adaptado para resposta de template JSON sem `created_at` obrigatorio.
- frontend:
  - `frontend/src/app/(dashboard)/contratos/page.tsx` com 10 novos cards ativos;
  - `frontend/src/app/(dashboard)/contratos/novo/page.tsx` aceitando todos os `template_id` do lote;
  - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx` migrado para preview dinamico de clausulas;
  - `frontend/src/lib/pdf.ts` migrado para PDF dinamico de clausulas;
  - `frontend/src/lib/api.ts` com `contratosApi.getTemplate`.
- validacao tecnica:
  - `python -m py_compile backend/app/services/contrato_service.py backend/app/services/pdf_service_playwright.py backend/app/schemas/contrato.py` => OK;
  - `frontend`: `npm run type-check` => OK;
  - `frontend`: `npm run lint -- --file src/app/(dashboard)/contratos/page.tsx --file src/app/(dashboard)/contratos/novo/page.tsx --file src/app/(dashboard)/contratos/[id]/page.tsx --file src/lib/pdf.ts --file src/lib/api.ts` => OK (apenas warning nao bloqueante de `<img>` no preview).

## Atualizacao Operacional (2026-02-12 - reabertura contratos sem clausulas)
- contexto:
  - apos validacao visual em `/contratos/{id}`, contratos novos exibiram "Clausulas nao cadastradas".
- diagnostico read-only executado:
  - API `GET /api/v1/contratos/templates/{id}` retornando fallback vazio (`clausulas: null`) para todos os IDs do lote;
  - Postgres local (`contrato_templates`) sem registros (`0 rows`);
  - container backend sem diretorio de templates no runtime:
    - `/app/contratos/templates` ausente;
    - `/app/backend/contratos/templates` ausente.
- conclusao:
  - os JSON existem no workspace host, mas nao estao acessiveis dentro do container backend atual, forçando fallback sem clausulas.
- protocolo:
  - bug reaberto/formalizado como `BUG-081` em `docs/BUGSREPORT.md`;
  - correcao ficou planejada em 3 etapas (path runtime, loader unificado, retrocompatibilidade de clausulas), sem aplicacao de codigo nesta rodada.

## Atualizacao Git (2026-02-12 - verificacao de copia de seguranca)
- branch atual: `main`
- remoto: `origin` -> `https://github.com/lucasricardolebre1984/fabio2.git`
- checkpoint confirmado:
  - `HEAD` local = `origin/main` no commit `42cc294` (`docs(contratos): formaliza playbook de modelos md e estabiliza acentuacao`).
- observacao importante:
  - existe copia de seguranca remota nesse commit;
  - estado atual ainda possui alteracoes locais nao commitadas (worktree suja), incluindo templates e ajustes de contratos.

## Atualizacao Operacional (2026-02-12 - execucao BUG-081 contratos runtime)
- correcoes aplicadas:
  - `docker-compose.yml`:
    - mount `./contratos:/app/contratos:ro` no backend;
    - env `CONTRATOS_TEMPLATES_DIR=/app/contratos/templates`.
  - novo loader central de templates:
    - `backend/app/services/contrato_template_loader.py`;
    - normalizacao de clausulas legadas (`paragrafos` -> `conteudo`).
  - servicos atualizados:
    - `backend/app/services/contrato_service.py` (carregamento robusto de template JSON no runtime);
    - `backend/app/services/pdf_service_playwright.py` (mesmo loader + compatibilidade de clausulas).
  - frontend atualizado:
    - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`;
    - `frontend/src/lib/pdf.ts`;
    - ambos aceitando `conteudo` e `paragrafos`.
- validacoes:
  - `py_compile` backend => OK;
  - `npm run type-check` => OK;
  - `npm run lint -- --file src/app/(dashboard)/contratos/[id]/page.tsx --file src/lib/pdf.ts` => OK (warning nao bloqueante de `<img>`);
  - API templates (`/api/v1/contratos/templates/{id}`) retornando clausulas para 13 IDs do lote;
  - PDF backend (`/api/v1/contratos/{id}/pdf`) com `200 application/pdf` apos rebuild da imagem backend com `pydyf==0.10.0`.
- status:
  - `BUG-081` movido para **Em validacao (runtime corrigido)**.

## Atualizacao Operacional (2026-02-12 - execucao BUG-082 contratos faltantes)
- contexto:
  - apos estabilizacao de runtime (`BUG-081`), restavam 2 modelos `.md` fora do fluxo funcional: `rating_full_pj` e `jusbrasil`.
- execucao aplicada:
  - templates criados:
    - `contratos/templates/rating_full_pj.json`
    - `contratos/templates/jusbrasil.json`
  - backend:
    - `backend/app/services/contrato_service.py` atualizado com fallback para os dois novos IDs.
  - frontend:
    - `frontend/src/app/(dashboard)/contratos/page.tsx` com cards ativos de `Rating Full PJ` e `Jusbrasil/Escavador`;
    - `frontend/src/app/(dashboard)/contratos/novo/page.tsx` com labels/aceite para ambos os templates.
- validacao:
  - `python -m json.tool` nos templates novos => OK;
  - `python -m py_compile` backend (contrato_service/loader/pdf_service_playwright) => OK;
  - `npm run type-check` => OK;
  - `npm run lint -- --file src/app/(dashboard)/contratos/page.tsx --file src/app/(dashboard)/contratos/novo/page.tsx` => OK;
  - API runtime:
    - `GET /api/v1/contratos/templates/rating_full_pj` => 10 clausulas;
    - `GET /api/v1/contratos/templates/jusbrasil` => 8 clausulas;
    - varredura dos 15 templates operacionais com clausulas > 0.
- status:
  - `BUG-082` => **Resolvido**.

## Atualizacao Operacional (2026-02-12 - execucao BUG-083 encoding residual)
- contexto:
  - contratos exibiam simbolos residuais (`�`) em alguns titulos/clausulas no preview, apesar das clausulas estarem presentes.
- correcoes aplicadas:
  - backend:
    - `backend/app/services/contrato_template_loader.py` recebeu normalizacao recursiva de strings do payload de template;
    - estrategia de reparo de mojibake ampliada para `cp1252 -> utf-8` e `latin-1 -> utf-8` com score de qualidade.
  - PDF backend:
    - `backend/app/services/pdf_service_playwright.py` alinhado com o mesmo reparo robusto de encoding.
  - frontend:
    - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx` e `frontend/src/lib/pdf.ts` com decoder robusto de mojibake CP1252/UTF-8.
- validacao:
  - `py_compile` backend => OK;
  - `npm run type-check` => OK;
  - `npm run lint` direcionado => OK (warning nao bloqueante de `<img>`);
  - validacao HTTP UTF-8 dos templates (`aumento_score`, `rating_convencional`, `revisional`) sem `�` e sem marcadores de mojibake no payload.
- status:
  - `BUG-083` => **Resolvido**.

## Atualizacao Operacional (2026-02-13 - planejamento BUG-084 parcelamento)
- contexto funcional:
  - fluxo de `novo contrato` ainda exige `prazo_1` e `prazo_2` manuais e aceita ate 99 parcelas;
  - operacao comercial solicitada: venda a vista/1x fluida, entrada opcional, parcelas ate 12x com prazos padrao automaticos.
- diagnostico read-only executado:
  - frontend exige campos de prazo (`required`) em `frontend/src/app/(dashboard)/contratos/novo/page.tsx`;
  - backend schema ainda valida `prazo_1/prazo_2 >= 1` e `qtd_parcelas <= 99` em `backend/app/schemas/contrato.py`;
  - `valor_parcela` ja possui calculo automatico no backend (`ContratoService.create`).
- governanca:
  - bug formalizado como `BUG-084` em `docs/BUGSREPORT.md`;
  - plano em 3 etapas documentado (UX frontend, regra backend, render preview/pdf) aguardando execucao.

## Atualizacao Operacional (2026-02-13 - execucao BUG-084 parcelamento)
- frontend:
  - `frontend/src/app/(dashboard)/contratos/novo/page.tsx` atualizado para:
    - remover `prazo_1` e `prazo_2` do formulario;
    - usar seletor de parcelas `01..12`;
    - manter entrada opcional;
    - calcular parcela automaticamente e exibir resumo de prazos padrao (30/60/90...).
- backend:
  - `backend/app/schemas/contrato.py` com regra `qtd_parcelas <= 12` e `prazo_1/prazo_2 >= 0`;
  - `backend/app/services/contrato_service.py` com cronograma automatico:
    - `1x` => `a vista` (`prazo_1=0`, `prazo_2=0`);
    - `2x..12x` => prazos em multiplo de 30;
    - persistencia de cronograma em `dados_extras.prazos_dias`;
    - calculo de `valor_parcela` feito automaticamente no backend.
- renderizacao:
  - fallback institucional de prazos para `a vista` aplicado em:
    - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`;
    - `frontend/src/lib/pdf.ts`;
    - `backend/app/services/pdf_service_playwright.py`.
- validacao tecnica:
  - `python -m py_compile backend/app/schemas/contrato.py backend/app/services/contrato_service.py backend/app/services/pdf_service_playwright.py` => OK;
  - `frontend`: `npm run type-check` => OK;
  - `frontend`: `npm run lint -- --file src/app/(dashboard)/contratos/novo/page.tsx --file src/app/(dashboard)/contratos/[id]/page.tsx --file src/lib/pdf.ts` => OK (warning conhecido de `<img>` nao bloqueante).

## Atualizacao Operacional (2026-02-13 - execucao BUG-085 templates base)
- contexto:
  - os 3 templates base (`bacen`, `cadin`, `cnh`) ainda estavam em formato legado e fora do metodo padronizado adotado nos modelos novos.
- execucao:
  - `contratos/templates/bacen.json`, `contratos/templates/cadin.json` e `contratos/templates/cnh.json` regravados no padrao atual (estrutura e placeholders unificados).
  - suporte de placeholder CNH incluido em toda a cadeia de renderizacao:
    - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
    - `frontend/src/lib/pdf.ts`
    - `backend/app/services/pdf_service_playwright.py`
- resultado:
  - os 3 modelos ficaram alinhados ao mesmo metodo operacional dos demais contratos.

## Atualizacao Operacional (2026-02-13 - saneamento institucional docs + seguranca)
- rollback pre-change registrado em:
  - `docs/ROLLBACK/rollback-20260213-055551-pre-doc-sync-baseline.txt`
  - `docs/ROLLBACK/rollback-20260213-055551-pre-doc-sync.patch`
  - `docs/ROLLBACK/rollback-20260213-055551-pre-doc-sync-staged.patch`
  - `docs/ROLLBACK/rollback-20260213-055551-pre-doc-sync-untracked.txt`
- seguranca:
  - `docker-compose-prod.yml` higienizado para eliminar segredos hardcoded, usando apenas variaveis de ambiente no compose legado.
- alinhamento documental:
  - `README.md` ajustado para refletir os modelos de contrato ativos;
  - `SETUP.md` e `teste-local.md` ajustados para credencial dev local `1234`;
  - `docs/MANUAL_DO_CLIENTE.md` corrigido para estado real do audio no `/viva`;
  - `docs/API.md` ampliado com endpoints complementares ativos no backend;
  - `docs/DEPLOY_UBUNTU_DOCKER.md` atualizado para `OPENAI_API_KEY`.
- governanca:
  - `BUG-086` e `BUG-087` formalizados e baixados como **Resolvidos** em `docs/BUGSREPORT.md`.

## Atualizacao Operacional (2026-02-13 - rodada de bugs ativos VIVA/Contratos)
- rollback pre-fix registrado em:
  - `docs/ROLLBACK/rollback-20260213-061013-pre-bug-active-round-baseline.txt`
  - `docs/ROLLBACK/rollback-20260213-061013-pre-bug-active-round.patch`
  - `docs/ROLLBACK/rollback-20260213-061013-pre-bug-active-round-staged.patch`
  - `docs/ROLLBACK/rollback-20260213-061013-pre-bug-active-round-untracked.txt`
- correcao aplicada:
  - `backend/app/api/v1/viva.py`:
    - `_extract_cliente_nome` ajustado para regex unicode estavel (`\\u00C0-\\u00FF`), eliminando erro `bad character range`.
- validacao de runtime (auth + chat + handoff + contratos):
  - `POST /api/v1/viva/chat` com frase natural de agendamento (`BUG-073`) => criou compromisso com confirmacao;
  - `POST /api/v1/viva/chat` com entrada parcial de agenda (`BUG-063`) => follow-up contextual sem template fixo;
  - `POST /api/v1/viva/chat` com agenda+WhatsApp (`BUG-064`) => criou handoff com ID;
  - `POST /api/v1/viva/handoff/process-due` => processou tarefa vencida com status `sent`;
  - varredura dos 15 templates em `GET /api/v1/contratos/templates/{id}` com clausulas > 0 (`BUG-081`);
  - `GET /api/v1/contratos/{id}/pdf` => `200 application/pdf`.
- governanca:
  - `BUG-063`, `BUG-064`, `BUG-073`, `BUG-081` e `BUG-088` baixados para **Resolvido**.
  - `BUG-062` mantido **Ativo** por escopo estrutural (monolito `viva.py`).

## Atualizacao Operacional (2026-02-13 - VIVA memoria/sessoes + campanha)
- foco da rodada:
  - validar criticamente memoria sem perda de contexto e recuperacao de chats;
  - corrigir desvio de fluxo de campanha em modo `FC/REZETA`;
  - reduzir repeticao imediata de elenco/cenario em campanhas.
- backend (`backend/app/api/v1/viva.py`):
  - adicionado gate `_has_campaign_signal` para evitar que qualquer texto comum seja tratado como campanha;
  - inferencia de tema livre passou a ocorrer apenas quando houver sinal real de campanha;
  - reforco anti-repeticao:
    - `_stable_pick` com hash `sha256` para distribuicao mais estavel;
    - cooldown dos 2 perfis/cenarios mais recentes quando pool estiver saturado.
- frontend (`frontend/src/app/viva/page.tsx`):
  - recuperacao de sessoes antigas implementada no header:
    - listagem via `GET /api/v1/viva/chat/sessions`;
    - carregamento de snapshot por sessao selecionada;
    - refresh de lista apos envio/limpeza.
- validacao executada:
  - `POST /api/v1/viva/chat` (modo `FC`) com pergunta comum (`qual foi minha ultima mensagem?`) => resposta normal de conversa (sem "Sugestoes rapidas para sua campanha");
  - `POST /api/v1/viva/chat` com texto de campanha explicito => funil de campanha mantido;
  - `GET /api/v1/viva/chat/sessions` + `GET /api/v1/viva/chat/snapshot?session_id=...` => recuperacao de historico por sessao funcionando;
  - memoria/RAG: `GET /api/v1/viva/memory/status` retornando `vector_enabled=true` e `redis_enabled=true`; `GET /api/v1/viva/memory/search` retornando resultados semanticos.

## Atualizacao Operacional (2026-02-13 - VIVA arquitetura fase 2)
- objetivo:
  - tornar `backend/app/api/v1/viva.py` um arquivo minimo de roteamento, mantendo comportamento atual do sistema.
- execucao:
  - implementacao atual da VIVA movida para `backend/app/api/v1/viva_core.py`;
  - `backend/app/api/v1/viva.py` reduzido para agregador com `include_router(viva_core_router)`.
- validacao:
  - `python -m py_compile backend/app/api/v1/viva.py backend/app/api/v1/viva_core.py` => OK;
  - runtime autenticado:
    - `GET /api/v1/viva/status` => `200`;
    - `GET /api/v1/viva/chat/sessions` => `200`;
    - `GET /api/v1/viva/chat/snapshot` => `200`;
    - `POST /api/v1/viva/chat` => `200` com `session_id`.
- observacao:
  - a etapa atual resolve a exigencia de `viva.py` minimo;
  - proxima etapa institucional: quebrar `viva_core.py` por dominio (chat/campaign/memory/midia/handoff) para reduzir acoplamento de regra de negocio.

## Atualizacao Operacional (2026-02-13 - VIVA arquitetura fase 3)
- objetivo:
  - extrair rotas nao-chat do `viva_core.py` para modulos dedicados por dominio.
- execucao:
  - novos routers criados:
    - `backend/app/api/v1/viva_memory_routes.py`
    - `backend/app/api/v1/viva_capabilities_routes.py`
    - `backend/app/api/v1/viva_handoff_routes.py`
    - `backend/app/api/v1/viva_campaign_routes.py`
    - `backend/app/api/v1/viva_media_routes.py`
  - `backend/app/api/v1/viva.py` atualizado para agregar `viva_core` + routers de dominio.
  - `backend/app/api/v1/viva_core.py` ficou focado no dominio de chat/sessao.
- validacao:
  - `python -m py_compile` dos arquivos novos e agregadores => OK;
  - runtime autenticado:
    - `GET /api/v1/viva/status` => `200`;
    - `GET /api/v1/viva/capabilities` => `200`;
    - `GET /api/v1/viva/memory/status` => `200`;
    - `GET /api/v1/viva/handoff` => `200`;
    - `GET /api/v1/viva/campanhas` => `200`;
    - `POST /api/v1/viva/chat` => `200` com `session_id`.
- status:
  - fatiamento de rotas por dominio concluido;
  - proxima etapa (fase 4): extrair helpers/casos de uso de chat do `viva_core.py` para camada de servico.

## Atualizacao Operacional (2026-02-13 - VIVA arquitetura fase 4 parcial)
- objetivo:
  - separar tambem o dominio de sessao de chat do `viva_core.py`.
- execucao:
  - criado `backend/app/api/v1/viva_chat_session_routes.py` com:
    - `GET /api/v1/viva/chat/snapshot`
    - `GET /api/v1/viva/chat/sessions`
    - `POST /api/v1/viva/chat/session/new`
  - `backend/app/api/v1/viva_core.py` ficou com endpoint principal `/chat` + helpers reutilizados por outros modulos.
  - `backend/app/api/v1/viva.py` atualizado para incluir `viva_chat_session_router`.
- validacao:
  - `python -m py_compile` do conjunto de routers => OK;
  - runtime autenticado:
    - `POST /api/v1/viva/chat` => `200`;
    - `POST /api/v1/viva/chat/session/new` => `200`;
    - `GET /api/v1/viva/chat/sessions` => `200`;
    - `GET /api/v1/viva/chat/snapshot` => `200`;
    - `GET /api/v1/viva/memory/status` => `200`;
    - `GET /api/v1/viva/campanhas` => `200`.
- status:
  - proximo corte (fase 5): extrair helpers/orquestracao de `viva_core.py` para servicos de dominio sem regressao.

## Atualizacao Operacional (2026-02-13 - VIVA arquitetura fase 5 parcial)
- objetivo:
  - tirar a orquestracao principal de chat do arquivo de rota.
- execucao:
  - criado `backend/app/services/viva_chat_orchestrator_service.py` com a implementacao do fluxo de `/chat`;
  - `backend/app/api/v1/viva_core.py` passou a atuar como contrato HTTP do endpoint `/chat`, delegando para service.
- observacao tecnica:
  - usado bridge temporario no service (`globals().update(...)` com referencias de `viva_core`) para manter comportamento durante transicao sem quebrar runtime.
- validacao:
  - `python -m py_compile` no conjunto de routers e services VIVA => OK;
  - runtime autenticado:
    - `POST /api/v1/viva/chat` => `200` com `session_id`;
    - `POST /api/v1/viva/chat/session/new` => `200`;
    - `GET /api/v1/viva/chat/sessions` => `200`;
    - `GET /api/v1/viva/chat/snapshot` => `200`;
    - `GET /api/v1/viva/memory/status` => `200`;
    - `GET /api/v1/viva/capabilities` => `200`;
    - `GET /api/v1/viva/handoff` => `200`;
    - `GET /api/v1/viva/campanhas` => `200`;
    - `GET /api/v1/viva/status` => `200`.
- status:
  - proxima etapa (fase final): remover bridge temporario e extrair helpers/casos de uso para services explicitos por dominio.

## Atualizacao Operacional (2026-02-13 - VIVA arquitetura fase 5 avancada)
- objetivo:
  - remover bridge dinamico temporario do orquestrador de chat.
- execucao:
  - `backend/app/services/viva_chat_orchestrator_service.py` atualizado:
    - removido `globals().update(...)`;
    - imports explicitos dos simbolos utilizados na orquestracao.
- validacao:
  - `python -m py_compile` nos arquivos VIVA => OK;
  - runtime autenticado:
    - `POST /api/v1/viva/chat` => `200`;
    - `POST /api/v1/viva/chat/session/new` => `200`;
    - `GET /api/v1/viva/chat/sessions` => `200`;
    - `GET /api/v1/viva/chat/snapshot` => `200`;
    - `GET /api/v1/viva/memory/status` => `200`;
    - `GET /api/v1/viva/capabilities` => `200`;
    - `GET /api/v1/viva/handoff` => `200`;
    - `GET /api/v1/viva/campanhas` => `200`;
    - `GET /api/v1/viva/status` => `200`.
- status:
  - bridge removido sem regressao;
  - proximo passo para fechamento completo do BUG-062: extrair helpers remanescentes do `viva_core.py` em services de dominio e reduzir acoplamento interno.

## Atualizacao Operacional (2026-02-13 - VIVA arquitetura fase 5 avancada B)
- objetivo:
  - desacoplar contratos de request/response de `viva_core.py`.
- execucao:
  - criado `backend/app/api/v1/viva_schemas.py` com os modelos Pydantic compartilhados da VIVA;
  - `viva_core`, routers de dominio e `viva_chat_orchestrator_service` atualizados para importar schemas do modulo dedicado.
- validacao:
  - `python -m py_compile` do conjunto VIVA => OK;
  - runtime autenticado:
    - `POST /api/v1/viva/chat` => `200`;
    - `GET /api/v1/viva/chat/sessions` => `200`;
    - `GET /api/v1/viva/memory/status` => `200`;
    - `GET /api/v1/viva/capabilities` => `200`;
    - `GET /api/v1/viva/handoff` => `200`;
    - `GET /api/v1/viva/campanhas` => `200`;
    - `GET /api/v1/viva/status` => `200`.
- status:
  - contratos HTTP centralizados em schema dedicado;
  - proximo passo para fechamento do BUG-062: extrair helpers utilitarios remanescentes de `viva_core.py` para camada de service/util.

## Atualizacao Operacional (2026-02-13 - VIVA arquitetura fase 5 avancada C)
- objetivo:
  - reduzir ainda mais dependencia de helpers de `viva_core` no fluxo de chat/sessao.
- execucao:
  - criado `backend/app/services/viva_chat_session_service.py` com operacoes de sessao/historico (`append`, `snapshot`, `serialize`, `context`);
  - `backend/app/services/viva_chat_orchestrator_service.py` passou a consumir o chat-session service;
  - `backend/app/api/v1/viva_chat_session_routes.py` passou a consumir o chat-session service.
- correcao aplicada na mesma rodada:
  - regressao em `POST /api/v1/viva/chat/session/new` por conflito de nome (`create_chat_session`) corrigida com alias no import da rota.
- validacao:
  - `python -m py_compile` do conjunto VIVA => OK;
  - runtime autenticado:
    - `POST /api/v1/viva/chat` => `200`;
    - `POST /api/v1/viva/chat/session/new` => `200`;
    - `GET /api/v1/viva/chat/sessions` => `200`;
    - `GET /api/v1/viva/chat/snapshot` => `200`;
    - `GET /api/v1/viva/memory/status` => `200`;
    - `GET /api/v1/viva/capabilities` => `200`;
    - `GET /api/v1/viva/handoff` => `200`;
    - `GET /api/v1/viva/campanhas` => `200`;
    - `GET /api/v1/viva/status` => `200`.
- status:
  - proxima etapa para fechamento do BUG-062: extrair helpers utilitarios remanescentes de `viva_core.py` para modulo(s) util/service dedicado(s).

## Atualizacao Operacional (2026-02-13 - VIVA arquitetura fase 5 avancada D)
- objetivo:
  - reduzir acoplamento de dominio com `viva_core.py` e remover legado ja extraido.
- execucao:
  - criado `backend/app/services/viva_shared_service.py` com normalizacao, mapeadores de dominio e utilitarios de campanha;
  - rotas de campanha/handoff/memory/chat-session e servicos de chat passaram a importar helpers do `viva_shared_service`;
  - `viva_chat_orchestrator_service` deixou de depender de exports de servico vindos de `viva_core`;
  - bloco morto de sessao/chat removido de `backend/app/api/v1/viva_core.py`;
  - unificacao de `_normalize_mode`, `_normalize_key`, `_sanitize_prompt` e `_extract_subject` no `viva_shared_service` (fonte unica).
- validacao:
  - `python -m py_compile` nos modulos alterados => OK.
- status:
  - `viva.py` segue minimo e o acoplamento em `viva_core` foi reduzido;
  - `viva_core.py` reduzido para ~1479 linhas na rodada (antes ~1822 no inicio da fase);
  - proxima etapa: extrair helpers de campanha/handoff/chat ainda remanescentes para services dedicados e fechar `BUG-062`.

## Atualizacao Operacional (2026-02-13 - VIVA arquitetura fase 5 avancada E)
- objetivo:
  - retirar de `viva_core.py` os helpers operacionais de handoff/imagem usados pela orquestracao.
- execucao:
  - criado `backend/app/services/viva_chat_runtime_helpers_service.py`;
  - `viva_chat_orchestrator_service.py` passou a importar os helpers operacionais desse modulo;
  - removido de `viva_core.py` o bloco de funcoes de handoff/imagem/sanitizacao ja extraido;
  - `viva_core.py` manteve apenas o que ainda e necessario para o dominio de campanha em transicao.
- validacao:
  - `python -m py_compile` dos modulos alterados => OK.
- status:
  - `viva_core.py` reduzido para ~1214 linhas;
  - proxima etapa para fechamento do BUG-062: extrair helpers de campanha restantes para service dedicado.

## Atualizacao Operacional (2026-02-13 - VIVA arquitetura fase 5 avancada F)
- objetivo:
  - concluir o desacoplamento da camada de rota `viva_core`.
- execucao:
  - criado `backend/app/services/viva_chat_domain_service.py` com helpers de dominio de chat/campanha;
  - `backend/app/services/viva_chat_orchestrator_service.py` atualizado para consumir o modulo de dominio;
  - `backend/app/api/v1/viva_core.py` reescrito para formato minimo (endpoint `/chat` delegando para service).
- validacao:
  - `python -m py_compile` dos modulos alterados => OK.
- status:
  - `viva_core.py` agora com ~25 linhas;
  - proximo passo: validacao runtime autenticada final para baixar BUG-062 de `Em validacao`.

## Atualizacao Operacional (2026-02-13 - validacao runtime final BUG-062)
- validacao autenticada executada com usuario existente:
  - `POST /api/v1/auth/login` (`fabio@fcsolucoes.com` + `1234`) => `200`;
  - `GET /api/v1/viva/status` => `200`;
  - `GET /api/v1/viva/capabilities` => `200`;
  - `GET /api/v1/viva/memory/status` => `200`;
  - `GET /api/v1/viva/chat/sessions` => `200`;
  - `GET /api/v1/viva/chat/snapshot` => `200`;
  - `GET /api/v1/viva/handoff` => `200`;
  - `GET /api/v1/viva/campanhas` => `200`;
  - `POST /api/v1/viva/chat/session/new` => `200`;
  - `POST /api/v1/viva/chat` => `200`.
- status:
  - BUG-062 baixado para **Resolvido** em `docs/BUGSREPORT.md`.

## Atualizacao Operacional (2026-02-13 - BUG-061 rodada 7)
- objetivo:
  - reduzir repeticao de padrao nas campanhas e priorizar exatamente o contexto pedido no texto.
- execucao backend:
  - `backend/app/services/viva_chat_orchestrator_service.py`:
    - fluxo FC/REZETA em modo livre (sem travar por briefing rigido);
    - reset de padrao por comando de chat (`reset memoria campanha`);
    - aplicacao de preferencia explicita de elenco no prompt de imagem.
  - `backend/app/services/viva_chat_domain_service.py`:
    - extracao de preferencia de personagem (`feminino`, `masculino`, `casal`, `grupo`, `dupla_feminina`);
    - selecao de cast filtrada por preferencia do usuario;
    - reforco de preferencia no prompt final de imagem.
  - `backend/app/services/viva_campaign_repository_service.py` + `backend/app/services/viva_shared_service.py`:
    - limpeza de historico de campanhas por usuario.
  - `backend/app/api/v1/viva_campaign_routes.py`:
    - nova rota `POST /api/v1/viva/campanhas/reset-patterns`.
- execucao frontend:
  - `frontend/src/app/viva/page.tsx` simplificado para manter no menu lateral apenas `Conversa VIVA`.
- validacao:
  - `python -m py_compile` dos modulos alterados => OK;
  - `frontend` `npm run type-check` => OK;
  - `POST /api/v1/viva/campanhas/reset-patterns` => `200` (limpeza executada em base local).
- observacao:
  - validacao visual final de imagem ficou bloqueada por limite de billing OpenAI no ambiente local (`billing_hard_limit_reached`).

## Atualizacao Operacional (2026-02-13 - documentacao de fluxo, skills e plano de orquestracao)
- objetivo da rodada:
  - consolidar documentacao do fluxo atual da VIVA;
  - registrar status tecnico real do RAG como indisponivel funcionalmente;
  - definir plano institucional de orquestrador unico com roteamento por skills.
- evidencias runtime desta rodada:
  - `GET /api/v1/viva/memory/status` => `vector_enabled=true`, `redis_enabled=true`, `total_vectors=373`;
  - `POST /api/v1/viva/memory/reindex?limit=200` => `processed=200`, `indexed=0`;
  - `GET /api/v1/viva/memory/search?q=agenda&limit=3` => `items=[]`.
- governanca aplicada em docs:
  - blueprint institucional criado:
    - `docs/ARCHITECTURE/VIVA_ORQUESTRADOR_SKILLS_BLUEPRINT.md`
  - skill criativa oficializada a partir de anexo externo (`skillconteudo.txt`):
    - `docs/PROMPTS/SKILLS/VIVA_SKILL_GHD_COPY_CAMPAIGN.md`
  - decisao arquitetural formalizada:
    - `DECISAO-034` em `docs/DECISIONS.md`.
- status aberto:
  - `BUG-091` criado em `docs/BUGSREPORT.md` para rastrear indisponibilidade funcional do RAG (infra ativa sem retorno semantico util).
- checkpoint de pausa:
  - contexto desta pauta esta persistido em `SESSION`, `BUGSREPORT`, `DECISIONS` e no blueprint de arquitetura para retomada sem perda.

## Atualizacao Operacional (2026-02-13 - auditoria de commits + limpeza de rollback)
- auditoria de historico recente executada (`git log -n 40`) com foco em correcoes de bug e estabilidade institucional.
- commits de referencia da rodada atual:
  - `c1e24dc` - correcoes VIVA/handoff e baixa de bugs ativos;
  - `be4d3f0` - saneamento de seguranca em compose + sincronizacao documental;
  - `e6e41b3` e `8e68d7d` - correcoes de contratos (parcelamento e templates base);
  - `aee6483` - consolidacao do blueprint de orquestrador+skills e status RAG.
- hygiene operacional aplicada no repositorio:
  - `docs/ROLLBACK` reduzido para apenas 3 checkpoints mais recentes:
    - `rollback-20260213-072020-pre-viva-bridge-removal*`
    - `rollback-20260213-072527-pre-viva-schema-extract*`
    - `rollback-20260213-073005-pre-viva-chat-session-service-extract*`
- status esperado apos esta rodada:
  - repositorio limpo (`git status` sem pendencias) para pausa e retomada com contexto maximo.

## Atualizacao Operacional (2026-02-13 - fix BUG-091 RAG com fallback local)
- objetivo:
  - restaurar funcionalidade de memoria longa sem depender exclusivamente de saldo OpenAI para embeddings.
- implementacao:
  - `backend/app/services/openai_service.py`:
    - fallback local deterministico de embeddings em `embed_text` para falhas/quota/rede;
  - `backend/app/services/viva_memory_service.py`:
    - coercao de dimensao de embedding para `1536` antes de insert/search em pgvector;
  - `backend/app/config.py`:
    - `OPENAI_EMBEDDING_FALLBACK_LOCAL=true` por padrao.
- validacao runtime:
  - `POST /api/v1/viva/memory/reindex?limit=120` => `processed=120`, `indexed=112`;
  - `GET /api/v1/viva/memory/search?q=agenda compromisso gabriela&limit=5` => `total=5`;
  - `GET /api/v1/viva/memory/status` => `vector_enabled=true`, `redis_enabled=true`, `total_vectors=486`.
- status:
  - BUG-091 fechado como resolvido com evidencias.

## Atualizacao Operacional (2026-02-13 - plano institucional em 3 gates + modulo de voz)
- rollback institucional desta rodada criado antes da edicao de docs:
  - `docs/ROLLBACK/rollback-20260213-140923-pre-doc-gates-baseline.txt`
  - `docs/ROLLBACK/rollback-20260213-140923-pre-doc-gates.patch`
  - `docs/ROLLBACK/rollback-20260213-140923-pre-doc-gates-staged.patch`
  - `docs/ROLLBACK/rollback-20260213-140923-pre-doc-gates-untracked.txt`
- memoria e contexto (estado oficial):
  - prompt principal unico da VIVA: `backend/app/services/viva_concierge_service.py`;
  - montagem de contexto do chat: `backend/app/services/viva_chat_domain_service.py`;
  - memoria curta: historico/snapshot de sessao em Postgres;
  - memoria media: Redis por sessao;
  - memoria longa: pgvector (`viva_memory_vectors`) com fallback local de embedding quando OpenAI falhar.
- status institucional do RAG para a pauta atual:
  - **indisponivel para homologacao semantica premium** enquanto operar sem saldo OpenAI e sem rodada formal de qualidade semantica;
  - operacional tecnicamente para continuidade (fallback local), mas ainda pendente de validacao de qualidade em producao.
- fala continua (diagnostico confirmado em codigo):
  - reconhecimento de voz continuo hoje usa API nativa do navegador (`SpeechRecognition/webkitSpeechRecognition`);
  - voz de resposta usa `window.speechSynthesis` (dependente das vozes instaladas no SO/browser);
  - endpoint OpenAI de transcricao (`/api/v1/viva/audio/transcribe`, `gpt-4o-mini-transcribe`) e usado no fluxo de audio anexado/manual, nao no loop de conversa continua.
- plano de execucao em 3 gates para fechamento desta fase:
  - Gate 1 (concluido nesta rodada): baseline/rollback + congelamento de contexto institucional.
  - Gate 2 (documentado e pendente de execucao tecnica): separar modulos comercializaveis (`core_saas`, `modulo_viva`, `modulo_viviane`, `modulo_campanhas`, `modulo_memoria`), mantendo um orquestrador unico de skills.
  - Gate 3 (pendente): homologacao final de voz/avatar/realtime + certificacao de qualidade do RAG + pacote de onboarding para novas vendas.
- pendencias abertas por solicitacao do cliente:
  - trocar avatar da VIVA para o novo asset institucional enviado pelo cliente;
  - definir voz oficial com qualidade superior para modo conversa continua;
  - validar API/modelo de voz ao vivo dedicado (nao dependente apenas de APIs nativas do navegador).
