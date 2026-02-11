# BUGSREPORT - Registro de Bugs

> **Projeto:** FC SoluÃ§Ãµes Financeiras SaaS  
> **Ãšltima AtualizaÃ§Ã£o:** 2026-02-11

---

## Bugs Ativos

| ID | Severidade | MÃ³dulo | DescriÃ§Ã£o | Status |
|---|---|---|---|---|
| BUG-010 | Baixa | PDF | WeasyPrint requer GTK+ no Windows | Resolvido (runtime Docker) |
| BUG-012 | MÃ©dia | VIVA | BotÃ£o de Ã¡udio no chat nÃ£o funciona | Resolvido |
| BUG-013 | MÃ©dia | VIVA | Erro `StackOverflowError` ao gerar imagem com prompt extra longo (REZETA/FC) | Resolvido |
| BUG-014 | MÃ©dia | VIVA | Upload de imagem falha quando a imagem Ã© PNG (MIME assumido como JPEG) | Resolvido |
| BUG-015 | Alta | VIVA | Fundo da imagem nÃ£o respeita paleta/brief do prompt (resultado genÃ©rico) | Em validaÃ§Ã£o (rodada 5 - tema livre) |
| BUG-016 | MÃ©dia | VIVA | Arte final perde partes do texto (overlay truncado) | Em validaÃ§Ã£o (rodada 3 - wrap/ellipsis) |
| BUG-017 | Alta | WhatsApp Chat API | Endpoints `/api/v1/whatsapp-chat/*` retornam 500 por incompatibilidade de modelagem (`SQLEnum`) com schema real (`VARCHAR`) | Resolvido |
| BUG-018 | Alta | WhatsApp Evolution | Backend consulta instÃ¢ncia/chave divergentes do runtime (instÃ¢ncia ativa `Teste`), causando falso desconectado (`Status 404`) | Resolvido |
| BUG-019 | MÃ©dia | Frontend WhatsApp | `/whatsapp/conversas` usa token incorreto (`localStorage.token`) e base URL hardcoded em `localhost:8000` | Resolvido |
| BUG-020 | Alta | Webhook WhatsApp | Resposta da VIVA nÃ£o Ã© enviada ao WhatsApp no webhook (envio real marcado como TODO) | Resolvido |
| BUG-021 | Alta | Webhook WhatsApp | Mensagem de Ã¡udio recebida no WhatsApp nÃ£o era transcrita para o fluxo da VIVA (Ã¡udio obrigatÃ³rio) | Resolvido |
| BUG-022 | MÃ©dia | Webhook WhatsApp | IntermitÃªncia de envio (`400 Text is required` e `exists:false`) por payload vazio/JID nÃ£o entregÃ¡vel no retorno da IA | Resolvido |
| BUG-023 | Alta | VIVA/OpenAI | `OPENAI_API_KEY` vazio no container por override do `docker-compose` bloqueava respostas da IA | Resolvido |
| BUG-024 | MÃ©dia | VIVA/OpenAI | GeraÃ§Ã£o de imagem falhava com `Unknown parameter: response_format` no endpoint OpenAI Images | Resolvido |
| BUG-025 | Alta | Contratos | CriaÃ§Ã£o de contrato em `/contratos/novo` falhava com `Network Error` porque `POST /api/v1/contratos` retornava `500` (`Template bacen nÃ£o encontrado`) | Resolvido |
| BUG-027 | Alta | Clientes/Contratos | Contratos criados sem vÃ­nculo de cliente nÃ£o apareciam na tela de clientes | Resolvido |
| BUG-028 | Alta | Contratos | GeraÃ§Ã£o de nÃºmero por contagem anual permitia duplicidade (`ix_contratos_numero`) quando havia gaps | Resolvido |
| BUG-026 | Alta | PDF | Endpoint `GET /api/v1/contratos/{id}/pdf` falhava com `500` por cadeia de dependencias inconsistente (Playwright ausente + incompatibilidade WeasyPrint/PyDyf) | Resolvido |
| BUG-029 | Alta | Clientes/Contratos | Duplicidade de cliente por CPF/CNPJ normalizado gerava `500` em `POST /api/v1/contratos` (`MultipleResultsFound`) e quebrava fluxo de fechamento de contrato | Resolvido |
| BUG-030 | MÃ©dia | Clientes/Contratos | Campo `total_contratos` em `/clientes` ficava desatualizado apÃ³s excluir contratos, mesmo apÃ³s sincronizaÃ§Ã£o de Ã³rfÃ£os | Resolvido |
| BUG-031 | MÃ©dia | Contratos/Layout | CabeÃ§alho institucional do contrato estava com logo desatualizada/arte inadequada para faixa azul no preview e nos geradores de PDF, divergindo da marca oficial `logo2.png` | Resolvido |
| BUG-032 | Alta | Contratos/CADIN | Texto jurÃ­dico do CADIN estava incompleto (clÃ¡usulas ausentes) e com perda de acentuaÃ§Ã£o no preview/PDF/template, divergindo do `cadinpfpjmodelo.docx` | Resolvido |
| BUG-033 | Alta | Contratos/Layout | Texto do preview de contrato apresentou caracteres corrompidos de acentuaÃ§Ã£o (mojibake), afetando leitura jurÃ­dica e identidade visual | Resolvido |
| BUG-034 | Baixa | Contratos/Layout | Campo `local_assinatura` legado (ex.: texto com encoding quebrado) ainda aparecia quebrado no rodapÃ© da assinatura em preview/PDF | Resolvido |
| BUG-037 | Alta | VIVA/Campanhas | Chat interno podia simular publicaÃ§Ã£o/links/download sem gerar e salvar arquivos reais no SaaS | Resolvido |
| BUG-038 | MÃ©dia | VIVA/Campanhas | Menu histÃ³rico de campanhas nÃ£o estava disponÃ­vel no dashboard e imagens geradas nÃ£o ficavam persistidas para revisÃ£o | Resolvido |
| BUG-039 | MÃ©dia | VIVA/Briefing | Fluxo de campanha podia travar pedindo o brief completo repetidamente quando faltava apenas CTA, sem resposta curta de continuidade | Resolvido |
| BUG-040 | MÃ©dia | VIVA/UI | BotÃ£o `Abrir imagem` no modal da VIVA abria aba em branco/sem conteÃºdo em parte dos navegadores | Resolvido |
| BUG-041 | MÃ©dia | VIVA/Briefing | ReferÃªncia visual anexada no chat nÃ£o era injetada no prompt final da campanha (imagem de saÃ­da sem aderÃªncia) | Resolvido |
| BUG-042 | MÃ©dia | Campanhas/UI | BotÃ£o `Abrir imagem` em `/campanhas` podia falhar por popup/blank tab, sem preview confiÃ¡vel no SaaS | Resolvido |
| BUG-044 | Alta | VIVA/Prompts | Drift entre `src/app/viva/PROMPTS`, `public/PROMPTS` e `docs/PROMPTS` podia carregar prompt divergente por fallback legado | Resolvido |
| BUG-045 | Alta | VIVA/Chat | Chat interno da VIVA nÃ£o persistia sessÃ£o/histÃ³rico por usuÃ¡rio e perdia contexto ao reabrir `/viva` | Resolvido |
| BUG-046 | Alta | VIVA/Agenda | Perguntas sobre agenda no chat interno entravam em loop de confirmaÃ§Ã£o e nÃ£o consultavam a agenda real automaticamente | Resolvido |
| BUG-047 | Alta | Agenda/API | Listagem/consulta de agenda nÃ£o filtrava por usuÃ¡rio, com risco de exibir/editar compromissos de terceiros | Resolvido |
| BUG-048 | Alta | Frontend/Build | `npm run build` falha por `useSearchParams()` sem `Suspense` em `/campanhas`, `/contratos/novo` e `/whatsapp/conversas` | Resolvido |
| BUG-049 | Alta | Backend/Testes | `pytest` interrompe na coleta por `ModuleNotFoundError: app.services.glm_image_service` em `backend/test_glm.py` | Resolvido |
| BUG-050 | Alta | Seguranca/Testes | Credenciais sensiveis hardcoded em `test_db.py` e `test_db2.py` (host, usuario e senha) | Resolvido |
| BUG-051 | Media | Documentacao/API | `docs/DEPLOY_UBUNTU_DOCKER.md` referencia `GET /api/v1/health`, endpoint inexistente no runtime atual | Resolvido |
| BUG-052 | Media | Documentacao/API | `docs/API.md` informa ausencia de auth em `/whatsapp-chat/*`, mas o backend exige token (`require_operador`) | Resolvido |
| BUG-053 | Baixa | Frontend/Tooling | `npm run lint` abre wizard interativo do Next.js (ESLint nao inicializado), impedindo lint automatizado | Resolvido |
| BUG-054 | Alta | VIVA/Persona | Contrato de persona da VIVA (concierge do Fabio) e da Viviane (secretaria humana) nao esta explicitamente separado por dominio, gerando ambiguidade de comportamento | Resolvido |
| BUG-055 | Alta | VIVA/Prompts | Pastas/arquivos de prompt duplicados (`frontend/public/PROMPTS`, `docs/PROMPTS`, `src/app/viva/PROMPTS`) aumentam drift e confusao operacional | Resolvido |
| BUG-056 | Alta | VIVA/Memoria | Memoria persistida existe, mas contexto do modelo no chat interno ainda depende do recorte do frontend (janela curta), sem reconstrucao server-side robusta por sessao | Resolvido |
| BUG-057 | Media | VIVA/Agenda | Interpretacao de agenda em linguagem natural ainda depende de regex/comandos rigidos em parte dos casos, elevando atrito conversacional | Resolvido |
| BUG-058 | Alta | VIVA/RAG | Ausencia de camada vetorial moderna (RAG) para memoria/conhecimento evolutivo de longo prazo no piloto | Resolvido |
| BUG-059 | Alta | Frontend/NextDev | `next dev` pode quebrar com `MODULE_NOT_FOUND` apontando para rota removida (`/api/viva/prompts/[promptId]/route`) por cache `.next` stale | Resolvido |
| BUG-060 | Alta | Frontend/Auth+Docs | Login no front exibe erro generico para qualquer falha e README publica senha de teste divergente do runtime local | Resolvido |
| BUG-061 | Alta | VIVA/Campanhas | Geracao de imagem pode ignorar tema do brief (ex.: Carnaval sem dividas) e cair em cena corporativa generica (senhor de terno em escritorio) | Em validacao (rodada 5 - tema+elenco+cenario) |
| BUG-062 | Alta | VIVA/Arquitetura | `backend/app/api/v1/viva.py` monolitico (chat+agenda+campanhas+midia+SQL) com alto acoplamento e baixa manutenibilidade | Em validacao (fatiamento SQL em repositorios) |
| BUG-063 | Alta | VIVA/Agenda UX | Fallback rigido de agenda exige formato textual prescritivo, reduz fluidez conversacional e gera efeito de "bot travado" | Resolvido |
| BUG-064 | Alta | VIVA->Viviane Orquestracao | Nao existe handoff operacional completo para aviso programado no WhatsApp (agenda da VIVA disparando persona Viviane no horario) | Resolvido |
| BUG-065 | Alta | VIVA/Handoff API | `GET /api/v1/viva/handoff` retorna `500` quando `meta_json` vem serializado como string e quebra validacao do schema | Resolvido |
| BUG-066 | Alta | VIVA/RAG Runtime | Falha em operacoes vetoriais podia abortar transacao principal do chat (`current transaction is aborted`) | Resolvido |
| BUG-067 | Alta | VIVA/Handoff UX | Consulta "tem pedidos de lembretes para a Viviane?" era roteada para agenda generica em vez de listar fila real de handoff | Resolvido |
| BUG-068 | Media | VIVA/UI Chat | Chat nao auto-rola para o final em toda interacao, obrigando rolagem manual durante conversa longa | Resolvido |
| BUG-069 | Media | VIVA/UI Chat | Campo de digitacao muito baixo para edicao de mensagens maiores, com baixa visibilidade | Resolvido |
| BUG-070 | Alta | VIVA/Audio UX | Audio era transcrito no front, mas sem texto digitado a transcricao nao era enviada para `/viva/chat`, entao VIVA nao respondia ao conteudo falado | Resolvido |
| BUG-071 | Media | VIVA/Audio UX | Gravacao de audio ainda ficava anexada aguardando Enter, em vez de fluxo direto institucional (parar > transcrever > enviar) | Resolvido |
| BUG-072 | Media | VIVA/UI+Audio UX | Atualizacao holografica ficou pouco perceptivel (avatar dentro da area rolavel) e audio gravado durante resposta podia voltar para anexo manual | Resolvido |
| BUG-073 | Alta | VIVA/Agenda NLU | Comando de agendamento em linguagem natural foi interpretado como consulta de agenda (nao criou compromisso) | Resolvido |
| BUG-074 | Media | VIVA/UI Holograma | Bloco de estilo do holograma ficava acoplado ao JSX da pagina e o cerebro 3D nao era interativo para iniciar conversa | Resolvido |
| BUG-075 | Alta | LP/HTML | Landing page externa exibindo trecho de JavaScript como texto por bloco duplicado apos fechamento estrutural do documento | Resolvido |
| BUG-076 | Alta | VIVA/UI Conversacao | Modo de conversacao da VIVA ficou acoplado ao chat normal (topo da pagina) em vez de ativacao dedicada por botao lateral/submenu | Resolvido |
| BUG-077 | Alta | VIVA/UI Conversacao | Conversa continua por voz + avatar central dedicado ainda nao atingiu experiencia institucional final | Resolvido |

