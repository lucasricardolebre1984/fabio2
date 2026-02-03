# 🚀 Instalação - FC Soluções Financeiras

## ⚡ MODO RÁPIDO (Se já tem os programas)

Se você já tem **Docker Desktop**, **Node.js** e **Python** instalados:

```powershell
cd C:\projetos\fabio2
.\configurar-projeto.ps1
```

---

## 📦 MODO COMPLETO (Instala tudo)

Se precisa instalar Docker, Node e Python:

### Passo 1: Baixar e Instalar Manualmente

| Programa | Download | Tamanho |
|----------|----------|---------|
| **Docker Desktop** | https://docker.com/products/docker-desktop | ~500MB |
| **Node.js LTS** | https://nodejs.org (botão verde) | ~30MB |
| **Python 3.11** | https://python.org/downloads | ~25MB |

> 💡 **Dica:** Instale um por um, seguindo os assistentes padrão (Next, Next, Finish)

### Passo 2: Reiniciar o PC
Após instalar os 3 programas, **reinicie o computador**.

### Passo 3: Configurar Projeto
Abra PowerShell (não precisa ser admin) e execute:

```powershell
cd C:\projetos\fabio2
.\configurar-projeto.ps1
```

Isso vai:
- ✅ Subir PostgreSQL e Redis (Docker)
- ✅ Instalar dependências Python (backend)
- ✅ Instalar dependências Node (frontend)

---

## 🚀 INICIAR O SISTEMA

Após configurar, inicie os servidores:

### Opção 1: Script Automático
```powershell
.\start.bat
```
Escolha opção **3** (Ambos).

### Opção 2: Manual (2 Terminais)

**Terminal 1 - Backend:**
```powershell
cd C:\projetos\fabio2\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd C:\projetos\fabio2\frontend
npm run dev
```

Acesse: **http://localhost:3000**

---

## ✅ VERIFICAR INSTALAÇÃO

Abra PowerShell e teste:

```powershell
docker --version      # Deve mostrar versão
node --version        # Deve mostrar v18+ ou v20+
python --version      # Deve mostrar 3.11+
```

Se algum der erro, aquele programa não está instalado corretamente.

---

## ❌ PROBLEMAS COMUNS

### "docker-compose não encontrado"
Docker Desktop não está instalado ou não está no PATH.

**Solução:**
1. Feche e abra o PowerShell novamente
2. Ou use: `docker compose` (sem hífen) ao invés de `docker-compose`

### "npm não encontrado"
Node.js não está instalado ou não está no PATH.

**Solução:**
1. Reinstale o Node.js
2. Marque a opção "Add to PATH" durante instalação

### "python não encontrado"
Python não está instalado ou não está no PATH.

**Solução:**
1. Reinstale o Python
2. Marque "Add Python to PATH" durante instalação

### "Cannot find module"
As dependências não foram instaladas.

**Solução:**
```powershell
cd C:\projetos\fabio2\frontend
npm install

cd C:\projetos\fabio2\backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📊 TAMANHO TOTAL

| Componente | Tamanho |
|------------|---------|
| Docker Desktop | ~500 MB |
| Node.js | ~100 MB |
| Python | ~100 MB |
| Projeto (node_modules) | ~500 MB |
| Projeto (venv) | ~300 MB |
| **Total** | **~1.5 GB** |

---

## 🎯 CHECKLIST

Antes de começar, verifique:
- [ ] Windows 10 ou 11 (64 bits)
- [ ] Pelo menos 4GB de RAM livre
- [ ] Pelo menos 5GB de espaço em disco
- [ ] Conexão com internet

---

## 💬 SUPORTE

Problemas? Me diga qual erro apareceu que eu ajudo!
