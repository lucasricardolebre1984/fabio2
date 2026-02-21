# PROJECT HEALTH VERIFICATION - 2026-02-21

> **Protocolo:** GODMOD (docs/PROMPTS/GODMOD.md)  
> **Objetivo:** Verificar saúde do projeto fabio2 (Git + Ubuntu) e documentar segundo padrão institucional.

---

## 1. Visão Geral

| Campo | Valor |
|-------|-------|
| Projeto | FC Soluções Financeiras SaaS (fabio2) |
| Tipo | SaaS (backend FastAPI + frontend Next.js) — **não** é repositório cursor-skill-creator |
| Ambiente Windows | `C:\projetos\fabio2` |
| Ambiente Ubuntu | `/home/ubuntu/fabio2` (EC2) |
| Repositório | https://github.com/lucasricardolebre1984/fabio2 |
| Branch institucional | `main` (única) |

---

## 2. Diagnóstico Git (Windows — executado em 2026-02-21)

### 2.1 Estado verificado

```text
Branch: main
Status: working tree clean
Sincronização: up to date with origin/main
Remote: origin → https://github.com/lucasricardolebre1984/fabio2.git
```

### 2.2 Últimos commits

```text
2f3018c refactor: unify VIVA/VIVIANE personas to canonical AGENT files
1a59413 fix: stop viviane handoff loop and dedupe inbound whatsapp messages
f5d50a6 docs: gate bug133 with evidence and rollback artifacts
0009654 docs: reconcile bug statuses and enforce per-gate rollback protocol
17da7da docs: validate ubuntu bug report and prioritize repair queue
```

### 2.3 Hash canônico atual

```text
2f3018ce7ce4729d0ccd6e4ea456eb50cefca893
```

### 2.4 Veredito Git

| Critério | Status |
|----------|--------|
| Branch = main | ✅ |
| Working tree limpo | ✅ |
| Sincronizado com origin/main | ✅ |
| Sem branches secundárias | ✅ |
| Remote configurado corretamente | ✅ |

**Git saudável no Windows.**

---

## 3. Diagnóstico Ubuntu (checklist para Lucas executar)

> ⚠️ Comandos abaixo devem ser executados **no servidor Ubuntu** por Lucas.  
> Conforme GODMOD §7.2: "dar o comando para lucas executar".

### 3.1 Script de diagnóstico read-only (copiar e colar no Ubuntu)

```bash
# === DIAGNÓSTICO FABIO2 - UBUNTU ===
# Executar em: ssh ubuntu@56.124.101.16 (ou IP atual do EC2)

cd ~/fabio2 || cd /home/ubuntu/fabio2

echo "=== GIT ==="
git rev-parse --abbrev-ref HEAD
git status --short
git log -1 --oneline
git rev-parse HEAD

echo "=== DOCKER ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo "=== HEALTH ==="
curl -s http://localhost:8000/health | head -5 || echo "Backend não respondeu"
curl -s -o /dev/null -w "%{http_code}" https://fabio.automaniaai.com.br/ 2>/dev/null || echo "Frontend externo não acessível"

echo "=== VARIÁVEIS CRÍTICAS (presença) ==="
[ -n "$OPENAI_API_KEY" ] && echo "OPENAI_API_KEY: definida" || echo "OPENAI_API_KEY: ausente"
[ -n "$EVOLUTION_API_KEY" ] && echo "EVOLUTION_API_KEY: definida" || echo "EVOLUTION_API_KEY: ausente"
[ -n "$WA_INSTANCE_NAME" ] && echo "WA_INSTANCE_NAME: $WA_INSTANCE_NAME" || echo "WA_INSTANCE_NAME: ausente"
```

### 3.2 Critérios de saúde Ubuntu

| Critério | Comando de verificação | Esperado |
|----------|------------------------|----------|
| Branch main | `git rev-parse --abbrev-ref HEAD` | `main` |
| Worktree limpo | `git status --short` | vazio |
| Hash alinhado ao Windows | `git rev-parse HEAD` | `2f3018ce...` (ou mais recente após pull) |
| Containers Up | `docker ps` | backend, frontend, nginx, postgres, redis, evolution-api |
| Health 200 | `curl -s localhost:8000/health` | JSON com status |
| Frontend acessível | `curl -s -o /dev/null -w "%{http_code}" https://fabio.automaniaai.com.br/` | `200` |

### 3.3 Se houver drift (Ubuntu desalinhado)

```bash
# APENAS após "APROVADO" do Lucas (GODMOD §2.1)
cd ~/fabio2
git fetch origin
git reset --hard origin/main
# Rebuild/restart conforme docs/RUNBOOK.md ou docker-compose
```

---

## 4. Mapeamento de documentação institucional

Conforme GODMOD §5.1 e docs/README.md:

| Documento | Caminho | Propósito |
|-----------|---------|-----------|
| STATUS | docs/STATUS.md | Estado atual, gates, pendências |
| FOUNDATION | docs/FOUNDATION.md | Gates institucionais, regras de execução |
| SESSION | docs/SESSION.md | Contexto da rodada atual |
| ARCHITECTURE | docs/ARCHITECTURE/OVERVIEW.md | Arquitetura e rotas |
| BUGSREPORT | docs/BUGSREPORT.md | Registro de bugs |
| RUNBOOK | docs/RUNBOOK.md | Operação local e homologação |
| GODMOD | docs/PROMPTS/GODMOD.md | Protocolo operacional DEV DEUS |

---

## 5. Prova de leitura (7 fatos dos docs)

1. **FOUNDATION**: Gate atual é fechar intermitência WhatsApp com evidências ponta a ponta para `@lid` e `@s.whatsapp.net`.
2. **STATUS**: BUG-133 (WhatsApp/SaaS intermitência) é pendência crítica em validação.
3. **ARCHITECTURE**: Persona canônica VIVA em `backend/COFRE/persona-skills/viva/AGENT.md`.
4. **FOUNDATION**: Branch única `main`; não criar branches secundárias.
5. **GODMOD**: Comandos destrutivos (git push, rm, deploy) requerem "APROVADO" explícito.
6. **SESSION**: Drift operacional Ubuntu foi tratado em rodada anterior; runtime alinhado ao main.
7. **BUGSREPORT**: Ordem de reparo P0 inclui BUG-133, BUG-119, BUG-118.

---

## 6. Skills e agentes (esclarecimento)

- **fabio2** não é um repositório de **Cursor Skills** (`.cursor/skills/`).
- O projeto usa **personas/skills** no COFRE: `backend/COFRE/persona-skills/viva/`, `backend/COFRE/persona-skills/viviane/`.
- Esses arquivos são para orquestração da IA VIVA/VIVIANE no SaaS, não para o Cursor IDE.

---

## 7. Resumo executivo

| Área | Status | Observação |
|------|--------|------------|
| Git (Windows) | ✅ Saudável | main, limpo, sincronizado |
| Git (Ubuntu) | ⏳ Pendente | Executar script §3.1 e reportar |
| Documentação | ✅ Alinhada | Estrutura institucional em ordem |
| Próximo gate | BUG-133 | Intermitência WhatsApp em homologação |

---

## 8. Próximos passos recomendados

1. Lucas executar script §3.1 no Ubuntu e anexar output em `docs/SESSION.md` ou neste audit.
2. Se hash Ubuntu ≠ `2f3018c`: executar `git pull origin main` (ou reset conforme §3.3 após "APROVADO").
3. Validar health e frontend conforme §3.2.
4. Continuar homologação BUG-133 conforme `docs/FOUNDATION.md`.

---

*Documento gerado conforme protocolo GODMOD. Atualizado em 2026-02-21.*