---

## Atualizacao 2026-02-11 (triagem geral de status)

- total no quadro: `64` bugs.
- resolvidos: `60`.
- pendentes/ativos/validacao/pausa: `4`.
- prioridade funcional atual aprovada:
  - foco em campanhas e geracao de imagem (`BUG-061`);
  - modulo conversa continua finalizado no submenu dedicado (`BUG-076`, `BUG-077`);
  - refatoracao estrutural do monolito `viva.py` em andamento com fatiamento de persistencia (`BUG-062`).
- observacao institucional:
  - ha itens em `Em validacao` que podem ja estar corrigidos e apenas sem baixa documental final; sera feita rodada dedicada de prova de vida para baixar status com evidencia.

---

## Workarounds Ativos

- AutenticaÃ§Ã£o em dev aceita senha `1234` (`security_stub.py`)
- PDF via browser print no frontend (`frontend/src/lib/pdf.ts`)
- Download de PDF pelo backend reabilitado em `GET /api/v1/contratos/{id}/pdf`

---

## Validacao Read-only (2026-02-08)

- `BUG-013`: validado com `POST /api/v1/viva/chat` usando `prompt_extra` longo; endpoint respondeu `200` e retornou `resposta` + `midia`, sem `StackOverflowError`.
- `BUG-014`: validado com `POST /api/v1/viva/vision/upload` enviando arquivo `image/png`; endpoint respondeu `200` com anÃ¡lise da imagem.
- `BUG-017`: validado com autenticaÃ§Ã£o real e chamadas `GET /api/v1/whatsapp-chat/status` e `GET /api/v1/whatsapp-chat/conversas`; ambos `200`.
- `BUG-019`: validaÃ§Ã£o por cÃ³digo + endpoint:
  - front usa `api` compartilhada (`frontend/src/lib/api.ts`) com `access_token`;
  - `/whatsapp/conversas` consome rotas relativas (`/whatsapp-chat/*`) sem URL hardcoded local no arquivo da pÃ¡gina.
- `BUG-025`: validado com `POST /api/v1/contratos` (`template_id=bacen`) retornando `200` apÃ³s fallback de template + correÃ§Ã£o de numeraÃ§Ã£o.
- `BUG-027`: validado com criaÃ§Ã£o de contrato e consulta `GET /api/v1/clientes?search=...`; cliente foi criado/vinculado automaticamente.
- `BUG-028`: validado com nova criaÃ§Ã£o de contrato sem colisÃ£o de Ã­ndice Ãºnico (`CNT-2026-0006` criado com sucesso).
- `BUG-026`: validado com autenticacao real em `GET /api/v1/contratos/{id}/pdf`; retorno `200`, `Content-Type: application/pdf` e bytes iniciando com `%PDF-`.
- `BUG-029`: validado em 2026-02-09 com:
  - `GET /api/v1/clientes/documento/334.292.588-47` retornando `200`;
  - `POST /api/v1/contratos` com CPF duplicado historico retornando `201` (sem `500`);
  - `POST /api/v1/clientes` para mesmo CPF retornando `409`;
  - `POST /api/v1/clientes/deduplicar-documentos` executado com sucesso e base saneada para 1 cliente por CPF/CNPJ.
- `BUG-030`: validado em 2026-02-09 com:
  - exclusÃ£o real de contrato e atualizaÃ§Ã£o imediata de `total_contratos` no cliente vinculado;
  - `POST /api/v1/clientes/sincronizar-contratos` retornando `clientes_recalculados` e reconciliando cache x contagem real;
  - consulta SQL de conferÃªncia (`cache == real`) para os clientes ativos.
- `BUG-031`: validado em 2026-02-09 com:
  - troca da marca para `logo2.png` no preview (`/contratos/[id]`);
  - troca da marca para `logo2.png` na geraÃ§Ã£o PDF frontend (`frontend/src/lib/pdf.ts`);
  - troca da marca para `logo2.png` na geraÃ§Ã£o PDF backend (`backend/app/services/pdf_service_playwright.py`).
- `BUG-032`: validado em 2026-02-09 com:
  - clÃ¡usulas 1Âª a 5Âª completas no preview (`/contratos/[id]`) para template CADIN;
  - texto com acentuaÃ§Ã£o correta no PDF frontend (`frontend/src/lib/pdf.ts`) e backend (`backend/app/services/pdf_service_playwright.py`);
  - `contratos/templates/cadin.json` alinhado ao conteÃºdo jurÃ­dico da fonte DOCX.
- `BUG-033`: validado em 2026-02-09 com:
  - preview de contrato sem mojibake (acentuaÃ§Ã£o correta em cabeÃ§alho, clÃ¡usulas e dados das partes);
  - geraÃ§Ã£o de PDF frontend e backend com acentuaÃ§Ã£o correta e sem caracteres quebrados;
  - aumento leve de escala visual do layout para melhor legibilidade.
- `BUG-034`: validado em 2026-02-09 com:
  - preview (`/contratos/[id]`) normalizando `local_assinatura` legado no rodapÃ© da assinatura;
  - PDF frontend (`frontend/src/lib/pdf.ts`) normalizando `local_assinatura` antes de montar HTML;
  - PDF backend (`backend/app/services/pdf_service_playwright.py`) normalizando `local_assinatura` no render Playwright.
  - cadastro de novo contrato (`/contratos/novo`) persistindo `Ribeirao Preto/SP` como valor padrÃ£o correto.

---

## Bugs Resolvidos (Resumo)

| ID | MÃ³dulo | DescriÃ§Ã£o | Data |
|---|---|---|---|
| BUG-001 | Backend | DATABASE_URL nÃ£o exportado | 2026-02-03 |
| BUG-002 | Frontend | `output: 'export'` quebrava dev | 2026-02-03 |
| BUG-003 | Backend | Pydantic incompatÃ­vel | 2026-02-03 |
| BUG-004 | Auth | bcrypt 72 bytes no Windows | 2026-02-03 |
| BUG-005 | API | Import `require_admin` faltando | 2026-02-03 |
| BUG-006 | PDF | WeasyPrint sem GTK+ | 2026-02-03 |
| BUG-007 | Templates | Path em Windows | 2026-02-03 |
| BUG-008 | Frontend | Erros de API sem tratamento | 2026-02-03 |
| BUG-009 | UI | Badge e Tabs faltando | 2026-02-03 |
| BUG-011 | DB | JSONB/UUID incompatÃ­vel | 2026-02-03 |
| BUG-010 | PDF | Bloqueio de GTK+ no host Windows mitigado com runtime containerizado | 2026-02-07 |
| BUG-013 | VIVA | Prompt extra longo em geraÃ§Ã£o de imagem nÃ£o derruba mais o fluxo com stack overflow | 2026-02-07 |
| BUG-014 | VIVA | Upload PNG em visÃ£o estabilizado sem fallback forÃ§ado para JPEG | 2026-02-07 |
| BUG-017 | WhatsApp Chat API | Endpoints `whatsapp-chat` estabilizados sem 500 por enum/schema | 2026-02-07 |
| BUG-018 | WhatsApp Evolution | InstÃ¢ncia e chave divergentes geravam falso desconectado | 2026-02-07 |
| BUG-019 | Frontend WhatsApp | Chat de conversas passou a usar token/baseURL corretos via cliente HTTP compartilhado | 2026-02-07 |
| BUG-020 | Webhook WhatsApp | Resposta da VIVA nÃ£o era enviada (TODO removido e envio ativo) | 2026-02-07 |
| BUG-021 | Webhook WhatsApp | TranscriÃ§Ã£o de Ã¡udio estabilizada no fluxo ativo da VIVA (OpenAI) | 2026-02-07 |
| BUG-022 | Webhook WhatsApp | Blindagem contra resposta vazia e JID nÃ£o entregÃ¡vel (`exists:false`) | 2026-02-07 |
| BUG-023 | VIVA/OpenAI | Removido override vazio de `OPENAI_API_KEY` no compose | 2026-02-07 |
| BUG-024 | VIVA/OpenAI | Ajustado payload OpenAI Images sem `response_format` incompatÃ­vel | 2026-02-07 |
| BUG-025 | Contratos | CriaÃ§Ã£o de contrato estabilizada com fallback de template e numeraÃ§Ã£o segura | 2026-02-07 |
| BUG-026 | PDF | Endpoint `/contratos/{id}/pdf` estabilizado com fallback Playwright->WeasyPrint e pin de `pydyf==0.10.0` | 2026-02-08 |
| BUG-027 | Clientes/Contratos | Reativado vÃ­nculo automÃ¡tico cliente<->contrato e endpoint de sincronizaÃ§Ã£o de Ã³rfÃ£os | 2026-02-07 |
| BUG-028 | Contratos | NumeraÃ§Ã£o alterada para sequÃªncia por maior nÃºmero do ano (sem colisÃ£o por gaps) | 2026-02-07 |
| BUG-029 | Clientes/Contratos | Unicidade por CPF/CNPJ normalizado estabilizada com saneamento de duplicados e fim do `500` na criaÃ§Ã£o de contrato | 2026-02-09 |
| BUG-030 | Clientes/Contratos | Recalculo de mÃ©tricas de clientes apÃ³s exclusÃ£o de contrato e sincronizaÃ§Ã£o global de contagens | 2026-02-09 |
| BUG-031 | Contratos/Layout | Marca oficial `logo2.png` padronizada no preview e nos pipelines de PDF | 2026-02-09 |
| BUG-032 | Contratos/CADIN | Texto do CADIN alinhado ao modelo oficial (clÃ¡usulas completas + acentuaÃ§Ã£o) em preview/PDF/template | 2026-02-09 |
| BUG-033 | Contratos/Layout | CorreÃ§Ã£o de acentuaÃ§Ã£o corrompida (mojibake) + ajuste leve de escala visual no preview/PDF | 2026-02-09 |
| BUG-034 | Contratos/Layout | NormalizaÃ§Ã£o de `local_assinatura` legado para evitar texto corrompido no rodapÃ© da assinatura (preview + PDF frontend/backend) | 2026-02-09 |
| BUG-044 | VIVA/Prompts | Drift de prompt encerrado com remocao da cadeia file-based no chat interno | 2026-02-10 |
| BUG-048 | Frontend/Build | Build estabilizado com boundary `Suspense` para pÃ¡ginas com `useSearchParams` | 2026-02-10 |
| BUG-049 | Backend/Testes | Coleta pytest estabilizada sem import legado quebrado em `backend/test_glm.py` | 2026-02-10 |
| BUG-050 | Seguranca/Testes | Credenciais removidas de scripts de teste com parametrizaÃ§Ã£o por variÃ¡veis de ambiente | 2026-02-10 |
| BUG-051 | Documentacao/API | Deploy docs alinhado ao endpoint real de health (`/health`) | 2026-02-10 |
| BUG-052 | Documentacao/API | API docs alinhada com autenticaÃ§Ã£o obrigatÃ³ria em `whatsapp-chat` | 2026-02-10 |
| BUG-053 | Frontend/Tooling | Lint frontend automatizado sem wizard (ESLint inicializado) | 2026-02-10 |
| BUG-055 | VIVA/Prompts | Remocao de prompts duplicados e rota legada de leitura no frontend | 2026-02-10 |
| BUG-067 | VIVA/Handoff UX | Consulta de pedidos para Viviane passou a retornar fila de handoff real por periodo/status, sem cair em agenda generica | 2026-02-10 |
| BUG-012 | VIVA | Botao de audio passou a gravar/parar no microfone (com fallback para upload manual), anexando audio no chat | 2026-02-10 |
| BUG-068 | VIVA/UI Chat | Auto-scroll reforcado para manter foco no fim da conversa, inclusive com carregamento de imagem | 2026-02-10 |
| BUG-069 | VIVA/UI Chat | Campo de digitacao ampliado com autoaltura para melhor visibilidade em mensagens longas | 2026-02-10 |
| BUG-070 | VIVA/Audio UX | Transcricao de audio agora entra no fluxo do `/viva/chat` mesmo sem texto digitado, com fallback claro em caso de baixa qualidade | 2026-02-10 |
| BUG-071 | VIVA/Audio UX | Gravacao do microfone passou a disparar envio automatico ao finalizar (sem depender de Enter e sem bolha de anexo de audio no fluxo normal) | 2026-02-10 |

