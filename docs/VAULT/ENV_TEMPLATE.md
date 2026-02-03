# ENV TEMPLATE - Variáveis de Ambiente

> **Projeto:** FC Soluções Financeiras SaaS  
> **Segurança:** NEVER commit .env files  

---

## 🔐 Backend (.env)

```bash
# ====================================================================
# AMBIENTE
# ====================================================================
ENVIRONMENT=development  # development | staging | production
DEBUG=true               # true (dev) | false (prod)

# ====================================================================
# SERVIDOR
# ====================================================================
HOST=0.0.0.0
PORT=8000
WORKERS=1                # 1 (dev) | 4+ (prod)

# ====================================================================
# BANCO DE DADOS (PostgreSQL)
# ====================================================================
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fabio2
# Ou separado:
DB_HOST=localhost
DB_PORT=5432
DB_USER=fabio2_user
DB_PASSWORD=senha_segura_aqui
DB_NAME=fabio2

# ====================================================================
# REDIS (Cache + Filas)
# ====================================================================
REDIS_URL=redis://localhost:6379/0
# Ou separado:
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# ====================================================================
# SEGURANÇA / AUTH
# ====================================================================
SECRET_KEY=chave_super_secreta_aleatoria_minimo_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# bcrypt
BCRYPT_ROUNDS=12

# ====================================================================
# CORS
# ====================================================================
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# ====================================================================
# EVOLUTION API (WhatsApp)
# ====================================================================
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=api_key_do_evolution
WEBHOOK_URL=https://seu-dominio.com/api/v1/whatsapp/webhook

# Configurações da instância
WA_INSTANCE_NAME=fc-solucoes
WA_QR_TIMEOUT=60000

# ====================================================================
# STORAGE (PDFs)
# ====================================================================
# Modo: local | s3
STORAGE_MODE=local

# Local
STORAGE_LOCAL_PATH=./storage

# AWS S3 (para produção)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
AWS_S3_BUCKET=fabio2-contratos
AWS_S3_ENDPOINT=  # Opcional (MinIO)

# ====================================================================
# LOGGING
# ====================================================================
LOG_LEVEL=INFO          # DEBUG | INFO | WARNING | ERROR
LOG_FORMAT=json         # json | text

# ====================================================================
# EMAIL (Futuro - notificações)
# ====================================================================
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_TLS=true
EMAIL_FROM=noreply@fcsolucoesfinanceiras.com
```

---

## 🎨 Frontend (.env.local)

```bash
# ====================================================================
# API
# ====================================================================
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
API_URL=http://localhost:8000/api/v1

# ====================================================================
# APP
# ====================================================================
NEXT_PUBLIC_APP_NAME=FC Soluções Financeiras
NEXT_PUBLIC_APP_URL=http://localhost:3000

# ====================================================================
# AUTH
# ====================================================================
# Chave para encrypt tokens no localStorage (opcional)
NEXT_PUBLIC_ENCRYPTION_KEY=chave_de_encrypt_frontend
```

---

## 🐳 Docker Compose (.env)

```bash
# ====================================================================
# POSTGRES
# ====================================================================
POSTGRES_USER=fabio2_user
POSTGRES_PASSWORD=senha_segura_postgres
POSTGRES_DB=fabio2

# ====================================================================
# PGADMIN (Opcional - dev)
# ====================================================================
PGADMIN_DEFAULT_EMAIL=admin@local.dev
PGADMIN_DEFAULT_PASSWORD=admin

# ====================================================================
# REDIS
# ====================================================================
REDIS_PASSWORD=senha_redis

# ====================================================================
# EVOLUTION API
# ====================================================================
EVOLUTION_API_KEY=api_key_evolution_segura
```

---

## 📝 Exemplo Completo (Dev)

### `.env` (backend/)
```bash
ENVIRONMENT=development
DEBUG=true

HOST=0.0.0.0
PORT=8000

DATABASE_URL=postgresql+asyncpg://fabio2_user:devpass@localhost:5432/fabio2

REDIS_URL=redis://localhost:6379/0

SECRET_KEY=dev_secret_key_nao_use_em_producao_32chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=http://localhost:3000

EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=dev_evolution_key

STORAGE_MODE=local
STORAGE_LOCAL_PATH=./storage

LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

### `.env.local` (frontend/)
```bash
# Desenvolvimento local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=FC Soluções Financeiras
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Produção (Kinghost)
# NEXT_PUBLIC_API_URL=https://api.automaniaai.com.br/api/v1
# NEXT_PUBLIC_APP_URL=https://www.automaniaai.com.br/fabio
```

---

## 🔒 Segurança - Checklist

- [ ] `.env` adicionado ao `.gitignore`
- [ ] `SECRET_KEY` tem mínimo 32 caracteres aleatórios
- [ ] Senhas de banco são fortes e únicas
- [ ] Chaves de API (Evolution, AWS) estão protegidas
- [ ] Em produção: `DEBUG=false`
- [ ] Em produção: `ENVIRONMENT=production`
- [ ] Em produção: HTTPS obrigatório
- [ ] Tokens de refresh têm expiração curta (7 dias máx)
- [ ] CORS origins são restritas

---

## 🚀 Produção (Checklist)

```bash
# Gerar SECRET_KEY segura
openssl rand -hex 32

# Variáveis obrigatórias
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<gerado_com_openssl>
DATABASE_URL=<connection_string_segura>
CORS_ORIGINS=https://seu-dominio.com
STORAGE_MODE=s3
AWS_ACCESS_KEY_ID=<iam_user_restricto>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_S3_BUCKET=<bucket_name>
```

---

*Atualizado em: 2026-02-03*
