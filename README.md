# FC Soluções Financeiras - SaaS de Gestão de Contratos

> **Status:** 🏗️ BLUEPRINT READY - Aguardando autorização para execução  
> **Versão:** 1.0.0  
> **Última Atualização:** 2026-02-03  

---

## 📋 Context Snapshot

### O que vamos construir
Um SaaS completo para **FC Soluções Financeiras** gerenciar contratos de forma institucional e eficiente. O sistema permite:
- Seleção de contratos pré-definidos (Bacen, Serasa, etc.)
- Preenchimento inteligente com atualização automática de valores por extenso
- Geração de contratos em layout institucional profissional
- Gestão completa de clientes com histórico
- Agenda integrada
- Comunicação via WhatsApp

### Por que existe
Facilitar a operação do sócio Fábio, permitindo geração rápida e profissional de contratos, gestão de clientes e comunicação integrada, eliminando processos manuais e reduzindo erros.

### Para quem (ICP/Personas + Perfis)

| Perfil | Descrição | Permissões |
|--------|-----------|------------|
| **Admin** | Proprietário/Sócio (Fábio) | Full access - todos os módulos |
| **Operador** | Assistente administrativo | Contratos (criar/editar), Clientes (visualizar), Agenda |

### MVP (Must-Have)
- ✅ Sistema de autenticação (login/logout)
- ✅ Menu Contratos com templates pré-definidos
- ✅ Template Bacen completo com campos dinâmicos
- ✅ Conversão automática de valores para extenso
- ✅ Geração de PDF em layout institucional
- ✅ Cadastro automático de cliente ao salvar contrato
- ✅ Menu Clientes com histórico
- ✅ Menu Agenda básica
- ✅ Integração WhatsApp (Evolution API)

### Fora do MVP (Pós-MVP)
- 🔄 Templates adicionais (Serasa, Protestos, etc.)
- 🔄 Dashboard com métricas
- 🔄 Assinatura digital dos contratos
- 🔄 Envio automático de contratos por email
- 🔄 Relatórios avançados
- 🔄 Multi-tenant (se futuramente expandir)

### Premissas de Infra/Operação
- **Dev:** Windows (PowerShell) - ambiente local de desenvolvimento
- **Server:** Ubuntu (Bash) - produção
- **Banco:** PostgreSQL
- **Cache:** Redis
- **Filas:** Redis/RQ
- **Storage:** Local (dev) / AWS S3 (prod)

### Gates Operacionais
- ✅ **Leitura:** Livre
- ✅ **Testes & Validação (somente leitura):** Livre
- 📝 **Write local (Windows):** Permitido com disciplina docs-first
- 🔒 **Write no servidor (Ubuntu):** Somente com **AUTORIZO WRITE**
- 🔒 **Push/Deploy:** Somente com **APROVADO**
- 🔒 **Destrutivo (force/reset/drop):** Somente com **APROVADO FORCE**

---

## 🏛️ Arquitetura Macro

### Estilo Arquitetural
**Modular Monolith** com separação clara de responsabilidades:
- Backend: FastAPI (Python) - API RESTful
- Frontend: Next.js 14+ (App Router) - SSR/CSR híbrido
- Banco: PostgreSQL relacional
- Cache/Fila: Redis

### Multi-Tenant
**[DECISÃO]** Single-tenant inicial (Fábio único usuário). Arquitetura preparada para evoluir para multi-tenant se necessário no futuro.

### AuthN/AuthZ
- **AuthN:** JWT (access + refresh tokens)
- **AuthZ:** RBAC simples (Admin vs Operador)
- **Senha:** bcrypt com salt
- **Proteção:** Rate limiting, CORS configurado

### Estratégia de Dados
- **Banco Principal:** PostgreSQL 15+
- **Migrations:** Alembic
- **ORM:** SQLAlchemy 2.0
- **Backup:** Dump diário automatizado
- **Retenção:** LGPD compliant (3 anos conforme necessidade fiscal)

### Observabilidade
- **Logs:** Estruturados (JSON) com correlation ID
- **Métricas:** Prometheus (preparado)
- **Alertas:** Configuráveis por threshold
- **Tracing:** OpenTelemetry (preparado)

### Integrações
- **WhatsApp:** Evolution API (baileys)
- **PDF:** ReportLab / WeasyPrint
- **Extenso:** num2words (pt_BR)