---

*Atualizado em: 2026-02-11*


## Atualizacao 2026-02-09 (rodada clientes + contratos)

### BUG-035: Mojibake na tela de contratos
**Data:** 2026-02-09
**Severidade:** Media
**Descricao:** textos da tela `/contratos` estavam com encoding quebrado (mojibake) em cards e acoes rapidas.
**Passos:** 1. Abrir `/contratos` 2. Ler descricoes dos cards 3. Validar bloco de acoes.
**Esperado:** textos com acentuacao legivel e consistente.
**Atual:** caracteres quebrados (`AÃƒÂ§ÃƒÂµes`, `RemoÃƒÂ§ÃƒÂ£o`, etc.).
**Status:** Resolvido

### BUG-036: Contagem/visibilidade de historico por cliente
**Data:** 2026-02-09
**Severidade:** Media
**Descricao:** no modulo clientes, contagem podia divergir em base legada e nao havia campo para visualizar historico de contratos por cliente.
**Passos:** 1. Excluir/criar contratos em sequencia 2. Comparar `/contratos/lista` x `/clientes` 3. Buscar historico no card do cliente.
**Esperado:** contagem coerente com contratos reais e historico visivel por cliente.
**Atual:** sem historico no card; risco de divergencia por metrica persistida antiga.
**Status:** Resolvido

### Validacao adicional (2026-02-09)
- `BUG-035`: `/contratos` renderizando descricoes e labels sem mojibake.
- `BUG-036`: `GET /api/v1/clientes` com total calculado por agregacao real de contratos.
- `BUG-036`: `/clientes` com botao `Ver historico` exibindo numero, template, status, valor e link do contrato.

### Atualizacao 2026-02-09 (VIVA - prompts e layout)
- `BUG-015` (em validacao):
  - front envia `modo` explicitamente para `/api/v1/viva/chat`;
  - backend prioriza `modo` do payload para aplicar fluxo FC/REZETA;
  - FC/REZETA agora exigem brief minimo (`objetivo`, `publico`, `formato`, `cta`) antes da geracao;
  - prompts do front unificados via rota interna `/api/viva/prompts/[promptId]` usando `frontend/src/app/viva/PROMPTS` como fonte canonica.
- `BUG-016` (em validacao):
  - modal de "Arte final" ajustado para uso em zoom 100% (scroll + largura maxima reduzida), evitando corte de botoes e preview.

### Atualizacao 2026-02-09 (VIVA - campanhas no SaaS)
- `BUG-037` (em validacao):
  - resposta textual da VIVA agora bloqueia afirmaÃ§Ãµes de upload/publicaÃ§Ã£o/link externo sem operaÃ§Ã£o real;
  - fluxo orienta geraÃ§Ã£o/anexo real no chat quando nÃ£o existe publicaÃ§Ã£o.
- `BUG-038` (em validacao):
  - backend com histÃ³rico persistente de campanhas em `viva_campanhas`;
  - novas rotas: `POST /api/v1/viva/campanhas`, `GET /api/v1/viva/campanhas`, `GET /api/v1/viva/campanhas/{id}`;
  - geraÃ§Ã£o de imagem em modos FC/REZETA salva automaticamente no histÃ³rico;
  - frontend com menu e tela `/campanhas` para revisar imagens, data e briefing salvo.
- `BUG-039` (em validacao):
  - parser de briefing reforÃ§ado para texto livre (`objetivo ... publico ... formato ...`), incluindo variaÃ§Ãµes comuns (`fortato`);
  - contexto de briefing preservado por mÃºltiplas mensagens de usuÃ¡rio;
  - quando faltar apenas `CTA`, resposta curta de continuidade substitui o loop de template completo;
  - opÃ§Ã£o de destrave rÃ¡pido com `usar CTA padrao`.

### Atualizacao 2026-02-09 (VIVA - FCNOVO + abertura de imagem)
- `BUG-039` (em validacao):
  - CTA deixou de bloquear geraÃ§Ã£o (fallback automÃ¡tico para `Saiba mais`);
  - fluxo de campanha nÃ£o entra em loop quando o usuÃ¡rio envia mensagem fora do briefing (ex.: saudaÃ§Ã£o);
  - pedido de dados faltantes ficou em linguagem natural, sem template rÃ­gido obrigatÃ³rio.
- `BUG-040` (em validacao):
  - corrigido `Abrir imagem` no modal de arte da VIVA para abrir preview interno (sem `about:blank`/popup bloqueado).
- `BUG-041` (em validacao):
  - anÃ¡lise de imagem anexada (`/viva/vision/upload`) agora Ã© incluÃ­da no payload de `/viva/chat` como referÃªncia visual do briefing.
- `BUG-042` (em validacao):
  - em `/campanhas`, aÃ§Ã£o `Abrir imagem` passou a usar modal de visualizaÃ§Ã£o no prÃ³prio SaaS com opÃ§Ã£o de download.

### Atualizacao 2026-02-09 (VIVA - fluxo simplificado sem burocracia)
- `BUG-039` (resolvido):
  - briefing de campanha em FC/Rezeta passou a aceitar conversa natural com defaults automÃ¡ticos (`objetivo`, `publico`, `formato`, `cta`);
  - confirmaÃ§Ã£o curta (`sim`, `ok`, `versao final png`, etc.) agora dispara geraÃ§Ã£o quando jÃ¡ existe contexto de campanha;
  - seleÃ§Ã£o curta (`1/2/3`) no passo de pÃºblico passa a ser interpretada e concluÃ­da.
- `BUG-043` (resolvido):
  - pedido de `logo` no modo FC/Rezeta nÃ£o deve mais cair no coletor de briefing de campanha; fluxo redireciona para geraÃ§Ã£o de logo/imagem direta.

### Atualizacao 2026-02-09 (pendencia aberta - gerador de imagem)
- `BUG-015` (pendente):
  - mesmo com melhorias de briefing e referencia visual, a imagem ainda pode repetir composicao padrao e nao refletir totalmente a cena solicitada;
  - proxima etapa: refino de scene-prompt + controle de variacao visual por campanha.

### Atualizacao 2026-02-09 (blocos 1 e 2 - prompts canonicos + memoria chat)
- `BUG-044` (em validacao):
  - rota `GET /api/viva/prompts/[promptId]` agora usa somente `frontend/src/app/viva/PROMPTS` como fonte canonica;
  - alias legado `CRIADORWEB -> CRIADORPROMPT` mantido sem fallback para `public/PROMPTS`.
- `BUG-045` (em validacao):
  - persistencia de chat adicionada com sessoes/mensagens por usuario (`viva_chat_sessions` e `viva_chat_messages`);
  - novas rotas:
    - `GET /api/v1/viva/chat/snapshot`
    - `POST /api/v1/viva/chat/session/new`
  - `POST /api/v1/viva/chat` passou a receber/retornar `session_id` e salvar mensagens (usuario + IA + midia);
  - frontend `/viva` agora recupera historico automaticamente ao abrir a tela e inicia nova sessao ao clicar em `Limpar`.

### Atualizacao 2026-02-10 (bloco 3 - agenda por linguagem natural)
- `BUG-046` (em validacao):
  - VIVA passou a consultar agenda real antes do modelo quando detectar pedido de agenda (ex.: "como esta minha agenda hoje?");
  - respostas de agenda agora retornam lista direta de compromissos sem loop de confirmaÃ§Ãµes;
  - follow-up curto ("sim", "quero", "todos") apÃ³s pergunta de agenda passa a executar listagem.
- `BUG-047` (em validacao):
  - `AgendaService` passou a suportar filtro por `user_id` em listagem/consulta/update/delete/concluir;
  - rotas de agenda passaram a usar `current_user.id` em todas as operaÃ§Ãµes;
  - chat VIVA passou a consultar/concluir apenas compromissos do usuÃ¡rio logado.

### Atualizacao 2026-02-10 (auditoria GODMOD pre-fix + frontend UP)
- Rollback institucional pre-fix registrado em:
  - `docs/ROLLBACK/rollback-20260210-104803-pre-fix-baseline.txt`
  - `docs/ROLLBACK/rollback-20260210-104803-pre-fix.patch`
  - `docs/ROLLBACK/rollback-20260210-104803-pre-fix-staged.patch`
  - `docs/ROLLBACK/rollback-20260210-104803-pre-fix-untracked.txt`
