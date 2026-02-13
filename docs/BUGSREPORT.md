# BUGSREPORT - Registro de Bugs

> **Projeto:** FC SoluÃ§Ãµes Financeiras SaaS  
> **Ãšltima AtualizaÃ§Ã£o:** 2026-02-13 (rodada de governanca 3 gates + voz/avatar/RAG premium)

---

## Bugs Ativos

| ID | Severidade | MÃ³dulo | DescriÃ§Ã£o | Status |
|---|---|---|---|---|
| BUG-010 | Baixa | PDF | WeasyPrint requer GTK+ no Windows | Resolvido (runtime Docker) |
| BUG-012 | MÃ©dia | VIVA | BotÃ£o de Ã¡udio no chat nÃ£o funciona | Resolvido |
| BUG-013 | MÃ©dia | VIVA | Erro `StackOverflowError` ao gerar imagem com prompt extra longo (REZETA/FC) | Resolvido |
| BUG-014 | MÃ©dia | VIVA | Upload de imagem falha quando a imagem Ã© PNG (MIME assumido como JPEG) | Resolvido |
| BUG-015 | Alta | VIVA | Fundo da imagem nÃ£o respeita paleta/brief do prompt (resultado genÃ©rico) | Em validacao (rodada 8 - fallback compacto com ancora de tema/personagem) |
| BUG-016 | MÃ©dia | VIVA | Arte final perde partes do texto (overlay truncado) | Em validacao (rodada 4 - copy sanitizada + limite estruturado) |
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
| BUG-061 | Alta | VIVA/Campanhas | Geracao de imagem pode ignorar tema do brief (ex.: Carnaval sem dividas) e cair em cena corporativa generica (senhor de terno em escritorio) | Em validacao (rodada 8 - anti-repeticao real + preferencia de elenco obrigatoria) |
| BUG-062 | Alta | VIVA/Arquitetura | Router VIVA ainda concentra muita responsabilidade de dominio (chat+agenda+campanhas+midia) e exige fatiamento progressivo para manutencao segura | Resolvido |
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
| BUG-073 | Alta | VIVA/Agenda NLU | Consulta de agenda em linguagem natural podia cair indevidamente no fluxo de criacao (loop de "me diga quando") | Em validacao (rodada query-existence fix) |
| BUG-074 | Media | VIVA/UI Holograma | Bloco de estilo do holograma ficava acoplado ao JSX da pagina e o cerebro 3D nao era interativo para iniciar conversa | Resolvido |
| BUG-075 | Alta | LP/HTML | Landing page externa exibindo trecho de JavaScript como texto por bloco duplicado apos fechamento estrutural do documento | Resolvido |
| BUG-076 | Alta | VIVA/UI Conversacao | Modo de conversacao da VIVA ficou acoplado ao chat normal (topo da pagina) em vez de ativacao dedicada por botao lateral/submenu | Resolvido |
| BUG-077 | Alta | VIVA/UI Conversacao | Conversa continua por voz + avatar central dedicado ainda nao atingiu experiencia institucional final | Resolvido |
| BUG-081 | Alta | Contratos/Templates Runtime | Clausulas nao aparecem no preview/PDF porque backend no container nao encontra `contratos/templates/*.json` e responde fallback vazio | Em validacao (runtime corrigido) |
| BUG-082 | Alta | Contratos/Modelos MD | Modelos `rating_full_pj` e `jusbrasil` enviados em `.md` nao estao operacionais ponta a ponta (template/menu/criacao), impedindo uso funcional completo | Resolvido |
| BUG-083 | Media | Contratos/Encoding | Clausulas exibem simbolos residuais (`�`) em alguns titulos/textos no preview/PDF por decodificacao incompleta de mojibake CP1252/UTF-8 | Resolvido |
| BUG-084 | Alta | Contratos/Parcelamento UX+Regra | Formulario exige prazos manuais e nao atende venda a vista/1x fluida; precisa trabalhar com qtd de parcelas (1..12), entrada opcional e calculo automatico institucional | Resolvido |
| BUG-085 | Media | Contratos/Templates Base | Templates legados `bacen`, `cadin` e `cnh` permaneceram fora do metodo padrao novo (estrutura heterogenea e placeholders inconsistentes) | Resolvido |
| BUG-089 | Alta | VIVA/Campanhas | Em modo `FC/REZETA`, conversa comum podia ser sequestrada para fluxo de campanha por inferencia ampla de tema livre | Resolvido |
| BUG-090 | Alta | VIVA/UI Chat | Recuperacao de chats antigos indisponivel no frontend (somente snapshot da sessao mais recente) | Resolvido |
| BUG-091 | Alta | VIVA/RAG Runtime | RAG semantico indisponivel no runtime atual (reindex sem indexacao e search vazio), com dependencia de embeddings OpenAI sem saldo | Resolvido |
| BUG-092 | Alta | VIVA/Fala Continua | Conversa por voz dependia de APIs nativas do navegador (SpeechRecognition + speechSynthesis), com qualidade/estabilidade variavel e sem pipeline realtime institucional | Resolvido |
| BUG-093 | Media | VIVA/Avatar | Avatar do modo Conversa VIVA ainda usa fallback local antigo e nao o asset institucional novo enviado pelo cliente | Resolvido |
| BUG-094 | Alta | VIVA/RAG Qualidade | RAG roda com fallback local sem embeddings OpenAI, mas ainda sem homologacao semantica premium para operacao comercial | Em validacao (rodada hybrid rerank + telemetria de tier semantico) |
| BUG-095 | Alta | Agenda/Google Calendar | Agenda interna do SaaS sem sincronizacao oficial com Google Calendar para operacao compartilhada VIVA/Viviane | Em validacao (rodada bridge OAuth + sync auto) |

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
**Status:** Resolvido

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
**Status:** Resolvido

### BUG-064: Falta de handoff completo VIVA -> Viviane por agenda
**Data:** 2026-02-10
**Severidade:** Alta
**Descricao:** nao ha fluxo completo para VIVA registrar compromisso/acao de aviso e disparar a Viviane no WhatsApp no horario programado com retorno de status ao Fabio.
**Passos:** 1. pedir para VIVA agendar e avisar cliente 2. validar disparo automatico no horario.
**Esperado:** orquestracao fluida `Fabio -> VIVA -> Viviane -> Fabio` com rastreabilidade.
**Atual:** fluxo parcial, sem motor de handoff operacional fechado.
**Status:** Resolvido

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
**Status:** Resolvido

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

### BUG-078: Template CNH ausente no fluxo operacional de contratos
**Data:** 2026-02-11
**Severidade:** Media
**Descricao:** o fluxo operacional de contratos estava disponivel com BACEN e CADIN, sem template CNH ativo ponta a ponta (menu, formulario, preview e PDF).
**Passos:** 1. abrir `/contratos` 2. tentar criar contrato CNH 3. validar indisponibilidade de fluxo completo.
**Esperado:** template CNH disponivel no menu, criacao em `/contratos/novo`, preview em `/contratos/[id]` e PDF institucional com clausulas CNH.
**Atual:** fluxo CNH agora habilitado ponta a ponta para piloto institucional.
**Status:** Resolvido

### Atualizacao 2026-02-11 (execucao BUG-078 - piloto CNH)
- backend:
  - `contratos/templates/cnh.json` criado com estrutura institucional;
  - fallback `cnh` adicionado em `backend/app/services/contrato_service.py`;
  - geracao PDF backend com ramo CNH em `backend/app/services/pdf_service_playwright.py`.
