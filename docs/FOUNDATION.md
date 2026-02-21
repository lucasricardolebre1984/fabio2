# FOUNDATION - Bases Institucionais de Execucao

Data de consolidacao: 2026-02-21
Escopo: regras minimas obrigatorias para operar o SaaS FC Solucoes Financeiras sem drift entre local, GitHub e Ubuntu.

## Objetivo institucional

- Manter uma unica linha de verdade tecnica em `main`.
- Garantir que runtime de producao reflita exatamente o que esta versionado.
- Evitar resposta inventada da IA e preservar COFRE como ancora semantica oficial.

## Fontes de verdade

- Codigo e historico: `main` em `https://github.com/lucasricardolebre1984/fabio2`
- Persona e skills: `backend/COFRE/persona-skills/`
- Memoria canonica: `backend/COFRE/memories/`
- Estado de sessao: `docs/SESSION.md`
- Status institucional: `docs/STATUS.md`
- Registro de bugs: `docs/BUGSREPORT.md`

## Gates institucionais da homologacao

- Gate 1: Git alinhado (`local == origin/main == ubuntu/main`).
- Gate 2: Stack prod em pe (`backend`, `frontend`, `nginx`, `postgres`, `redis`, `evolution-api`).
- Gate 3: Saude externa valida (`/` e `/health` em `https://fabio.automaniaai.com.br`).
- Gate 4: Fluxos SaaS sem invencao (agenda/clientes/contratos/campanhas via rotas reais).
- Gate 5: WhatsApp com ingestao + resposta persistida (`whatsapp_conversas` e `whatsapp_mensagens`).
- Gate 6: COFRE coerente com runtime (persona/skills/memorias + blindagem/rollback).
- Gate 7: Documentacao atualizada para handoff.

## Proximo gate institucional (rodada atual)

Fechar gate de WhatsApp intermitente com evidencias de ponta a ponta para contatos `@lid` e `@s.whatsapp.net`, sem regressao de contexto da VIVA.

## Regras de execucao

- Nao criar branch secundaria; operar em `main`.
- Nao fazer deploy com worktree sujo em Ubuntu.
- Toda alteracao relevante deve atualizar `docs/SESSION.md` e `docs/STATUS.md`.
- Todo bug novo entra em `docs/BUGSREPORT.md` antes da correcao.

## Checklist rapido de handoff

- Confirmar commit ativo em local e Ubuntu.
- Confirmar containers `Up` e health endpoint `200`.
- Confirmar variaveis criticas (`OPENAI_*`, `EVOLUTION_API_KEY`, `WA_INSTANCE_NAME`).
- Confirmar eventos webhook chegando em `/api/v1/webhook/evolution`.
- Confirmar persistencia em banco (`whatsapp_conversas`, `whatsapp_mensagens`).
- Anexar evidencias no final de `docs/SESSION.md`.