- Validacao read-only com frontend ativo:
  - `/`, `/viva`, `/contratos`, `/contratos/novo?template=bacen`, `/whatsapp`, `/whatsapp/conversas`, `/campanhas`: `200`
  - `/api/v1/auth/login` + chamadas autenticadas (`/auth/me`, `/viva/status`, `/whatsapp/status`, `/agenda`, `/clientes`): `200`
  - `POST /api/v1/viva/chat`: `200` com `session_id`
- Achados novos formalizados para correcao na proxima rodada:
  - `BUG-048`, `BUG-049`, `BUG-050`, `BUG-051`, `BUG-052`, `BUG-053`.

### BUG-048: Build falha por `useSearchParams` sem `Suspense`
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** build de producao falha em tres paginas por uso de `useSearchParams()` fora de boundary de `Suspense`.
**Passos:** 1. Executar `npm run build` em `frontend` 2. Observar etapa `Generating static pages`.
**Esperado:** build concluir sem erro.
**Atual:** erro de prerender em `/campanhas`, `/contratos/novo` e `/whatsapp/conversas`.
**Status:** Resolvido

### BUG-049: Suite `pytest` interrompida por import quebrado
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** `backend/test_glm.py` importa `app.services.glm_image_service`, modulo ausente no backend atual.
**Passos:** 1. Executar `pytest` em `backend` 2. Observar erro de coleta.
**Esperado:** suite coletar e executar testes.
**Atual:** `ModuleNotFoundError` interrompe a execucao.
**Status:** Resolvido

### BUG-050: Credenciais hardcoded em scripts de teste
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** scripts `test_db.py` e `test_db2.py` contem host/usuario/senha em texto claro versionado.
**Passos:** 1. Abrir `test_db.py` 2. Abrir `test_db2.py`.
**Esperado:** nenhum segredo/credencial sensivel hardcoded no repositorio.
**Atual:** credenciais expostas em texto puro.
**Status:** Resolvido

### BUG-051: Documentacao cita endpoint de health inexistente
**Data:** 2026-02-10
**Severidade:** Media
**Descricao:** documento de deploy cita `GET /api/v1/health`, mas o runtime expoe `GET /health`.
**Passos:** 1. Consultar `docs/DEPLOY_UBUNTU_DOCKER.md` 2. Testar `GET /api/v1/health`.
**Esperado:** docs refletirem endpoint real.
**Atual:** rota documentada retorna `404`.
**Status:** Resolvido

### BUG-052: Documentacao diverge de auth real no WhatsApp Chat
**Data:** 2026-02-10
**Severidade:** Media
**Descricao:** `docs/API.md` afirma ausencia de validacao de token em `/whatsapp-chat/*`, mas backend usa `require_operador`.
**Passos:** 1. Consultar `docs/API.md` (secao WhatsApp Chat) 2. Chamar `/api/v1/whatsapp-chat/status` sem token.
**Esperado:** docs e runtime coerentes.
**Atual:** sem token retorna `401`.
**Status:** Resolvido

### BUG-053: Lint nao automatizavel no frontend
**Data:** 2026-02-10
**Severidade:** Baixa
**Descricao:** `npm run lint` inicia assistente interativo de setup do Next.js em vez de executar lint.
**Passos:** 1. Executar `npm run lint` em `frontend`.
**Esperado:** comando lint rodar em modo nao interativo.
**Atual:** wizard interativo bloqueia validacao CI/local automatica.
**Status:** Resolvido

### Atualizacao 2026-02-10 (execucao de correcoes BUG-048..053)
- `BUG-048` (resolvido):
  - paginas com `useSearchParams` encapsuladas em `Suspense`:
    - `frontend/src/app/(dashboard)/campanhas/page.tsx`
    - `frontend/src/app/(dashboard)/contratos/novo/page.tsx`
    - `frontend/src/app/whatsapp/conversas/page.tsx`
  - validacao: `npm run build` concluiu e gerou estaticamente `/campanhas`, `/contratos/novo`, `/whatsapp/conversas`.
- `BUG-049` (resolvido):
  - `backend/test_glm.py` convertido para placeholder legado com `pytest.mark.skip`, removendo import quebrado na coleta.
  - validacao: `python -m pytest -q ..\\test_db.py ..\\test_db2.py .\\test_glm.py` -> `3 skipped` (sem erro de coleta).
- `BUG-050` (resolvido):
  - credenciais removidas de `test_db.py` e `test_db2.py`.
  - testes agora usam variaveis de ambiente (`TEST_DATABASE_URL` / `TEST_DB_*`) e fazem `skip` quando nao configuradas.
- `BUG-051` (resolvido):
  - `docs/DEPLOY_UBUNTU_DOCKER.md` atualizado para apenas `/health`.
- `BUG-052` (resolvido):
  - `docs/API.md` (secao WhatsApp Chat) alinhado para exigir Bearer JWT (`require_operador`) e retorno `401` sem token.
- `BUG-053` (resolvido):
  - frontend com ESLint inicializado (`frontend/.eslintrc.json` + `eslint` + `eslint-config-next`).
  - validacao: `npm run lint` executa direto sem wizard interativo.

### Atualizacao 2026-02-10 (pre-clean GODMOD: persona dupla + plano completo)
- Rollback institucional pre-clean registrado em:
  - `docs/ROLLBACK/rollback-20260210-112843-pre-clean-baseline.txt`
  - `docs/ROLLBACK/rollback-20260210-112843-pre-clean.patch`
  - `docs/ROLLBACK/rollback-20260210-112843-pre-clean-staged.patch`
  - `docs/ROLLBACK/rollback-20260210-112843-pre-clean-untracked.txt`
- Diagnostico consolidado:
  - VIVA e Viviane possuem papeis distintos de negocio, mas o contrato tecnico ainda esta fragmentado.
  - Persistem duplicacoes de prompts em multiplos caminhos.
  - Memoria do chat interno esta parcial (persistencia + janela curta de contexto no front).
  - Fluxo de agenda ainda tem pontos de rigidez conversacional.
  - Nao existe RAG vetorial moderno para aprendizado evolutivo.

### BUG-054: Contrato de persona dual nao consolidado
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** separacao de responsabilidades entre VIVA (concierge do Fabio no SaaS) e Viviane (secretaria humana/comercial) nao esta formalizada em um contrato unico de runtime por dominio.
**Passos:** 1. Revisar `backend/app/api/v1/viva.py` 2. Revisar `backend/app/services/viva_ia_service.py` 3. Comparar respostas `/viva` x webhook.
**Esperado:** personas explicitamente separadas por canal e objetivo de negocio.
**Atual:** coexistem regras/personas em fluxos diferentes, com risco de sobreposicao.
**Status:** Em validaÃ§Ã£o

### BUG-055: Prompts duplicados e drift estrutural
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** ha duplicidade de prompts em `frontend/public/PROMPTS`, `docs/PROMPTS` e `frontend/src/app/viva/PROMPTS`.
**Passos:** 1. Mapear arquivos `PROMPTS` no repo 2. Conferir rota de leitura atual.
**Esperado:** um unico caminho canonico para prompts ativos.
**Atual:** multiplas copias aumentam risco de divergencia.
**Status:** Resolvido

### BUG-056: Memoria parcial no chat interno
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** apesar de persistir sessoes/mensagens no backend, o contexto de inferencia do chat interno depende de recorte curto enviado pelo frontend.
**Passos:** 1. Revisar `frontend/src/app/viva/page.tsx` 2. Revisar montagem de contexto em `/api/v1/viva/chat`.
**Esperado:** reconstrucao server-side da memoria por sessao para contexto consistente.
**Atual:** memoria efetiva fica limitada e pode perder continuidade semantica.
**Status:** Em validaÃ§Ã£o

### BUG-057: Agenda ainda com rigidez conversacional
**Data:** 2026-02-10
**Severidade:** Media
**Descricao:** parser de agenda aceita linguagem natural em parte dos casos, mas ainda depende de formatos/regex em varias entradas reais.
**Passos:** 1. Testar frases naturais com variacoes de data/hora 2. Validar conclusao sem UUID.
**Esperado:** fluxo natural com baixo atrito e prompts de correcao curtos.
**Atual:** em alguns casos retorna instrucao de formato e quebra fluidez.
**Status:** Em validaÃ§Ã£o

### BUG-058: Ausencia de RAG vetorial moderno no piloto
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** sistema nao possui camada vetorial moderna para memoria de longo prazo e recuperacao semantica.
**Passos:** 1. Buscar integracao vetorial no backend 2. Validar inexistencia de provider vetorial.
**Esperado:** RAG com embeddings + busca semantica em store vetorial.
**Atual:** conhecimento dinamico baseado em texto/csv e regras locais.
**Status:** Ativo

### Plano de Correcao Completo (rodada institucional)
1. Bloco A (docs + rollback + inventario):
   - congelar estado com rollback;
   - registrar bugs e plano em `BUGSREPORT`, `STATUS`, `SESSION`, `DECISIONS`.
2. Bloco B (desfrankenstein de prompts):
   - remover caminhos duplicados de prompt fora do fluxo canonico;
   - manter apenas protocolo GODMOD em docs.
3. Bloco C (persona por dominio):
   - definir VIVA como concierge do Fabio no backend `/viva`;
   - manter Viviane exclusiva no fluxo WhatsApp/webhook.
4. Bloco D (memoria):
   - mover montagem de contexto para backend por `session_id`;
   - reduzir dependencia de janela curta do frontend.
5. Bloco E (agenda natural):
   - melhorar parser com tolerancia linguistica e confirmacoes objetivas;
   - reduzir exigencia de formato/UUID para operacoes comuns.
6. Bloco F (RAG piloto):
   - escolher stack vetorial definitiva;
   - implementar ingestao, chunking, embeddings, retrieval e observabilidade.

### Atualizacao 2026-02-10 (execucao bloco B/C/D inicial)
- `BUG-055` (resolvido):
  - removidos prompts duplicados e rota de leitura legada:
    - `frontend/src/app/viva/PROMPTS/*` (removido)
    - `frontend/public/PROMPTS/*` (removido)
    - `frontend/src/app/api/viva/prompts/[promptId]/route.ts` (removido)
    - `docs/PROMPTS/*` mantidos apenas `GODMOD.md` e `PROJETISTA.md`.
- `BUG-044` (resolvido):
  - encerrado drift de prompt no runtime do frontend ao retirar cadeia de prompt file-based no chat interno.
- `BUG-054` (em validacao):
  - backend do chat interno recebeu persona dedicada de concierge:
    - `backend/app/services/viva_concierge_service.py`
    - uso em `backend/app/api/v1/viva.py` no builder de mensagens.
  - persona comercial da Viviane permanece no dominio WhatsApp/webhook:
    - `backend/app/services/viva_ia_service.py`
    - `backend/app/services/evolution_webhook_service.py`.
- `BUG-056` (em validacao):
  - contexto de inferencia passou a ser montado a partir do snapshot server-side da sessao:
    - `backend/app/api/v1/viva.py` (`_load_chat_snapshot` + `_context_from_snapshot`).
- `BUG-057` (em validacao):
  - conclusao de agenda passou a aceitar busca por titulo (alem de UUID), reduzindo atrito em linguagem natural.
- `BUG-058` (ativo):
  - direcao arquitetural definida para o piloto: `pgvector` (fase 1) com caminho de escala para Qdrant (fase 2);
  - implementacao da camada RAG ainda pendente nesta entrega.
- higiene adicional:
  - removidos artefatos legados sem uso:
    - `backend/app/services/openrouter_service.py`
    - `backend/app/services/brainimage_service_v1_backup.py`.
