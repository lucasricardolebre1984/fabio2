# STATUS do projeto - FC Solucoes Financeiras

Data: 10/02/2026
Sessao: rodada GODMOD de limpeza estrutural (persona dual + memoria + RAG) em execucao
Status: V1.9 em transicao arquitetural controlada com rollback institucional pre-clean

## Objetivo atual
Consolidar operacao comercial da Viviane no WhatsApp com regras de negocio,
qualificacao de lead, politica de preco e governanca de atendimento humano.

## Funcionalidades operacionais
- Contratos com templates dinamicos
- Clientes e agenda
- Chat interno VIVA em `/viva`
- Conexao WhatsApp em `/whatsapp`
- Gestao de conversas em `/whatsapp/conversas`

## Estado WhatsApp/VIVA
- Instancia Evolution definitiva: `fc-solucoes`
- Instancia de teste removida: `tmp-fc-8601`
- Persona comercial aprovada: Viviane, consultora da Rezeta
- Fontes de conhecimento organizadas em `frontend/src/app/viva/REGRAS`
- Provedor IA ativo: OpenAI (`gpt-5-mini`)

## Estado Contratos/PDF
- `GET /api/v1/contratos/{id}/pdf` reabilitado com sucesso (sem `500`)
- Fallback de renderizacao aplicado: Playwright -> WeasyPrint
- Dependencia fixada: `pydyf==0.10.0` (compatibilidade com WeasyPrint 60.2)

## Estado Clientes/Contratos (2026-02-09)
- Unicidade operacional por CPF/CNPJ normalizado estabilizada.
- Bug de `500` ao criar contrato com cliente duplicado eliminado.
- Endpoint admin para saneamento de base:
  - `POST /api/v1/clientes/deduplicar-documentos`
- Tela `/clientes` com acoes de:
  - cadastro manual
  - edicao
  - exclusao (admin)
  - saneamento de duplicados
- Tela `/contratos/novo` com busca de cliente por documento e autopreenchimento.

## Decisoes validadas com cliente
- Modo B (VIVA conduz; humano por excecao)
- Tom hibrido (consultivo + acolhedor)
- Fluxo 1 (objetivo -> perfil -> urgencia -> proximo passo)
- SLA 24/7 com callback em ate 15 min
- Coleta obrigatoria: nome, telefone, servico, cidade, urgencia
- Diagnostico 360 como recomendacao inicial
- Venda direta sem 360: Limpa Nome, Score e Rating
- Oferta inicial com margem de 15% sobre tabela
- Negociacao fina de preco somente com humano
- Objecao financeira registrada para follow-up

## Proximo gate
Iniciar ciclo de melhoria incremental (etiquetas de lead, scripts PF/PJ e painel de metricas),
fechando os bugs ativos de experiencia da VIVA (`BUG-012`, `BUG-015`, `BUG-016`)
sem regressao no fluxo comercial homologado.

## Documentos de referencia
- `docs/WHATSAPP_VIVA_PACOTE_DEFINITIVO.md`
- `docs/INTEGRACAO_WHATSAPP_VIVA.md`
- `docs/DECISIONS.md`
- `docs/SESSION.md`
- `docs/API.md`

---

Atualizado em: 10/02/2026

## Estado Contratos/Layout (2026-02-09)
- Logo oficial `logo2.png` padronizada no fluxo de contratos (preview + PDF frontend + PDF backend).
- Novo template operacional `CADIN PF/PJ` adicionado ao sistema.
- Menu de contratos com CADIN habilitado.
- Tela de novo contrato agora respeita `template` na URL (`/contratos/novo?template=cadin`).
- Template base criado em `contratos/templates/cadin.json`.


