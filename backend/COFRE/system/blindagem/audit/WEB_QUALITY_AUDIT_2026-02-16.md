# Web Quality Audit - 2026-02-16

Data: 2026-02-16  
Metodo: skill `web-quality-audit`  
Escopo: `frontend`, `backend`, `docs`, runtime local Docker

## Resumo executivo

Veredito: `Parcial / Reprovado para homologacao`

Motivos principais:
- vulnerabilidades criticas/altas no frontend (`next`, `axios`);
- suite de testes backend falhando (`12 failed`);
- `type-check` do frontend quebrando por dependencia de `.next/types`;
- runtime ainda com `security_stub` no fluxo de autenticacao.

## Evidencias tecnicas

### Frontend

- `npm run lint`: OK com warning
  - `frontend/src/app/(dashboard)/contratos/[id]/editar/page.tsx:45`
  - warning `react-hooks/exhaustive-deps` (`carregarContrato`).
- `npm run type-check`: falhou
  - `TS6053` por arquivos ausentes em `.next/types` por `include` fixo.
  - referencia: `frontend/tsconfig.json:34`, `frontend/tsconfig.json:35`.
- `npm run build`: OK (com o mesmo warning de lint).

### Backend

- `python -m pip check`: OK (sem conflitos de dependencia).
- `pytest -q`: falhou (`12 failed, 15 passed, 1 skipped`).
  - classes de falha:
    - auth/contratos retornando `307` onde os testes esperam `401`;
    - erros asyncpg/event loop (`another operation is in progress`, `Event loop is closed`).

### Seguranca de configuracao

- `backend/app/config.py:17` -> `DEBUG: bool = True`
- `backend/app/config.py:55` -> `SECRET_KEY` dev padrao
- `backend/app/api/v1/auth.py:8` -> importa `security_stub`
- `backend/app/api/deps.py:10` -> importa `security_stub`
- `backend/app/core/security_stub.py:24` -> aceita senha fixa `1234`
- `backend/app/main.py:86` -> `allow_methods=["*"]`
- `backend/app/main.py:87` -> `allow_headers=["*"]`

### Dependencias e CVEs (frontend)

Comando: `npm audit --json`  
Resultado:
- `next@14.1.0`: vulnerabilidades `critical/high` (autorizacao, SSRF, DoS);
- `axios`: `high` (`GHSA-43fc-jf86-j433`);
- `eslint-config-next` / `glob`: `high`.

## Lighthouse (login)

Arquivo de evidencia: `docs/AUDIT/lighthouse-login.json`

- Performance: `78`
- Accessibility: `90`
- Best Practices: `96`
- SEO: `100`

Observacao:
- execucao no Windows retornou erro de cleanup temporario (`EPERM`) ao final,
  mas o JSON foi gerado e parseado com sucesso (`fetchTime` valido).

## Infra local

- Containers ativos:
  - `fabio2-backend` (`8000`)
  - `fabio2-postgres` (`5432`)
  - `redis` (`6379`)
  - `fabio2-evolution` (`8080`)
- Healthcheck backend: `GET http://localhost:8000/health` -> `200`.
- `docker compose` emite warning de atributo `version` obsoleto no
  `docker-compose.local.yml`.

## Bugs abertos registrados nesta auditoria

- `BUG-116`: Vulnerabilidades criticas/altas no frontend (`next`, `axios`).
- `BUG-117`: `type-check` quebra por dependencia de `.next/types`.
- `BUG-118`: Suite de testes backend falhando (auth/contratos/viva).
- `BUG-119`: `security_stub` ainda ligado no runtime de autenticacao.
- `BUG-120`: CORS amplo (`allow_methods` e `allow_headers` com `*`).

## Plano de correcao priorizado

1. Seguranca runtime:
   - remover `security_stub` do fluxo real;
   - endurecer CORS por origem/metodo/header necessarios.
2. Dependencias:
   - upgrade de `next` para faixa corrigida;
   - upgrade de `axios` para versao sem advisory.
3. Qualidade de build:
   - corrigir `tsconfig` para `type-check` sem acoplamento a `.next`.
4. Regressao funcional:
   - estabilizar testes backend e revisar contratos de status HTTP.
5. Higiene documental e encoding:
   - normalizar trechos com mojibake em docs/codigo.