- validacao tecnica:
  - `npm run type-check` (frontend): OK
  - `npm run lint` (frontend): OK (warnings nao bloqueantes)
  - `npm run build` (frontend): OK
  - `python -m py_compile` (backend): OK para arquivos alterados
  - `pytest` alvo legado: `3 skipped` sem erro de coleta.
  - smoke runtime:
    - `GET /health`: `200`
    - `GET /viva` (frontend): `200`
    - `POST /api/v1/viva/chat` autenticado: `200` com `session_id`
    - `POST /api/v1/viva/chat` com `agendar reuniao teste viva amanha 10:30`: `200`
    - `POST /api/v1/viva/chat` com `concluir reuniao teste viva` (sem UUID): `200`.

### BUG-059: Next dev quebrando com referencia stale de rota removida
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** apos remover a rota `frontend/src/app/api/viva/prompts/[promptId]/route.ts`, o `next dev` pode manter dependencia stale no cache `.next` e falhar com `MODULE_NOT_FOUND` para a rota ja apagada.
**Passos:** 1. remover rota antiga 2. subir `npm run dev` sem limpar `.next` 3. observar erro de requireStack para `.../api/viva/prompts/[promptId]/route`.
**Esperado:** dev server recompilar sem dependencias de rota removida.
**Atual:** Watchpack/Webpack pode referenciar caminho antigo ate limpar cache local.
**Status:** Resolvido

### Atualizacao 2026-02-10 (incidente next dev local apos limpeza de prompts)
- ambiente fonte de verdade: local (`c:\projetos\fabio2`), sem deploy Ubuntu ativo nesta rodada.
- incidente observado no `npm run dev`:
  - `MODULE_NOT_FOUND` para `../../../../.next/server/app/api/viva/prompts/[promptId]/route`
  - warnings Watchpack em arquivos de sistema Windows (`C:\pagefile.sys`, `C:\swapfile.sys`, `C:\hiberfil.sys`).
- causa raiz:
  - cache `.next` stale apos remocao da rota de prompts legacy.
- correcao aplicada:
  - adicionado script de recuperacao no frontend:
    - `npm run clean:next` (remove `.next`)
    - `npm run dev:reset` (limpa cache e sobe `next dev`)
  - validacao: `npm run clean:next` OK; `npm run build` OK.
- procedimento oficial de recuperacao (passo a passo):
  1. encerrar qualquer `next dev` aberto.
  2. executar `cd frontend`.
  3. executar `npm run clean:next`.
  4. executar `npm run dev:reset`.
  5. se ainda houver ruido, apagar tambem `frontend/tsconfig.tsbuildinfo` e repetir.

### BUG-060: Mensagem de login generica + credencial de teste divergente
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** frontend mostrava "Email ou senha incorretos" para qualquer excecao (inclusive backend offline), enquanto `README.md` indicava senha de teste `senha123` divergente do runtime local (`security_stub.py` usa `1234`).
**Passos:** 1. abrir login no front 2. usar senha `senha123` 3. observar erro de credencial 4. simular falha de conexao e observar mesma mensagem generica.
**Esperado:** mensagem distinta para credencial invalida versus erro de conexao/servidor; documentacao alinhada com credencial dev real.
**Atual:** comportamento ajustado e docs alinhadas.
**Status:** Resolvido

### Atualizacao 2026-02-10 (correcao BUG-060)
- Frontend login (`frontend/src/app/page.tsx`):
  - `401` => "Email ou senha incorretos";
  - `403` => detalhe de usuario inativo;
  - outros HTTP => detalhe do backend ou codigo;
  - sem resposta HTTP => mensagem de conexao com backend.
- README alinhado:
  - `README.md` agora indica senha de teste local `1234` e referencia o `security_stub.py`.
- Validacao objetiva:
  - `POST /api/v1/auth/login` com `1234` => `200`.
  - `POST /api/v1/auth/login` com `senha123` => `401`.
  - `npm run type-check` => OK.
  - `npm run lint` => OK (warnings historicos nao bloqueantes).
- rollback institucional da micro-rodada:
  - `docs/ROLLBACK/rollback-20260210-140052-login-auth-baseline.txt`
  - `docs/ROLLBACK/rollback-20260210-140052-login-auth.patch`
  - `docs/ROLLBACK/rollback-20260210-140052-login-auth-staged.patch`
  - `docs/ROLLBACK/rollback-20260210-140052-login-auth-untracked.txt`

### Atualizacao 2026-02-10 (execucao BUG-061 - aderencia de tema em campanhas)
- Ajustes tecnicos aplicados em `backend/app/api/v1/viva.py`:
  - pipeline de copy de campanha refeito para usar `tema + objetivo + publico + oferta` como base da cena;
  - fallback deixou de fixar cena corporativa padrao (terno/escritorio) e passou a montar seed dinamica por briefing;
  - prompt de imagem para FC/Rezeta agora reforca paleta por marca e evita estereotipo corporativo quando nao solicitado;
  - fluxo conversacional de campanha ajustado para modo natural:
    - sugere 3 modelos rapidos quando o usuario descreve campanha;
    - gera imediatamente quando houver comando direto (`gerar agora`, `gera imagem`) ou confirmacao;
    - limite de conducoes curtas controlado por gate count.
- Ajuste de interpretacao:
  - detector de intencao direta de geracao ficou menos agressivo (nao trata "vou fazer campanha" como "gerar agora");
  - parser de oferta preserva percentual (`8%`) em frases naturais.
- Validacao objetiva desta rodada:
  - `python -m compileall backend/app/api/v1/viva.py backend/app/services/viva_concierge_service.py` => OK;
  - teste de parser no `backend\\venv` com frase natural de campanha => campos esperados (`tema`, `publico`, `formato`, `oferta 8%`) extraidos.
  - smoke API autenticado (`localhost:8000`):
    - `POST /api/v1/viva/chat` com frase natural de campanha (modo `FC`) => resposta de "Sugestoes rapidas" em ate 3 gates;
    - `POST /api/v1/viva/chat` na mesma sessao com `gerar agora` => `Imagem gerada com sucesso e salva em Campanhas.` com `midia[0].tipo = imagem`;
    - `GET /api/v1/viva/campanhas?page=1&page_size=3` => item novo persistido no historico.
- Status:
  - `BUG-061` movido para **Em validacao** (pendente validacao visual final no chat `/viva` com geracao real de imagem).

### Atualizacao 2026-02-10 (reabertura BUG-061 - repeticao de personagem)
- incidente observado no front `/campanhas`: multiplas artes com composicao visual muito semelhante (mesmo personagem masculino em escritorio), mesmo em briefs de temas diferentes.
- impacto: queda de aderencia de campanha por marca/tema e percepcao de baixa inteligencia criativa da VIVA.
- acao planejada nesta rodada:
  - reforcar prompt de cena com anti-repeticao de personagem e composicao;
  - vincular mais forte tema/publico/oferta na direcao de arte;
  - aplicar variacao controlada de enquadramento e situacao por geracao.

### Atualizacao 2026-02-10 (execucao BUG-061 - anti-repeticao visual)
- ajustes aplicados em `backend/app/api/v1/viva.py`:
  - prompt de imagem de campanha agora injeta direcao obrigatoria por `tema + publico + oferta + objetivo`;
  - adicionado `variation_id` por geracao para quebrar repeticao de personagem/composicao;
  - reforco explicito no prompt: nao repetir personagem/rosto de geracoes anteriores;
  - formatacao de imagem passou a usar tamanho dinamico por `formato` (ex.: `4:5` -> `1024x1536`).
- validacao objetiva:
  - `python -m compileall backend/app/api/v1/viva.py` => OK;
  - `POST /api/v1/viva/chat` (modo FC, tema carnaval sem dividas, desconto 8%, gerar agora) => `200` com midia;
  - `GET /api/v1/viva/campanhas?modo=FC&page=1&page_size=1` => ultimo item salvo com:
    - `meta.size = 1024x1536`;
    - `overlay.publico = Publico geral (PF)`;
    - `overlay.tema` preenchido;
    - `overlay.scene` descrevendo grupo diverso e sem terno como padrao.
- status:
  - `BUG-061` mantido em **Em validacao** (aguardando validacao visual final do Fabio no front `/campanhas`).

### Atualizacao 2026-02-11 (reabertura BUG-061 - repeticao de personagem persiste)
- incidente validado novamente pelo usuario no front `/campanhas`: campanhas diferentes ainda retornam padrÃ£o visual parecido (mesma tipologia de rosto/composicao).
- auditoria tecnica (somente leitura):
  - `backend/app/api/v1/viva.py` ja possui guardrails anti-repeticao e `variation_id`;
  - porem o fluxo ainda converge para campos default recorrentes (`objetivo=Geracao de leads`, `publico=Publico geral (PF)`) quando o brief vem incompleto;
  - `scene` e sanitizada com limite curto (`_sanitize_prompt(..., 240)`), reduzindo riqueza de direcao visual e favorecendo prompt genÃ©rico;
  - geracao de copy em `_generate_campaign_copy` usa temperatura baixa (`0.35`), aumentando repetibilidade de cena/headline.
- decisao da rodada:
  - `BUG-061` reaberto para correÃ§Ã£o focada em diversidade visual (persona/cena/composicao) antes de novos modulos.
- status:
  - `BUG-061` => **Reaberto (Ativo)**.

### Atualizacao 2026-02-11 (execucao BUG-061 - rodada 2 diversidade visual)
- backend ajustado em `backend/app/api/v1/viva.py`:
  - nova variacao humana por seed (`_persona_scene_variant`) com combinacao de perfil, ambiente e acao;
  - variacao estavel por seed (`_stable_pick`) aplicada em elenco/humor;
  - `scene` ampliada de limite curto para limite maior (420 chars) para reduzir prompt comprimido/generico;
  - prompt final de imagem reforcado com:
    - diretriz de elenco obrigatoria;
    - variacao de enquadramento;
    - humor visual por campanha;
    - anti-repeticao explicita de rosto/cabelo/faixa etaria/composicao;
  - geracao de copy da campanha com maior variabilidade (`temperature` de 0.35 para 0.6) e instrucao anti-repeticao mais forte.
- validacao tecnica executada:
  - `python -m compileall app/api/v1/viva.py` => OK;
  - smoke local de prompt com 3 `variation_id` diferentes para mesmo brief:
    - diretrizes de elenco diferentes;
    - enquadramentos diferentes;
    - humor visual variando por seed.
- status:
  - `BUG-061` => **Em validacao (rodada 2)** aguardando validacao visual do Fabio no front `/campanhas`.

### Atualizacao 2026-02-11 (execucao BUG-015 + BUG-061 - rodada 3 tema dinamico)
- solicitacao institucional aplicada:
  - remover hardcode de tema sazonal no backend (nao depender de lista fixa tipo carnaval/score etc.);
  - manter direcao 100% dinamica a partir do briefing livre do usuario.
- backend ajustado em `backend/app/api/v1/viva.py`:
  - `_theme_scene_hint` refatorado para estrategia generica:
    - prioriza `tema` informado;
    - fallback por `oferta`/`objetivo`;
    - sem branch de temas especificos.
  - parser de tema livre (`_infer_campaign_fields_from_free_text`) reforcado:
    - extrai `tema ...` explicitamente;
    - fallback por frase natural `campanha de/do/da/para ...`.
  - parser de oferta percentual ajustado para cortar ruido de frase longa:
    - evita capturar `formato/publico/objetivo` junto da oferta.
  - diversidade de personagens ampliada com memoria curta de campanhas:
    - novo pool de perfis por publico (`PF/MEI/PJ`);
    - selecao anti-repeticao via historico recente (`cast_profile` + `recent_cast_ids`);
    - prompt final inclui diretriz de elenco obrigatoria e ids recentes para evitar repeticao visual.
