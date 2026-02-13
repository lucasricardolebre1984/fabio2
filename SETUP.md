# 🚀 Setup Local - Windows (CORRIGIDO)

> **Última atualização:** 2026-02-13  
> **Status:** Funcional com workarounds documentados  

---

## ⚠️ BUGS CONHECIDOS (Ver BUGSREPORT.md)

| Bug | Impacto | Workaround |
|-----|---------|------------|
| BUG-001 | Criação de usuário | Criar via endpoint /docs ou SQL direto |
| BUG-002 | ✓ Resolvido | - |
| BUG-003 | ✓ Resolvido | - |

---

## 📋 PRÉ-REQUISITOS

- Windows 10/11 (64 bits)
- 4GB RAM livre
- 5GB espaço em disco
- Internet

---

## 🔧 INSTALAÇÃO DOS PROGRAMAS

### 1. Docker Desktop
https://docker.com/products/docker-desktop

### 2. Node.js LTS
https://nodejs.org (botão verde)

### 3. Python 3.11
https://python.org/downloads

> 💡 **Reinicie o PC após instalar os 3!**

---

## 🚀 CONFIGURAÇÃO DO PROJETO

### Passo 1: Subir Bancos (Docker)
```powershell
cd c:\projetos\fabio2
docker-compose -f docker-compose.local.yml up -d
```

Verifique:
```powershell
docker ps
```
Deve mostrar 3 containers (postgres, redis, evolution)

---

### Passo 2: Configurar Backend

```powershell
cd c:\projetos\fabio2\backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Criar arquivo `.env`:
```powershell
copy .env.example .env
```

Ou crie manualmente `backend/.env`:
```env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql+asyncpg://fabio2_user:fabio2_pass@localhost:5432/fabio2
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=dev_key_change_me
STORAGE_MODE=local
STORAGE_LOCAL_PATH=./storage
```

---

### Passo 3: Iniciar Backend
```powershell
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/docs

---

### Passo 4: Configurar Frontend

```powershell
cd c:\projetos\fabio2\frontend
npm install
```

Criar `.env.local`:
```powershell
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
```

---

### Passo 5: Iniciar Frontend
```powershell
npm run dev
```

Acesse: http://localhost:3000

---

## 👤 CRIAR USUÁRIO ADMIN

### Opção A: Via Swagger UI (Recomendado)

1. Acesse http://localhost:8000/docs
2. Faça login via `POST /api/v1/auth/login` com um usuário já existente.
3. Se não houver usuário, use a Opção B (script SQL/Python) para criar localmente.

### Opção B: Via Script Python (Com BUG-001)

> ⚠️ BUG-001: Script init_db.py pode falhar. Use alternativa abaixo.

Crie arquivo `criar_usuario_simples.py`:
```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.security import get_password_hash

DATABASE_URL = "postgresql+asyncpg://fabio2_user:fabio2_pass@localhost:5432/fabio2"
PASSWORD_HASH = get_password_hash("1234")

async def criar():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # Inserir usuário direto
        await conn.execute(text("""
            INSERT INTO users (id, email, hashed_password, nome, role, ativo, created_at)
            VALUES (
                gen_random_uuid(),
                'fabio@fcsolucoes.com',
                :password_hash,
                'Fabio',
                'admin',
                true,
                NOW()
            )
        """), {"password_hash": PASSWORD_HASH})
    print("Usuário criado!")
    print("Email: fabio@fcsolucoes.com")
    print("Senha: 1234")

asyncio.run(criar())
```

Execute:
```powershell
python criar_usuario_simples.py
```

---

## ✅ LOGIN

- **Email:** `fabio@fcsolucoes.com`
- **Senha:** `1234` (dev local com `security_stub.py`)

---

## 🐛 TROUBLESHOOTING

### "relation users does not exist"
As tabelas não foram criadas. Verifique se o backend subiu corretamente.

### "Email ou senha incorretos"
Usuário não existe no banco. Execute o script de criação.

### Frontend não carrega
Verifique se `next.config.js` não tem `output: 'export'`

---

## 📁 ESTRUTURA FINAL

```
c:\projetos\fabio2
├── backend/
│   ├── venv/
│   ├── .env
│   └── app/
├── frontend/
│   ├── node_modules/
│   └── .env.local
└── docker-compose.local.yml
```

---

## 🎯 CHECKLIST PRÉ-LOGIN

- [ ] Docker rodando (postgres, redis)
- [ ] Backend rodando (uvicorn)
- [ ] Frontend rodando (npm run dev)
- [ ] Usuário criado no banco
- [ ] Acesso http://localhost:3000

---

## 📚 DOCUMENTAÇÃO RELACIONADA

- [BUGSREPORT.md](./docs/BUGSREPORT.md) - Bugs conhecidos
- [DEPLOY_AWS.md](./DEPLOY_AWS.md) - Deploy produção
- [README.md](./README.md) - Visão geral

---

*Atualizado em: 2026-02-13*
