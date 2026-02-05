# RUNBOOK - Operação Local

> **Projeto:** FC Soluções Financeiras SaaS  
> **Data:** 2026-02-05

---

## Pré-requisitos

- Docker Desktop instalado
- Python 3.11+
- Node.js 18+

---

## Subir serviços com Docker (recomendado)

```powershell
cd c:\projetos\fabio2

docker-compose -f docker-compose.local.yml up -d
```

Serviços esperados
- PostgreSQL: 5432
- Redis: 6379
- Evolution API: 8080

---

## Backend (local)

```powershell
cd c:\projetos\fabio2\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check
```powershell
Invoke-RestMethod http://localhost:8000/health
```

---

## Frontend (local)

```powershell
cd c:\projetos\fabio2\frontend
npm run dev
```

Acesso
- http://localhost:3000

---

## URLs Principais

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- VIVA: http://localhost:3000/viva
- WhatsApp: http://localhost:3000/whatsapp/conversas

---

## Troubleshooting Rápido

Backend não sobe
- Verificar se porta 8000 está livre
- Verificar Docker (PostgreSQL ativo)

Frontend não sobe
- Verificar porta 3000
- Limpar cache `.next`

Evolution API não responde
- Verificar container `fabio2-evolution`
- Confirmar porta 8080

---

*Documento atualizado em: 2026-02-05*
