# COFRE da VIVA (canonico)

`COFRE` e a raiz unica de persona, skills e trilha de memorias da VIVA.

## Estrutura canonica

- `persona-skills/`
  - `AGENT.md`: prompt mestre institucional.
  - `skill-generate-campanha-neutra.md`
  - `skill-interpretar-contratos.md`
  - `skill-memoria-cofre.md`
  - `skillconteudo.txt` (compatibilidade legada ainda usada em runtime)
- `memories/`
  - espelho por tabela em `backend/COFRE/memories/<tabela>/`
  - no Git: somente estrutura de pastas + `.gitkeep`
  - arquivos `*.jsonl` e assets sao runtime local (nao versionar)
- `system/`
  - `endpoints_manifest.json`: catalogo canonico de modulos/capacidades/endpoints.
  - `blindagem/`: trilha oficial de auditoria operacional e rollback.
    - `blindagem/audit/*`: evidencias de auditoria tecnica.
    - `blindagem/rollback/*`: patches de rollback versionados.
    - `blindagem/BLINDAGEM_INDEX.md`: inventario unico da blindagem.

## Regras institucionais (anti-frankenstein)

1. Persona e skills oficiais existem somente em `backend/COFRE/persona-skills/`.
2. Nao criar persona paralela fora do COFRE.
3. Nao commitar dados de runtime em `backend/COFRE/memories/`.
4. Toda exclusao funcional no SaaS deve refletir no espelho COFRE quando aplicavel.
5. Catalogo de capacidades/modulos vem de `backend/COFRE/system/endpoints_manifest.json`.
6. Artefatos de blindagem (auditoria e rollback) ficam em `backend/COFRE/system/blindagem/`.

## Observacao de compatibilidade

`skillconteudo.txt` permanece por compatibilidade com `viva_agent_profile_service.py`.
Remover esse arquivo exige ajuste de codigo e validacao de persona em runtime.
