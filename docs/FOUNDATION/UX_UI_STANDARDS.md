# UX/UI STANDARDS - Design System

> **Projeto:** FC Soluções Financeiras SaaS  
> **Versão:** 1.0.0  
> **Tom:** Profissional, Institucional, Confiança  

---

## 🎨 Paleta de Cores

### Cores Primárias (Azul Metálico)
```css
/* Define a identidade institucional */
--primary-50: #f0f4f8;   /* Fundos claros */
--primary-100: #d9e2ec;  /* Hover suave */
--primary-200: #bcccdc;  /* Bordas claras */
--primary-300: #9fb3c8;  /* Elementos desabilitados */
--primary-400: #829ab1;  /* Placeholders */
--primary-500: #627d98;  /* COR PRINCIPAL */
--primary-600: #486581;  /* Hover primary */
--primary-700: #334e68;  /* Textos importantes */
--primary-800: #243b53;  /* Sidebar */
--primary-900: #102a43;  /* Texto sidebar */
```

### Cores Neutras (Cinza)
```css
/* Base para texto e superfícies */
--gray-50: #f7fafc;   /* Fundo geral */
--gray-100: #edf2f7;  /* Cards/header */
--gray-200: #e2e8f0;  /* Bordas/dividers */
--gray-300: #cbd5e0;  /* Input borders */
--gray-400: #a0aec0;  /* Placeholders */
--gray-500: #718096;  /* Texto secundário */
--gray-600: #4a5568;  /* Texto corpo */
--gray-700: #2d3748;  /* Títulos */
--gray-800: #1a202c;  /* Títulos fortes */
--gray-900: #171923;  /* Texto máximo contraste */
```

### Cores Semânticas
```css
/* Estados e feedback */
--success-50: #f0fff4;
--success-500: #38a169;  /* Sucesso */
--success-600: #2f855a;

--warning-50: #fffaf0;
--warning-500: #d69e2e;  /* Alerta */
--warning-600: #b7791f;

--danger-50: #fff5f5;
--danger-500: #e53e3e;   /* Erro/Crítico */
--danger-600: #c53030;

--info-50: #ebf8ff;
--info-500: #3182ce;     /* Informação */
--info-600: #2b6cb0;
```

---

## 🔤 Tipografia

### Fonte
- **Principal:** Inter (Google Fonts)
- **Monospace:** JetBrains Mono (códigos, valores)

### Escala
| Elemento | Tamanho | Peso | Altura | Cor |
|----------|---------|------|--------|-----|
| H1 | 32px | 700 | 1.2 | gray-900 |
| H2 | 24px | 600 | 1.3 | gray-800 |
| H3 | 20px | 600 | 1.4 | gray-800 |
| H4 | 18px | 600 | 1.4 | gray-700 |
| Body | 16px | 400 | 1.6 | gray-600 |
| Small | 14px | 400 | 1.5 | gray-500 |
| Caption | 12px | 500 | 1.4 | gray-400 |

### Uso
```
H1: Título de página (ex: "Contratos")
H2: Seção principal (ex: "Novo Contrato")
H3: Subseções (ex: "Dados do Contratante")
H4: Cards e widgets
Body: Texto geral, descrições
Small: Labels de formulário, metadata
Caption: Timestamps, badges
```

---

## 🧩 Componentes

### Botões

#### Primary Button
```
Background: --primary-500
Text: white
Border: none
Radius: 6px
Padding: 10px 20px
Font: 14px 600
Shadow: 0 1px 3px rgba(0,0,0,0.1)

Hover:
  Background: --primary-600
  Transform: translateY(-1px)
  Shadow: 0 4px 6px rgba(0,0,0,0.1)

Disabled:
  Background: --gray-300
  Cursor: not-allowed
```

#### Secondary Button
```
Background: white
Border: 1px solid --gray-300
Text: --gray-700
Radius: 6px

Hover:
  Background: --gray-50
  Border-color: --gray-400
```

#### Danger Button
```
Background: --danger-500
Text: white

Hover:
  Background: --danger-600
```

### Inputs

#### Text Input
```
Height: 40px
Background: white
Border: 1px solid --gray-300
Radius: 6px
Padding: 0 12px
Font: 16px

Focus:
  Border-color: --primary-500
  Ring: 0 0 0 3px --primary-100

Error:
  Border-color: --danger-500
  Ring: 0 0 0 3px --danger-50
```

#### Label
```
Font: 14px 500
Color: --gray-700
Margin-bottom: 6px
```

#### Helper Text
```
Font: 12px
Color: --gray-500
Margin-top: 4px
```

### Cards

```
Background: white
Radius: 8px
Shadow: 0 1px 3px rgba(0,0,0,0.08)
Padding: 24px
Border: 1px solid --gray-200

Hover (clickable):
  Shadow: 0 4px 6px rgba(0,0,0,0.1)
  Transform: translateY(-2px)
```

### Tabelas

```
Header:
  Background: --gray-100
  Font: 12px 600 uppercase
  Color: --gray-600
  Padding: 12px 16px

Row:
  Border-bottom: 1px solid --gray-200
  Padding: 16px
  
  Hover:
    Background: --gray-50

Zebra (opcional):
  Odd rows: --gray-50
```

### Badges

```
Default:
  Background: --gray-100
  Color: --gray-700
  Radius: 9999px
  Padding: 4px 12px
  Font: 12px 500

Success: bg-success-50 text-success-600
Warning: bg-warning-50 text-warning-600
Danger: bg-danger-50 text-danger-600
Info: bg-info-50 text-info-600
```

