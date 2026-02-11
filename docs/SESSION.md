# SESSION - contexto atual da sessao

Sessao ativa: 10/02/2026
Status: rodada GODMOD pre-clean iniciada (persona dual + limpeza estrutural + memoria/RAG)
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
