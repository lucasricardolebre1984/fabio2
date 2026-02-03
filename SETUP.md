# 🚀 Setup Local - Windows

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop) instalado
- [Python 3.11+](https://python.org) instalado
- [Node.js 18+](https://nodejs.org) instalado
- Git (opcional, para atualizações)

---

## Passo 1: Iniciar Banco de Dados (Docker)

```powershell
# No terminal PowerShell (na pasta do projeto)
cd c:\projetos\fabio2

# Subir apenas PostgreSQL e Redis
docker-compose up -d postgres redis

# Verificar se está rodando
docker ps
```

Deve aparecer:
- `fabio2-postgres` (porta 5432)
- `fabio2-redis` (porta 6379)

---

## Passo 2: Backend (FastAPI)

```powershell
# Abrir NOVO terminal

cd c:\projetos\fabio2\backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente
.\venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env
copy ..\.env.example .env

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Acesse:** http://localhost:8000/docs (documentação API)

---

## Passo 3: Frontend (Next.js)

```powershell
# Abrir NOVO terminal (manter backend rodando!)

cd c:\projetos\fabio2\frontend

# Instalar dependências
npm install

# Criar .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Iniciar servidor
npm run dev
```

**Acesse:** http://localhost:3000

---

## Passo 4: Criar Usuário (Primeiro Acesso)

```powershell
# Abrir NOVO terminal

cd c:\projetos\fabio2\backend
.\venv\Scripts\activate

# Abrir Python interativo
python
```

```python
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash

async def create_user():
    async with AsyncSessionLocal() as db:
        user = User(
            email="fabio@fcsolucoes.com",
            hashed_password=get_password_hash("senha123"),
            nome="Fábio",
            role="admin",
            ativo=True
        )
        db.add(user)
        await db.commit()
        print("Usuário criado!")

asyncio.run(create_user())
exit()
```

---

## Login

- **URL:** http://localhost:3000
- **Email:** fabio@fcsolucoes.com
- **Senha:** senha123

---

## Comandos Úteis

```powershell
# Parar Docker
docker-compose down

# Ver logs PostgreSQL
docker logs fabio2-postgres

# Resetar banco (CUIDADO!)
docker-compose down -v
docker-compose up -d postgres
```

---

## ⚠️ Kinghost - Limitações

**Kinghost Compartilhado NÃO suporta:**
- Backend Python/FastAPI ❌
- PostgreSQL ❌
- Redis ❌
- Docker ❌

**Solução para produção:**
1. **VPS** (Hetzner, DigitalOcean, AWS Lightsail) ~ R$ 20-50/mês
2. **Railway/Render** (gratuito/pago) - Deploy automático
3. **Heroku** - Fácil mas caro

**Ou manter local + ngrok** (para testes):
```powershell
# Instalar ngrok
choco install ngrok

# Expor backend
ngrok http 8000
```

---

## Suporte

Problemas? Verifique:
1. Docker Desktop está rodando?
2. Portas 5432, 6379, 8000, 3000 estão livres?
3. Python e Node estão no PATH?