---

## 📁 Estrutura do Repositório

```
.
├── README.md                     # Este arquivo
├── AGENTS.md                     # Instruções para agentes AI
├── .gitignore                    # Git ignore padronizado
├── docker-compose.yml            # Ambiente local completo
├── .env.example                  # Template de variáveis
│
├── backend/                      # API FastAPI
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── main.py                   # Entry point
│   ├── pytest.ini
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # App factory
│   │   ├── config.py             # Settings (pydantic)
│   │   │
│   │   ├── api/                  # Rotas
│   │   │   ├── __init__.py
│   │   │   ├── deps.py           # Dependências (DB, Auth)
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py       # Login/logout
│   │   │   │   ├── contratos.py  # CRUD + geração
│   │   │   │   ├── clientes.py   # CRUD clientes
│   │   │   │   ├── agenda.py     # Eventos
│   │   │   │   └── whatsapp.py   # Integração WA
│   │   │   └── router.py         # Agregador v1
│   │   │
│   │   ├── core/                 # Core business
│   │   │   ├── __init__.py
│   │   │   ├── security.py       # JWT, hashing
│   │   │   ├── exceptions.py     # Custom exceptions
│   │   │   └── constants.py      # Constantes
│   │   │
│   │   ├── db/                   # Database
│   │   │   ├── __init__.py
│   │   │   ├── session.py        # Engine + SessionLocal
│   │   │   └── base.py           # Base declarativa
│   │   │
│   │   ├── models/               # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── cliente.py
│   │   │   ├── contrato.py
│   │   │   ├── contrato_template.py
│   │   │   └── agenda.py
│   │   │
│   │   ├── schemas/              # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── cliente.py
│   │   │   ├── contrato.py
│   │   │   └── agenda.py
│   │   │
│   │   ├── services/             # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── contrato_generator.py
│   │   │   ├── pdf_service.py
│   │   │   ├── extenso_service.py
│   │   │   └── whatsapp_service.py
│   │   │
│   │   └── utils/                # Utilities
│   │       ├── __init__.py
│   │       └── helpers.py
│   │
│   ├── alembic/                  # Migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │
│   └── tests/                    # Testes
│       ├── __init__.py
│       ├── conftest.py
│       └── test_*.py
│
├── frontend/                     # Next.js 14+
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── Dockerfile
│   │
│   ├── src/
│   │   ├── app/                  # App Router
│   │   │   ├── layout.tsx        # Root layout
│   │   │   ├── page.tsx          # Landing/login
│   │   │   ├── (dashboard)/      # Área logada
│   │   │   │   ├── layout.tsx    # Dashboard layout
│   │   │   │   ├── page.tsx      # Home dashboard
│   │   │   │   ├── contratos/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   ├── novo/
│   │   │   │   │   │   └── page.tsx
│   │   │   │   │   └── [id]/
│   │   │   │   │       └── page.tsx
│   │   │   │   ├── clientes/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── agenda/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── whatsapp/
│   │   │   │       └── page.tsx
│   │   │   └── api/              # API routes (Next)
│   │   │
│   │   ├── components/           # Componentes React
│   │   │   ├── ui/               # shadcn/ui base
│   │   │   ├── layout/           # Layout components
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   └── RootLayout.tsx
│   │   │   ├── contratos/        # Contrato components
│   │   │   │   ├── TemplateSelector.tsx
│   │   │   │   ├── ContratoForm.tsx
│   │   │   │   ├── ContratoPreview.tsx
│   │   │   │   └── ValorInput.tsx
│   │   │   ├── clientes/         # Cliente components
│   │   │   └── agenda/           # Agenda components
│   │   │
│   │   ├── hooks/                # Custom hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useContratos.ts
│   │   │   └── useClientes.ts
│   │   │
│   │   ├── lib/                  # Utilities
│   │   │   ├── api.ts            # Axios instance
│   │   │   ├── utils.ts          # Helpers
│   │   │   └── constants.ts
│   │   │
│   │   ├── stores/               # Zustand stores
│   │   │   ├── authStore.ts
│   │   │   └── contratoStore.ts
│   │   │
│   │   ├── types/                # TypeScript types
│   │   │   ├── index.ts
│   │   │   ├── contrato.ts
│   │   │   └── cliente.ts
│   │   │
│   │   └── styles/
│   │       └── globals.css
│   │
│   └── public/                   # Assets estáticos
│       └── logo.png
│
├── contratos/                    # Templates e recursos
│   ├── templates/                # JSON schemas dos contratos
│   │   ├── bacen.json
│   │   └── index.ts
│   ├── bacenmodelo.docx          # Original (referência)
│   └── Base estrutural.pdf       # Original (referência)
│
└── docs/                         # Documentação GODMOD
    ├── STATUS.md
    ├── DECISIONS.md
    ├── BUGSREPORT.md
    ├── ARCHITECTURE/
    │   └── OVERVIEW.md
    ├── FOUNDATION/
    │   └── UX_UI_STANDARDS.md
    ├── VAULT/
    │   └── ENV_TEMPLATE.md
    ├── API/
    │   └── openapi.json
    ├── CONTRATOS/
    │   └── CAMPOS_BACEN.md
    └── PROMPTS/
        ├── PROJETISTA.md
        ├── GODMOD.md
        └── CODER.md
```

