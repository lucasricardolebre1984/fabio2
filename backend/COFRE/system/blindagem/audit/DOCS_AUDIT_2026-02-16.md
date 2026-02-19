# Auditoria de Documentacao - 2026-02-16

Escopo: pasta `docs/` inteira.
Objetivo: separar documentacao ativa da legada e alinhar fonte de verdade institucional.

## Criterios usados

- Aderencia ao estado real de runtime
- Alinhamento com arquitetura COFRE
- Clareza operacional para homologacao e deploy institucional
- Preservacao de historico sem poluir documentos ativos

## Decisao por grupos

### Manter como ativo (com revisao aplicada nesta rodada)

- `docs/README.md` (novo indice canonico)
- `docs/STATUS.md` (reescrito)
- `docs/SESSION.md` (reescrito para contexto corrente)
- `docs/CONTEXT.md` (reescrito)
- `docs/RUNBOOK.md` (reescrito)
- `docs/ARCHITECTURE.md` (reescrito)
- `docs/ARCHITECTURE/OVERVIEW.md` (reescrito)

### Manter como ativo (sem mudanca nesta rodada)

- `docs/API.md`
- `docs/COFRE_RAG_PROTOCOL.md`
- `docs/BUGSREPORT.md`
- `docs/DECISIONS.md`
- `docs/DEPLOY_UBUNTU_DOCKER.md`
- `docs/DEPLOY_SECRETS.md`
- `docs/AUDIT/menu-endpoint-matrix.md`
- `docs/AUDIT/menu-endpoint-matrix.json`

### Removidos da estrutura ativa

- `docs/DEPLOY_VERCEL.md`
- `docs/MUDANCAS_WHATSAPP_VIVA.md`

Motivo da remocao:
- fluxo fora da estrategia institucional atual
- conteudo historico de ciclo antigo, sem ser fonte de verdade de runtime

## Pendencias documentais para proxima rodada

- Normalizar encoding historico de `docs/DECISIONS.md` e `docs/BUGSREPORT.md` (trechos com caracteres corrompidos).
- Reduzir tamanho de `docs/BUGSREPORT.md` com secao de arquivo historico anual, mantendo bugs ativos no topo.
- Publicar check-list de homologacao funcional VIVA (agenda/contratos/clientes/campanhas) com evidencias por endpoint.

## Resultado

Documentacao ativa consolidada para o modelo institucional atual:
- COFRE como fonte semantica unica
- matriz de integridade menu -> API -> banco -> COFRE mantida
- legado removido da trilha operacional ativa

Data: 2026-02-16