## Estado Contratos/Layout (2026-02-09 - logo transparente + CADIN completo)
- Logo oficial do cabecalho atualizada para `logo2.png` (transparente) no preview e nos dois fluxos de PDF.
- Template CADIN corrigido com clausulas completas e acentuacao conforme `cadinpfpjmodelo.docx`.
- Pipeline backend Playwright ajustado para usar marca transparente e subtitulo/template CADIN com texto canonico.

## Estado Contratos/Layout (2026-02-09 - acentuacao e legibilidade)
- Corrigido bug de acentuacao corrompida (mojibake) na visualizacao de contratos.
- Corrigido texto no PDF frontend/backend para manter acentos institucionais.
- Layout ampliado levemente (preview + PDF) para melhorar leitura operacional.

## Estado Contratos/Layout (2026-02-09 - ajuste final de assinatura)
- Rollback local adicional registrado:
  - `docs/ROLLBACK/rollback-20260209-131517.patch`
- Normalizacao de `local_assinatura` legado aplicada em:
  - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
  - `frontend/src/lib/pdf.ts`
  - `backend/app/services/pdf_service_playwright.py`
- Correcao preventiva no cadastro de novo contrato:
  - `frontend/src/app/(dashboard)/contratos/novo/page.tsx` agora usa `Ribeirao Preto/SP` no default de `local_assinatura`.
- Resultado esperado: rodape da assinatura com local exibido corretamente para registros novos e legados.

## Estado Clientes/Contratos (2026-02-09 - fechamento rodada)
- `/contratos` sem texto corrompido no menu de templates.
- `/clientes` com historico de contratos por cliente no proprio card.
- Contagem exibida em `/clientes` calculada por agregacao real de contratos no backend.
- Rollback desta rodada registrado em `docs/ROLLBACK/rollback-20260209-164001.patch`.

## Estado VIVA (2026-02-09 - prompts FC/REZETA e arte final)
- Rollback local adicional registrado em:
  - `docs/ROLLBACK/rollback-20260209-181844.patch`
- Frontend `/viva` envia `modo` explicitamente para `/api/v1/viva/chat`.
- Backend `/api/v1/viva/chat` prioriza `modo` do payload para aplicar fluxo correto de campanha.
- FC/REZETA agora conduzem brief minimo antes da geracao de imagem:
  - campos obrigatorios: `objetivo`, `publico`, `formato`, `cta`.
- Fonte canonica dos prompts da VIVA no frontend:
  - `frontend/src/app/viva/PROMPTS` (via rota interna `/api/viva/prompts/[promptId]`).
- Modal de "Arte final" ajustado para uso em zoom 100% (scroll e limite de largura) sem ocultar botoes de acao.

## Estado VIVA (2026-02-09 - campanhas e historico)
- Novo menu `Campanhas` ativo no dashboard (`/campanhas`).
- Historico persistente de campanhas IA em banco (`viva_campanhas`) com data, modo, imagem e briefing.
- Geracoes FC/REZETA no `/viva` salvam automaticamente no historico e retornam `campanha_id`.
- Chat bloqueia resposta operacional ficticia de upload/publicacao/link quando nao houve operacao real.
- Briefing de campanha com contexto acumulado e destrave de CTA:
  - aceita entrada em texto livre;
  - quando faltar apenas CTA, nao repete o template completo em loop.
- Rota de leitura para historico pronta:
  - `GET /api/v1/viva/campanhas`

## Estado VIVA (2026-02-09 - FCNOVO e fluxo de imagem)
- Prompt FC atualizado com base em `FCNOVO.md` e rotas operacionais do SaaS.
- Briefing de campanha menos engessado:
  - obrigatoriedade reduzida para `objetivo + publico + formato`;
  - CTA com fallback padrao (`Saiba mais`);
  - sem loop de repeticao ao receber mensagens fora do briefing.
- Referencia visual por anexo ativa:
  - resultado de `/api/v1/viva/vision/upload` agora segue junto para `/api/v1/viva/chat`.
