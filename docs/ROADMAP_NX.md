# Roadmap Nx — Modularização do frontend

**Projeto:** FC Soluções Financeiras SaaS (fabio2)  
**Data:** 21 de fevereiro de 2026  
**Status:** Planejado

---

## Objetivo

Migrar o frontend Next.js para um workspace Nx que separa módulos por domínio
funcional. Isso melhora a manutenibilidade, permite builds incrementais e
estabelece limites claros entre features.

---

## Pré-requisito institucional

Conclua o gate de homologação WhatsApp (BUG-133) antes de iniciar a migração.
A migração Nx é uma mudança estrutural que exige base estável.

---

## Estrutura atual

```
fabio2/
├── frontend/              # Next.js 14 — app monolítico
│   └── src/app/
│       ├── (dashboard)/contratos/
│       ├── (dashboard)/clientes/
│       ├── (dashboard)/agenda/
│       ├── (dashboard)/campanhas/
│       ├── whatsapp/
│       └── viva/
├── backend/               # FastAPI (Python)
└── contratos/             # Templates
```

---

## Estrutura alvo

```
fabio2/
├── apps/
│   └── web/               # Next.js (frontend atual)
├── libs/
│   ├── feature-contratos/
│   ├── feature-clientes/
│   ├── feature-agenda/
│   ├── feature-campanhas/
│   ├── feature-whatsapp/
│   ├── feature-viva/
│   ├── shared-ui/         # Componentes reutilizáveis
│   ├── shared-api/       # Cliente API (axios, tipos)
│   └── shared-util/      # Helpers, formatação
├── backend/               # FastAPI (mantido fora do Nx)
├── nx.json
└── package.json           # Root workspace
```

---

## Fases de execução

### Fase 0: Inicialização do workspace

1. Execute `npx create-nx-workspace@latest` na raiz do projeto.
2. Escolha o preset que permite apps existentes (por exemplo, "apps").
3. Verifique que `nx.json` e `package.json` raiz foram criados.

**Risco:** Baixo. O backend e o frontend permanecem inalterados.

---

### Fase 1: Mover o frontend para `apps/web`

1. Crie o diretório `apps/`.
2. Mova o conteúdo de `frontend/` para `apps/web/`.
3. Atualize `nx.json` e `project.json` para referenciar `apps/web`.
4. Atualize `docker-compose.prod.yml` para apontar o build para `apps/web`.
5. Execute `nx build web` e confirme que o build passa.

**Risco:** Médio. Exige ajuste de caminhos no Docker e CI.

---

### Fase 2: Extrair libs compartilhadas

1. Crie `libs/shared-ui` com componentes reutilizáveis (botões, inputs, modais).
2. Crie `libs/shared-api` com o cliente HTTP e tipos de API.
3. Crie `libs/shared-util` com helpers de formatação e validação.
4. Atualize os imports em `apps/web` para usar `@fabio2/shared-ui`, etc.
5. Execute `nx build web` e `nx test web` para validar.

**Risco:** Baixo. Refatoração incremental.

---

### Fase 3: Extrair features por domínio

Extraia uma feature por vez, na ordem abaixo:

1. **feature-contratos** — páginas e componentes de contratos.
2. **feature-clientes** — páginas e componentes de clientes.
3. **feature-agenda** — páginas e componentes de agenda.
4. **feature-campanhas** — páginas e componentes de campanhas.
5. **feature-whatsapp** — páginas e componentes de WhatsApp.
6. **feature-viva** — páginas e componentes da VIVA.

Para cada feature:

1. Crie `libs/feature-<nome>`.
2. Mova os componentes e páginas relacionados.
3. Configure dependências em `project.json`.
4. Atualize os imports em `apps/web`.
5. Execute `nx build web` e valide o fluxo no navegador.

**Risco:** Alto. Cada extração pode quebrar rotas ou imports.

---

### Fase 4: Regras de boundary

1. Configure `@nx/enforce-module-boundaries` em `nx.json`.
2. Defina que `feature-*` não importa de outro `feature-*`.
3. Defina que `feature-*` importa apenas de `shared-*`.
4. Execute `nx run-many -t lint` e corrija violações.

**Risco:** Médio. Pode exigir refatoração de dependências circulares.

---

## Backend Python

O backend FastAPI permanece fora do workspace Nx. O Nx foca em JavaScript e
TypeScript. O Docker e o deploy continuam usando `backend/` como hoje.

---

## Checklist de validação (best practices)

Antes de considerar cada fase concluída:

### Segurança

- [ ] Nenhuma dependência vulnerável (`npm audit`).
- [ ] HTTPS em produção (já aplicado).
- [ ] Sem exposição de source maps em produção.

### Build e deploy

- [ ] `nx build web` conclui com sucesso.
- [ ] `docker compose -f docker-compose.prod.yml up -d --build` funciona.
- [ ] O site em `https://fabio.automaniaai.com.br` responde 200.

### Documentação

- [ ] Atualize `docs/ARCHITECTURE/OVERVIEW.md` com a nova estrutura.
- [ ] Atualize `docs/RUNBOOK.md` com o comando `nx build web`.
- [ ] Registre evidências em `docs/SESSION.md`.

---

## Referências

- [Nx Workspace](https://nx.dev/concepts/more-concepts/applications-and-libraries)
- [Nx Module Boundaries](https://nx.dev/concepts/more-concepts/enforce-module-boundaries)
- `docs/DECISIONS.md` — DECISÃO-013: Migração para Nx
- `docs/FOUNDATION.md` — Gates institucionais

---

*Documento criado conforme skills docs-writer e best-practices. Atualizado em
21 de fevereiro de 2026.*
