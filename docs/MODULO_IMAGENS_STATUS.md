# MÓDULO DE IMAGENS - STATUS E DOCUMENTAÇÃO

> **Data:** 2026-02-04  
> **Status:** 🟡 FUNCIONAL (90% Completo)  
> **Responsável:** Lucas Lebre (Automania-AI)  
> **Protocolo:** GODMOD  

---

## 🎯 VISÃO GERAL

Módulo completo de geração e gestão de imagens para campanhas de marketing do SaaS FC Soluções Financeiras.

**Empresas atendidas:**
- **FC Soluções Financeiras** - Corretora de crédito/consultoria
- **Rezeta Brasil** - Recuperação de crédito/limpar nome

---

## ✅ FUNCIONALIDADES IMPLEMENTADAS

### 1. Geração de Imagens com IA (GLM-Image)

**Status:** ✅ **100% FUNCIONAL**

**Integração:** Z.AI GLM-Image API  
**Custo:** US$ 0,015/imagem (~R$ 0,075)  
**Modelo:** glm-image  

**Endpoints:**
```
POST /api/v1/imagens/gerar
{
  "prompt": "campanha semana do empresário",
  "formato": "1:1" | "16:9" | "9:16",
  "nome": "Campanha Teste" (opcional)
}
```

**Caminhos dos arquivos:**
- `backend/app/services/glm_image_service.py` - Integração Z.AI
- `backend/app/services/brainimage_service.py` - CÉREBRO INSTITUCIONAL
- `backend/app/services/imagem_service.py` - Service principal
- `backend/app/api/v1/imagens.py` - Endpoints API

### 2. CÉREBRO INSTITUCIONAL (BRAINIMAGE)

**Status:** ✅ **ATIVO E FUNCIONAL**

Transforma prompts simples em direções criativas profissionais.

**Local:** `backend/app/services/brainimage_service.py`

**Funcionamento:**
```python
Input:  "camelo surfando"
Output: "Professional marketing image for financial services campaign: 
         camelo surfando. composição horizontal panorâmica... 
         Shot with lente 50mm, profundidade de campo média..."
```

**Keywords detectadas automaticamente:**
- Sazonais: ano novo, natal, black friday, semana do empresário
- Produtos: crédito, limpar nome, refinanciamento
- Moods: celebração, profissional, confiança, urgência

### 3. Sistema de Custos

**Status:** ✅ **FUNCIONANDO**

**Tabela:** `imagens_custos` (PostgreSQL)

**Modelo:** `backend/app/models/imagem_custo.py`

**Campos:**
- id (UUID)
- imagem_id (UUID, FK para imagens)
- modelo (glm-image)
- provider (zai)
- custo_usd (0.015)
- custo_brl (0.075)
- taxa_cambio (5.0)
- dimensoes, formato
- tempo_geracao_ms
- status (sucesso/erro)
- prompt_original, prompt_enhanced
- created_at

**Endpoints:**
```
GET /api/v1/custos/dashboard     # Dashboard com métricas
GET /api/v1/custos/historico     # Histórico de gerações
GET /api/v1/custos/mes-atual     # Custo acumulado do mês
GET /api/v1/custos/config        # Configuração
```

### 4. Galeria de Imagens

**Status:** ✅ **FUNCIONANDO**

**Página:** `/imagens`

**Funcionalidades:**
- Grid/List view toggle
- Filtros por status (rascunho/aprovada)
- Filtros por tipo (gerada/upload)
- Tabs: Todas, Geradas por IA, Uploads, Campanhas
- Preview com botão "Aprovar"

### 5. Workflow de Aprovação

**Status:** ✅ **FUNCIONANDO**

Ao aprovar, a imagem é movida para:
```
storage/imagens/ → storage/campanhas/YYYYMMDD_nome.png
```

---

## ❌ BUGS CONHECIDOS

### BUG-001: Upload de Imagem Quebrado

**Severidade:** Alta  
**Status:** Em correção

**Erro:**
```json
[{"type":"missing","loc":["body","file"],"msg":"Field required"}]
```

**Causa:** Endpoint espera FormData mas frontend está enviando JSON

**Arquivos afetados:**
- `backend/app/api/v1/imagens.py` - Endpoint upload
- `frontend/src/app/(dashboard)/imagens/upload/page.tsx` - Frontend

**Solução pendente:** Corrigir envio FormData no frontend

---