- Preview de imagem estabilizado:
  - `/viva` modal "Abrir imagem" abre internamente;
  - `/campanhas` usa modal interno para visualizacao/download (sem popup externo).

## Estado VIVA (2026-02-09 - pendencia gerador de imagem)
- BUG-015 mantido como pendente.
- Sintoma atual: gerador ainda repete composicao visual em alguns pedidos (baixa variacao de cena).
- Proxima rodada: refino de prompt de cena e controle de diversidade de composicao.

## Estado VIVA (2026-02-09 - blocos 1 e 2 aplicados)
- Rollback institucional registrado: `docs/ROLLBACK/rollback-20260209-213516-baseline.txt`.
- Bloco 1 concluido (prompts/persona):
  - fonte canonica de prompts ativa em `frontend/src/app/viva/PROMPTS`;
  - endpoint `/api/viva/prompts/[promptId]` sem fallback legado em `public/PROMPTS`;
  - alias `CRIADORWEB -> CRIADORPROMPT` mantido por compatibilidade.
- Bloco 2 concluido (memoria persistente):
  - backend persiste sessao e historico por usuario;
  - endpoints de memoria ativos:
    - `GET /api/v1/viva/chat/snapshot`
    - `POST /api/v1/viva/chat/session/new`
  - chat `/api/v1/viva/chat` retornando `session_id` para continuidade;
  - frontend `/viva` recupera historico automaticamente ao abrir e reinicia sessao ao limpar.

## Proximo passo do plano (aguardando validacao front)
1. Validacao do usuario no frontend para blocos 1 e 2.
2. Depois da validacao: executar bloco 3 (agenda por linguagem natural) e bloco 4 (streaming/autoscroll continuo).

## Estado VIVA/Agenda (2026-02-10 - bloco 3 aplicado)
- Chat VIVA agora prioriza ferramentas de agenda (dados reais) antes do modelo quando detectar intencao de agenda.
- Consulta em linguagem natural habilitada:
  - hoje / amanha / semana;
  - follow-up curto de confirmacao (sim/quero/todos) apos pergunta de agenda.
- Criacao de compromisso reforcada:
  - formato estruturado legado continua ativo;
  - frase natural com data/hora passou a funcionar.
- Confirmacao/conclusao via chat:
  - comando natural com ID do compromisso.
- Agenda com escopo por usuario:
  - backend filtrando listagem/consulta/update/concluir/delete por `created_by` do usuario logado.

## Estado Read-only (2026-02-10 - auditoria GODMOD com frontend UP)
- Rollback institucional pre-fix criado antes de qualquer correcao:
  - `docs/ROLLBACK/rollback-20260210-104803-pre-fix-baseline.txt`
  - `docs/ROLLBACK/rollback-20260210-104803-pre-fix.patch`
  - `docs/ROLLBACK/rollback-20260210-104803-pre-fix-staged.patch`
  - `docs/ROLLBACK/rollback-20260210-104803-pre-fix-untracked.txt`
- Frontend validado online:
  - `/`, `/viva`, `/contratos`, `/contratos/novo?template=bacen`, `/whatsapp`, `/whatsapp/conversas`, `/campanhas` com `200`.
- Backend e integracoes validados:
  - `/health` e `/api/v1/webhook/evolution` com `200`;
  - auth + chamadas protegidas em `auth/me`, `clientes`, `agenda`, `whatsapp/status`, `whatsapp-chat/status`, `viva/status` com `200`;
  - `POST /api/v1/viva/chat` com resposta valida e `session_id`.
- Risco atual de release:
  - sem bloqueio nos gates de build/lint/type-check desta rodada;
  - permanecem apenas warnings de lint nao-bloqueantes (`react-hooks/exhaustive-deps` e `@next/next/no-img-element`).

## Proximo gate (2026-02-10)
Concluir rodada seguinte de qualidade incremental:
1. reduzir warnings de lint sem impacto funcional imediato;
2. ampliar cobertura de testes backend para agenda/VIVA;
3. manter protocolo de rollback institucional antes de novos blocos de correcao.