- validacao tecnica executada:
  - `python -m py_compile app/api/v1/viva.py` => OK;
  - smoke parser (`backend/venv`) com texto livre:
    - entrada: `campanha de pascoa sem aperto ... 8% de desconto ... formato 4:5`;
    - saida: `tema='pascoa sem aperto'` e `oferta='8% de desconto no limpa nome'`.
  - smoke prompt builder:
    - confirma inclusao de `Elenco obrigatorio desta peca` e `Perfis recentes para evitar repeticao`.
- status:
  - `BUG-015` => **Em validacao (rodada dinamica)**.
  - `BUG-061` => **Em validacao (rodada 3)**.

### BUG-062: Monolito tecnico em `viva.py`
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** `backend/app/api/v1/viva.py` concentra responsabilidades de chat, agenda, campanhas, audio, visao, video e acesso SQL, com alto acoplamento e baixa evolucao segura.
**Passos:** 1. abrir o arquivo 2. revisar funcoes/rotas e responsabilidades misturadas.
**Esperado:** router leve + servicos especializados por dominio (agenda, campanhas, memoria, handoff WhatsApp).
**Atual:** arquivo monolitico com regras de negocio e persistencia misturadas.
**Status:** Ativo

### BUG-063: Rigidez conversacional no fallback de agenda
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** em falhas parciais de interpretacao, o chat retorna instrucao prescritiva de formato fixo, reduzindo fluidez e passando percepcao de bot travado.
**Passos:** 1. enviar pedido de agenda com variacao natural 2. observar resposta exigindo template textual.
**Esperado:** follow-up contextual curto e inteligente, sem exigir frase identica.
**Atual:** fallback com frase fixa e orientacao rigida.
**Status:** Ativo

### BUG-064: Falta de handoff completo VIVA -> Viviane por agenda
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** nao ha fluxo completo para VIVA registrar compromisso/acao de aviso e disparar a Viviane no WhatsApp no horario programado com retorno de status ao Fabio.
**Passos:** 1. pedir para VIVA agendar e avisar cliente 2. validar disparo automatico no horario.
**Esperado:** orquestracao fluida `Fabio -> VIVA -> Viviane -> Fabio` com rastreabilidade.
**Atual:** fluxo parcial, sem motor de handoff operacional fechado.
**Status:** Ativo

### BUG-065: Falha de serializacao `meta_json` na listagem de handoff
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** endpoint `GET /api/v1/viva/handoff` pode retornar `500` quando `meta_json` chega como `str` e o `response_model` espera `dict`.
**Passos:** 1. autenticar no backend 2. criar handoff via chat ou endpoint 3. consultar `/api/v1/viva/handoff`.
**Esperado:** listagem responder `200` com `meta_json` em objeto JSON.
**Atual:** erro de validacao Pydantic (`meta_json` tipo `str`).
**Status:** Resolvido

### Atualizacao 2026-02-10 (correcao BUG-065)
- ajuste aplicado em `backend/app/api/v1/viva.py`:
  - `_handoff_row_to_item` passou a normalizar `meta_json` com `_safe_json(...)` para entradas `dict` e `str`;
  - `_campaign_row_to_item` recebeu a mesma blindagem para `overlay_json` e `meta_json`.
- validacao objetiva:
  - `python -m compileall backend/app/api/v1/viva.py` => OK;
  - `POST /api/v1/auth/login` => `200`;
  - `POST /api/v1/viva/chat` com agenda+handoff => `200` com ID de handoff;
  - `GET /api/v1/viva/handoff?page=1&page_size=5` => `200` e `meta_json` retornando objeto (sem `500`).

### Atualizacao 2026-02-10 (Aprovado - kickoff redesign VIVA em 3 etapas)
- Etapa 1 (documentacao + rollback institucional):
  - registrar bugs estruturais (`BUG-062`, `BUG-063`, `BUG-064`);
  - publicar blueprint tecnico em `docs/ARCHITECTURE/VIVA_REDESIGN.md`;
  - gerar commit de seguranca antes da refatoracao pesada.
- Etapa 2 (refatoracao backend por dominios):
  - separar router, orquestrador e servicos de agenda/campanhas/midia/memoria;
  - remover fallback rigido de agenda e adotar follow-up contextual.
- Etapa 3 (orquestracao e memoria evolutiva):
  - implementar fluxo `Fabio -> VIVA -> Viviane -> Fabio`;
  - memoria longa com `pgvector` + filtros contextuais por empresa/modulo/usuario.

### Atualizacao 2026-02-10 (execucao inicial BUG-063 - agenda menos robotica)
- Ajuste aplicado em `backend/app/api/v1/viva.py`:
  - substituido fallback fixo de agenda por `_build_agenda_recovery_reply(...)` com resposta contextual;
  - removida instrucao prescritiva unica "use: agendar TITULO | DD/MM...".
- Comportamento novo:
  - quando faltar horario, a VIVA pede apenas data/hora em linguagem natural;
  - quando horario estiver inconsistente, pede confirmacao curta;
  - sem exigir frase identica para continuar o fluxo.
- Status:
  - `BUG-063` movido para **Em validacao**.

### Atualizacao 2026-02-10 (execucao inicial BUG-064 - handoff VIVA -> Viviane)
- Novos componentes:
  - `backend/app/services/viva_handoff_service.py`
  - `backend/app/services/viva_capabilities_service.py`
  - `backend/app/services/viva_agenda_nlu_service.py`
- Novos endpoints em `backend/app/api/v1/viva.py`:
  - `GET /api/v1/viva/capabilities`
  - `POST /api/v1/viva/handoff/schedule`
  - `GET /api/v1/viva/handoff`
  - `POST /api/v1/viva/handoff/process-due`
- Integracao no chat:
  - ao detectar pedido de agenda + "avisar cliente no WhatsApp", a VIVA cria compromisso e agenda handoff para Viviane.
- Validacao objetiva:
  - `GET /api/v1/viva/capabilities` retornando catalogo (`4` dominios);
  - `POST /api/v1/viva/chat` com "agendar ... avisar cliente no whatsapp <numero>" retornando handoff ID;
  - `GET /api/v1/viva/handoff` listando tarefa `pending`;
  - `POST /api/v1/viva/handoff/schedule` com horario vencido + `POST /api/v1/viva/handoff/process-due` processando envio (`processed=1`, `sent=1`).
- Status:
  - `BUG-064` movido para **Em validacao**.

### Atualizacao 2026-02-10 (fechamento BUG-063 e BUG-064)
- Fluidez de agenda validada:
  - `POST /api/v1/viva/chat` com pedido incompleto de agenda retorna follow-up contextual curto, sem exigir template fixo.
- Handoff VIVA -> Viviane validado ponta-a-ponta:
  - tarefa criada via chat/endpoint;
  - processamento automatico em background no backend (worker de lifespan);
  - transicao de status observada (`pending -> sent`) em tarefa vencida.
- Evidencias tecnicas:
  - health backend `200` apos restart;
  - `GET /api/v1/viva/capabilities` ativo;
  - `GET /api/v1/viva/handoff` listando tarefas;
  - tarefa teste vencida com `attempts=1`, `sent_at` preenchido e `status=sent`.
- Status:
  - `BUG-063` => **Resolvido**.
  - `BUG-064` => **Resolvido**.

### BUG-066: Falha de transacao no chat com memoria vetorial
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** em falhas internas de memoria vetorial (DDL/query), a transacao do request podia ficar abortada e quebrar o fluxo do chat com erro SQL subsequente.
**Passos:** 1. enviar mensagem no chat com memoria vetorial ativa 2. ocorrer erro interno em operacao RAG 3. observar `current transaction is aborted`.
**Esperado:** falhas de memoria nao derrubarem a transacao principal do chat.
**Atual:** operacoes de memoria isoladas com savepoint, sem contaminar fluxo principal.
**Status:** Resolvido

### Atualizacao 2026-02-10 (execucao RAG vetorial + memoria hibrida)
- infraestrutura:
  - Postgres migrado para imagem com extensao vetorial:
    - `docker-compose.yml`, `docker-compose.local.yml`, `docker-compose-prod.yml`, `docker-compose.prod.yml` usando `pgvector/pgvector:pg15`;
  - extensao `vector` validada no runtime local.
- backend:
  - novo servico `backend/app/services/viva_memory_service.py`:
    - memoria media (Redis) por sessao;
    - memoria longa (pgvector) por usuario/sessao;
    - busca semantica (`memory/search`);
    - reindexacao de historico salvo (`memory/reindex`);
    - status operacional (`memory/status`).
  - `backend/app/services/openai_service.py`:
    - suporte a embeddings (`OPENAI_EMBEDDING_MODEL`, endpoint `/embeddings`).
  - `backend/app/api/v1/viva.py`:
    - ingestao de memoria em mensagens de usuario/IA;
    - contexto de memoria recuperado e injetado no prompt de sistema;
    - novos endpoints:
      - `GET /api/v1/viva/memory/status`
      - `GET /api/v1/viva/memory/search`
      - `POST /api/v1/viva/memory/reindex`
      - `GET /api/v1/viva/chat/sessions` (recuperacao de sessoes salvas)
    - ajuste de handoff para evitar serializacao indevida de `meta`.
  - blindagem de runtime:
    - operacoes de memoria isoladas em `savepoint` para impedir quebra da transacao principal do chat.
- validacao objetiva:
  - `GET /health` => `200`;
  - `GET /api/v1/viva/memory/status` => `vector_enabled=true`, `redis_enabled=true`;
  - `POST /api/v1/viva/memory/reindex?limit=120` => processa/indexa historico;
  - `GET /api/v1/viva/memory/search?q=...` => retorna itens com score;
  - `POST /api/v1/viva/chat/session/new` + busca de memoria => historico longo continua acessivel apos limpar chat.
- status:
  - `BUG-056` => **Resolvido**.
  - `BUG-058` => **Resolvido**.
  - `BUG-066` => **Resolvido**.

### BUG-067: Consulta de lembretes da Viviane roteada para agenda generica
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** perguntas como "tem pedidos de lembretes para a Viviane?" estavam sendo interpretadas como consulta de agenda comum e nao retornavam a fila de handoff (WhatsApp) da Viviane.
**Passos:** 1. Criar handoff pendente para amanha 2. Perguntar no chat "tem pedidos de lembretes para a Viviane?" ou "... amanha?".
**Esperado:** listar pedidos reais de handoff da Viviane por periodo, com status.
**Atual:** fluxo corrigido com deteccao explicita de intent de handoff, filtro por periodo e resposta dedicada da fila da Viviane.
**Status:** Resolvido

### Atualizacao 2026-02-10 (query Viviane no chat)
- backend:
  - `backend/app/api/v1/viva.py` recebeu deteccao dedicada para consulta de handoff da Viviane;
  - adicionados filtros de status (`pending/sent/failed`) e periodo (`hoje/amanha/semana`);
  - resposta agora e formatada como fila de pedidos da Viviane (cliente + horario + status + resumo da mensagem).
