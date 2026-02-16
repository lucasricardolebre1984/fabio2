# SESSION - contexto da rodada atual

Data da rodada: 2026-02-16
Branch: main
Status: consolidacao de arquitetura COFRE + correcao institucional da documentacao ativa + ajuste de roteamento de contratos na VIVA.

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

## Regra de historico

O historico tecnico antigo permanece preservado em arquivos de rollback e em documentos no VAULT.
Este arquivo passa a registrar apenas o contexto corrente de sessao.

Atualizado em: 2026-02-16