## Estado de Correcao (2026-02-10 - BUG-048..053)
- `npm run type-check`: concluido com sucesso.
- `npm run lint`: concluido sem wizard interativo (apenas warnings).
- `npm run build`: concluido com sucesso e rotas estaticas geradas (`/campanhas`, `/contratos/novo`, `/whatsapp/conversas`).
- `pytest` alvo (`test_db.py`, `test_db2.py`, `backend/test_glm.py`): `3 skipped`, sem falha de coleta.
- Documentacao alinhada:
  - `docs/DEPLOY_UBUNTU_DOCKER.md` atualizado para `/health`;
  - `docs/API.md` atualizado com exigencia de Bearer em `/whatsapp-chat/*`.

## Estado Atual (2026-02-10 - pre-clean persona/RAG)
- Rollback institucional pre-clean criado:
  - `docs/ROLLBACK/rollback-20260210-112843-pre-clean-baseline.txt`
  - `docs/ROLLBACK/rollback-20260210-112843-pre-clean.patch`
  - `docs/ROLLBACK/rollback-20260210-112843-pre-clean-staged.patch`
  - `docs/ROLLBACK/rollback-20260210-112843-pre-clean-untracked.txt`
- Diretriz de negocio validada com cliente:
  - VIVA = alma/concierge do Fabio no servidor e no SaaS interno;
  - Viviane = secretaria humana/comercial para fluxo de atendimento externo.
- Problemas priorizados da rodada:
  - `BUG-054` persona dual sem contrato tecnico consolidado;
  - `BUG-055` prompts duplicados e drift;
  - `BUG-056` memoria parcial por dependencia de contexto curto no frontend;
  - `BUG-057` agenda natural com rigidez residual;
  - `BUG-058` ausencia de RAG vetorial moderno para piloto.

## Proximo Gate (2026-02-10 - bloco executivo)
1. limpar duplicacoes de prompts e caminhos legados;
2. consolidar contrato de persona por dominio no backend;
3. migrar memoria efetiva para montagem server-side por sessao;
4. preparar base para RAG moderno com escolha tecnica definitiva do store vetorial.

## Execucao Parcial (2026-02-10 - blocos B/C/D)
- Bloco B concluido:
  - prompts duplicados removidos do frontend/docs;
  - rota legada `/api/viva/prompts/[promptId]` removida;
  - mantidos apenas `docs/PROMPTS/GODMOD.md` e `docs/PROMPTS/PROJETISTA.md`.
- Bloco C em validacao:
  - VIVA concierge consolidada no backend do chat interno:
    - `backend/app/services/viva_concierge_service.py`
    - `backend/app/api/v1/viva.py`
  - Viviane mantida no fluxo comercial WhatsApp (webhook).
- Bloco D em validacao:
  - contexto efetivo do modelo agora usa snapshot server-side por sessao.
- Higiene de legado:
  - removidos arquivos sem uso:
    - `backend/app/services/openrouter_service.py`
    - `backend/app/services/brainimage_service_v1_backup.py`.
- Smoke executado:
  - `GET /health` = `200`
  - `GET /viva` = `200`
  - `POST /api/v1/viva/chat` autenticado = `200` com `session_id`
  - agenda natural: criar e concluir compromisso por titulo = `200`.

## Gate Atual
Prosseguir para bloco F (RAG piloto) com decisao tecnica do vetor store e plano de implantacao em fases.

## Diretriz RAG (2026-02-10)
- Vetor store do piloto definido: `pgvector` no Postgres atual.
- Caminho de escala previsto: reavaliar migracao para Qdrant em fase 2 (alto volume/QPS).

