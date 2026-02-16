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

## Auditoria documental

- Matriz menu -> API -> banco -> COFRE: `docs/AUDIT/menu-endpoint-matrix.md`
- Auditoria de documentacao desta rodada: `docs/AUDIT/DOCS_AUDIT_2026-02-16.md`

## Regra institucional de manutencao

- Atualizar `docs/STATUS.md` e `docs/SESSION.md` em toda rodada relevante.
- Registrar bug em `docs/BUGSREPORT.md` antes de corrigir.
- Manter apenas documentacao ativa institucional nesta pasta.
- Nao usar Vercel como alvo institucional desta operacao; alvo principal e Ubuntu AWS + espelhamento de front conforme estrategia comercial.
