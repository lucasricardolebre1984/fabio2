# PROJECT CONTEXT - FC Soluções Financeiras SaaS

> **Documento de Contexto Institucional**  
> **Versão:** 1.0.0  
> **Data:** 2026-02-04  
> **Status:** AUDITORIA INSTITUCIONAL  
> **Branch:** main (5af16a2)  
> **Responsável:** Lucas Lebre (Automania-AI)

---

## 📋 VISÃO GERAL DO PROJETO

**SaaS de gestão de contratos** para FC Soluções Financeiras, com módulos de:
- Contratos (Bacen, Serasa, Protesto)
- Clientes (CRM integrado)
- Agenda (compromissos)
- WhatsApp (Evolution API)
- **Imagens (NOVO - HuggingFace + CÉREBRO INSTITUCIONAL)**

**Stack:** FastAPI + PostgreSQL + Redis + Next.js 14 + Tailwind

---

## 🏗️ ARQUITETURA ATUAL

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 14)                       │
│              http://localhost:3000 (desenvolvimento)            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │Contratos │ │ Clientes │ │  Agenda  │ │WhatsApp  │ │Imagens │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP/REST
┌──────────────────────────────┼──────────────────────────────────┐
│                     BACKEND (FastAPI)                           │
│              http://localhost:8000/api/v1                       │
├──────────────────────────────┼──────────────────────────────────┤
│  API Routers:                │                                  │
│  - /auth                     │  Services:                       │
│  - /contratos                │  - ContratoService               │
│  - /clientes                 │  - ClienteService                │
│  - /agenda                   │  - WhatsAppService               │
│  - /whatsapp                 │  - ImagemService (NOVO)          │
│  - /imagens (NOVO)           │                                  │
├──────────────────────────────┴──────────────────────────────────┤
│  External APIs:                                                 │
│  - Evolution API (WhatsApp) - localhost:8080                    │
│  - HuggingFace Inference (Imagens) - api-inference.huggingface.co│
└─────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│                     DATABASE                                    │
│  PostgreSQL (Docker) - localhost:5432                           │
│  Redis (Docker) - localhost:6379                                │
├──────────────────────────────┴──────────────────────────────────┤
│  Tabelas:                                                       │
│  - users, contratos, clientes, agenda, imagens (NOVO)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 MÓDULO DE IMAGENS - ESPECIFICAÇÃO

### Objetivo
Gerar imagens profissionais para marketing usando IA, com direção criativa do CÉREBRO INSTITUCIONAL.

### Arquitetura Híbrida (Opção B)

| Provedor | Tipo | Limite | Uso |
|----------|------|--------|-----|
| **HuggingFace Inference** | Freemium | 1.000 req/mês | Imagens leves (flyers, posts) |
| **OpenAI DALL-E** | Pago | Por crédito | Imagens pesadas (alta resolução) |
| **Local (futuro)** | Próprio | Ilimitado | GPU dedicada |

### Prompt System
**Arquivo:** `docs/PROMPTS/BRAINIMAGE.md` (CÉREBRO INSTITUCIONAL)

```yaml
Função: Diretor Criativo + Especialista em Realismo + Designer Corporativo
Modos:
  - TXT→IMG: Criação do zero com prompt otimizado
  - IMG→IMG: Edição preservando identidade
Formatos: 1:1, 16:9, 9:16
Saída: Brief + Prompt Final + Negative Prompt + Variações
```

### Pasta Campanhas
```
storage/
├── imagens/           # Uploads e gerações temporárias
└── campanhas/         # Imagens aprovadas
    ├── 20260204_nome_imagem.png
    ├── 20260205_promocao_bacen.png
    └── ...
```

---