## 🚀 PRÓXIMOS PASSOS (Roadmap)

### Fase 1: Correções Críticas
- [ ] Corrigir upload de imagem (BUG-001)
- [ ] Adicionar indicador de custo na tela de geração

### Fase 2: Contexto Empresarial
- [ ] Atualizar BRAINIMAGE.md com dados das empresas:
  - FC Soluções Financeiras (cnpj, logo, cores, serviços)
  - Rezeta Brasil (cnpj, logo, cores, serviços)
- [ ] Criar templates de campanhas específicas:
  - "Limpar nome"
  - "Crédito para negativado"
  - "Semana do empresário"
  - "Ano novo, vida nova"

### Fase 3: Upload como Referência
- [ ] Permitir upload de imagem de base na geração
- [ ] Integração com GLM-4V (visão) para análise de imagem

### Fase 4: Chat com IA
- [ ] Novo menu "Falar com IA" no sidebar
- [ ] Integração com GLM-4 para conversa
- [ ] Contexto do sistema financeiro

### Fase 5: Ferramentas Z.AI
- [ ] GLM Slide/Poster Agent (apresentações)
- [ ] GLM ASR (transcrição de áudio)
- [ ] Análise de Layout

---

## 📁 ESTRUTURA DE ARQUIVOS

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── imagens.py          # Endpoints CRUD + gerar
│   │   └── custos.py           # Dashboard de custos
│   ├── models/
│   │   ├── imagem.py           # Model Imagem
│   │   └── imagem_custo.py     # Model ImagemCusto
│   ├── schemas/
│   │   ├── imagem.py           # Schemas Pydantic
│   │   └── imagem_custo.py     # Schemas de custos
│   ├── services/
│   │   ├── imagem_service.py   # Service principal
│   │   ├── glm_image_service.py # Integração Z.AI
│   │   ├── brainimage_service.py # CÉREBRO INSTITUCIONAL
│   │   └── custo_service.py    # Dashboard custos
│   └── config.py               # Config ZAI_API_KEY
├── migrations/
│   └── create_imagens_custos.sql # Migration PostgreSQL
└── .env                        # ZAI_API_KEY

frontend/
├── src/app/(dashboard)/imagens/
│   ├── page.tsx                # Galeria
│   ├── gerar/page.tsx          # Gerar com IA
│   └── upload/page.tsx         # Upload (BUG-001)
└── src/components/layout/Sidebar.tsx # Menu Imagens

docs/
├── PROMPTS/
│   ├── BRAINIMAGE.md           # Prompt engineering
│   └── GODMOD.md               # Protocolo operacional
└── MODULO_IMAGENS_STATUS.md    # Este arquivo
```

---

## 🔧 COMANDOS ÚTEIS

### Testar Geração (Python)
```powershell
cd C:\projetos\fabio2\backend
.\venv\Scripts\activate
python test_glm.py
```

### Verificar Custos (API)
```bash
curl http://localhost:8000/api/v1/custos/dashboard \
  -H "Authorization: Bearer <token>"
```

### Migration PostgreSQL
```sql
-- Tabela já criada, mas para referência:
CREATE TABLE imagens_custos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    imagem_id UUID REFERENCES imagens(id),
    modelo VARCHAR(50),
    provider VARCHAR(50),
    custo_usd NUMERIC(10,6),
    custo_brl NUMERIC(10,6),
    ...
);
```

---

## 💰 CUSTOS OPERACIONAIS

| Serviço | Custo | Observação |
|---------|-------|------------|
| GLM-Image | US$ 0,015/img | ~R$ 0,075 por imagem |
| GLM-4 (Chat) | US$ 0,50/M tokens | Para chat futuro |
| GLM-4V (Visão) | US$ 0,50/M tokens | Para análise de imagem |
| GLM Slide Agent | US$ 0,70/M tokens | Para apresentações |
| GLM ASR | US$ 0,50/hora | Para transcrição |

**Projeção mensal:**
- 100 imagens/mês = R$ 7,50
- 1000 imagens/mês = R$ 75,00

---

## 📞 CONTATO E SUPORTE

- **Responsável:** Lucas Lebre
- **Empresa:** Automania-AI
- **Cliente:** FC Soluções Financeiras / Rezeta Brasil
- **Repositório:** https://github.com/lucasricardolebre1984/fabio2

---

*Documento criado seguindo Protocolo GODMOD*  
*Atualizado em: 2026-02-04 14:50*
