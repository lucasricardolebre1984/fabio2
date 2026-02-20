# AWS EC2 Go-Live (1 Pagina)

Projeto: FC Solucoes Financeiras SaaS  
Data: 2026-02-20  
Stack validada: `docker-compose.prod.yml` (sincronizado com `docker-compose-prod.yml`)

## 1) Pre-check local concluido

- Build frontend container: OK
- Build backend container: OK
- Stack prod-like `docker compose ... up -d --build`: OK
- Smoke frontend (rotas): OK
- Endpoints API protegidos via nginx (`/api/v1/...`): OK
- Evolution via nginx (`/evolution/`): OK

## 2) Variaveis obrigatorias no servidor (`.env.prod`)

```env
DB_USER=fabio2_user
DB_PASSWORD=troque_senha_forte
DB_NAME=fabio2
SECRET_KEY=troque_chave_forte_com_32_plus
CORS_ORIGINS=https://SEU_DOMINIO
NEXT_PUBLIC_API_URL=https://SEU_DOMINIO/api/v1
EVOLUTION_API_KEY=troque_token_evolution
WA_INSTANCE_NAME=fc-solucoes
OPENAI_API_KEY=troque_openai
```

## 3) Deploy copy/paste (Ubuntu)

```bash
cd /opt
git clone https://github.com/lucasricardolebre1984/fabio2.git
cd fabio2

cat > .env.prod <<'EOF'
DB_USER=fabio2_user
DB_PASSWORD=troque_senha_forte
DB_NAME=fabio2
SECRET_KEY=troque_chave_forte_com_32_plus
CORS_ORIGINS=https://SEU_DOMINIO
NEXT_PUBLIC_API_URL=https://SEU_DOMINIO/api/v1
EVOLUTION_API_KEY=troque_token_evolution
WA_INSTANCE_NAME=fc-solucoes
OPENAI_API_KEY=troque_openai
EOF

docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.prod ps
```

## 4) Bootstrap de usuario admin

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T backend python criar_usuario.py
```

Credencial padrao criada pelo script:
- Email: `fabio@fcsolucoes.com`
- Senha inicial: `1234`

## 5) Smoke final de producao

```bash
curl -sS http://localhost/health
curl -sS http://localhost/evolution/
curl -I http://localhost/

curl -sS -X POST http://localhost/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"fabio@fcsolucoes.com","password":"1234"}'
```

## 6) SSL e dominio (recomendado antes de liberar cliente)

1. Apontar DNS para IP da EC2.
2. Subir proxy SSL (Nginx + Certbot ou Cloudflare proxy).
3. Ajustar `NEXT_PUBLIC_API_URL` e `CORS_ORIGINS` para HTTPS real.
4. Reiniciar stack apos ajuste de `.env.prod`.

## 7) Rollback institucional desta rodada

Arquivos:
- `backend/COFRE/system/blindagem/rollback/rollback_pre_aws_go_live_20260220_144959_baseline.txt`
- `backend/COFRE/system/blindagem/rollback/rollback_pre_aws_go_live_20260220_144959.patch`
- `backend/COFRE/system/blindagem/rollback/rollback_aws_prod_hardening_20260220_153717_baseline.txt`
- `backend/COFRE/system/blindagem/rollback/rollback_aws_prod_hardening_20260220_153717.patch`

Uso rapido:
```bash
git apply --reverse backend/COFRE/system/blindagem/rollback/rollback_aws_prod_hardening_20260220_153717.patch
```