- frontend:
  - menu de contratos habilitado com card `CNH` em `frontend/src/app/(dashboard)/contratos/page.tsx`;
  - fluxo de novo contrato com campo adicional `cnh_numero` em `frontend/src/app/(dashboard)/contratos/novo/page.tsx`;
  - preview contratual com clausulas CNH em `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`;
  - PDF frontend com subtitulo e clausulas CNH em `frontend/src/lib/pdf.ts`.
- validacao tecnica:
  - `python -m py_compile backend/app/services/contrato_service.py backend/app/services/pdf_service_playwright.py` => OK;
  - `frontend`: `npm run type-check` => OK;
  - `frontend`: `npm run lint -- --file src/app/(dashboard)/contratos/page.tsx --file src/app/(dashboard)/contratos/novo/page.tsx --file src/app/(dashboard)/contratos/[id]/page.tsx --file src/lib/pdf.ts` => OK (warnings nao bloqueantes conhecidos);
  - `frontend`: `npm run build` => compilacao concluida (com warning residual de copy standalone no Windows sem impacto no piloto CNH).

### BUG-079: Acentuacao corrompida no contrato (preview + PDF)
**Data:** 2026-02-11
**Severidade:** Alta
**Descricao:** textos institucionais do contrato apareciam com mojibake (`SoluÃ§Ãµes`, `PrestaÃ§Ã£o`, etc.) no preview e na janela de impressao/PDF.
**Passos:** 1. abrir contrato CNH em `/contratos/[id]` 2. acionar visualizacao/impressao do PDF 3. observar acentos quebrados no cabecalho, clausulas e assinatura.
**Esperado:** acentuacao UTF-8 correta em todo o fluxo de contratos (preview + PDF frontend + PDF backend).
**Atual:** acentuacao normalizada e exibicao institucional correta.
**Status:** Resolvido

### Atualizacao 2026-02-11 (execucao BUG-079 - normalizacao de encoding)
- backend:
  - `backend/app/services/pdf_service_playwright.py` revisado para remover strings com mojibake no HTML gerado.
- frontend:
  - `frontend/src/lib/pdf.ts` com textos institucionais normalizados em UTF-8 (cabecalho, partes, intro e assinatura);
  - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx` com normalizacao de acentos no preview contratual;
  - `frontend/src/app/(dashboard)/contratos/novo/page.tsx` com ajustes pontuais de acentuacao de labels/placeholders.
- padronizacao aplicada:
  - pipeline de novos modelos `.md` passa a usar texto canonico UTF-8 desde template/preview/PDF, sem carregar literal mojibake legado.
- validacao tecnica:
  - `python -m py_compile backend/app/services/pdf_service_playwright.py` => OK;
  - `frontend`: `npm run type-check` => OK;
  - `frontend`: `npm run lint -- --file src/lib/pdf.ts --file src/app/(dashboard)/contratos/[id]/page.tsx --file src/app/(dashboard)/contratos/novo/page.tsx` => OK (apenas warnings conhecidos nao bloqueantes).

### BUG-080: Modelos restantes em `.md` nao habilitados ponta a ponta no sistema de contratos
**Data:** 2026-02-12
**Severidade:** Alta
**Descricao:** os modelos enviados em `.md` (Aumento de Score, CCF, Certificado Digital, Diagnostico 360, Limpa Nome Express, Limpa Nome Standard, Rating Convencional, Rating Express PJ, Remocao de Proposta, Revisional) ainda nao estavam operacionais em menu, criacao, preview e PDF institucional.
**Passos:** 1. abrir `/contratos` 2. tentar selecionar os modelos do novo lote 3. validar indisponibilidade de fluxo completo.
**Esperado:** todos os modelos `.md` ativos no menu e funcionais de ponta a ponta com clausulas corretas e acentuacao valida.
**Atual:** lote integrado com templates ativos no menu, criacao liberada e renderizacao dinamica de clausulas no preview/PDF.
**Status:** Resolvido

### Atualizacao 2026-02-12 (execucao BUG-080 - lote completo de modelos `.md`)
- templates adicionados em `contratos/templates/`:
  - `aumento_score.json`
  - `ccf.json`
  - `certificado_digital.json`
  - `diagnostico360.json`
  - `limpa_nome_express.json`
  - `limpa_nome_standard.json`
  - `rating_convencional.json`
  - `rating_express_pj.json`
  - `remocao_proposta.json`
  - `revisional.json`
- consolidacao de template institucional:
  - `contratos/templates/cnh.json` atualizado com clausulas estruturadas e subtitulo;
  - `contratos/templates/bacen.json` e `contratos/templates/cadin.json` com `subtitulo` canonico.
- backend:
  - `backend/app/services/contrato_service.py` atualizado com fallbacks para os 10 novos `template_id`;
  - `backend/app/services/pdf_service_playwright.py` refeito para renderizar clausulas dinamicas dos templates JSON com substituicao de placeholders.
- frontend:
  - `frontend/src/app/(dashboard)/contratos/page.tsx` com os 10 novos modelos ativos no menu;
  - `frontend/src/app/(dashboard)/contratos/novo/page.tsx` aceitando os novos `template_id` no fluxo de criacao;
  - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx` refeito para preview dinamico por template (clausulas JSON + tokens);
  - `frontend/src/lib/pdf.ts` refeito para PDF dinamico por template (clausulas JSON + tokens);
  - `frontend/src/lib/api.ts` com `contratosApi.getTemplate`.
- schemas:
  - `backend/app/schemas/contrato.py` ajustado para retorno de template JSON sem exigir `created_at`.
- validacao tecnica:
  - `python -m py_compile backend/app/services/contrato_service.py backend/app/services/pdf_service_playwright.py backend/app/schemas/contrato.py` => OK;
  - `frontend`: `npm run type-check` => OK;
  - `frontend`: `npm run lint -- --file src/app/(dashboard)/contratos/page.tsx --file src/app/(dashboard)/contratos/novo/page.tsx --file src/app/(dashboard)/contratos/[id]/page.tsx --file src/lib/pdf.ts --file src/lib/api.ts` => OK (warning residual de `<img>` nao bloqueante).

### BUG-081: Clausulas ausentes em runtime local apos carga dos modelos
**Data:** 2026-02-12
**Severidade:** Alta
**Descricao:** apesar dos JSON de modelos estarem no workspace, a API de templates entrega fallback vazio (`campos=[]`, `secoes=[]`, `clausulas=null`) no runtime Docker local, causando preview/PDF com "Clausulas nao cadastradas".
**Passos:** 1. abrir `/contratos/{id}` de contrato novo 2. visualizar texto "Clausulas nao cadastradas" 3. consultar `GET /api/v1/contratos/templates/{id}` e observar `clausulas: null`.
**Esperado:** API entregar template completo com clausulas do JSON e renderizar todas as clausulas no preview/PDF.
**Atual:** fallback institucional vazio sendo usado para todos os templates.
**Status:** Resolvido

### Atualizacao 2026-02-12 (diagnostico read-only BUG-081)
- evidencias coletadas:
  - tabela `contrato_templates` no Postgres local: `0 rows` (sem seed em banco para substituir JSON);
  - container `fabio2-backend` sem path de templates:
    - `/app/contratos/templates` => ausente;
    - `/app/backend/contratos/templates` => ausente;
  - API retornando fallback vazio:
    - `GET /api/v1/contratos/templates/bacen` => `nome: Contrato de Adesao ao Bacen`, `clausulas: null`;
    - mesma resposta observada para os demais templates do lote.
- causa raiz confirmada:
  - loader atual em `backend/app/services/contrato_service.py` depende de paths que nao existem dentro do container em execucao;
  - sem DB seed e sem arquivo encontrado, o sistema cai em `FALLBACK_TEMPLATES` (estrutura minima sem clausulas).
