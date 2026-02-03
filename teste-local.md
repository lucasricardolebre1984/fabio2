# ✅ Checklist de Teste Local

## Preparação

- [ ] Docker Desktop está rodando
- [ ] Portas 5432, 6379, 8000, 3000, 8080 estão livres

---

## Teste 1: Subir Bancos (Docker)

```powershell
cd c:\projetos\fabio2
docker-compose -f docker-compose.local.yml up -d
```

**Esperado:**
- ✅ `fabio2-postgres` running
- ✅ `fabio2-redis` running  
- ✅ `fabio2-evolution` running

**Comando para verificar:**
```powershell
docker ps
```

---

## Teste 2: Backend

### 2.1 Instalar dependências (primeira vez)
```powershell
cd c:\projetos\fabio2\backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2.2 Criar .env
```powershell
copy ..\.env.example .env
```

### 2.3 Iniciar servidor
```powershell
uvicorn app.main:app --reload
```

**Esperado:**
- ✅ Mensagem: `Application startup complete`
- ✅ Acesse: http://localhost:8000/docs
- ✅ Deve aparecer Swagger UI com as rotas

---

## Teste 3: Frontend

### 3.1 Instalar dependências (primeira vez)
```powershell
cd c:\projetos\fabio2\frontend
npm install
```

### 3.2 Criar .env.local
```powershell
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
```

### 3.3 Iniciar
```powershell
npm run dev
```

**Esperado:**
- ✅ Mensagem: `ready started server on 0.0.0.0:3000`
- ✅ Acesse: http://localhost:3000
- ✅ Deve aparecer tela de login

---

## Teste 4: Criar Usuário

Com backend rodando, abra **novo terminal**:

```powershell
cd c:\projetos\fabio2\backend
.\venv\Scripts\activate
python
```

```python
import asyncio
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
        print("✅ Usuário criado!")

asyncio.run(create_user())
exit()
```

---

## Teste 5: Login

1. Acesse: http://localhost:3000
2. Email: `fabio@fcsolucoes.com`
3. Senha: `senha123`
4. Clique em **Entrar**

**Esperado:**
- ✅ Redireciona para Dashboard
- ✅ Sidebar aparece com menu
- ✅ Dashboard mostra cards

---

## Teste 6: Navegação

Clique em cada menu e verifique:

- [ ] **Contratos** → Lista vazia + botão "Novo Contrato"
- [ ] **Clientes** → Lista vazia + mensagem informativa
- [ ] **Agenda** → Lista vazia
- [ ] **WhatsApp** → Status "desconectado" + botão conectar

---

## Teste 7: API (Opcional)

Teste via Swagger: http://localhost:8000/docs

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "fabio@fcsolucoes.com", "password": "senha123"}'

# Listar templates
curl -X GET "http://localhost:8000/api/v1/contratos/templates" \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## ✅ APROVAÇÃO

Se todos os testes passaram:

```
[✅] Docker OK
[✅] Backend OK  
[✅] Frontend OK
[✅] Login OK
[✅] Navegação OK

STATUS: APROVADO PARA COMMIT FINAL
```

**Comando para parar tudo:**
```powershell
docker-compose -f docker-compose.local.yml down
# Ctrl+C nos terminais do backend e frontend
```

---

## ❌ Problemas Comuns

### "Cannot connect to Docker"
- Inicie o Docker Desktop

### "Port already in use"
- Feche outros programas usando porta 3000 ou 8000

### "Module not found"
- Verifique se ativou o venv: `.\venv\Scripts\activate`

### "npm install erro"
- Apague pasta `node_modules` e tente novamente

### "CORS error"
- Verifique se NEXT_PUBLIC_API_URL está correto no .env.local