---

## 🎯 Módulos (Boundaries + Contratos)

### Módulo: Autenticação
**Responsabilidade:** Gerenciar login, logout, sessão e permissões

**Endpoints:**
```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me
```

**Schemas:**
```typescript
// Login
interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
  user: User;
}

// User
interface User {
  id: string;
  email: string;
  nome: string;
  role: "admin" | "operador";
  ativo: boolean;
  created_at: string;
}
```

### Módulo: Contratos
**Responsabilidade:** Gerenciar templates, criação, preenchimento e geração de PDF

**Endpoints:**
```
GET    /api/v1/contratos/templates           # Lista templates disponíveis
GET    /api/v1/contratos/templates/:id       # Detalhes do template
POST   /api/v1/contratos                     # Criar contrato
GET    /api/v1/contratos                     # Listar contratos
GET    /api/v1/contratos/:id                 # Detalhes
PUT    /api/v1/contratos/:id                 # Atualizar
DELETE /api/v1/contratos/:id                 # Remover
POST   /api/v1/contratos/:id/pdf             # Gerar PDF
POST   /api/v1/contratos/:id/enviar          # Enviar por WhatsApp
```

**Schemas:**
```typescript
// Template
interface ContratoTemplate {
  id: string;
  nome: string;           // "Bacen - Remoção SCR"
  tipo: string;           // "bacen"
  descricao: string;
  campos: CampoTemplate[];
  clausulas: Clausula[];
  created_at: string;
}

interface CampoTemplate {
  nome: string;           // "valor_total"
  label: string;          // "Valor Total"
  tipo: "texto" | "numero" | "data" | "cpf_cnpj" | "email" | "telefone" | "extenso";
  obrigatorio: boolean;
  placeholder?: string;
  mascara?: string;       // "R$ #.##0,00"
  extenso_campo?: string; // Se tipo="extenso", qual campo referencia
}

interface Clausula {
  numero: string;         // "PRIMEIRA"
  titulo: string;         // "DO OBJETO"
  conteudo: string;       // Texto com placeholders [CAMPO]
  ordem: number;
}

// Contrato
interface Contrato {
  id: string;
  template_id: string;
  numero: string;         // "CNT-2026-0001"
  status: "rascunho" | "finalizado" | "enviado" | "cancelado";
  
  // Dados do contratante
  contratante_nome: string;
  contratante_documento: string;
  contratante_email: string;
  contratante_endereco: string;
  contratante_telefone?: string;
  
  // Dados do contrato
  valor_total: number;
  valor_total_extenso: string;
  valor_entrada: number;
  valor_entrada_extenso: string;
  qtd_parcelas: number;
  qtd_parcelas_extenso: string;
  valor_parcela: number;
  valor_parcela_extenso: string;
  prazo_1: number;
  prazo_1_extenso: string;
  prazo_2: number;
  prazo_2_extenso: string;
  local_assinatura: string;
  data_assinatura: string;
  
  // Metadados
  cliente_id?: string;    // Referência ao cliente criado
  created_by: string;     // User ID
  created_at: string;
  updated_at: string;
  pdf_url?: string;
}
```

### Módulo: Clientes
**Responsabilidade:** Cadastro e histórico de clientes