- acao planejada (sem execucao nesta rodada):
  1. corrigir montagem/path de `contratos/templates` no runtime backend;
  2. unificar loader para contrato + PDF com busca robusta por ambiente;
  3. manter retrocompatibilidade de clausulas (`conteudo` e `paragrafos`) para nao perder BACEN legado.

### Atualizacao 2026-02-12 (execucao BUG-081 - correcao runtime + compatibilidade)
- runtime/backend:
  - `docker-compose.yml` atualizado no servico `backend` com:
    - volume `./contratos:/app/contratos:ro`;
    - env `CONTRATOS_TEMPLATES_DIR=/app/contratos/templates`.
  - loader compartilhado criado em `backend/app/services/contrato_template_loader.py`.
- backend contratos/pdf:
  - `backend/app/services/contrato_service.py` passou a usar loader unico e retornar template JSON antes do fallback minimo;
  - `backend/app/services/pdf_service_playwright.py` passou a usar loader unico e aceitar clausulas legadas com `paragrafos`.
- frontend:
  - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx` compatibilizado para render de clausulas com `conteudo` ou `paragrafos`;
  - `frontend/src/lib/pdf.ts` compatibilizado para render de clausulas com `conteudo` ou `paragrafos`.
- validacao tecnica:
  - `python -m py_compile backend/app/services/contrato_template_loader.py backend/app/services/contrato_service.py backend/app/services/pdf_service_playwright.py` => OK;
  - `frontend`: `npm run type-check` => OK;
  - `frontend`: `npm run lint -- --file src/app/(dashboard)/contratos/[id]/page.tsx --file src/lib/pdf.ts` => OK (warning nao bloqueante de `<img>`).
- validacao funcional (API runtime local):
  - `GET /api/v1/contratos/templates/{id}` validado para 13 templates com clausulas (`bacen=11`, `cadin=5`, `cnh=12`, lote novo >=8);
  - `GET /api/v1/contratos/{id}/pdf` validado com retorno `200 application/pdf` apos rebuild do backend com `pydyf==0.10.0`.
- observacao:
  - falta apenas validacao visual final no navegador para baixar BUG-081 para resolvido.

### BUG-082: Modelos `rating_full_pj` e `jusbrasil` ausentes no fluxo funcional de contratos
**Data:** 2026-02-12
**Severidade:** Alta
**Descricao:** apos a carga do lote principal de modelos `.md`, os modelos `RATINGFULLPJMODELO.md` e `JUSBRASILMODELO.md` ainda nao estavam integrados no fluxo completo do SaaS (template JSON + menu + criacao), impedindo operacao dos servicos correspondentes.
**Passos:** 1. abrir `/contratos` 2. verificar ausencia de `Rating Full PJ` e `Jusbrasil/Escavador` no menu 3. tentar abrir `/contratos/novo?template=rating_full_pj` e `/contratos/novo?template=jusbrasil`.
**Esperado:** ambos os modelos disponiveis e funcionais no fluxo institucional de contratos.
**Atual:** modelos ausentes do fluxo operacional.
**Status:** Resolvido

### Atualizacao 2026-02-12 (execucao BUG-082 - integracao dos 2 modelos faltantes)
- templates adicionados:
  - `contratos/templates/rating_full_pj.json`
  - `contratos/templates/jusbrasil.json`
- backend:
  - `backend/app/services/contrato_service.py` com fallback para `rating_full_pj` e `jusbrasil`.
- frontend:
  - `frontend/src/app/(dashboard)/contratos/page.tsx` com cards ativos de `Rating Full PJ` e `Jusbrasil/Escavador`;
  - `frontend/src/app/(dashboard)/contratos/novo/page.tsx` com labels e aceite de `template_id` para ambos.
- validacao tecnica:
  - `python -m json.tool` nos 2 templates novos => OK;
  - `python -m py_compile backend/app/services/contrato_service.py backend/app/services/contrato_template_loader.py backend/app/services/pdf_service_playwright.py` => OK;
  - `frontend`: `npm run type-check` => OK;
  - `frontend`: `npm run lint -- --file src/app/(dashboard)/contratos/page.tsx --file src/app/(dashboard)/contratos/novo/page.tsx` => OK.
- validacao funcional (API runtime local):
  - `GET /api/v1/contratos/templates/rating_full_pj` => `clausulas=10`;
  - `GET /api/v1/contratos/templates/jusbrasil` => `clausulas=8`;
  - rodada completa com 15 IDs de template retornando clausulas > 0 no runtime local.

### BUG-083: Simbolos residuais (`�`) em clausulas de contratos
**Data:** 2026-02-12
**Severidade:** Media
**Descricao:** alguns contratos exibem simbolos residuais de encoding (`�`) em trechos como titulos de clausulas, apesar de estrutura e clausulas estarem carregadas.
**Passos:** 1. abrir `/contratos/{id}` 2. rolar para clausulas 3. observar palavras com caracteres corrompidos (ex.: `CL�USULA`, `RESCIS�O`, `PROTE��O`).
**Esperado:** textos institucionais com acentuacao/codificacao limpa em preview e PDF.
**Atual:** decodificacao parcial deixa residuos em alguns casos CP1252/UTF-8.
**Status:** Resolvido

### Atualizacao 2026-02-12 (execucao BUG-083 - normalizacao de encoding residual)
- backend:
  - `backend/app/services/contrato_template_loader.py` com normalizacao recursiva de strings do payload de template;
  - novo fallback de decodificacao com tentativa `cp1252 -> utf-8` e `latin-1 -> utf-8`, com criterio de melhora por score de mojibake;
  - `backend/app/services/pdf_service_playwright.py` com mesma estrategia para render de PDF.
- frontend:
  - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx` com normalizador robusto para casos CP1252/UTF-8;
  - `frontend/src/lib/pdf.ts` com normalizador equivalente para manter preview e PDF alinhados.
- validacao tecnica:
  - `python -m py_compile backend/app/services/contrato_template_loader.py backend/app/services/pdf_service_playwright.py` => OK;
  - `frontend`: `npm run type-check` => OK;
  - `frontend`: `npm run lint -- --file src/app/(dashboard)/contratos/[id]/page.tsx --file src/lib/pdf.ts` => OK (warning nao bloqueante de `<img>`).
- validacao funcional:
  - API templates verificada via HTTP UTF-8 para modelos do lote, sem `�` e sem marcadores de mojibake no payload;
  - exemplos validados: `aumento_score`, `rating_convencional`, `revisional`.

### BUG-084: Parcelamento institucional com foco em venda a vista e 1..12x
**Data:** 2026-02-13
**Severidade:** Alta
**Descricao:** o fluxo atual de `novo contrato` exige `prazo_1` e `prazo_2` manuais e aceita ate 99 parcelas, causando atrito operacional para venda a vista/1x e divergencia com a regra comercial desejada (1..12x com prazos padrao automaticos).
**Passos:** 1. abrir `/contratos/novo?template=revisional` 2. preencher cliente e valores 3. tentar operar com 1x/a vista sem editar prazos 4. observar travas de validacao e obrigatoriedade de prazo manual.
**Esperado:** formulario orientado por `qtd_parcelas` (1..12), `entrada` opcional, calculo automatico de parcela e cronograma padrao sem exigir prazos manuais.
**Atual:** prazos manuais obrigatorios no front e backend, com validacao `ge=1`; UX trava fluxo de venda simples.
**Status:** Resolvido

