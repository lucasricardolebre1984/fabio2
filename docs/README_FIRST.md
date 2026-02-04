# ⚠️ LEIA PRIMEIRO - QUALQUER AGENTE

> **Você acabou de entrar no projeto FC Soluções Financeiras SaaS**
> 
> **LEIA ESTE ARQUIVO ANTES DE QUALQUER AÇÃO**

---

## 🚨 INFORMAÇÃO CRÍTICA

### Status Atual (2026-02-04)
- ✅ Sistema funcional na porta 3000/8000
- ✅ Rollback executado para estado estável (5af16a2)
- 🟡 Aguardando implementação: Módulo de Imagens
- 📋 Auditoria institucional em andamento

### Regras de Ouro (GODMOD Protocol)
1. **NUNCA** execute git commit/push sem "APROVADO" do Lucas
2. **NUNCA** crie branches - use apenas `main`
3. **SEMPRE** siga os GATES documentados
4. **SEMPRE** teste local antes de commitar
5. **SEMPRE** tenha plano de rollback

---

## 📖 ORDEM DE LEITURA OBRIGATÓRIA

**LEIA NA ORDEM (não pule):**

1. **`docs/README_FIRST.md`** (este arquivo)
2. **`docs/PROJECT_CONTEXT.md`** - Contexto completo do sistema
3. **`docs/GATE_PLAN.md`** - Plano atual e próximos passos
4. **`docs/PROMPTS/GODMOD.md`** - Protocolo operacional
5. **`docs/SESSION.md`** - Estado atual da sessão

**Tempo estimado:** 10-15 minutos

---

## 🎯 O QUE VOCÊ PRECISA FAZER AGORA

### Se você foi chamado para:

#### **Implementar Módulo de Imagens**
- Leia `docs/GATE_PLAN.md` completamente
- Verifique em `docs/SESSION.md` qual GATE está pendente
- Aguarde "APROVADO" do Lucas para iniciar
- Siga o GATE 1 → 2 → 3 → 4 → 5 em sequência

#### **Corrigir Bug/Fazer Manutenção**
- Leia `docs/BUGSREPORT.md` ou `docs/BUGS_REPORT.md`
- Verifique `docs/SESSION.md` para contexto
- Diagnostique com comandos read-only primeiro
- Proponha solução antes de executar

#### **Deploy/Produção**
- Leia `docs/DEPLOY_AWS.md`
- Verifique status em `docs/SESSION.md`
- **NUNCA** faça deploy sem aprovação dupla

---

## 🏗️ ESTRUTURA DO PROJETO

```
backend/          # FastAPI + PostgreSQL + Redis
├── app/
│   ├── api/v1/   # Rotas REST
│   ├── models/   # SQLAlchemy
│   ├── schemas/  # Pydantic
│   └── services/ # Business logic
└── requirements.txt

frontend/         # Next.js 14 + Tailwind
└── src/
    ├── app/(dashboard)/  # Páginas
    ├── components/       # Componentes React
    └── lib/              # Utilitários

docs/             # DOCUMENTAÇÃO (LEIA TUDO)
├── README_FIRST.md      # ← VOCÊ ESTÁ AQUI
├── PROJECT_CONTEXT.md   # Contexto institucional
├── GATE_PLAN.md         # Plano estruturado atual
├── SESSION.md           # Estado da sessão
├── PROMPTS/
│   ├── GODMOD.md        # Protocolo operacional
│   └── BRAINIMAGE.md    # CÉREBRO INSTITUCIONAL
└── ...

storage/          # Arquivos (novo - será criado)
├── imagens/      # Uploads e gerações
└── campanhas/    # Imagens aprovadas
```

---

## 💻 COMANDOS ESSENCIAIS

### Verificar Estado
```powershell
# Git
git status
git log --oneline -5

# Processos
Get-Process node, python | Select-Object ProcessName, Id

# Portas
Test-NetConnection -ComputerName localhost -Port 3000
Test-NetConnection -ComputerName localhost -Port 8000
```

### Iniciar Sistema
```powershell
# Terminal 1 - Backend
cd C:\projetos\fabio2\backend
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd C:\projetos\fabio2\frontend
npm run dev
```

### Rollback de Emergência
```powershell
Stop-Process -Name node, python -Force
git reset --hard 5af16a2
git clean -fd
```

---

## 🚦 GATE ATUAL

**Verifique em `docs/GATE_PLAN.md` o status atual.**

Se estiver em GATE 1+:
- Não pule etapas
- Complete cada GATE antes de passar ao próximo
- Teste antes de commitar
- Documente no SESSION.md

---

## 📞 QUEM CONTATAR

- **Lucas Lebre (Automania-AI)** - Responsável técnico
- **Fábio** - Cliente/Usuário final

---

## ✅ CHECKLIST ANTES DE COMEÇAR

- [ ] Li `docs/README_FIRST.md` (este arquivo)
- [ ] Li `docs/PROJECT_CONTEXT.md`
- [ ] Li `docs/GATE_PLAN.md`
- [ ] Li `docs/PROMPTS/GODMOD.md`
- [ ] Verifiquei `docs/SESSION.md` para estado atual
- [ ] Sistema está rodando localmente (testei login)
- [ ] Estou na branch `main`
- [ ] Working tree está limpo (`git status`)

---

**APÓS LER TUDO, DIGA:**
> "Li toda a documentação. Estou pronto para [tarefa]. Aguardo APROVADO."

---

*Este arquivo garante que qualquer agente possa entrar no projeto e ser produtivo em 15 minutos.*
*Atualizado em: 2026-02-04*
