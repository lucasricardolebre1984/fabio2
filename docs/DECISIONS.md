# DECISIONS - Registro de Decisões Arquiteturais

> **Projeto:** FC Soluções Financeiras SaaS  
> **Formato:** ADR (Architecture Decision Records)  

---

## ADR-001: Stack Tecnológica

**Data:** 2026-02-03  
**Status:** APROVADO  

### Contexto
Necessidade de escolher stack moderna, produtiva e sustentável para SaaS de gestão de contratos.

### Decisão
- **Backend:** FastAPI (Python 3.11+)
- **Frontend:** Next.js 14+ (App Router)
- **Banco:** PostgreSQL 15+
- **Cache/Fila:** Redis
- **UI:** Tailwind CSS + shadcn/ui
- **ORM:** SQLAlchemy 2.0

### Alternativas Consideradas
- Django + React: Mais pesado, menos flexível
- Node.js + Express: Menos maduro para tipagem
- Vue.js: Menos demanda de mercado 2026

### Consequências
- ✅ Alta produtividade
- ✅ Type safety (TypeScript + Python types)
- ✅ Ecossistema maduro
- ⚠️ Curva de aprendizado shadcn/ui

---

## ADR-002: Modelo de Multi-tenancy

**Data:** 2026-02-03  
**Status:** APROVADO  

### Contexto
Definir estratégia de isolamento de dados.

### Decisão
**Single-tenant** para MVP. Schema preparado para evoluir para multi-tenant shared database + schema separation se necessário.

### Justificativa
- Apenas 1-2 usuários iniciais
- Reduz complexidade
- Migração futura é viável

---

## ADR-003: Estratégia de Templates de Contratos

**Data:** 2026-02-03  
**Status:** APROVADO  

### Contexto
Como armazenar e renderizar templates de contratos dinâmicos.

### Decisão
- Templates em **JSON** (banco + arquivo)
- Placeholders no formato `[CAMPO]` e `(CAMPO)`
- Geração de PDF via **WeasyPrint** (HTML → PDF)
- Conversão de valores via **num2words**

### Estrutura JSON
```json
{
  "nome": "Bacen",
  "campos": [...],
  "clausulas": [...]
}
```

### Justificativa
- JSON é legível e versionável
- HTML/CSS permite layout institucional preciso
- num2words é padrão e confiável

---

## ADR-004: Integração WhatsApp

**Data:** 2026-02-03  
**Status:** APROVADO  

### Contexto
Escolher solução de integração WhatsApp.

### Decisão
**Evolution API** (baileys) via Docker.

### Alternativas
- WhatsApp Business API (Meta): Caro, burocrático
- WPPConnect: Menos ativo
- whatsapp-web.js: Requer Node separado

### Consequências
- ✅ Gratuito
- ✅ Ativo e documentado
- ✅ API RESTful
- ⚠️ Necessita manter instância ativa

---

## ADR-005: Autenticação

**Data:** 2026-02-03  
**Status:** APROVADO  

### Contexto
Sistema de login seguro e escalável.

### Decisão
- **JWT** com access + refresh tokens
- Access token: 15 minutos
- Refresh token: 7 dias
- Hash de senha: bcrypt

### Justificativa
- Stateless (escala horizontal)
- Padrão da indústria
- Implementação madura em FastAPI

---

## ADR-006: Design System

**Data:** 2026-02-03  
**Status:** APROVADO  

### Contexto
Definir identidade visual institucional.

### Decisão
- **Cores:** Azul metálico (#627d98) + Cinza neutro
- **Tipografia:** Inter (Google Fonts)
- **Componentes:** shadcn/ui customizado
- **Layout:** Sidebar fixa (280px) + conteúdo fluido

### Justificativa
- Azul metálico transmite confiança/profissionalismo
- shadcn/ui é moderno e customizável
- Clean, profissional, 2026-ready

---

## ADR-007: Estratégia de PDF

**Data:** 2026-02-03  
**Status:** APROVADO  

### Contexto
Gerar contratos em PDF com layout institucional.

### Decisão
**WeasyPrint** para geração de PDF via HTML/CSS.

### Fluxo
1. Template JSON → HTML renderizado
2. CSS institucional aplicado
3. WeasyPrint converte para PDF
4. Armazenado localmente (dev) ou S3 (prod)

### Justificativa
- Controle total de layout via CSS
- Suporte a cabeçalho/rodapé
- Fontes personalizadas

---

## ADR-008: Gerenciamento de Estado

**Data:** 2026-02-03  
**Status:** APROVADO  

### Contexto
Escolher solução de state management no frontend.

### Decisão
**Zustand** para estado global + React Query (TanStack Query) para server state.

### Justificativa
- Zustand: Simples, sem boilerplate
- React Query: Cache, revalidação, loading states automáticos

---

## ADR-009: Validação de Dados

**Data:** 2026-02-03  
**Status:** APROVADO  

### Contexto
Validar CPF/CNPJ, emails, telefones.

### Decisão
- **Backend:** Pydantic + validators customizados
- **Frontend:** Zod para schemas + react-hook-form

### Bibliotecas
- `validate-docbr` (CPF/CNPJ)
- `email-validator`
- `phonenumbers`

---

## ADR-010: Versionamento de API

**Data:** 2026-02-03  
**Status:** APROVADO  

### Contexto
Estrutura de rotas da API.

### Decisão
Prefixo `/api/v1/` para todas as rotas.

### Rationale
- Permite evolução futura (v2) sem breaking changes
- Claro e explícito

---

*Registro atualizado em: 2026-02-03*
