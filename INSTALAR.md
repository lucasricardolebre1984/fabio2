# 🚀 Instalação Completa - Windows

## Opção 1: Script Automático (Recomendado)

### Passo 1: Abrir PowerShell como Administrador
1. Pressione `Windows + X`
2. Clique em **"Windows PowerShell (Admin)"** ou **"Terminal (Admin)"**

### Passo 2: Executar Script
```powershell
cd c:\projetos\fabio2
.\instalar-tudo.ps1
```

Isso vai instalar automaticamente:
- ✅ Chocolatey (gerenciador de pacotes)
- ✅ Docker Desktop
- ✅ Node.js (LTS)
- ✅ Python 3.11
- ✅ Configurar projeto (bancos, backend, frontend)

**Pode levar 10-20 minutos na primeira vez.**

### Passo 3: Reiniciar (se pedir)
Se o script pedir para reiniciar, reinicie e execute o script novamente.

### Passo 4: Iniciar Sistema
O script vai perguntar se quer iniciar os servidores. Digite `s` e Enter.

Ou manualmente, abra 2 terminais:

**Terminal 1 - Backend:**
```powershell
cd c:\projetos\fabio2\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd c:\projetos\fabio2\frontend
npm run dev
```

Acesse: http://localhost:3000

---

## Opção 2: Instalação Manual

Se preferir instalar manualmente, baixe e instale:

1. **Docker Desktop**: https://docker.com/products/docker-desktop
2. **Node.js LTS**: https://nodejs.org
3. **Python 3.11**: https://python.org

Depois execute:
```powershell
cd c:\projetos\fabio2
docker-compose -f docker-compose.local.yml up -d
cd backend && python -m venv venv && .\venv\Scripts\activate && pip install -r requirements.txt
cd ..\frontend && npm install
```

---

## ❌ Problemas?

| Problema | Solução |
|----------|---------|
| "Não é possível executar scripts" | Execute: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Docker não inicia | Verifique se Virtualização está habilitada na BIOS |
| npm install lento | Normal na primeira vez, aguarde |
| pip install lento | Normal, aguarde |

---

## ✅ Verificação

Após instalação, verifique:
```powershell
docker --version      # Deve mostrar versão
node --version        # Deve mostrar v18+ ou v20+
python --version      # Deve mostrar 3.11+
```
