# COFRE da VIVA (canonico)

`COFRE` e a raiz unica de persona, skills e trilha de memorias da VIVA.

## Estrutura

- `persona-skills/`
  - `AGENT.md`: prompt mestre institucional.
  - `skill-generate-campanha-neutra.md`
  - `skill-interpretar-contratos.md`
  - `skill-memoria-cofre.md`
  - `skillconteudo.txt` (legacy compat)
- `memories/`
  - `viva_chat_sessions/`
  - `viva_chat_messages/`
  - `viva_campanhas/`
    - `items/`
    - `assets/`
  - `viva_handoff_tasks/`
  - `viva_memory_vectors/`
  - `redis_viva_memory_medium/`
  - cada pasta recebe arquivos `YYYY-MM-DD.jsonl`
- `system/`
  - `endpoints_manifest.json`: catalogo canonico de modulos/capacidades/endpoints.

## Regra operacional

1. Edite persona e skill somente em `backend/COFRE/persona-skills/`.
2. Nao crie persona paralela em outras pastas de runtime.
3. Use `backend/COFRE/memories/` para auditoria e tuning da memoria.
4. Delete funcional no SaaS deve refletir delete no COFRE quando aplicavel.
5. Catalogos de capacidades/modulos devem sair de `COFRE/system/endpoints_manifest.json`.

## Compatibilidade

Nao existe fallback operacional para persona/skills fora do COFRE.
O backend carrega `AGENT.md` e skills somente de `COFRE/persona-skills`.
