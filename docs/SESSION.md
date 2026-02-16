# SESSION - contexto da rodada atual

Data da rodada: 2026-02-16
Branch: main
Status: consolidacao de arquitetura COFRE + correcao institucional da documentacao ativa + auditoria completa de qualidade web.

## Objetivo da rodada

- Validar e normalizar a pasta `docs` para refletir o estado real do SaaS.
- Separar documentacao ativa de documentacao legada.
- Reforcar COFRE como unica fonte institucional para persona, skills e memorias.

## Entregas desta rodada

- Criado indice canonico: `docs/README.md`
- Reescrito estado ativo: `docs/STATUS.md`
- Reescrita arquitetura ativa: `docs/ARCHITECTURE/OVERVIEW.md`
- Reescrito contexto do produto: `docs/CONTEXT.md`
- Reescrito runbook operacional: `docs/RUNBOOK.md`
- Criada auditoria documental: `docs/AUDIT/DOCS_AUDIT_2026-02-16.md`
- Criada auditoria de qualidade web: `docs/AUDIT/WEB_QUALITY_AUDIT_2026-02-16.md`
- Evidencia de Lighthouse login registrada em: `docs/AUDIT/lighthouse-login.json`
- Documentos legados removidos da estrutura ativa de `docs/`
- Correcao no chat VIVA para contratos:
  - modelos de contrato separados de contratos emitidos por cliente;
  - suporte a comando direto de continuidade (`listar`, `nomes`);
  - filtro por cliente em consulta de contratos emitidos.
- Correcao no NLU de agenda:
  - consulta passou a aceitar variacoes `liste agenda` e `lite agenda` na rota de agenda real.
- Refatoracao de estrutura por dominio:
  - criado `backend/app/services/viva_domain_query_router_service.py`;
  - orquestrador VIVA passou a delegar consultas de contratos/clientes/campanhas/servicos para esse router.

## Novos bugs abertos nesta auditoria

- BUG-116: vulnerabilidades criticas/altas no frontend (`next`, `axios`)
- BUG-117: `npm run type-check` quebrando por dependencia de `.next/types`
- BUG-118: suite backend falhando em auth/contratos/viva
- BUG-119: `security_stub` ativo no fluxo real de autenticacao
- BUG-120: CORS amplo no backend (`allow_methods=*`, `allow_headers=*`)

## Regra de historico

O historico tecnico antigo permanece preservado em arquivos de rollback e em documentos no VAULT.
Este arquivo passa a registrar apenas o contexto corrente de sessao.

Atualizado em: 2026-02-16
