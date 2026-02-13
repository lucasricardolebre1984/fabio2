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

## Estado Contratos (2026-02-11 - piloto CNH)
- template piloto novo habilitado: `CNH`.
- cobertura ponta a ponta concluida:
  - menu `/contratos`;
  - criacao `/contratos/novo?template=cnh`;
  - preview `/contratos/[id]`;
  - PDF frontend e PDF backend.
- artefatos tecnicos:
  - `contratos/templates/cnh.json`;
  - `backend/app/services/contrato_service.py` (fallback `cnh`);
  - `backend/app/services/pdf_service_playwright.py` (ramo clausulas CNH);
  - `frontend/src/app/(dashboard)/contratos/page.tsx`;
  - `frontend/src/app/(dashboard)/contratos/novo/page.tsx`;
  - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`;
  - `frontend/src/lib/pdf.ts`.
- status operacional:
  - pronto para homologacao do cliente no piloto;
  - proximo gate: replicar o mesmo padrao para os demais modelos padronizados enviados.

## Estado Contratos (2026-02-11 - encoding UTF-8 estabilizado)
- bug de acentuacao no fluxo de contrato baixado (`BUG-079`):
  - preview de contrato;
  - PDF frontend;
  - PDF backend.
- diretriz para os proximos modelos:
  - ingestao de modelos `.md` com texto canonico UTF-8 e validacao de render final antes de liberar o modulo.
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

## Atualizacao Operacional (2026-02-10 - finalizacao para entrega)
- Worker automatico de handoff ativado no ciclo de vida da API:
  - processamento de tarefas vencidas a cada ~30s em `backend/app/main.py`.
- Ajuste de linguagem da persona VIVA:
  - reforco para tom mais humano/profissional e anti-rigidez em `backend/app/services/viva_concierge_service.py`.
- Validacao final:
  - tarefa de handoff vencida processada automaticamente com status `sent`.

## Atualizacao Operacional (2026-02-10 - memoria hibrida + RAG pgvector)
- camada de memoria fechada no backend VIVA:
  - curta: snapshot por sessao (PostgreSQL);
  - media: Redis por sessao;
  - longa: vetores em `pgvector` (`viva_memory_vectors`).
- endpoints novos para operacao e prova de vida:
  - `GET /api/v1/viva/memory/status`
  - `GET /api/v1/viva/memory/search`
  - `POST /api/v1/viva/memory/reindex`
  - `GET /api/v1/viva/chat/sessions`
- infraestrutura atualizada:
  - stacks compose movidos para `pgvector/pgvector:pg15`.
- validacao da rodada:
  - `vector_enabled=true` e `redis_enabled=true` no endpoint de status;
  - busca semantica retornando resultados com score;
  - apos `chat/session/new`, memoria longa continua recuperavel por busca.
- plano das proximas ordens documentado em:
  - `docs/ARCHITECTURE/VIVA_NEXT_EXECUTION_PLAN.md`

## Atualizacao Operacional (2026-02-10 - audio institucional no chat VIVA)
- ajuste final no frontend VIVA para fluxo de audio institucional:
  - ao parar a gravacao (`MediaRecorder.onstop`), o audio agora segue direto para transcricao + envio ao chat;
  - removida a dependencia de `Enter` para concluir fluxo normal de audio;
  - no fluxo normal, deixa de aparecer bolha de "Anexos enviados" de audio aguardando envio manual.
- arquivo alterado:
  - `frontend/src/app/viva/page.tsx`
- validacao tecnica:
  - `npm run lint -- --file src/app/viva/page.tsx` (ok; warnings conhecidos de `<img>` nao bloqueantes);
  - `npm run type-check` (ok).
- rastreabilidade:
  - `BUG-071` registrado e resolvido em `docs/BUGSREPORT.md`.

## Atualizacao Operacional (2026-02-10 - avatar holografico 3D VIVA)
- melhoria visual aplicada no frontend da VIVA:
  - avatar central com efeito holografico 3D;
  - movimentos suaves de flutuacao, scanline, rings e pulso de glow;
  - reforco visual quando VIVA esta ativa (`loading`/gravacao).
- arquivo alterado:
  - `frontend/src/app/viva/page.tsx`
- compatibilidade:
  - comportamento responsivo preservado para mobile (`@media max-width: 768px`).
- validacao tecnica:
  - `npm run lint -- --file src/app/viva/page.tsx` (ok, warnings conhecidos de `<img>`);
  - `npm run type-check` (ok).

## Atualizacao Operacional (2026-02-11 - hotfix ultima att VIVA)
- incidente:
  - feedback de campo indicou que a ultima att nao estava consistente no fluxo real.
- correcao aplicada:
  - `frontend/src/app/viva/page.tsx`:
    - bloco holografico movido para fora da area de rolagem do chat;
    - envio de audio pendente reforcado por fila automatica apos encerramento de `loading`;
    - `handleSend` estabilizado com `useCallback` para evitar efeito instavel no fluxo de audio.
- validacao:
  - `npm run type-check` => OK;
  - `npm run lint -- --file src/app/viva/page.tsx` => OK (somente warnings nao bloqueantes de `<img>`).
- rastreabilidade:
  - `BUG-072` movido para **Em validacao** em `docs/BUGSREPORT.md`.

## Atualizacao Operacional (2026-02-11 - incidente agenda em linguagem natural)
- incidente em producao local (chat `/viva`):
  - frase de criacao de compromisso foi interpretada como consulta de agenda.
- evidencia funcional:
  - entrada: "agende o Andre amanha as 10 para mim. Mande para a agenda."
  - saida: "Voce nao tem compromissos de amanha."
- impacto:
  - perda de confianca no fluxo de secretaria (VIVA nao executa comando imperativo de agenda).
- acao institucional:
  - bug formalizado como `BUG-073` (Ativo) em `docs/BUGSREPORT.md`.
- status da janela:
  - sem correcao de codigo nesta rodada, por solicitacao de encerramento do usuario.
- proxima acao planejada (amanha):
  - corrigir desambiguacao de intencao de agenda priorizando verbos de criacao;
  - revalidar com cenarios de linguagem natural e confirmar persistencia na agenda.

## Atualizacao Operacional (2026-02-11 - execucao BUG-073 e BUG-076)
- `BUG-073` (agenda NLU):
  - parser ajustado para tratar criacao com linguagem natural (`agende ... amanha as 10`);
  - classificacao de intencao de consulta ficou menos agressiva quando houver verbo de criacao.
- `BUG-076` (UI conversacao):
  - modo de conversacao passou para botao lateral dedicado (`Conversa VIVA`);
  - bloco visual/voz nao fica mais acoplado ao chat padrao;
  - respostas em voz (TTS) ativadas apenas no modo conversacao, com controle de pausa.
- validacao:
  - `frontend`: type-check e lint do arquivo `src/app/viva/page.tsx` sem erros bloqueantes;
  - `backend`: compileall dos modulos de agenda/chat sem erro;
  - smoke local do parser confirma criacao de compromisso e desvio de consulta eliminado no caso reportado.
- status:
  - `BUG-073` -> Em validacao.
  - `BUG-076` -> Em validacao.

## Atualizacao Operacional (2026-02-11 - execucao BUG-077 conversa continua VIVA)
- ajuste funcional concluido no frontend (`frontend/src/app/viva/page.tsx`):
  - modo `Conversa VIVA` isolado do chat padrao (sem lista de mensagens na tela quando ativo);
  - captura de voz continua automatica no navegador, sem disparo manual de whisper por turno;
  - retomada automatica da escuta apos resposta em voz da VIVA (TTS), com pausa durante fala da assistente;
  - avatar holografico 3D central com fallback de imagem institucional.
- validacao tecnica:
  - `npm run type-check` => OK;
  - `npm run lint -- --file src/app/viva/page.tsx` => OK (warnings nao bloqueantes de `<img>`).
- rastreabilidade:
  - `BUG-077` atualizado para **Em validacao** em `docs/BUGSREPORT.md`.

## Atualizacao Operacional (2026-02-11 - prioridade funcional campanhas)
- diretriz executiva da rodada:
  - pausar evolucao do modulo de conversa continua/3D da VIVA para concentrar esforco em campanhas e geracao de imagem.
- status institucional atualizado:
  - `BUG-076` -> **Em pausa (prioridade campanhas)**;
  - `BUG-077` -> **Em pausa (prioridade campanhas)**;
  - `BUG-061` -> **Reaberto (Ativo)** apos nova validacao de repeticao de personagens.
- prova tecnica (somente leitura):
  - `backend/app/api/v1/viva.py` permanece monolitico e ativo em backlog (`BUG-062`): ~2769 linhas, 21 rotas HTTP, 90+ funcoes/async funcs.

## Atualizacao Operacional (2026-02-11 - execucao BUG-061 rodada 2)
- foco da entrega:
  - reduzir repeticao de personagens e composicoes nas campanhas geradas.
- backend atualizado em `backend/app/api/v1/viva.py`:
  - variacao de elenco por seed (`_persona_scene_variant`);
  - variacao estavel de escolhas visuais (`_stable_pick`);
  - prompt final com diretriz de elenco + enquadramento + humor visual;
  - anti-repeticao explicita reforcada (rosto/cabelo/faixa etaria/composicao);
  - `scene` ampliada para preservar contexto visual e evitar prompt excessivamente generico;
  - temperatura da copy de campanha elevada para ampliar diversidade controlada.
- validacao executada:
  - `python -m compileall app/api/v1/viva.py` => OK;
  - smoke local com 3 seeds distintos => diretrizes visuais diferentes na saida de prompt.
- status:
  - `BUG-061` movido para **Em validacao (rodada 2)**, pendente validacao visual final no front `/campanhas`.

## Atualizacao Operacional (2026-02-11 - execucao BUG-015 + BUG-061 rodada 3)
- correcoes aplicadas no backend (`backend/app/api/v1/viva.py`):
  - direcao visual de campanha agora dinamica por briefing (`tema/oferta/objetivo`), sem hardcode de tema especifico;
  - parser de tema livre para frases naturais (`campanha de/do/da/para ...`);
  - parser de oferta percentual refinado para extracao limpa sem ruido de campos seguintes;
  - anti-repeticao de personagens com memoria curta de campanhas recentes:
    - pool de perfis por publico;
    - selecao de elenco com exclusao de perfis usados recentemente;
    - injecao de `cast_profile` + `recent_cast_ids` no prompt final.
- validacao tecnica:
  - `python -m py_compile app/api/v1/viva.py` => OK;
  - smoke em `backend/venv` confirmou:
    - tema livre extraido corretamente;
    - oferta percentual extraida corretamente;
    - prompt com bloco de elenco obrigatorio + historico recente.
- status:
  - `BUG-015` => Em validacao (rodada dinamica)
  - `BUG-061` => Em validacao (rodada 3)

## Atualizacao Operacional (2026-02-11 - execucao adicional BUG-073)
- backend:
  - `backend/app/services/viva_agenda_nlu_service.py` atualizado para robustez de acento/encoding em agenda natural:
    - hora lida em texto normalizado;
    - data por `amanh*`/`hoj*`;
    - fallback de hora isolada com contexto temporal.
- validacao:
  - `python -m py_compile app/services/viva_agenda_nlu_service.py` => OK;
  - smoke local com frase `agende ... amanhã às 10` retornou payload de criacao com horario correto.
- status:
  - `BUG-073` => Em validacao (aguardando validacao final no navegador/chat real).

## Atualizacao Operacional (2026-02-11 - execucao BUG-016 rodada 2)
- frontend:
  - `frontend/src/app/viva/page.tsx` atualizado para reduzir perda de texto no overlay da arte:
    - parser com limites maiores para headline/subheadline/bullets/quote;
    - modal de arte final com altura maior de blocos de texto e `overflow-y-auto`;
    - exportacao em canvas com mais area util para textos e wrap com limite vertical.
- validacao:
  - `npm run type-check` => OK;
  - `npm run lint -- --file src/app/viva/page.tsx` => OK (somente warnings nao bloqueantes de `<img>`).
- status:
  - `BUG-016` => Em validacao (rodada 2).

## Atualizacao Operacional (2026-02-11 - execucao BUG-015 + BUG-061 rodada 4)
- backend:
  - `backend/app/api/v1/viva.py` reforcado para diversidade visual real em campanhas:
    - `scene_profile` adicionado como novo eixo de variacao (alem de `cast_profile`);
    - memoria anti-repeticao agora considera historico recente de elenco e cenario;
    - pools de cenario ampliados para PF/MEI/PJ;
    - prompt final com bloqueio explicito de composicoes genericas repetitivas;
    - chamada de imagem para campanhas com `quality=high`.
  - robustez extra no fluxo:
    - `_generate_campaign_copy` com fallback seguro em caso de falha/timeout da etapa de copy, evitando quebra do chat por `500` silencioso.
- validacao:
  - `python -m py_compile app/api/v1/viva.py` => OK;
  - simulacao de selecao sequencial:
    - `cast_profile`: 8/8 variacoes unicas;
    - `scene_profile`: 8/8 variacoes unicas.
- status:
  - `BUG-015` => Em validacao (rodada 4 - diversidade).
  - `BUG-061` => Em validacao (rodada 4 - diversidade).

## Atualizacao Operacional (2026-02-11 - snapshot institucional para git)
- validacao completa antes do commit:
  - backend `py_compile` dos modulos alterados => OK;
  - frontend `type-check` => OK;
  - frontend `lint` de `src/app/viva/page.tsx` => OK (somente warnings nao bloqueantes);
  - probes read-only de API e auth => todos endpoints criticos em `200`.
- decisao:
  - liberar snapshot de seguranca no git (`commit + push`) com estado validado.

## Atualizacao Operacional (2026-02-11 - bloco de baixa por validacao)
- rodada concluida com foco em reduzir pendencias em `Em validacao`.
- ajuste tecnico aplicado:
  - `backend/app/services/viva_agenda_nlu_service.py` aceitando comando natural iniciado por `agenda ...` para criacao de compromisso.
- baixa de bugs confirmada por evidencia:
  - API/sessao/agenda/campanhas: `BUG-038`, `BUG-045`, `BUG-046`, `BUG-047`, `BUG-073`;
  - leitura de codigo + smoke funcional: `BUG-037`, `BUG-040`, `BUG-041`, `BUG-042`, `BUG-054`, `BUG-057`.
- saldo atualizado:
  - resolvidos: `57`;
  - pendentes/ativos/pausa/validacao: `7`.

## Atualizacao Operacional (2026-02-11 - fechamento do bloco final dos 7 pendentes)
- arquitetura/backend:
  - SQL de chat/campanhas removido do router `viva.py` e movido para repositórios dedicados:
    - `backend/app/services/viva_chat_repository_service.py`
    - `backend/app/services/viva_campaign_repository_service.py`
  - objetivo: reduzir acoplamento entre rota HTTP e persistencia (passo de fatiamento do `BUG-062`).
- campanhas:
  - inferencia de tema livre reforcada para texto natural sem formato fixo;
  - prompt visual com ancora obrigatoria de tema/oferta/cena + reforco de paleta por marca;
  - variacao adicional de aparencia para reduzir repeticao de personagens.
- UX VIVA:
  - overlay/export da arte final com truncamento seguro (ellipsis) e mais area de texto;
  - audio manual convertido para fluxo direto (sem anexo pendente);
  - modo `Conversa VIVA` mantido no submenu dedicado, com avatar central e movimento 3D por ponteiro.
- validacao tecnica:
  - `python -m py_compile app/api/v1/viva.py app/services/viva_chat_repository_service.py app/services/viva_campaign_repository_service.py` => OK;
  - `npm run type-check` => OK;
  - `npm run lint -- --file src/app/viva/page.tsx` => OK (warnings nao bloqueantes de `<img>`).
- status consolidado:
  - resolvidos: `60`;
  - pendentes em validacao: `4` (`BUG-015`, `BUG-016`, `BUG-061`, `BUG-062`).

## Estado Contratos (2026-02-11 - governanca de novos modelos)
- playbook oficial publicado para subida de modelos `.md`:
  - `docs/CONTRATOS/PLAYBOOK_MODELOS_MD.md`
- cobertura do playbook:
  - template JSON, fallback backend, menu, criacao, preview, PDF frontend/backend, validacao tecnica/funcional e fechamento documental.
- objetivo:
  - permitir carga dos proximos 9-10 modelos com processo replicavel e sem margem de erro.

## Estado Contratos (2026-02-12 - lote completo de modelos `.md` integrado)
- modelos ativos adicionados ao sistema:
  - aumento_score, ccf, certificado_digital, diagnostico360, limpa_nome_express, limpa_nome_standard, rating_convencional, rating_express_pj, remocao_proposta, revisional.
- fluxo ponta a ponta habilitado:
  - menu `/contratos`;
  - criacao `/contratos/novo?template=<id>`;
  - preview `/contratos/[id]` com clausulas dinamicas;
  - PDF frontend (`src/lib/pdf.ts`) e PDF backend (`pdf_service_playwright.py`) com clausulas dinamicas e substituicao de placeholders.
- governanca:
  - BUG institucional associado: `BUG-080` => **Resolvido**.
- validacao:
  - backend `py_compile` => OK;
  - frontend `type-check` => OK;
  - frontend `lint` direcionado => OK (warning residual de `<img>` nao bloqueante).

## Estado Contratos (2026-02-12 - incidente de clausulas nao renderizadas)
- sintoma em producao local:
  - preview de contrato exibindo "Clausulas nao cadastradas" mesmo apos carga dos modelos `.md`.
- causa raiz confirmada por diagnostico read-only:
  - backend em container nao encontra `contratos/templates/*.json` no runtime atual;
  - tabela `contrato_templates` local sem seed (`0 rows`);
  - API cai em fallback vazio (`clausulas: null`) em `GET /api/v1/contratos/templates/{id}`.
- governanca:
  - incidente formalizado como `BUG-081` em `docs/BUGSREPORT.md`;
  - correcao ainda nao aplicada neste bloco (somente diagnostico + plano).

## Estado Git (2026-02-12 - copia de seguranca)
- copia de seguranca confirmada no remoto:
  - `HEAD` local e `origin/main` alinhados em `42cc294`.
- estado de trabalho atual:
  - worktree local com alteracoes pendentes (modificados + novos arquivos) ainda sem commit.
- implicacao:
  - rollback para checkpoint remoto e possivel a qualquer momento;
  - alteracoes locais atuais exigem commit dedicado antes de novo push.

## Estado Contratos (2026-02-12 - runtime corrigido para templates)
- correcao estrutural aplicada no ambiente local:
  - backend agora monta `./contratos` no container (`/app/contratos`) e usa `CONTRATOS_TEMPLATES_DIR=/app/contratos/templates`;
  - carregamento de templates centralizado em `backend/app/services/contrato_template_loader.py`.
- impacto funcional:
  - `GET /api/v1/contratos/templates/{id}` voltou a retornar clausulas reais para todos os templates operacionais;
  - preview e PDF frontend/backend passam a aceitar clausulas em formato `conteudo` e `paragrafos` (retrocompatibilidade com BACEN legado).
- sanity check de PDF:
  - imagem backend reconstruida com dependencias alinhadas (`weasyprint==60.2` + `pydyf==0.10.0`);
  - `GET /api/v1/contratos/{id}/pdf` validado com `200 application/pdf`.
- status de bug:
  - `BUG-081` em **Em validacao (runtime corrigido)**, aguardando prova visual final no navegador.

## Estado Contratos (2026-02-12 - fechamento do lote funcional completo)
- modelos adicionais integrados:
  - `rating_full_pj`
  - `jusbrasil`
- artefatos criados/atualizados:
  - `contratos/templates/rating_full_pj.json`
  - `contratos/templates/jusbrasil.json`
  - `backend/app/services/contrato_service.py` (fallbacks novos)
  - `frontend/src/app/(dashboard)/contratos/page.tsx` (cards novos)
  - `frontend/src/app/(dashboard)/contratos/novo/page.tsx` (labels novos)
- validacao de stack:
  - backend `py_compile` => OK;
  - frontend `type-check` => OK;
  - frontend `lint` direcionado => OK.
- validacao funcional:
  - API templates com clausulas:
    - `rating_full_pj=10`
    - `jusbrasil=8`
  - varredura completa dos 15 templates operacionais retornando clausulas no runtime local.
- status de bug:
  - `BUG-082` em **Resolvido**.

## Estado Contratos (2026-02-12 - saneamento final de encoding)
- incidente:
  - simbolos residuais (`�`) em parte das clausulas no preview/PDF.
- correcao estrutural:
  - normalizacao robusta de mojibake aplicada no backend loader de templates e no gerador PDF backend;
  - normalizacao equivalente aplicada no preview/PDF frontend para manter consistencia visual.
- arquivos-chave:
  - `backend/app/services/contrato_template_loader.py`
  - `backend/app/services/pdf_service_playwright.py`
  - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
  - `frontend/src/lib/pdf.ts`
- validacao:
  - backend compile OK;
  - frontend type-check/lint OK;
  - payload UTF-8 de templates validado sem `�` nos modelos amostrados.
- status de bug:
  - `BUG-083` em **Resolvido**.

## Estado Contratos (2026-02-13 - proximo bloco funcional priorizado)
- bug de entrada formalizado:
  - `BUG-084` (Parcelamento UX+Regra).
- objetivo do bloco:
  - remover friccao de venda a vista e padronizar parcelamento em `1..12x` sem prazos manuais no formulario.
- escopo planejado:
  - frontend com seletor de parcelas `1..12`, entrada opcional e simulacao de parcela;
  - backend com limite `<=12`, prazos automaticos em multiplos de 30 e cronograma salvo em `dados_extras`;
  - preview/PDF com compatibilidade para placeholders legados e texto institucional para a vista.
- status:
  - aguardando execucao do bloco BUG-084.

## Estado Contratos (2026-02-13 - BUG-084 executado)
- resultado funcional:
  - fluxo de `novo contrato` nao exige mais prazos manuais;
  - parcelamento limitado a `1..12x` com seletor fechado;
  - entrada segue opcional;
  - valor da parcela passa a ser calculado automaticamente.
- regra de negocio aplicada:
  - backend gera prazos padrao automaticamente:
    - `1x` => `a vista`;
    - `2x..12x` => `30/60/90/...`;
  - cronograma salvo em `dados_extras.prazos_dias` para rastreabilidade;
  - placeholders legados de prazo continuam funcionais com fallback `a vista` no preview e nos PDFs.
- validacao tecnica:
  - backend `py_compile` => OK;
  - frontend `type-check` => OK;
  - frontend `lint` direcionado => OK (warning nao bloqueante existente sobre `<img>`).
- status:
  - `BUG-084` => **Resolvido**.

## Estado Contratos (2026-02-13 - BUG-085 executado)
- escopo:
  - padronizacao dos templates base `bacen`, `cadin` e `cnh` para o mesmo metodo dos modelos novos.
- resultado:
  - estrutura dos 3 templates unificada no padrao atual;
  - placeholders institucionais alinhados para preview/PDF;
  - suporte a token CNH (`[NÚMERO CNH]` / `[NUMERO CNH]`) adicionado em frontend e backend.
- status:
  - `BUG-085` => **Resolvido**.

## Estado Institucional (2026-02-13 - saneamento de seguranca + docs)
- seguranca:
  - `docker-compose-prod.yml` sanitizado para remover segredos hardcoded e adotar variaveis de ambiente.
- documentacao sincronizada com runtime:
  - `README.md` atualizado com escopo real de modelos ativos;
  - `SETUP.md` e `teste-local.md` alinhados com credencial dev `1234`;
  - `docs/MANUAL_DO_CLIENTE.md` atualizado para audio ativo no chat interno `/viva`;
  - `docs/API.md` atualizado com endpoints complementares ativos em producao local;
  - `docs/DEPLOY_UBUNTU_DOCKER.md` alinhado para OpenAI (`OPENAI_API_KEY`).
- governanca:
  - `BUG-086` (drift de documentacao) => **Resolvido**;
  - `BUG-087` (segredos em compose legado) => **Resolvido**.
