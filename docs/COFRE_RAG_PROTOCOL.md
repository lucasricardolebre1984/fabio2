# COFRE RAG Protocol

Status: ativo  
Data: 2026-02-16

## Objetivo
Definir fonte unica e auditavel para persona, skills e memorias da VIVA.

## Fonte unica
- Persona principal: `backend/COFRE/persona-skills/AGENT.md`
- Skills oficiais: `backend/COFRE/persona-skills/*.md`
- Memorias espelhadas por tabela: `backend/COFRE/memories/<tabela>/`

## Tabelas espelhadas (MVP atual)
- `viva_chat_sessions`
- `viva_chat_messages`
- `viva_campanhas`
- `viva_handoff_tasks`
- `viva_memory_vectors`
- `redis_viva_memory_medium`

## Regra de delete sincronizado
Toda exclusao funcional no produto deve refletir no COFRE:
- delete de campanha por ID: remove registro no banco + snapshot do item no COFRE + tentativa de remover asset local vinculado.
- reset de campanhas: limpa banco + logs/snapshots/assets de campanhas no COFRE.

## Regra de governanca
- Nao criar persona paralela fora do COFRE.
- Nao criar skill operacional fora de `backend/COFRE/persona-skills`.
- Toda mudanca de comportamento institucional da VIVA deve atualizar o AGENT canonico.

## Regra de versionamento
- Dados de runtime em `backend/COFRE/memories/` nao devem ser commitados.
- O repositório deve manter apenas estrutura de pastas com `.gitkeep`.

## Observabilidade minima
- Endpoint de status: `GET /api/v1/cofre/memories/status`
- Endpoint de tabelas: `GET /api/v1/cofre/memories/tables`
- Endpoint de tail: `GET /api/v1/cofre/memories/{table_name}/tail`