---

## 📐 Layout

### Estrutura de Página
```
┌─────────────────────────────────────────────────────────┐
│  [Logo]  FC Soluções Financeiras      [User] ▼          │ ← Header (64px)
├────────┬────────────────────────────────────────────────┤
│        │                                                │
│  [📄]  │              CONTEÚDO PRINCIPAL                │
│ Contratos                                               │
│        │         max-width: 1400px                      │
│  [👥]  │         padding: 24px                          │
│Clientes│                                                │
│        │                                                │
│  [📅]  │                                                │
│ Agenda │                                                │
│        │                                                │
│  [💬]  │                                                │
│   WA   │                                                │
│        │                                                │
└────────┴────────────────────────────────────────────────┘
  ↑
  Sidebar (280px)
  Background: --primary-900
```

### Breakpoints
```
Mobile: < 640px
Tablet: 640px - 1024px
Desktop: 1024px - 1400px
Wide: > 1400px
```

### Grid
```css
/* Container */
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Grid de cards */
.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
}

/* Colunas comuns */
.col-3 { grid-column: span 3; }  /* 4 por linha */
.col-4 { grid-column: span 4; }  /* 3 por linha */
.col-6 { grid-column: span 6; }  /* 2 por linha */
.col-12 { grid-column: span 12; } /* 1 por linha */
```

---

## 🎭 Ícones

### Biblioteca
- **Lucide React** (ícones consistentes)

### Uso Comum
| Contexto | Ícone |
|----------|-------|
| Contratos | FileText |
| Clientes | Users |
| Agenda | Calendar |
| WhatsApp | MessageCircle |
| Adicionar | Plus |
| Editar | Pencil |
| Excluir | Trash2 |
| Salvar | Save |
| Buscar | Search |
| Filtro | Filter |
| Download | Download |
| Enviar | Send |
| Sucesso | CheckCircle |
| Erro | XCircle |
| Alerta | AlertTriangle |
| Info | Info |

---

## 🌙 Modo Escuro (Futuro)

```css
/* Toggle via class no html */
.dark {
  --bg-primary: --gray-900;
  --bg-card: --gray-800;
  --text-primary: --gray-100;
  --text-secondary: --gray-400;
  --border: --gray-700;
}
```

**[DECISÃO]** Modo escuro fora do MVP. Implementar na fase de polish.

---

## ♿ Acessibilidade

### Requisitos
- Contraste mínimo 4.5:1 para texto
- Foco visível em todos elementos interativos
- Labels associados a inputs
- Alt text em imagens
- Keyboard navigation funcional

### Foco
```css
:focus-visible {
  outline: 2px solid --primary-500;
  outline-offset: 2px;
}
```

---

## 📝 Exemplo de Aplicação

### Página de Contratos
```
┌─────────────────────────────────────────────────────────┐
│ CONTRATOS                              [+ Novo] [🔍]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌───────────────────────────────────────────────────┐  │
│ │ [Todos] [Rascunho] [Finalizado] [Enviado] ▼ [📅] │  │
│ └───────────────────────────────────────────────────┘  │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐│
│ │ Número    │ Cliente        │ Valor      │ Status   ││
│ ├───────────┼────────────────┼────────────┼──────────┤│
│ │CNT-0001   │ João Silva     │ R$ 1.500,50│ 🟡 Rasc..││
│ │CNT-0002   │ Maria Santos   │ R$ 3.200,00│ 🟢 Final.││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ [1] [2] [3] ... [10]                    Mostrando 1-10 │
└─────────────────────────────────────────────────────────┘
```

### Formulário de Contrato
```
┌─────────────────────────────────────────────────────────┐
│ NOVO CONTRATO - BACEN                                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌──────────────┐ ┌──────────────┐                       │
│ │ Tipo *       │ │ Número       │                       │
│ │ [Bacem ▼]    │ │ CNT-2026-001 │                       │
│ └──────────────┘ └──────────────┘                       │
│                                                         │
│ ──── DADOS DO CONTRATANTE ─────────────────────────────│
│                                                         │
│ ┌────────────────────────────────────────┐              │
│ │ Nome Completo *                        │              │
│ │ [João da Silva                       ] │              │
│ └────────────────────────────────────────┘              │
│                                                         │
│ ┌──────────────────┐ ┌──────────────────┐              │
│ │ CPF/CNPJ *       │ │ E-mail *         │              │
│ │ [000.000.000-00] │ │ [joao@email.com] │              │
│ └──────────────────┘ └──────────────────┘              │
│                                                         │
│ ──── VALORES ──────────────────────────────────────────│
│                                                         │
│ ┌──────────────────┐ ┌──────────────────────────────┐  │
│ │ Valor Total *    │ │ Valor por Extenso (auto)     │  │
│ │ [R$ 1.500,50   ] │ │ mil quinhentos reais e cinq..│  │
│ └──────────────────┘ └──────────────────────────────┘  │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐│
│ │ PREVIEW DO CONTRATO                                 ││
│ │ ┌─────────────────────────────────────────────────┐ ││
│ │ │ FC Soluções Financeiras                         │ ││
│ │ │                                                 │ ││
│ │ │ CONTRATO DE PRESTAÇÃO DE SERVIÇOS              │ ││
│ │ │ ...                                             │ ││
│ │ └─────────────────────────────────────────────────┘ ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│           [Cancelar]    [💾 Salvar Rascunho] [✓ Finalizar]│
└─────────────────────────────────────────────────────────┘
```

---

*Documento atualizado em: 2026-02-03*