**Endpoints:**
```
POST   /api/v1/clientes
GET    /api/v1/clientes
GET    /api/v1/clientes/:id
PUT    /api/v1/clientes/:id
DELETE /api/v1/clientes/:id
GET    /api/v1/clientes/:id/contratos    # Histórico de contratos
GET    /api/v1/clientes/:id/historico    # Timeline completa
```

**Schemas:**
```typescript
interface Cliente {
  id: string;
  nome: string;
  tipo_pessoa: "fisica" | "juridica";
  documento: string;      // CPF ou CNPJ formatado
  email: string;
  telefone?: string;
  endereco?: string;
  cidade?: string;
  estado?: string;
  cep?: string;
  observacoes?: string;
  
  // Campos contratuais automáticos
  primeiro_contrato_em?: string;
  ultimo_contrato_em?: string;
  total_contratos: number;
  
  created_at: string;
  updated_at: string;
}
```

### Módulo: Agenda
**Responsabilidade:** Gestão de eventos e compromissos

**Endpoints:**
```
POST   /api/v1/agenda/eventos
GET    /api/v1/agenda/eventos
GET    /api/v1/agenda/eventos/:id
PUT    /api/v1/agenda/eventos/:id
DELETE /api/v1/agenda/eventos/:id
GET    /api/v1/agenda/eventos?inicio=&fim=   # Range
```

**Schemas:**
```typescript
interface Evento {
  id: string;
  titulo: string;
  descricao?: string;
  tipo: "reuniao" | "ligacao" | "prazo" | "outro";
  data_inicio: string;    // ISO 8601
  data_fim?: string;
  cliente_id?: string;    // Vinculado a cliente
  contrato_id?: string;   // Vinculado a contrato
  concluido: boolean;
  created_by: string;
  created_at: string;
}
```

### Módulo: WhatsApp
**Responsabilidade:** Integração com Evolution API

**Endpoints:**
```
GET    /api/v1/whatsapp/status           // Status da conexão
POST   /api/v1/whatsapp/conectar         // Iniciar sessão
POST   /api/v1/whatsapp/desconectar      // Encerrar sessão
POST   /api/v1/whatsapp/enviar-texto     // Enviar mensagem
POST   /api/v1/whatsapp/enviar-arquivo   // Enviar documento
GET    /api/v1/whatsapp/mensagens        // Histórico
```

**Schemas:**
```typescript
interface WhatsAppStatus {
  conectado: boolean;
  numero?: string;
  nome_perfil?: string;
  qr_code?: string;       // Base64 quando aguardando scan
  ultima_atualizacao: string;
}

interface EnviarMensagemRequest {
  numero: string;         // 5516999999999
  mensagem: string;
}

interface EnviarArquivoRequest {
  numero: string;
  arquivo_url: string;    // URL pública do PDF
  legenda?: string;
}
```

---

## 📅 Etapas do Projeto (Foundation → Scale)

### FASE 1: Foundation (Semana 1)
**Objetivo:** Ambiente funcional e autenticação

| # | Tarefa | Critério de Aceite | Status |
|---|--------|-------------------|--------|
| 1.1 | Setup Docker Compose | `docker-compose up` sobe todos os serviços | ⬜ |
| 1.2 | Configurar FastAPI | Health check `/health` responde 200 | ⬜ |
| 1.3 | Configurar Next.js | `npm run dev` inicia sem erros | ⬜ |
| 1.4 | Modelagem DB | Migrations aplicam sem erro | ⬜ |
| 1.5 | Auth Backend | Login retorna JWT válido | ⬜ |
| 1.6 | Auth Frontend | Login redireciona para dashboard | ⬜ |
| 1.7 | Layout Dashboard | Sidebar com navegação funcional | ⬜ |

### FASE 2: Core Contratos (Semana 2)
**Objetivo:** Sistema de contratos operacional

| # | Tarefa | Critério de Aceite | Status |
|---|--------|-------------------|--------|
| 2.1 | Schema Template Bacen | JSON válido com todos os campos | ⬜ |
| 2.2 | API Templates | Listagem funciona | ⬜ |
| 2.3 | Service Extenso | "1500.50" → "mil quinhentos reais e cinquenta centavos" | ⬜ |
| 2.4 | Form Dinâmico | Renderiza campos do template | ⬜ |
| 2.5 | Preview ao vivo | Atualização em tempo real | ⬜ |
| 2.6 | Geração PDF | PDF gerado com layout institucional | ⬜ |
| 2.7 | CRUD Contratos | Create/Read/Update/Delete funcionando | ⬜ |

