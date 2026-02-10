# BUGSREPORT - Registro de Bugs

> **Projeto:** FC SoluÃ§Ãµes Financeiras SaaS  
> **Ãšltima AtualizaÃ§Ã£o:** 2026-02-09

---

## Bugs Ativos

| ID | Severidade | MÃ³dulo | DescriÃ§Ã£o | Status |
|---|---|---|---|---|
| BUG-010 | Baixa | PDF | WeasyPrint requer GTK+ no Windows | Resolvido (runtime Docker) |
| BUG-012 | MÃ©dia | VIVA | BotÃ£o de Ã¡udio no chat nÃ£o funciona | Ativo |
| BUG-013 | MÃ©dia | VIVA | Erro `StackOverflowError` ao gerar imagem com prompt extra longo (REZETA/FC) | Resolvido |
| BUG-014 | MÃ©dia | VIVA | Upload de imagem falha quando a imagem Ã© PNG (MIME assumido como JPEG) | Resolvido |
| BUG-015 | Alta | VIVA | Fundo da imagem nÃ£o respeita paleta/brief do prompt (resultado genÃ©rico) | Pendente |
| BUG-016 | MÃ©dia | VIVA | Arte final perde partes do texto (overlay truncado) | Em validaÃ§Ã£o |
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
| BUG-037 | Alta | VIVA/Campanhas | Chat interno podia simular publicaÃ§Ã£o/links/download sem gerar e salvar arquivos reais no SaaS | Em validaÃ§Ã£o |
| BUG-038 | MÃ©dia | VIVA/Campanhas | Menu histÃ³rico de campanhas nÃ£o estava disponÃ­vel no dashboard e imagens geradas nÃ£o ficavam persistidas para revisÃ£o | Em validaÃ§Ã£o |
| BUG-039 | MÃ©dia | VIVA/Briefing | Fluxo de campanha podia travar pedindo o brief completo repetidamente quando faltava apenas CTA, sem resposta curta de continuidade | Resolvido |
| BUG-040 | MÃ©dia | VIVA/UI | BotÃ£o `Abrir imagem` no modal da VIVA abria aba em branco/sem conteÃºdo em parte dos navegadores | Em validaÃ§Ã£o |
| BUG-041 | MÃ©dia | VIVA/Briefing | ReferÃªncia visual anexada no chat nÃ£o era injetada no prompt final da campanha (imagem de saÃ­da sem aderÃªncia) | Em validaÃ§Ã£o |
| BUG-042 | MÃ©dia | Campanhas/UI | BotÃ£o `Abrir imagem` em `/campanhas` podia falhar por popup/blank tab, sem preview confiÃ¡vel no SaaS | Em validaÃ§Ã£o |

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

---

*Atualizado em: 2026-02-09*


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
