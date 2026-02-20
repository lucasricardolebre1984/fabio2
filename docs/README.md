# Docs - Fonte de Verdade

Data de consolidacao: 2026-02-16
Escopo: estrutura ativa de documentacao institucional do SaaS FC Solucoes Financeiras.

## Como usar esta pasta

1. Leia primeiro `docs/STATUS.md` para estado atual do sistema.
2. Leia `docs/ARCHITECTURE/OVERVIEW.md` para arquitetura e rotas canonicas.
3. Leia `docs/COFRE_RAG_PROTOCOL.md` para governanca de persona/skills/memorias.
4. Leia `docs/API.md` para contrato de endpoints.
5. Leia `docs/RUNBOOK.md` para operacao local e homologacao.

## Documentos ativos (obrigatorios)

- `docs/STATUS.md`
- `docs/SESSION.md`
- `docs/ARCHITECTURE/OVERVIEW.md`
- `docs/COFRE_RAG_PROTOCOL.md`
- `docs/API.md`
- `docs/BUGSREPORT.md`
- `docs/RUNBOOK.md`
- `docs/DECISIONS.md`

## Manuais operacionais

- `docs/CONTRATOS_LAYOUT_LOGO_MANUAL_AGENTES.md` (ajuste seguro do cabecalho institucional de contratos)

## Auditoria documental

- Matriz menu -> API -> banco -> COFRE: `backend/COFRE/system/blindagem/audit/menu-endpoint-matrix.md`
- Auditoria de documentacao desta rodada: `backend/COFRE/system/blindagem/audit/DOCS_AUDIT_2026-02-16.md`
- Auditoria de qualidade web (perf/a11y/seo/best-practices + seguranca): `backend/COFRE/system/blindagem/audit/WEB_QUALITY_AUDIT_2026-02-16.md`
- Consolidado de blindagem (auditoria + rollback): `backend/COFRE/system/blindagem/BLINDAGEM_INDEX.md`

## Regra institucional de manutencao

- Atualizar `docs/STATUS.md` e `docs/SESSION.md` em toda rodada relevante.
- Registrar bug em `docs/BUGSREPORT.md` antes de corrigir.
- Manter apenas documentacao ativa institucional nesta pasta.
- Nao usar Vercel como alvo institucional desta operacao; alvo principal e Ubuntu AWS + espelhamento de front conforme estrategia comercial.