### FASE 3: Clientes & Integração (Semana 3)
**Objetivo:** Cadastro automático e histórico

| # | Tarefa | Critério de Aceite | Status |
|---|--------|-------------------|--------|
| 3.1 | API Clientes | CRUD completo | ⬜ |
| 3.2 | Auto-cadastro | Cliente criado ao salvar contrato | ⬜ |
| 3.3 | Lista Clientes | Tabela com busca e filtros | ⬜ |
| 3.4 | Histórico Cliente | Timeline de contratos | ⬜ |
| 3.5 | Integração Evolution | Conexão WhatsApp estabelecida | ⬜ |
| 3.6 | Envio de PDF | Contrato enviado via WhatsApp | ⬜ |

### FASE 4: Agenda & Polish (Semana 4)
**Objetivo:** Sistema completo e refinado

| # | Tarefa | Critério de Aceite | Status |
|---|--------|-------------------|--------|
| 4.1 | API Agenda | CRUD eventos | ⬜ |
| 4.2 | Calendário Frontend | Visualização mensal/semanal | ⬜ |
| 4.3 | Vincular Eventos | Cliente/Contrato nos eventos | ⬜ |
| 4.4 | Responsividade | Mobile funcional | ⬜ |
| 4.5 | Testes E2E | Fluxo crítico coberto | ⬜ |
| 4.6 | Documentação | README atualizado | ⬜ |

---

## 🎨 Design System (UX/UI Standards)

### Paleta de Cores
```css
/* Primary - Azul Metálico */
--primary-50: #f0f4f8;
--primary-100: #d9e2ec;
--primary-200: #bcccdc;
--primary-300: #9fb3c8;
--primary-400: #829ab1;
--primary-500: #627d98;    /* Base */
--primary-600: #486581;
--primary-700: #334e68;
--primary-800: #243b53;
--primary-900: #102a43;

/* Neutral - Cinza */
--gray-50: #f7fafc;
--gray-100: #edf2f7;
--gray-200: #e2e8f0;
--gray-300: #cbd5e0;
--gray-400: #a0aec0;
--gray-500: #718096;
--gray-600: #4a5568;
--gray-700: #2d3748;
--gray-800: #1a202c;
--gray-900: #171923;

/* Accent */
--accent-success: #38a169;
--accent-warning: #d69e2e;
--accent-danger: #e53e3e;
--accent-info: #3182ce;
```

### Tipografia
- **Headings:** Inter (600-700)
- **Body:** Inter (400-500)
- **Mono:** JetBrains Mono (códigos)

### Componentes Base
- **Botões:** Radius 6px, sombra suave, hover -10% luminosidade
- **Inputs:** Border 1px gray-300, focus ring primary-500
- **Cards:** Radius 8px, sombra shadow-md, padding 24px
- **Tabela:** Header gray-100, linhas alternadas, hover gray-50

### Layout
- **Sidebar:** 280px fixo, cor primary-900
- **Header:** 64px altura, sticky top
- **Content:** max-width 1400px, padding 24px
- **Grid:** 12 colunas, gap 24px

---

## ✅ Critérios de "Pronto para Executar"

- [x] Estrutura de pastas criada
- [x] README.md completo
- [x] Documentação GODMOD em docs/
- [x] Template Bacen mapeado em JSON
- [x] Design System definido
- [x] API Contracts documentados
- [x] Roadmap com 4 fases
- [ ] Ambiente Docker configurado
- [ ] Primeiro commit no GitHub

---

## 🚀 Próximo Passo Único

**AUTORIZO WRITE** para criar:
1. `docker-compose.yml` (PostgreSQL + Redis + backend + frontend)
2. Backend base FastAPI (main.py, config, models iniciais)
3. Frontend base Next.js (layout, página de login)
4. Template Bacen em JSON

---

**STATUS:** PROJECT BLUEPRINT READY  
**MODE:** ARCHITECT ONLY  
**COMPAT:** GODMOD-DOCS-PROMPTS  
**ORIGEM:** automaniaai.com.br