- validacao:
  - `POST /api/v1/viva/chat` com "tem pedidos de lembretes para a Viviane ?" => resposta dedicada (sem agenda generica);
  - `POST /api/v1/viva/handoff/schedule` + consulta "tem pedidos ... amanha?" => itens pendentes listados corretamente.

### BUG-068: Chat sem auto-scroll consistente
**Data:** 2026-02-10
**Severidade:** Media
**Descricao:** a conversa podia crescer sem manter o viewport no final, exigindo rolagem manual em mensagens longas.
**Passos:** 1. conversar por varias mensagens 2. gerar imagem 3. observar necessidade de rolar manualmente para ver o fim.
**Esperado:** chat acompanhar automaticamente o final da conversa.
**Atual:** auto-scroll reforcado com sentinela no fim da lista e ajuste apos render/carregamento.
**Status:** Resolvido

### BUG-069: Campo de digitacao pequeno para mensagens longas
**Data:** 2026-02-10
**Severidade:** Media
**Descricao:** textarea com altura inicial baixa, reduzindo visibilidade ao editar mensagens maiores.
**Passos:** 1. digitar mensagem com varias linhas 2. tentar revisar/editar antes de enviar.
**Esperado:** area de digitacao mais alta com crescimento conforme conteudo.
**Atual:** textarea ampliada (`minHeight=88`, `maxHeight=220`) com autoaltura e melhor legibilidade.
**Status:** Resolvido

### BUG-070: Transcricao de audio nao entrava no fluxo da VIVA
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** ao enviar apenas audio, o frontend mostrava a transcricao mas nao encaminhava esse texto para `/viva/chat`, entao a VIVA nao respondia ao conteudo falado.
**Passos:** 1. gravar audio sem digitar texto 2. enviar 3. observar que aparece transcricao mas sem resposta contextual da VIVA.
**Esperado:** transcricao deve virar mensagem do usuario para a VIVA responder normalmente.
**Atual:** fluxo ajustado para enviar a transcricao ao `/viva/chat` mesmo sem texto digitado, com fallback de aviso quando a transcricao vier vazia/ruim.
**Status:** Resolvido

### BUG-071: Gravacao ainda aguardava Enter e anexava audio no chat
**Data:** 2026-02-10
**Severidade:** Media
**Descricao:** mesmo com transcricao ativa, o fluxo de gravacao ainda podia ficar parado em "Anexos enviados", exigindo Enter manual e exibindo bolha de arquivo de audio.
**Passos:** 1. clicar mic para gravar 2. clicar mic para parar 3. observar anexo de audio pendente aguardando envio manual.
**Esperado:** ao parar gravacao, transcrever e enviar direto para a VIVA sem passo manual.
**Atual:** `onstop` do `MediaRecorder` envia automaticamente para `handleSend` com `anexosOverride` de audio; sem dependencia de Enter no fluxo normal.
**Status:** Resolvido

### Atualizacao 2026-02-10 (audio + UX chat VIVA)
- frontend:
  - `frontend/src/app/viva/page.tsx`:
    - botao de microfone passou a gravar/parar audio com `MediaRecorder` (fallback para upload manual quando necessario);
    - anexos de audio agora podem ser adicionados mesmo em repeticao do mesmo arquivo (reset do input file);
    - transcricao de audio agora entra no `POST /viva/chat` automaticamente quando nao houver texto digitado;
    - parada de gravacao no microfone passou a disparar envio automatico (stop > transcreve > envia), sem anexo pendente no fluxo normal;
    - mensagem de fallback clara quando a transcricao do audio vier vazia/baixa qualidade;
    - auto-scroll reforcado com sentinela no fim das mensagens e chamada apos novas mensagens/loading/imagens;
    - campo de digitacao ampliado e com autoajuste de altura para conversa longa.
- validacao:
  - `npm run lint -- --file src/app/viva/page.tsx` (ok, apenas avisos existentes de `img`);
  - `npm run type-check` (ok).
- status:
  - `BUG-012` => **Resolvido**.
  - `BUG-068` => **Resolvido**.
  - `BUG-069` => **Resolvido**.
  - `BUG-070` => **Resolvido**.
  - `BUG-071` => **Resolvido**.

### Atualizacao 2026-02-11 (execucao BUG-072 - audio em fila + holograma visivel)
- causa observada:
  - avatar holografico estava acoplado ao bloco rolavel do chat, reduzindo percepcao visual da atualizacao;
  - envio de audio durante resposta da VIVA podia cair no caminho manual em cenarios de concorrencia.
- correcao aplicada em `frontend/src/app/viva/page.tsx`:
  - avatar holografico movido para secao dedicada fixa logo abaixo do header (fora da `ScrollArea`);
  - fila de audio pendente (`pendingAudioAutoSend`) mantida para envio automatico quando `loading` encerra;
  - `handleSend` estabilizado com `useCallback` para evitar reexecucoes inconsistentes no efeito da fila.
- validacao tecnica:
  - `npm run type-check` => OK;
  - `npm run lint -- --file src/app/viva/page.tsx` => OK (somente warnings historicos de `<img>`).
- status:
  - `BUG-072` => **Em validacao** (aguardando confirmacao visual final em navegador pelo Fabio).

### BUG-073: Agendamento natural virou consulta de agenda
**Data:** 2026-02-11
**Severidade:** Alta
**Descricao:** no chat da VIVA, a frase de acao "agende o Andre amanha as 10 para mim. Mande para a agenda." foi tratada como consulta/listagem, retornando "Voce nao tem compromissos de amanha." sem criar compromisso.
**Passos:** 1. abrir `/viva` 2. enviar mensagem de criacao usando verbo de acao ("agende ... amanha as 10") 3. observar resposta da VIVA.
**Esperado:** criar compromisso para amanha as 10 e confirmar criacao (com ID/retorno de agenda).
**Atual:** VIVA responde com listagem vazia de amanha e nao executa criacao.
**Status:** Ativo

### Atualizacao 2026-02-11 (registro institucional de encerramento do dia)
- Solicitacao do usuario: apenas documentar o incidente e encerrar a rodada para retomada amanha.
- Acao executada: bug registrado sem aplicar correcao de codigo nesta janela.
- Proximo gate (retomada): corrigir desambiguacao de intencao em agenda (prioridade para verbo imperativo de criacao: "agende", "marque", "crie compromisso") antes da leitura de termos de consulta ("amanha", "hoje", "compromissos").

### BUG-076: Modo conversacao acoplado ao chat padrao
**Data:** 2026-02-11
**Severidade:** Alta
**Descricao:** o bloco visual da VIVA foi inserido no fluxo normal do chat, sem ativacao dedicada por submenu lateral para modo de conversacao.
**Passos:** 1. abrir `/viva` 2. observar bloco visual no topo do chat padrao 3. notar ausencia de chaveamento lateral dedicado.
**Esperado:** modo de conversacao ativado por botao lateral proprio e separado do fluxo normal do chat.
**Atual:** modo conversacao e visual estavam acoplados ao chat padrao.
**Status:** Em pausa (prioridade campanhas)

### Atualizacao 2026-02-11 (execucao BUG-073 + BUG-076)
- backend (`BUG-073`):
  - arquivo: `backend/app/services/viva_agenda_nlu_service.py`;
  - desambiguacao reforcada de intencao de criacao vs consulta:
    - inclusao de verbos imperativos (`agende`, `marque`, `crie`, `adicione`);
    - reducao de falso positivo em consulta quando houver verbo de criacao;
  - parser natural aceitando horario curto (ex.: `amanha as 10`, `10h`, `10:30`);
  - saneamento de titulo do compromisso para remover ruido de frases longas.
- frontend (`BUG-076`):
  - arquivo: `frontend/src/app/viva/page.tsx`;
  - novo botao lateral `Conversa VIVA` para ativar/desativar modo de conversacao;
  - bloco de conversacao exibido somente quando modo lateral estiver ativo;
  - voz de resposta da VIVA (TTS) ligada ao modo de conversacao, com toggle `Voz ativa/pausada`;
  - fallback institucional de avatar quando `public/viva-avatar.png` nao existir.
- validacao tecnica executada:
  - `frontend`: `npm run type-check` => OK;
  - `frontend`: `npm run lint -- --file src/app/viva/page.tsx` => OK (warnings nao bloqueantes de `<img>`);
  - `backend`: `python -m compileall app/services/viva_agenda_nlu_service.py app/api/v1/viva.py` => OK;
  - smoke NLU local:
    - entrada: `agende o Andre amanha as 10 ...`;
    - resultado: payload de criacao com `date_time` valido e `is_agenda_query_intent=False`.
- status:
  - `BUG-073` => **Em validacao** (aguardando validacao final no chat real com backend em execucao).
  - `BUG-076` => **Em validacao** (aguardando validacao visual final em `/viva`).

### BUG-077: Conversa VIVA sem voz continua e ainda acoplada ao chat visual
**Data:** 2026-02-11
**Severidade:** Alta
**Descricao:** no modo de conversacao da VIVA, o usuario ainda precisava acionar fluxo manual de audio e o layout mantinha estrutura de chat visivel, contrariando o requisito de experiencia continua por voz com avatar central dedicado.
**Passos:** 1. abrir `/viva` 2. ativar "Conversa VIVA" 3. validar que o chat continua visivel e que o fluxo de fala nao fica totalmente continuo.
**Esperado:** modo dedicado de conversacao por voz, com escuta automatica continua (sem botao Whisper/manual), resposta por voz e avatar central 3D sem feed de chat na tela.
**Atual:** modo parcial/hibrido, com elementos do chat tradicional ainda presentes no fluxo.
**Status:** Em pausa (prioridade campanhas)

### Atualizacao 2026-02-11 (execucao BUG-077 - conversa continua dedicada)
- frontend:
  - arquivo: `frontend/src/app/viva/page.tsx`;
  - modo `Conversa VIVA` passou a ser tela dedicada (sem feed de mensagens/chat visivel);
  - ativacao da escuta continua automatica com Web Speech API (`SpeechRecognition`/`webkitSpeechRecognition`), sem fluxo manual de Whisper/botao de envio;
  - pausa automatica da escuta enquanto a VIVA fala (TTS) e retomada automatica ao finalizar resposta;
  - avatar central holografico 3D com fallback em cadeia (`/viva-avatar.png`, `/viva-avatar-3d.png`, `/viva.png`, fallback Bot);
  - status de voz exibido em tempo real (`Escutando`, `Processando`, `Aguardando`) e toggle de voz da VIVA.
- validacao tecnica:
  - `frontend`: `npm run type-check` => OK;
  - `frontend`: `npm run lint -- --file src/app/viva/page.tsx` => OK (warnings nao bloqueantes de `<img>`).

### Atualizacao 2026-02-11 (pausa institucional do modulo Conversa VIVA)
- solicitacao do usuario: pausar evolucao da conversa continua/3D para priorizar funcional de campanhas e geracao de imagem.
- acao aplicada:
  - `BUG-076` e `BUG-077` movidos para estado **Em pausa (prioridade campanhas)**;
  - nenhuma nova alteracao de codigo de UI de conversa sera feita nesta janela.
- proximo foco aprovado:
  - atacar diversidade visual de campanhas e reduzir risco de repeticao de personagens (`BUG-061`);
  - manter `BUG-062` (monolito `viva.py`) no backlog tecnico ativo para fatiamento por dominio.

