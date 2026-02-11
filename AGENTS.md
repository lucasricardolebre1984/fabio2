# AGENTS.md - Instruções para Agentes AI

> **Projeto:** FC Soluções Financeiras SaaS  
> **Repositório:** https://github.com/lucasricardolebre1984/fabio2  

---

## 📋 Visão Geral

Este é um **SaaS de gestão de contratos** para FC Soluções Financeiras.

### Funcionalidades Principais
1. **Contratos:** Templates pré-definidos (Bacen, Serasa, Protesto) com preenchimento dinâmico
2. **Visualização:** Preview do contrato com layout institucional
3. **Edição:** Editar contratos existentes
4. **Clientes:** Cadastro automático por contrato, sincronização de órfãos e cadastro manual
5. **Agenda:** Gestão de compromissos (criar/listar/concluir/excluir)
6. **WhatsApp:** Integração Evolution API com webhook ativo e atendimento VIVA

### Stack Tecnológica
- **Backend:** FastAPI + PostgreSQL + Redis
- **Frontend:** Next.js 14 + Tailwind CSS + shadcn/ui
- **PDF:** WeasyPrint
- **WhatsApp:** Evolution API

---

## 🏗️ Arquitetura

### Estrutura de Pastas
```
.
├── backend/          # FastAPI
│   ├── app/
│   │   ├── api/      # Rotas
│   │   ├── core/     # Segurança
│   │   ├── db/       # Database
│   │   ├── models/   # SQLAlchemy
│   │   ├── schemas/  # Pydantic
│   │   └── services/ # Business logic
│   └── tests/
├── frontend/         # Next.js
│   └── src/
│       ├── app/      # App Router
│       ├── components/
│       ├── hooks/
│       ├── lib/
│       └── stores/
├── contratos/        # Templates JSON
│   └── templates/
└── docs/             # Documentação GODMOD
    ├── PROMPTS/
    ├── ARCHITECTURE/
    ├── FOUNDATION/
    ├── VAULT/
    └── CONTRATOS/
```

### Design System
- **Cores:** Azul metálico (#627d98) + Cinza neutro
- **Tipografia:** Inter
- **Componentes:** shadcn/ui

---

## 🔐 Segurança

### Gates Operacionais
| Ação | Requer |
|------|--------|
| Leitura | - |
| Testes | - |
| Write local | - (com disciplina) |
| Write servidor | **AUTORIZO WRITE** |
| Push/Deploy | **APROVADO** |
| Destrutivo | **APROVADO FORCE** |

### Convenções
- Nunca commitar `.env`
- Nunca expor secrets em logs
- Sempre validar inputs
- Usar prepared statements (SQL)

---

## 📚 Documentação Importante

Leia antes de trabalhar:

1. **docs/ARCHITECTURE/OVERVIEW.md** - Arquitetura completa
2. **docs/FOUNDATION/UX_UI_STANDARDS.md** - Design system
3. **docs/DECISIONS.md** - Decisões arquiteturais
4. **docs/CONTRATOS/CAMPOS_BACEN.md** - Especificação do contrato Bacen
5. **docs/BUGSREPORT.md** - Bugs conhecidos e resolvidos
6. **docs/SESSION.md** - Contexto atual da sessão
7. **docs/CONTRATOS/PLAYBOOK_MODELOS_MD.md** - Processo oficial para subir modelos `.md` sem margem para erro

---

## 🚀 Comandos Úteis

### Desenvolvimento Local
```powershell
# Tudo com Docker
docker-compose up -d

# Backend apenas
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend apenas
cd frontend
npm install
npm run dev
```

### URLs Locais
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Docs API: http://localhost:8000/docs
- PGAdmin: http://localhost:5050
- Evolution API: http://localhost:8080

### Rotas do Sistema
| Rota | Descrição |
|------|-----------|
| `/` | Login |
| `/contratos` | Menu de Templates |
| `/contratos/lista` | Lista de Contratos |
| `/contratos/novo` | Criar Contrato |
| `/contratos/[id]` | Visualizar Contrato |
| `/contratos/[id]/editar` | Editar Contrato |
| `/clientes` | Lista de Clientes |
| `/agenda` | Agenda |
| `/whatsapp` | WhatsApp |

---

## 🐛 Bug Reports

Registrar em `docs/BUGSREPORT.md` antes de corrigir.
Após qualquer mudança de código que impacte bug, atualizar o status correspondente em `docs/BUGSREPORT.md` na mesma entrega (bug novo, bug resolvido ou bug reaberto).

Template:
```markdown
### BUG-XXX: [Título]
**Data:** YYYY-MM-DD
**Severidade:** Alta/Média/Baixa
**Descrição:** [descrição]
**Passos:** 1... 2... 3...
**Esperado:** [comportamento]
**Atual:** [comportamento]
```

### Workarounds Ativos (Dev)

| Workaround | Arquivo | Descrição |
|------------|---------|-----------|
| Autenticação | `app/core/security_stub.py` | Aceita senha "1234" para qualquer usuário |
| PDF | `app/services/pdf_service_stub.py` | Retorna JSON em vez de PDF (aguardando GTK+) |

---

## ✉️ Contato

- **Empresa:** Automania-AI
- **Responsável:** Lucas Lebre
- **Projeto para:** FC Soluções Financeiras (Fábio)

---

*Atualizado em: 2026-02-07 22:10*