## Atualizacao Operacional (2026-02-10 - incidente Next dev cache stale)
- Fonte de verdade desta rodada: ambiente local Windows (`c:\projetos\fabio2`).
- Ambiente Ubuntu/container remoto ainda nao bootstrapado para este ciclo; docs de deploy nao devem ser tratados como estado runtime atual.
- Incidente frontend observado apos limpeza de prompts:
  - `MODULE_NOT_FOUND` no `next dev` apontando para rota removida `api/viva/prompts/[promptId]/route`.
- Causa raiz:
  - cache `.next` stale mantendo dependencia de rota legada removida.
- Correcao aplicada:
  - scripts adicionados em `frontend/package.json`:
    - `clean:next`
    - `dev:reset`
  - validacao tecnica:
    - `npm run clean:next`: OK
    - `npm run build`: OK
- Procedimento padrao de recuperacao local:
  1. parar `next dev`
  2. `npm run clean:next`
  3. `npm run dev:reset`

## Atualizacao Operacional (2026-02-10 - BUG-060 auth/documentacao)
- Diagnostico confirmado: API/backend vivos, mas README tinha senha de teste divergente do runtime dev.
- Correcao aplicada:
  - `frontend/src/app/page.tsx`: tratamento de erro de login por tipo de falha (401/403/HTTP/conexao).
  - `README.md`: senha local atualizada para `1234` com nota do `security_stub.py`.
- Prova de vida da rodada:
  - `GET /health`: `200`
  - `POST /api/v1/auth/login` (`1234`): `200`
  - `POST /api/v1/auth/login` (`senha123`): `401`
- Rollback institucional desta micro-rodada (auth/docs):
  - `docs/ROLLBACK/rollback-20260210-140052-login-auth-baseline.txt`
  - `docs/ROLLBACK/rollback-20260210-140052-login-auth.patch`
  - `docs/ROLLBACK/rollback-20260210-140052-login-auth-staged.patch`
  - `docs/ROLLBACK/rollback-20260210-140052-login-auth-untracked.txt`

## Atualizacao Operacional (2026-02-10 - kickoff redesign VIVA aprovado)
- Aprovado inicio do redesign VIVA em 3 etapas.
- Blueprint tecnico publicado:
  - `docs/ARCHITECTURE/VIVA_REDESIGN.md`
- Bugs estruturais registrados para rastreabilidade:
  - `BUG-062` monolito `viva.py`
  - `BUG-063` rigidez de fallback em agenda
  - `BUG-064` ausencia de handoff completo VIVA -> Viviane
- Acao imediata da etapa 1:
  - gerar commit de seguranca baseline com estado atual completo do repositorio.

## Atualizacao Operacional (2026-02-10 - inicio etapa 2)
- Primeiro corte tecnico executado:
  - agenda fallback da VIVA ficou contextual e menos prescritivo;
  - removido texto fixo que exigia formato rigido para continuar.
- Arquivo alterado:
  - `backend/app/api/v1/viva.py`
- Rastreabilidade:
  - `BUG-063` em validacao.

## Atualizacao Operacional (2026-02-10 - etapa 2 avancada: handoff Viviane)
- Estrutura por dominio iniciada no backend VIVA:
  - NLU de agenda extraido para `backend/app/services/viva_agenda_nlu_service.py`;
  - handoff operacional extraido para `backend/app/services/viva_handoff_service.py`;
  - catalogo de capacidades em `backend/app/services/viva_capabilities_service.py`.
- Novos endpoints VIVA:
  - `GET /api/v1/viva/capabilities`
  - `POST /api/v1/viva/handoff/schedule`
  - `GET /api/v1/viva/handoff`
  - `POST /api/v1/viva/handoff/process-due`
- Fluxo chat atualizado:
  - pedido de agenda com "avisar cliente no WhatsApp" agora cria compromisso + tarefa de handoff.
- Validacao tecnica:
  - compile dos arquivos alterados: OK;
  - `GET /api/v1/viva/capabilities`: OK;
  - handoff via chat + listagem + processamento: OK.
