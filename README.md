# FC Soluções Financeiras - SaaS de Gestão de Contratos

> **Status:** 🧪 EM TESTES LOCAIS - Aguardando aprovação para deploy AWS  
> **Versão:** 1.0.0  
> **Última Atualização:** 2026-02-07  

---

## 📋 Resumo do Sistema

SaaS completo para **FC Soluções Financeiras** gerenciar contratos de forma institucional.

### Funcionalidades
- ✅ **Contratos:** Templates pré-definidos (Bacen) com preenchimento dinâmico
- ✅ **Clientes:** Cadastro automático por contrato + cadastro manual + sincronização de órfãos
- ✅ **Agenda:** Gestão mínima funcional (criar, listar, concluir e excluir)
- ✅ **WhatsApp:** Integração Evolution API + webhook VIVA ativo
- ✅ **VIVA Interna:** comando de agenda via chat (`agendar TITULO | DD/MM/AAAA HH:MM | descricao opcional`)

### Modelos de Contrato
- ✅ **Bacen** (Remoção SCR) - Pronto para uso
- ⏳ **Outros modelos** - Aguardando (amanhã)

---

## 🚀 Quick Start - Teste Local

### Opção 1: Script Automático (Recomendado)

```powershell
cd c:\projetos\fabio2
.\setup-windows.ps1
```

### Opção 2: Manual

**1. Bancos de Dados (Docker):**
```powershell
docker-compose -f docker-compose.local.yml up -d
```

**2. Backend (Terminal 1):**
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

**3. Frontend (Terminal 2):**
```powershell
cd frontend
npm run dev
```

**4. Acesse:** http://localhost:3000

---

## 📖 Documentação

| Documento | Descrição |
|-----------|-----------|
| [SETUP.md](./SETUP.md) | Guia completo de instalação |
| [teste-local.md](./teste-local.md) | Checklist de testes |
| [DEPLOY_AWS.md](./DEPLOY_AWS.md) | Guia deploy AWS EC2 |
| [docs/ARCHITECTURE/OVERVIEW.md](./docs/ARCHITECTURE/OVERVIEW.md) | Arquitetura do sistema |

### Regra Institucional de Bugs
- Sempre registrar bug novo em `docs/BUGSREPORT.md` antes da correção.
- Sempre atualizar o status em `docs/BUGSREPORT.md` na mesma entrega quando um bug for resolvido, reaberto ou reclassificado.

---

## 🏗️ Tecnologias

### Backend
- **FastAPI** (Python 3.11+)
- **PostgreSQL** 15
- **Redis** (cache/filas)
- **WeasyPrint** (PDF)
- **Evolution API** (WhatsApp)

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui**

---

## 🔐 Login Padrão (Testes)

Após criar usuário:
- **Email:** fabio@fcsolucoes.com
- **Senha (dev local):** 1234

Observação:
- Em ambiente local, o `security_stub.py` aceita senha `1234` para testes.

---

## 🌐 Deploy

### Ambientes

| Ambiente | URL | Status |
|----------|-----|--------|
| Local | http://localhost:3000 | ✅ Pronto |
| AWS EC2 | http://SEU_IP_EC2 | ⏳ Aguardando deploy |

### Deploy AWS EC2

Veja [DEPLOY_AWS.md](./DEPLOY_AWS.md) para instruções completas.

**Resumo:**
```bash
# Na EC2 Ubuntu
git clone https://github.com/lucasricardolebre1984/fabio2.git
cd fabio2
docker-compose up -d --build
```

---

## 📂 Estrutura

```
fabio2/
├── backend/              # FastAPI
│   ├── app/
│   │   ├── api/v1/      # Rotas
│   │   ├── models/      # SQLAlchemy
│   │   ├── schemas/     # Pydantic
│   │   └── services/    # Lógica de negócio
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # Next.js 14
│   ├── src/
│   │   ├── app/         # App Router
│   │   └── components/  # UI
│   └── Dockerfile
├── contratos/
│   └── templates/
│       └── bacen.json   # Template Bacen
├── docs/                # Documentação GODMOD
└── docker-compose.yml   # Config produção
```

---

## ✅ Checklist Pré-Deploy

- [ ] Testes locais passaram
- [ ] Usuário admin criado
- [ ] Variáveis de ambiente configuradas
- [ ] Secrets trocados (não usar defaults)
- [ ] Backup configurado
- [ ] SSL/HTTPS configurado

---

## 🐛 Suporte

Problemas? Verifique:
1. [teste-local.md](./teste-local.md) - Problemas comuns
2. [DEPLOY_AWS.md](./DEPLOY_AWS.md) - Troubleshooting

---

**Feito com 💙 para FC Soluções Financeiras**

*Automania-AI - 2026*
