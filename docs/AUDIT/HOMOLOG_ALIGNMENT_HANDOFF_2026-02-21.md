# HOMOLOG ALIGNMENT HANDOFF - 2026-02-21

## Escopo

Consolidar entendimento institucional para continuidade da homologacao sem perda de contexto entre agentes.

## Estado confirmado

- Repositorio local: `C:\projetos\fabio2`
- Branch: `main`
- Commit alvo: `070d406`
- `origin/main`: alinhado ao mesmo commit.
- Servidor Ubuntu: `~/fabio2` em `main` no commit `070d406`.

## Drift operacional (Ubuntu) - resolvido

### Achado

- Arquivo rastreado alterado: `docker-compose.prod.yml`
- Artefatos locais nao rastreados: overrides de compose e matriz de auditoria local.

### Acao aplicada

- Backup de artefatos locais em `~/backups/drift-cleanup-<timestamp>/`.
- Restauracao de `docker-compose.prod.yml` para estado do Git.
- Exclusao dos artefatos de override nao institucionais.
- Inclusao de `.env.prod` e `backups/` no `.git/info/exclude` local do servidor.

### Prova final

- `git status --short` vazio no Ubuntu.
- `git rev-parse --abbrev-ref HEAD` -> `main`
- `git log -1 --pretty=format:%h` -> `070d406`

## Documentacao corrigida nesta rodada

- Criado: `docs/FOUNDATION.md`
- Atualizado: `docs/README.md`
- Atualizado: `docs/ARCHITECTURE.md`
- Atualizado: `docs/PROMPTS/GODMOD.md`
  - caminho de bug report corrigido para `docs/BUGSREPORT.md`
  - caminho de leitura do cofre corrigido para `backend/COFRE/*`
- Atualizado: `docs/SESSION.md`

## Mapa de verdade institucional

- Persona canonica: `backend/COFRE/persona-skills/AGENT.md`
- Skills canonicas: `backend/COFRE/persona-skills/*.md`
- Memoria canonica: `backend/COFRE/memories/`
- Status oficial: `docs/STATUS.md`
- Fundamentos/gates: `docs/FOUNDATION.md`
- Registro de bugs: `docs/BUGSREPORT.md`

## Ponto pendente principal (proximo agente)

- Fechar intermitencia do WhatsApp com evidencia ponta a ponta por contato:
  - evento inbound recebido no webhook
  - mensagem persistida em `whatsapp_mensagens`
  - outbound enviado com `enviada=true`
  - conversa visivel na central `/whatsapp/conversas`

## Comandos de verificacao recomendados

```bash
git status --short
git log -1 --oneline
docker compose -f docker-compose.prod.yml --env-file .env.prod ps
curl -I https://fabio.automaniaai.com.br
curl -sS https://fabio.automaniaai.com.br/health
```