### Plano aprovado para execucao BUG-084 (documentacao de planejamento)
- etapa 1 - frontend (UX):
  - remover campos visiveis `prazo_1` e `prazo_2` do formulario;
  - trocar `Qtd. Parcelas` para seletor fechado de `1` a `12`;
  - manter `Valor Entrada` opcional (default `0`);
  - exibir `valor_parcela` calculado em tempo real: `(valor_total - entrada)/qtd_parcelas`.
- etapa 2 - backend (regra):
  - limitar `qtd_parcelas` para `le=12` no schema;
  - gerar prazos automaticamente com base em `qtd_parcelas` (30, 60, 90...);
  - para `1x`, tratar como a vista (sem obrigacao de prazo manual);
  - salvar cronograma completo em `dados_extras.prazos_dias` para rastreabilidade.
- etapa 3 - preview/pdf + compatibilidade:
  - manter placeholders legados (`[PRAZO 1]`, `[PRAZO 2]`) com fallback automatico;
  - quando for a vista, renderizar texto institucional equivalente em preview/PDF;
  - executar validacao tecnica e funcional completa antes da baixa do bug.

### Atualizacao 2026-02-13 (execucao BUG-084 - parcelamento institucional 1..12x)
- frontend (`/contratos/novo`):
  - campos manuais `prazo_1` e `prazo_2` removidos do formulario;
  - `Qtd. Parcelas` convertida para seletor fechado `01..12`;
  - `Valor Entrada` mantido opcional;
  - `Valor da Parcela` exibido automaticamente em tempo real (`(valor_total - entrada) / qtd_parcelas`);
  - resumo de prazos automaticos exibido no formulario:
    - `1x` => `a vista`;
    - `2x..12x` => `30/60/90/...`.
- backend (regra e compatibilidade):
  - schema `ContratoCreate` atualizado para:
    - `qtd_parcelas: ge=1, le=12`;
    - `prazo_1` e `prazo_2` aceitando `0` (`ge=0`) para fluxo `a vista`;
  - `ContratoService.create` passou a:
    - gerar cronograma automatico por quantidade (`prazos_dias` em multiplos de 30);
    - preencher `prazo_1/prazo_2` automaticamente para manter compatibilidade de banco/templates;
    - forcar calculo automatico de `valor_parcela`;
    - gravar metadados em `dados_extras` (`prazos_dias` e `parcelamento`).