### BUG-074: Holograma 3D sem interacao e bloco de estilo misturado no JSX
**Data:** 2026-02-11
**Severidade:** Media
**Descricao:** no chat `/viva`, o bloco de estilo do holograma estava embutido no final do componente e o cerebro 3D nao tinha interacao para incentivar clique e inicio da conversa.
**Passos:** 1. abrir `/viva` 2. rolar o codigo do componente 3. validar holograma sem acao de clique/foco no chat.
**Esperado:** estilos centralizados no CSS global e avatar 3D clicavel, com movimento/feedback visual para guiar o usuario.
**Atual:** estilos movidos para `frontend/src/styles/globals.css`, cerebro 3D clicavel com efeito de movimento e foco no campo de mensagem.
**Status:** Resolvido

### Atualizacao 2026-02-11 (correcao BUG-074)
- frontend:
  - `frontend/src/app/viva/page.tsx`:
    - holograma convertido em botao acessivel com `aria-label`, clique e foco no composer;
    - cerebro alterado para `BrainCircuit` com CTA visual "Clique para conversar";
    - efeito de movimento 3D no hover/pointer para aumentar percepcao de interatividade;
    - remocao do bloco `<style jsx global>` no fim do componente.
  - `frontend/src/styles/globals.css`:
    - centralizacao de todo o design system do holograma (rings, scanline, nodes, animacoes, responsividade).
- validacao tecnica:
  - `npm run type-check` => OK
  - `npm run lint -- --file src/app/viva/page.tsx` => OK (apenas warnings conhecidos de `<img>`).

### BUG-075: JavaScript aparecendo como texto na landing page externa
**Data:** 2026-02-11
**Severidade:** Alta
**Descricao:** na landing page da Automania, um trecho de JavaScript do chat (ex.: `openChat`, `chat.appendChild`) estava sendo renderizado no corpo da pagina como texto visivel ao usuario.
**Passos:** 1. abrir a landing page publicada/local 2. rolar ate o rodape 3. observar codigo JS aparecendo junto de textos institucionais.
**Esperado:** scripts executados apenas no contexto JS, sem renderizacao de codigo cru no HTML visivel.
**Atual:** bloco duplicado e fora da estrutura principal do documento causa vazamento visual de JS.
**Status:** Resolvido

### Atualizacao 2026-02-11 (correcao BUG-075)
- origem identificada fora do repo SaaS:
  - `C:/Users/Lucas/Desktop/public_html/Kimi_Agent_Ajustes de UI no site (1)/index.html`
- causa raiz:
  - documento com bloco duplicado de script/markup, levando renderizacao de JS cru no corpo da pagina.
- acao aplicada:
  - restaurada versao integra do HTML sem duplicidade estrutural (base valida equivalente a `site novo/index.html`);
  - confirmada presenca unica de `</html>` e script encerrado corretamente.
- resultado:
  - removido vazamento visual de codigo (`openChat`, `chat.appendChild`, etc.) no rodape/conteudo.

### Atualizacao 2026-02-11 (execucao adicional BUG-073 - tolerancia de acentos/encoding)
- incidente reproduzido em teste local:
  - frase com `amanhã às 10` podia cair em `Data/hora invalida` em cenarios de encoding imperfeito.
- correcao aplicada em `backend/app/services/viva_agenda_nlu_service.py`:
  - parser de hora natural passou a ler no texto normalizado (`as 10`), cobrindo variacao com/sem acento;
  - fallback de hora por numero isolado condicionado a dica temporal (`amanha/hoje`);
  - deteccao de data aceita variacoes quebradas (`amanh*`, `hoj*`);
  - limpeza final de titulo reforcada para remover ruido residual de encoding.
- validacao:
  - `python -m py_compile app/services/viva_agenda_nlu_service.py` => OK;
  - smoke local com frase natural longa (`agende ... amanhã às 10`) retornou payload de criacao com `date_time` correto.
- status:
  - `BUG-073` permanece **Em validacao** aguardando prova final em uso real no chat `/viva`.

### Atualizacao 2026-02-11 (execucao BUG-016 - overlay truncado rodada 2)
- frontend ajustado em `frontend/src/app/viva/page.tsx` para reduzir corte de texto em preview/export da arte:
  - aumento de limites de texto no parser de overlay (headline/subheadline/bullets/quote);
  - modal `Arte final` com areas superior/inferior maiores (`32%` / `40%`) e `overflow-y-auto`;
  - melhorias de quebra de linha (`break-words`, `leading` mais compacto);
  - exportacao PNG via canvas com mais area para texto e distribuicao mais segura:
    - topo maior para headline/subheadline;
    - base maior para bullets/quote/cta;
    - wrap com limite vertical (`maxY`) para evitar corte seco.
- validacao tecnica:
  - `frontend`: `npm run type-check` => OK;
  - `frontend`: `npm run lint -- --file src/app/viva/page.tsx` => OK (apenas warnings nao bloqueantes de `<img>`).
- status:
  - `BUG-016` => **Em validacao (rodada 2)** aguardando validacao visual final no fluxo real.

### Atualizacao 2026-02-11 (execucao BUG-015 + BUG-061 - rodada 4 diversidade visual)
- backend atualizado em `backend/app/api/v1/viva.py` para reduzir repeticao de personagem/cenario na geracao de campanhas:
  - adicionado `scene_profile` (novo eixo de variacao) alem de `cast_profile`;
  - historico recente agora considera **elenco** e **cenario** para evitar repeticao nas proximas pecas;
  - pool de cenarios ampliado para PF/MEI/PJ (mais combinacoes antes de repetir);
  - prompt final recebeu bloqueio explicito de estereotipos de banco de imagem (ex.: mesmo retrato corporativo repetido).
- robustez do fluxo:
  - `_generate_campaign_copy` agora tem fallback seguro quando a etapa de copy (LLM) falhar/timeout, evitando `500` silencioso no `/viva/chat`;
  - geracao de imagem em campanhas (`FC`/`REZETA`) passou a usar `quality=high`.
- validacao tecnica local:
  - `python -m py_compile app/api/v1/viva.py` => OK;
  - simulacao de selecao sequencial:
    - `cast_profile` variou em 8/8 iteracoes;
    - `scene_profile` variou em 8/8 iteracoes (pool ampliado).
- status:
  - `BUG-015` => **Em validacao (rodada 4 - diversidade)**.
  - `BUG-061` => **Em validacao (rodada 4 - diversidade)**.

### Atualizacao 2026-02-11 (snapshot pre-commit validado)
- validacao tecnica consolidada do estado atual:
  - backend: `py_compile` dos modulos alterados => OK;
  - frontend: `type-check` => OK;
  - frontend: `lint` direcionado em `/viva` => OK (apenas warnings nao bloqueantes);
  - API read-only: health/auth/viva/agenda/clientes respondendo `200`.
- acao:
  - estado liberado para commit de seguranca e push no branch principal.

### Atualizacao 2026-02-11 (bloco adicional de baixa por prova viva)
- validacao executada (runtime local, somente leitura + smoke API):
  - `BUG-038`:
    - `POST /api/v1/viva/campanhas` => `200`;
    - `GET /api/v1/viva/campanhas?limit=20` => `200` com item salvo (`QA Persistencia Campanha`).
  - `BUG-045`:
    - `POST /api/v1/viva/chat/session/new` => `200`;
    - `POST /api/v1/viva/chat` + `GET /api/v1/viva/chat/snapshot` => sessao persistida com mensagens.
  - `BUG-046`:
    - `POST /api/v1/viva/chat` com `como esta minha agenda hoje?` => resposta direta da agenda real (`Seus compromissos de hoje`), sem loop rigido.
  - `BUG-047`:
    - criacao de eventos em dois usuarios QA distintos;
    - `GET /api/v1/agenda` por token mostrou isolamento correto (sem vazamento cruzado).
  - `BUG-073`:
    - frase real do incidente (`agende o Andre amanha as 10...`) voltou a criar compromisso;
    - listagem de amanha confirmou evento criado.
- validacao por leitura de codigo (frontend/backend):
  - `BUG-037`: sanitizacao anti-publicacao fake confirmada por teste direto de `_sanitize_fake_asset_delivery_reply`.
  - `BUG-040`/`BUG-042`:
    - `Abrir imagem` usa modal interno (`setImagemAtiva`) em `frontend/src/app/viva/page.tsx` e `frontend/src/app/(dashboard)/campanhas/page.tsx`;
    - sem `window.open`/`_blank` nesses fluxos.
  - `BUG-041`:
    - analise de imagem via `/viva/vision/upload` e injecao de `Referencia visual enviada pelo usuario` no payload de `/viva/chat`.
  - `BUG-054`:
    - persona interna separada em `viva_concierge_service.py` (VIVA concierge do Fabio);
    - persona WhatsApp separada em `viva_ia_service.py` (Viviane consultora da Rezeta), acionada por `evolution_webhook_service.py`.
  - `BUG-057`:
    - parser natural reforcado para mais verbos (incluindo `agenda ...`) e tolerancia temporal; smoke confirmou criacao sem formato rigido.
- status baixado neste bloco:
  - `BUG-037`, `BUG-038`, `BUG-040`, `BUG-041`, `BUG-042`, `BUG-045`, `BUG-046`, `BUG-047`, `BUG-054`, `BUG-057`, `BUG-073` => **Resolvidos**.

### Atualizacao 2026-02-11 (execucao bloco final dos 7 pendentes)
- backend (`BUG-062`):
  - SQL de chat e campanhas removido do router `backend/app/api/v1/viva.py` e extraido para repositorios:
    - `backend/app/services/viva_chat_repository_service.py`
    - `backend/app/services/viva_campaign_repository_service.py`
  - endpoints de sessao/campanha agora consomem servico de persistencia, reduzindo acoplamento de dominio + SQL no arquivo monolitico.
- backend campanhas (`BUG-015` + `BUG-061`):
  - parser de tema livre reforcado para conversa natural sem formato fixo (`_extract_unstructured_theme`);
  - prompt de imagem com ancora obrigatoria de `tema/oferta/cena`;
  - reforco de identidade de marca por distribuicao de cor (FC: azul/branco dominante, Rezeta: verde/azul dominante);
  - variacao adicional de aparencia (`_appearance_variant`) para reduzir repeticao de personagem.
- frontend arte final (`BUG-016`):
  - parser de overlay reduzido para 4 bullets maximos;
  - `wrapText` do export agora usa truncamento com ellipsis em vez de corte seco;
  - areas de texto do modal/export ampliadas para evitar perda de copy.
- frontend audio/voz (`BUG-072`, `BUG-076`, `BUG-077`):
  - upload manual de audio virou fluxo direto (selecionou audio -> transcreve/enviou), sem depender de Enter/anexo manual;
  - modo `Conversa VIVA` mantido como tela dedicada por submenu lateral;
  - holograma ganhou tilt 3D por ponteiro para reforco de presenca no modo conversacao.
- validacao tecnica:
  - `backend`: `python -m py_compile app/api/v1/viva.py app/services/viva_chat_repository_service.py app/services/viva_campaign_repository_service.py` => OK;
  - `frontend`: `npm run type-check` => OK;
  - `frontend`: `npm run lint -- --file src/app/viva/page.tsx` => OK (warnings nao bloqueantes de `<img>`).
- status desta rodada:
  - `BUG-072`, `BUG-076`, `BUG-077` => **Resolvidos**.
  - `BUG-015`, `BUG-016`, `BUG-061`, `BUG-062` => **Em validacao** (aguardando prova visual/funcional final em ambiente do Fabio).