## 📁 ESTRUTURA DE DIRETÓRIOS

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── contratos.py
│   │   │       ├── clientes.py
│   │   │       ├── agenda.py
│   │   │       ├── whatsapp.py
│   │   │       └── imagens.py (NOVO)
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── imagem.py (NOVO)
│   │   ├── schemas/
│   │   │   └── imagem.py (NOVO)
│   │   └── services/
│   │       ├── contrato_service.py
│   │       └── imagem_service.py (NOVO)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/(dashboard)/
│       │   ├── contratos/
│       │   ├── clientes/
│       │   ├── agenda/
│       │   ├── whatsapp/
│       │   └── imagens/ (NOVO)
│       │       └── page.tsx
│       ├── components/
│       │   ├── layout/Sidebar.tsx (MODIFICAR)
│       │   └── imagens/ (NOVO)
│       │       └── GeradorImagemModal.tsx
│       └── lib/
│           └── api.ts
├── docs/
│   ├── PROMPTS/
│   │   ├── BRAINIMAGE.md (CÉREBRO INST. - EXISTENTE)
│   │   └── GODMOD.md (PROTOCOLO OPERACIONAL)
│   ├── PROJECT_CONTEXT.md (ESTE ARQUIVO)
│   ├── SESSION.md (CONTEXTO DA SESSÃO)
│   └── STATUS.md (STATUS DO PROJETO)
└── storage/
    ├── imagens/ (NOVO)
    └── campanhas/ (NOVO)
```

---

## 🔐 WORKAROUNDS ATIVOS

| Workaround | Motivo | Arquivo | Status |
|------------|--------|---------|--------|
| security_stub.py | Bcrypt 72 bytes no Windows | backend/app/core/security_stub.py | ✅ Funcional |
| DEV_PASSWORD = "1234" | Facilitar dev | security_stub.py | ✅ Funcional |
| PDF via browser | WeasyPrint precisa GTK+ | frontend/src/lib/pdf.ts | ✅ Funcional |

---

## 🚀 AMBIENTE DE DESENVOLVIMENTO

### URLs Locais
| Serviço | URL | Status |
|---------|-----|--------|
| Frontend | http://localhost:3000 | ✅ Porta correta |
| Backend | http://localhost:8000 | ✅ Rodando |
| Docs API | http://localhost:8000/docs | ✅ Swagger |
| PostgreSQL | localhost:5432 | ✅ Docker |
| Redis | localhost:6379 | ✅ Docker |
| Evolution API | http://localhost:8080 | ✅ Conectado |

### Credenciais
```
Login: fabio@fcsolucoes.com
Senha: 1234 (dev)
WhatsApp: Lucas Lebre - 5516981903443
```

---

## 📊 GATES DE IMPLEMENTAÇÃO

### GATE 0: Documentação ✅
- [x] Criar PROJECT_CONTEXT.md
- [ ] Atualizar SESSION.md
- [ ] Criar GATE_PLAN.md

### GATE 1: Backend API
- [ ] Model Imagem (SQLAlchemy)
- [ ] Schema Imagem (Pydantic)
- [ ] Service Imagem (HuggingFace)
- [ ] Router /api/v1/imagens
- [ ] Pasta storage/imagens
- [ ] Pasta storage/campanhas

### GATE 2: Frontend Menu
- [ ] Adicionar "Imagens" no Sidebar
- [ ] Criar página /imagens
- [ ] Layout grid de imagens

### GATE 3: Frontend Gerador
- [ ] GeradorImagemModal.tsx
- [ ] Integração com API
- [ ] Upload de arquivos
- [ ] Preview de imagens

### GATE 4: Workflow Campanhas
- [ ] Botão "Aprovar para Campanha"
- [ ] Mover arquivo para campanhas/
- [ ] Renomear com data

### GATE 5: Testes & Commit
- [ ] Testar geração de imagem
- [ ] Testar upload
- [ ] Testar aprovação
- [ ] Documentar no MANUAL_DO_CLIENTE
- [ ] Commit atômico

---

## ⚠️ ROLLBACK ESTRUTURADO

**Se algo falhar em qualquer GATE:**

```bash
# 1. Abortar imediatamente
Stop-Process -Name node, python -Force

# 2. Restaurar estado anterior
git reset --hard 5af16a2

# 3. Limpar arquivos não rastreados
git clean -fd

# 4. Reiniciar serviços limpos
# (comandos em docs/SESSION.md)
```

---

## 📞 CONTATOS

- **Empresa:** Automania-AI
- **Responsável:** Lucas Lebre
- **Cliente:** FC Soluções Financeiras (Fábio)
- **Projeto:** fabio2
- **Repositório:** https://github.com/lucasricardolebre1984/fabio2

---

*Documento criado para auditoria institucional*  
*Atualizado em: 2026-02-04*  
*Status: GATE 0 - Documentação*