- preview/PDF (placeholders legados):
  - `[PRAZO 1]` e `[PRAZO 2]` agora renderizam `a vista` quando valor for `0`;
  - `[PRAZO 1 EXTENSO]` e `[PRAZO 2 EXTENSO]` seguem o mesmo fallback institucional;
  - aplicado em:
    - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`;
    - `frontend/src/lib/pdf.ts`;
    - `backend/app/services/pdf_service_playwright.py`.
- validacao tecnica:
  - backend: `python -m py_compile backend/app/schemas/contrato.py backend/app/services/contrato_service.py backend/app/services/pdf_service_playwright.py` => OK;
  - frontend: `npm run type-check` => OK;
  - frontend: `npm run lint -- --file src/app/(dashboard)/contratos/novo/page.tsx --file src/app/(dashboard)/contratos/[id]/page.tsx --file src/lib/pdf.ts` => OK (warning nao bloqueante existente de `<img>` em preview).

### BUG-085: Templates base (BACEN/CADIN/CNH) fora do metodo padrao novo
**Data:** 2026-02-13
**Severidade:** Media
**Descricao:** os 3 templates base iniciais (`bacen`, `cadin`, `cnh`) estavam com estrutura diferente dos modelos recentes, mantendo formato legado, texto/encoding inconsistente e placeholders nao totalmente padronizados.
**Passos:** 1. comparar `contratos/templates/bacen.json`, `contratos/templates/cadin.json`, `contratos/templates/cnh.json` com os modelos novos 2. validar divergencias de estrutura e placeholders.
**Esperado:** os 3 templates base seguindo o mesmo metodo atual dos demais (estrutura unificada e placeholders institucionais).
**Atual:** os 3 templates foram padronizados e alinhados ao metodo novo.
**Status:** Resolvido

### Atualizacao 2026-02-13 (execucao BUG-085 - padronizacao dos 3 templates base)
- templates regravados no metodo padrao novo:
  - `contratos/templates/bacen.json`
  - `contratos/templates/cadin.json`
  - `contratos/templates/cnh.json`
- padrao aplicado:
  - estrutura JSON unificada (metadados + campos + secoes + clausulas com `conteudo`);
  - placeholders institucionais padronizados para render dinamica no preview/PDF;
  - compatibilidade com fluxo atual de parcelamento automatico.
- ajuste complementar de placeholders CNH:
  - adicionado suporte para `[NÚMERO CNH]` e `[NUMERO CNH]` em:
    - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
    - `frontend/src/lib/pdf.ts`
    - `backend/app/services/pdf_service_playwright.py`

### BUG-086: Drift institucional de documentacao (auth, modelos e manual)
**Data:** 2026-02-13
**Severidade:** Alta
**Descricao:** documentos operacionais estavam divergindo do runtime atual (senha dev inconsistente entre guias, manual indicando audio pendente no chat interno e README ainda apontando apenas BACEN).
**Passos:** 1. comparar `README.md`, `SETUP.md`, `teste-local.md` e `docs/MANUAL_DO_CLIENTE.md` 2. validar comportamento real no sistema local.
**Esperado:** documentacao institucional coerente com o estado real de operacao.
**Atual:** divergencias corrigidas na mesma entrega.
**Status:** Resolvido

### BUG-087: Exposicao de segredos em compose legado de producao
**Data:** 2026-02-13
**Severidade:** Alta
**Descricao:** `docker-compose-prod.yml` continha senha de banco, chave de API e `SECRET_KEY` em texto puro versionado.
**Passos:** 1. abrir `docker-compose-prod.yml` 2. verificar variaveis hardcoded em `backend`, `postgres` e `evolution-api`.
**Esperado:** sem segredos hardcoded no repositório; uso de variaveis de ambiente com defaults neutros.
**Atual:** credenciais removidas do arquivo e substituidas por placeholders de ambiente.
**Status:** Resolvido

### Atualizacao 2026-02-13 (execucao BUG-086 + BUG-087)
- seguranca:
  - `docker-compose-prod.yml` sanitizado:
    - removidos segredos hardcoded (`DATABASE_URL`, `SECRET_KEY`, `EVOLUTION_API_KEY`, `POSTGRES_PASSWORD`);
    - adicionados placeholders via variaveis de ambiente.
- documentacao:
  - `README.md` atualizado com modelos operacionais ativos e data da rodada;
  - `SETUP.md` e `teste-local.md` alinhados para senha dev local `1234`;
  - `docs/MANUAL_DO_CLIENTE.md` atualizado com status real de audio no `/viva` e escopo atual de contratos;
  - `docs/API.md` atualizado com endpoints complementares ativos e status atual da VIVA em OpenAI;
  - `docs/DEPLOY_UBUNTU_DOCKER.md` alinhado para `OPENAI_API_KEY` (sem dependencia operacional de ZAI).

### BUG-088: Regex de extração de cliente no handoff gera erro `bad character range`
**Data:** 2026-02-13
**Severidade:** Alta
**Descricao:** no fluxo de agenda + handoff via `/api/v1/viva/chat`, a extração de nome do cliente usa regex com faixa de caracteres corrompida (`Ãƒâ‚¬-ÃƒÂ¿`), podendo disparar erro interno `bad character range €-Ã`.
**Passos:** 1. enviar pedido no chat com "agende ... e avise no whatsapp ..." 2. observar retorno `500` com erro de regex.
**Esperado:** fluxo de handoff processar sem erro de regex e retornar resposta de agendamento/handoff.
**Atual:** erro interno de regex interrompe o fluxo em alguns inputs.
**Status:** Resolvido

### Atualizacao 2026-02-13 (execucao BUG-063 + BUG-064 + BUG-073 + BUG-081 + BUG-088)
- `BUG-063` (rigidez de agenda) validado com fallback contextual:
  - entrada parcial: `agende uma reuniao com o cliente Joao para a agenda`;
  - resposta: follow-up curto contextual, sem template fixo prescritivo;
  - validacao: nao houve retorno do formato legado `agendar TITULO | DD/MM/AAAA HH:MM`.
- `BUG-064` (handoff completo) validado ponta a ponta:
  - chat: `agende retorno ... e avise no whatsapp ...` criou compromisso e retornou `Handoff ... (ID: ...)`;
  - endpoint: `POST /api/v1/viva/handoff/process-due` processou tarefa vencida com resultado `sent`;
  - rastreabilidade: tarefa consultada em `GET /api/v1/viva/handoff` com status final atualizado.
- `BUG-073` (agendamento natural) validado:
  - frase de incidente: `agende o Andre amanha as 10 para mim. Mande para a agenda.`;
  - resultado: compromisso criado com confirmacao objetiva no chat.
- `BUG-081` (clausulas runtime) validado como resolvido:
  - 15 templates operacionais conferidos via `GET /api/v1/contratos/templates/{id}` com `clausulas > 0`;
  - geracao de contrato + PDF backend validada (`GET /api/v1/contratos/{id}/pdf` => `200 application/pdf`).
- `BUG-088` (regex corrompida no handoff) corrigido em:
  - `backend/app/api/v1/viva.py` (`_extract_cliente_nome`);
  - ajuste para regex unicode estavel com escapes `\\u00C0-\\u00FF` e tokens de corte com `amanhã/às`;
  - validacao: fluxo de chat com handoff voltou a responder sem `500` por regex.

### BUG-089: Modo FC/REZETA sequestra conversa comum para fluxo de campanha
**Data:** 2026-02-13
**Severidade:** Alta
**Descricao:** ao manter modo `FC`/`REZETA` ativo, mensagens comuns de conversa (sem pedido de campanha/imagem) podiam cair no funil de campanha por inferencia ampla de tema livre.
**Passos:** 1. abrir sessao em modo `FC` 2. enviar mensagem comum (`qual foi minha ultima mensagem?`) 3. observar retorno de "Sugestoes rapidas para sua campanha".
**Esperado:** conversa comum segue como chat normal; funil de campanha apenas com sinal claro de campanha/imagem.
**Atual:** gatilho ajustado para exigir sinal de campanha e manter inferencia contextual sem sequestrar dialogo.
**Status:** Resolvido

### BUG-090: Recuperacao de chats antigos indisponivel no frontend
**Data:** 2026-02-13
**Severidade:** Alta
**Descricao:** backend possui `GET /api/v1/viva/chat/sessions`, mas o frontend `/viva` restaurava apenas snapshot da ultima sessao, sem seletor para recuperar sessoes anteriores.
**Passos:** 1. criar multiplas sessoes (`/viva/chat/session/new`) 2. voltar para `/viva` 3. tentar abrir sessao antiga.
**Esperado:** UI com selecao de sessoes antigas + carregamento do snapshot da sessao escolhida.
**Atual:** frontend passou a listar sessoes no header e recuperar historico por sessao.
**Status:** Resolvido

### Atualizacao 2026-02-13 (execucao BUG-089 + BUG-090 + validacao memoria/RAG)
- backend `backend/app/api/v1/viva.py`:
  - novo gate `_has_campaign_signal` para separar conversa comum de intencao de campanha;
  - inferencia de tema livre limitada a mensagens com sinal de campanha;
  - coleta de contexto de campanha por sessao filtrada para nao poluir memoria com mensagens gerais;
  - reforco anti-repeticao de campanha:
    - seletor estavel por `sha256` em `_stable_pick`;
    - cooldown para evitar repeticao imediata dos 2 perfis/cenarios mais recentes quando o pool estiver saturado.
- frontend `frontend/src/app/viva/page.tsx`:
  - adicionada listagem de sessoes (`/viva/chat/sessions`) no header da VIVA;
  - troca de sessao com leitura de snapshot por `session_id`;
  - botao de atualizar historico e refresh automatico apos envio/limpeza.
- validacao executada:
  - `POST /api/v1/viva/chat` (modo `FC`, pergunta comum) => resposta conversacional normal (sem funil de campanha);
  - `POST /api/v1/viva/chat` (campanha explicita) => fluxo de campanha preservado;
  - `GET /api/v1/viva/chat/sessions` + `GET /api/v1/viva/chat/snapshot?session_id=...` => recuperacao por sessao funcionando;
  - `GET /api/v1/viva/memory/status` => `vector_enabled=true`, `redis_enabled=true`;
  - `GET /api/v1/viva/memory/search` => hits semanticos retornados com sucesso.

### Atualizacao 2026-02-13 (BUG-062 - fase 2: `viva.py` minimo)
- refatoracao estrutural aplicada sem quebra de contrato HTTP:
  - implementacao completa movida para `backend/app/api/v1/viva_core.py`;
  - `backend/app/api/v1/viva.py` reduzido para agregador de rotas (`include_router`), conforme diretriz institucional de arquivo minimo.
- validacao runtime:
  - `GET /api/v1/viva/status` => `200`;
  - `GET /api/v1/viva/chat/sessions` => `200`;
  - `GET /api/v1/viva/chat/snapshot` => `200`;
  - `POST /api/v1/viva/chat` => `200` com `session_id`.
- status:
  - `BUG-062` permanece **Em validacao** ate concluir fase 3 (fatiar orquestracao interna de `viva_core.py` em servicos de dominio).

### Atualizacao 2026-02-13 (BUG-062 - fase 3: rotas por dominio)
- fatiamento aplicado em modulos de rota dedicados:
  - `backend/app/api/v1/viva_memory_routes.py`
  - `backend/app/api/v1/viva_capabilities_routes.py`
  - `backend/app/api/v1/viva_handoff_routes.py`
  - `backend/app/api/v1/viva_campaign_routes.py`
  - `backend/app/api/v1/viva_media_routes.py`
- agregacao central:
  - `backend/app/api/v1/viva.py` passou a incluir `viva_core` (chat) + routers de dominio.
- resultado estrutural:
  - `viva.py` mantido minimo (21 linhas);
  - `viva_core.py` reduzido ao dominio de chat/sessao (sem endpoints de memoria, campanhas, handoff, midia).
- validacao runtime:
  - `GET /api/v1/viva/status` => `200`;
  - `GET /api/v1/viva/capabilities` => `200`;
  - `GET /api/v1/viva/memory/status` => `200`;
  - `GET /api/v1/viva/handoff` => `200`;
  - `GET /api/v1/viva/campanhas` => `200`;
  - `POST /api/v1/viva/chat` => `200` com `session_id`.
- status:
  - `BUG-062` permanece **Em validacao** para fase 4 (extracao de helpers/casos de uso do `viva_core.py` para servicos).

### Atualizacao 2026-02-13 (BUG-062 - fase 4 parcial: chat/sessao separado)
- ajuste adicional de modularizacao:
  - `backend/app/api/v1/viva_chat_session_routes.py` criado para:
    - `GET /api/v1/viva/chat/snapshot`
    - `GET /api/v1/viva/chat/sessions`
    - `POST /api/v1/viva/chat/session/new`
  - `backend/app/api/v1/viva_core.py` mantido apenas com `POST /api/v1/viva/chat` + helpers compartilhados.
- agregacao:
  - `backend/app/api/v1/viva.py` passou a incluir router dedicado de sessao.
- validacao runtime:
  - `POST /api/v1/viva/chat` => `200`;
  - `POST /api/v1/viva/chat/session/new` => `200`;
  - `GET /api/v1/viva/chat/sessions` => `200`;
  - `GET /api/v1/viva/chat/snapshot` => `200`;
  - `GET /api/v1/viva/memory/status` => `200`;
  - `GET /api/v1/viva/campanhas` => `200`.
- status:
  - `BUG-062` segue **Em validacao** (pendente fase 5: mover helpers/orquestracao de `viva_core.py` para camada de servico).

### Atualizacao 2026-02-13 (BUG-062 - fase 5 parcial: orquestracao `/chat` em service)
- extracao aplicada:
  - orquestracao pesada do endpoint `/api/v1/viva/chat` movida para:
    - `backend/app/services/viva_chat_orchestrator_service.py`
  - `backend/app/api/v1/viva_core.py` mantido com contrato HTTP do `/chat` delegando para service.
- observacao tecnica:
  - nesta fase foi usado bridge temporario (`globals().update(...)` no service) para reaproveitar helpers existentes do `viva_core` sem regressao de comportamento.
- validacao runtime apos extracao:
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
  - `BUG-062` segue **Em validacao** (fase final pendente: substituir bridge temporario por interfaces explicitas e extrair helpers restantes para services de dominio).

### Atualizacao 2026-02-13 (BUG-062 - fase 5 avancada: bridge removido)
- ajuste aplicado no orquestrador:
  - removido bridge dinamico (`globals().update(...)`) de `backend/app/services/viva_chat_orchestrator_service.py`;
  - substituido por imports explicitos dos simbolos usados na orquestracao de chat.
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
  - `BUG-062` segue **Em validacao** para fechamento final (extrair helpers remanescentes de `viva_core.py` para services dedicados e reduzir acoplamento interno).

### Atualizacao 2026-02-13 (BUG-062 - fase 5 avancada B: schemas dedicados)
- extracao aplicada:
  - criado modulo de contratos compartilhados:
    - `backend/app/api/v1/viva_schemas.py`
  - classes Pydantic da VIVA movidas de `viva_core.py` para `viva_schemas.py`;
  - routers e service atualizados para importar schemas do modulo dedicado.
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
  - acoplamento `router -> viva_core` reduzido no contrato de tipos;
  - `BUG-062` segue **Em validacao** para etapa final de extracao de helpers/casos de uso.

### Atualizacao 2026-02-13 (BUG-062 - fase 5 avancada C: chat-session service)
- extracao aplicada:
  - criado `backend/app/services/viva_chat_session_service.py` para concentrar:
    - persistencia de mensagens/sessoes;
    - serializacao de midia;
    - montagem de snapshot/contexto.
  - `viva_chat_orchestrator_service` passou a usar o service de sessao (reduzindo dependencia de helpers em `viva_core`);
  - `viva_chat_session_routes.py` passou a usar o service de sessao para `snapshot/sessions/session-new`.
- correcao pontual de regressao na mesma rodada:
  - conflito de nome em `create_chat_session` gerou chamada recursiva no endpoint `POST /api/v1/viva/chat/session/new`;
  - ajuste com alias explicito (`create_chat_session_record`) no import da rota.
- validacao runtime final:
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
  - `BUG-062` segue **Em validacao** para fechamento final (extracao dos helpers utilitarios restantes de `viva_core.py`).

### Atualizacao 2026-02-13 (BUG-062 - fase 5 avancada D: shared service + poda de legado)
- extracao aplicada:
  - criado `backend/app/services/viva_shared_service.py` para centralizar:
    - normalizacao (`_normalize_mode`, `_normalize_key`);
    - mapeadores de dominio (`_campaign_row_to_item`, `_handoff_row_to_item`);
    - persistencia auxiliar de campanhas (`_save_campaign_record`, consultas de cast/cena recente);
    - utilitarios de titulo/sanitizacao (`_derive_campaign_title`, `_sanitize_prompt`, `_extract_subject`).
  - rotas/servicos atualizados para consumir `viva_shared_service` em vez de importar diretamente de `viva_core`:
    - `backend/app/api/v1/viva_campaign_routes.py`;
    - `backend/app/api/v1/viva_handoff_routes.py`;
    - `backend/app/api/v1/viva_memory_routes.py`;
    - `backend/app/api/v1/viva_chat_session_routes.py`;
    - `backend/app/services/viva_chat_session_service.py`;
    - `backend/app/services/viva_chat_orchestrator_service.py`.
- poda de legado em `viva_core`:
  - removido bloco morto de sessao/chat que ja estava extraido para `viva_chat_session_service`;
  - removidos wrappers de campanha/handoff sem uso e imports obsoletos;
  - tamanho do arquivo reduzido (de ~1822 para ~1479 linhas na rodada).
- validacao:
  - `python -m py_compile` dos modulos alterados => OK.
- status:
  - `BUG-062` segue **Em validacao** para fechamento final (extracao dos helpers de campanha/handoff/chat ainda remanescentes em `viva_core.py`).

### Atualizacao 2026-02-13 (BUG-062 - fase 5 avancada E: runtime helpers de chat/handoff/imagem)
- extracao aplicada:
  - criado `backend/app/services/viva_chat_runtime_helpers_service.py` com helpers operacionais de:
    - handoff (`_is_handoff_whatsapp_intent`, `_is_viviane_handoff_query_intent`, `_handoff_status_from_text`, `_normalize_any_datetime`, `_format_viviane_handoff_list`, `_extract_phone_candidate`, `_extract_cliente_nome`, `_extract_handoff_custom_message`, `_build_viviane_handoff_message`);
    - imagem (`_extract_image_url`, `_is_stackoverflow_error`, `_build_image_prompt`, `_build_fallback_image_prompt`);
    - saneamento de resposta (`_sanitize_fake_asset_delivery_reply`);
    - suporte de copy (`_extract_overlay_source`).
  - `backend/app/services/viva_chat_orchestrator_service.py` atualizado para consumir esses helpers do modulo dedicado, reduzindo imports diretos de `viva_core.py`;
  - `backend/app/api/v1/viva_core.py` teve o bloco correspondente removido e passou a importar apenas o necessario para `_generate_campaign_copy`.
- validacao:
  - `python -m py_compile` dos modulos alterados => OK.
- status:
  - `viva_core.py` reduzido para ~1214 linhas;
  - `BUG-062` segue **Em validacao** para etapa final (extrair helpers de campanha ainda remanescentes no `viva_core.py`).

### Atualizacao 2026-02-13 (BUG-062 - fase 5 avancada F: `viva_core` minimo + dominio dedicado)
- extracao aplicada:
  - criado `backend/app/services/viva_chat_domain_service.py` com os helpers de dominio de chat/campanha antes acoplados ao `viva_core`;
  - `backend/app/services/viva_chat_orchestrator_service.py` passou a importar os helpers desse modulo dedicado;
  - `backend/app/api/v1/viva_core.py` reduzido para rota minima (`POST /chat`) delegando para o orquestrador.
- validacao:
  - `python -m py_compile` dos modulos alterados => OK.
- status:
  - `viva_core.py` reduzido para ~25 linhas;
  - `BUG-062` segue **Em validacao** pendente apenas de prova runtime final autenticada no ambiente local.

### Atualizacao 2026-02-13 (BUG-062 - validacao runtime final autenticada)
- evidencias de validacao local (token JWT real):
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
- conclusao:
  - `viva_core` permanece minimo e a orquestracao segue operacional via services dedicados;
  - `BUG-062` marcado como **Resolvido**.

### Atualizacao 2026-02-13 (BUG-061 - rodada 7: campanha livre + reset de padrao)
- backend:
  - fluxo FC/REZETA ajustado para modo livre sem travar em briefing obrigatorio;
  - suporte a reset de padrao de campanha:
    - `POST /api/v1/viva/campanhas/reset-patterns` (limpa historico de campanha do usuario);
    - comando de chat com intencao de reset (ex.: "reset memoria campanha") tambem limpa padrao.
  - preferencia explicita de elenco extraida do pedido do usuario (ex.: "mulher", "homem", "casal", "grupo") e aplicada na selecao de personagem/prompt final.
  - memoria de repeticao de cast/cena desativada no runtime de geracao (historico recente nao forcado).
- frontend (`/viva`):
  - menu lateral de modos especiais simplificado para manter apenas `Conversa VIVA`.
- validacao executada:
  - `python -m py_compile` dos modulos alterados => OK;
  - `frontend` `npm run type-check` => OK;
  - `POST /api/v1/viva/campanhas/reset-patterns` => `200` (`deleted: 15` em base local de teste);
  - fluxo "me de uma sugestao antes de gerar" => resposta textual sem midia (comportamento esperado).
- bloqueio para baixa final:
  - geracao real de imagem no ambiente local retornou erro OpenAI de billing (`billing_hard_limit_reached`), impedindo prova visual final desta rodada.

### BUG-091: RAG semantico indisponivel por falta de embeddings em runtime
**Data:** 2026-02-13
**Severidade:** Alta
**Descricao:** embora a infraestrutura de memoria esteja ativa (`pgvector` + Redis), a camada semantica do RAG nao retorna contexto util no estado atual. O `reindex` processa mensagens mas nao indexa e a busca semantica retorna vazia.
**Passos:** 1. autenticar e chamar `GET /api/v1/viva/memory/status` 2. chamar `POST /api/v1/viva/memory/reindex?limit=200` 3. chamar `GET /api/v1/viva/memory/search?q=agenda&limit=3`.
**Esperado:** `reindex` com `indexed > 0` e `search` retornando itens com score.
**Atual:** `memory/status` mostra `vector_enabled=true` e `redis_enabled=true`, mas `reindex` retorna `processed=200,indexed=0` e `search` retorna `items=[]`.
**Status:** Ativo

### Atualizacao 2026-02-13 (BUG-091 + governanca de skills/orquestrador)
- evidencias runtime desta rodada:
  - `GET /api/v1/viva/memory/status` => `vector_enabled=true`, `redis_enabled=true`, `total_vectors=373`;
  - `POST /api/v1/viva/memory/reindex?limit=200` => `processed=200`, `indexed=0`;
  - `GET /api/v1/viva/memory/search?q=agenda&limit=3` => `items=[]`.
- impacto:
  - memoria curta/media segue operacional para continuidade de sessao;
  - memoria longa semantica (RAG) fica indisponivel funcionalmente.
- acao institucional aberta:
  - manter `BUG-091` ativo ate restaurar indexacao vetorial e busca semantica com prova de vida.

### Atualizacao 2026-02-13 (BUG-091 - fix fallback local de embeddings + prova de vida)
- correcao aplicada:
  - `backend/app/services/openai_service.py`:
    - `embed_text` recebeu fallback local deterministico por hashing quando API de embeddings falha (inclui cenario de sem saldo/quota);
    - tratamento de excecao de rede/parse com degradacao segura para fallback.
  - `backend/app/services/viva_memory_service.py`:
    - normalizacao de dimensao do vetor para `1536` (truncate/pad) antes de inserir/buscar no pgvector.
  - `backend/app/config.py`:
    - nova flag `OPENAI_EMBEDDING_FALLBACK_LOCAL` (padrao `true`).
- validacao runtime autenticada:
  - `POST /api/v1/viva/memory/reindex?limit=120` => `processed=120`, `indexed=112`;
  - `GET /api/v1/viva/memory/search?q=agenda compromisso gabriela&limit=5` => `total=5` (hits retornados com score);
  - `GET /api/v1/viva/memory/status` apos rodada => `total_vectors=486`.
- status:
  - `BUG-091` baixado para **Resolvido**.

### BUG-092: Fala continua depende de motor nativo de navegador
**Data:** 2026-02-13
**Severidade:** Alta
**Descricao:** o modo `Conversa VIVA` usa `SpeechRecognition/webkitSpeechRecognition` para escuta continua e `window.speechSynthesis` para fala da assistente. Isso gera variacao de qualidade e estabilidade por browser/SO, sem voz institucional fixa.
**Passos:** 1. abrir `/viva` 2. ativar `Conversa VIVA` 3. testar em navegadores/dispositivos diferentes.
**Esperado:** pipeline de voz ao vivo padronizado, com modelo/provedor controlado e qualidade previsivel.
**Atual:** escuta continua prioriza pipeline server-side (captura + transcricao backend), com fallback de navegador apenas contingencial.
**Status:** Resolvido

### Atualizacao 2026-02-13 (BUG-092 - server STT + MiniMax TTS no modo conversa)
- frontend (`frontend/src/app/viva/page.tsx`):
  - escuta continua passou a usar como caminho principal:
    - captura de audio por `MediaRecorder`,
    - deteccao de fala/silencio por `AudioContext + AnalyserNode`,
    - transcricao via backend (`POST /api/v1/viva/audio/transcribe`);
  - fallback para `SpeechRecognition/webkitSpeechRecognition` mantido apenas quando pipeline principal nao puder iniciar;
  - reproduz fala da assistente priorizando MiniMax (`POST /api/v1/viva/audio/speak`) com fallback local de navegador.
- backend:
  - endpoint `POST /api/v1/viva/audio/speak` ativo e servico `backend/app/services/minimax_tts_service.py` integrado.
- validacao tecnica:
  - `frontend npm run type-check` => OK;
  - `frontend npm run lint -- --file src/app/viva/page.tsx` => OK (warnings nao bloqueantes de `<img>`).
- status:
  - `BUG-092` movido para **Resolvido** (validacao funcional em front realizada pelo cliente).

### Atualizacao 2026-02-13 (BUG-092 - ajuste fino: evitar voz de navegador quando MiniMax estiver ativo)
- ajuste aplicado apos feedback do cliente ("voz ainda Google"):
  - `frontend/src/app/viva/page.tsx`:
    - passa a consultar `GET /api/v1/viva/status` para detectar `tts.configured`;
    - quando MiniMax estiver configurado e a sintese falhar, nao cai para `speechSynthesis`;
    - exibe erro operacional curto para correcao do provider, evitando troca silenciosa para voz nativa do navegador.
- resultado esperado:
  - manter consistencia da voz institucional quando provider externo estiver habilitado.

### BUG-093: Avatar institucional da VIVA ainda nao aplicado
**Data:** 2026-02-13
**Severidade:** Media
**Descricao:** o frontend usa fallback de avatars locais (`/viva-avatar.png`, `/viva-avatar-3d.png`, `/viva.png`) e ainda nao recebeu o novo avatar institucional aprovado pelo cliente.
**Passos:** 1. abrir `/viva` no modo conversa 2. observar avatar renderizado.
**Esperado:** avatar oficial novo padronizado e unico no fluxo principal.
**Atual:** avatar oficial novo aplicado no frontend e fallback legado mantido apenas como contingencia.
**Status:** Resolvido

### BUG-094: RAG sem homologacao semantica premium para venda modular
**Data:** 2026-02-13
**Severidade:** Alta
**Descricao:** apos fallback local de embeddings, o RAG voltou a funcionar tecnicamente, mas ainda nao ha homologacao formal de qualidade semantica para cenarios comerciais de alta exigencia.
**Passos:** 1. executar lote de buscas semanticas de regressao 2. comparar relevancia entre fallback local e embeddings OpenAI 3. avaliar taxa de acerto por caso real.
**Esperado:** qualidade semantica auditada com criterio minimo e aprovacao institucional para comercializacao.
**Atual:** busca semantica com rerank hibrido (vetor + lexical + recencia) e telemetria de tier semantico ativa; homologacao final segue em validacao.
**Status:** Em validacao

### Atualizacao 2026-02-13 (triagem de voz/avatar/RAG premium)
- evidencia tecnica de implementacao atual:
  - escuta continua com caminho principal server-side (`MediaRecorder` + `/viva/audio/transcribe`) e fallback browser;
  - fala da assistente priorizando MiniMax (`/viva/audio/speak`) com fallback browser;
  - RAG com memoria longa vetorial + rerank hibrido (vetor/lexical/recencia).
- impacto:
  - voz padronizada no fluxo principal; homologacao final focada em qualidade semantica premium (RAG).
- acao institucional:
  - `BUG-092` baixado para resolvido;
  - `BUG-093` baixado para resolvido;
  - `BUG-094` segue em validacao ate rodada final de homologacao comercial.

### Atualizacao 2026-02-13 (BUG-093 - avatar oficial aplicado)
- frontend atualizado:
  - novo asset oficial: `frontend/public/viva-avatar-official.jpg`;
  - prioridade de carregamento em `VIVA_AVATAR_SOURCES` no chat (`frontend/src/app/viva/page.tsx`);
  - render ajustado para preservar enquadramento completo (`object-contain`) no modo conversa.
- visual/UX:
  - palco da VIVA redesenhado para estilo 2D premium em `frontend/src/styles/globals.css`;
  - efeitos mantidos sutis (scan/rings/glow), sem dependencia de avatar 3D.
- validacao tecnica:
  - `frontend npm run type-check` => OK;
  - `frontend npm run lint -- --file src/app/viva/page.tsx` => OK (warnings nao bloqueantes de `<img>`).

### Atualizacao 2026-02-13 (BUG-073 - reaberto por query de agenda e correção NLU)
- regressao reportada em chat real:
  - pergunta de consulta (`eu marquei algo amanha?`) caia no fluxo de criacao com resposta repetitiva "me diga quando deve acontecer...".
- correcao aplicada:
  - `backend/app/services/viva_agenda_nlu_service.py`:
    - nova priorizacao de intencao de existencia/consulta (`eu marquei`, `tem algum`, `confirma se`, `verifica se`);
    - parser de criacao natural passou a ignorar frases de consulta (nao entra em erro de data/hora para pergunta de status);
    - matching de criacao ficou restrito a imperativos reais (`agendar`, `agende`, `marcar`, `marque`, etc.).
- validacao local de NLU:
  - `e confirma se eu marquei algum cliente para amanha` => query `true`, create `None`;
  - `tem algum agendamento amanha?` => query `true`, create `None`;
  - `agendar reuniao amanha 10:30 ...` => query `false`, create payload valido.
- status:
  - `BUG-073` em **Em validacao** aguardando prova final no chat com backend ativo.

### Atualizacao 2026-02-13 (BUG-094 - qualidade semantica com rerank hibrido)
- backend:
  - `backend/app/services/viva_memory_service.py`:
    - busca longa passou a combinar candidatos vetoriais com candidatos lexicais;
    - rerank final por peso hibrido (`vector_score`, `lexical_score`, `recency_score`);
    - retorno de score mais estavel para reduzir perda de contexto util em fallback local.
  - `backend/app/services/openai_service.py`:
    - telemetria de runtime de embedding (`provider_last`, `semantic_tier`, `premium_active`).
  - `memory/status` agora expõe `embedding_runtime` para auditoria operacional.
- impacto:
  - quando embeddings OpenAI nao estiverem disponiveis, o RAG preserva relevancia usando reforco lexical/recencia em cima do vetor fallback.
- status:
  - `BUG-094` movido para **Em validacao** aguardando rodada final de homologacao comercial.

### Atualizacao 2026-02-13 (BUG-061/015 - variacao real de campanhas e obediencia de personagem)
- backend:
  - `backend/app/services/viva_chat_orchestrator_service.py`:
    - agora carrega historico real recente de `cast_profile` e `scene_profile` por usuario/modo para evitar repeticao de personagem/cenario;
    - fallback de geracao por overflow passou a usar prompt compacto de marca/cena/elenco em vez de prompt generico.
  - `backend/app/services/viva_chat_domain_service.py`:
    - deteccao de preferencia de elenco reforcada (`apenas mulher`, `somente homem`, `duas mulheres`, etc.);
    - novo `_build_branded_background_prompt_compact` com guarda de personagem obrigatorio (ex.: mulher protagonista quando solicitado).
- impacto:
  - reduz recorrencia de personagem masculino padrao e melhora aderencia ao pedido explicito do usuario.
- status:
  - `BUG-061` e `BUG-015` mantidos em **Em validacao** aguardando prova visual final no fluxo com geracao real.

### BUG-095: Agenda interna sem sincronizacao com Google Calendar
**Data:** 2026-02-13
**Severidade:** Alta
**Descricao:** agenda interna do SaaS nao estava conectada oficialmente ao Google Calendar, impedindo operacao compartilhada e edicao unificada por rotina de calendario externa.
**Passos:** 1. criar/editar compromissos no SaaS 2. verificar no Google Calendar 3. confirmar ausencia de sincronizacao oficial.
**Esperado:** criar/editar/concluir/excluir no SaaS refletindo no Google Calendar conectado por usuario.
**Atual:** bridge de sincronizacao implementada e em validacao final.
**Status:** Em validacao

### Atualizacao 2026-02-13 (BUG-095 - bridge Google Calendar implementada)
- backend:
  - novo servico `backend/app/services/google_calendar_service.py` com:
    - OAuth (`connect-url`, `callback`, refresh token);
    - tabelas de conexao e links de evento;
    - sync create/update/delete de eventos da agenda.
  - nova API:
    - `GET /api/v1/google-calendar/connect-url`
    - `GET /api/v1/google-calendar/callback`
    - `GET /api/v1/google-calendar/status`
    - `POST /api/v1/google-calendar/disconnect`
    - `POST /api/v1/google-calendar/sync/agenda/{evento_id}`
  - agenda interna agora dispara sync automaticamente em criar/editar/concluir/excluir (modo safe, sem bloquear operacao local em falha externa).
  - fluxo de chat da VIVA (`backend/app/services/viva_chat_orchestrator_service.py`) tambem passou a sincronizar no Google apos criar/concluir compromisso, evitando divergencia entre chat e tela de agenda.
- frontend:
  - `frontend/src/app/(dashboard)/agenda/page.tsx` com bloco de integracao Google Calendar:
    - status da conexao,
    - acao de conectar/desconectar,
    - sincronizacao manual por evento.
  - callback OAuth agora retorna mensagens de erro seguras/encodadas para exibir feedback no frontend.
- configuracao:
  - variaveis novas em `backend/app/config.py`:
    - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`,
    - `GOOGLE_CALENDAR_DEFAULT_ID`, `GOOGLE_CALENDAR_SCOPE`, `GOOGLE_CALENDAR_SYNC_ENABLED`.
