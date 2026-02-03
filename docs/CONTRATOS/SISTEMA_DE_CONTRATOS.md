# SISTEMA DE CONTRATOS - DOCUMENTAÇÃO TÉCNICA INSTITUCIONAL

> **FC Soluções Financeiras SaaS**  
> **Versão:** 1.0.0  
> **Data:** 2026-02-03  
> **Autor:** DEV DEUS (Automania-AI)  
> **Status:** Produção

---

## 📋 SUMÁRIO EXECUTIVO

Este documento estabelece o **padrão técnico institucional** para criação, manutenção e expansão do sistema de contratos da FC Soluções Financeiras. É a **fonte única de verdade** para qualquer agente de IA ou desenvolvedor que precise:

- Entender o funcionamento do sistema atual
- Criar novos templates de contrato
- Inserir novas cláusulas
- Replicar o layout para novos módulos

---

## 🎯 ARQUITETURA DO SISTEMA

### 1.1 Visão Geral

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SISTEMA DE CONTRATOS FC                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Bacen     │    │   Serasa    │    │  Protesto   │    │   Novo      │  │
│  │  (Ativo)    │    │  (Futuro)   │    │  (Futuro)   │    │  (Template) │  │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘  │
│         │                  │                  │                  │         │
│         └──────────────────┴──────────────────┴──────────────────┘         │
│                            │                                                │
│                            ▼                                                │
│              ┌─────────────────────────────┐                               │
│              │     LAYOUT BASE             │                               │
│              │  (Componentes Reutilizáveis)│                               │
│              │                             │                               │
│              │  • Cabeçalho Institucional  │                               │
│              │  • Seção CONTRATANTE        │                               │
│              │  • Seção CONTRATADA         │                               │
│              │  • Cláusulas Dinâmicas      │                               │
│              │  • Assinaturas              │                               │
│              │  • Rodapé                   │                               │
│              └─────────────────────────────┘                               │
│                            │                                                │
│                            ▼                                                │
│              ┌─────────────────────────────┐                               │
│              │     MOTOR DE RENDERIZAÇÃO   │                               │
│              │                             │                               │
│              │  • Preview em Tempo Real    │                               │
│              │  • Geração de PDF           │                               │
│              │  • Validação de Dados       │                               │
│              │  • Cálculo de Extenso       │                               │
│              └─────────────────────────────┘                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Princípios Fundamentais

| Princípio | Descrição | Aplicação |
|-----------|-----------|-----------|
| **DRY** (Don't Repeat) | Não repetir código | Layout base reutilizável para todos os contratos |
| **Separação de Responsabilidades** | Cada arquivo tem uma função | Templates JSON = dados; Layout = apresentação |
| **Configuração sobre Código** | Mudanças via JSON, não código | Novas cláusulas = editar JSON |
| **Consistência Visual** | Mesmo layout institucional | Todos os contratos seguem padrão FC |

---

## 🏗️ ESTRUTURA DE DIRETÓRIOS

```
contratos/
├── templates/                    # 📁 Templates JSON dos contratos
│   ├── bacen.json               # Contrato Bacen (SCR)
│   ├── serasa.json              # Contrato Serasa (futuro)
│   ├── protesto.json            # Contrato Protesto (futuro)
│   └── _schema.json             # Schema de validação dos templates
│
└── docs/                        # 📁 Documentação específica
    └── SISTEMA_DE_CONTRATOS.md  # 📄 ESTE DOCUMENTO

frontend/src/app/(dashboard)/contratos/
├── [id]/
│   └── page.tsx                 # 📄 Visualização do contrato (LAYOUT BASE)
├── [id]/editar/
│   └── page.tsx                 # 📄 Edição do contrato
├── novo/
│   └── page.tsx                 # 📄 Criação de novo contrato
└── lista/
    └── page.tsx                 # 📄 Listagem de contratos

frontend/src/lib/
└── pdf.ts                       # 📄 Geração de PDF (LAYOUT BASE)
```

---

## 🎨 LAYOUT BASE INSTITUCIONAL

### 3.1 Especificação Visual

O **Layout Base** é o coração do sistema. Todo contrato deve seguir EXATAMENTE esta estrutura:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ███████████████████████████████████████████████████████████████████████████ │
│ █  [LOGO]  F C Soluções Financeiras                                      █ │
│ ███████████████████████████████████████████████████████████████████████████ │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│              CONTRATO DE PRESTAÇÃO DE SERVIÇOS                              │
│                   [NOME DO SERVIÇO - ex: Bacen - Remoção SCR]               │
│                                                                             │
│              Nº: CNT-2026-XXXX    Data: DD/MM/AAAA                          │
│                                                                             │
├────────────────────────────────┬────────────────────────────────────────────┤
│        CONTRATANTE             │           CONTRATADA                       │
│                                │                                            │
│  Nome: [NOME DO CLIENTE]       │  Razão Social: FC SERVIÇOS E SOLUÇÕES     │
│  CPF/CNPJ: [DOCUMENTO]         │  ADMINISTRATIVAS LTDA                      │
│  E-mail: [EMAIL]               │  CNPJ: 57.815.628/0001-62                 │
│  Contato: [TELEFONE]           │  E-mail: contato@fcsolucoesfinanceiras.com│
│  Endereço: [ENDERECO]          │  Contato: (16) 99301-7396                 │
│                                │  Endereço: Rua Maria das Graças...        │
├────────────────────────────────┴────────────────────────────────────────────┤
│                                                                             │
│ CLÁUSULA PRIMEIRA - DO OBJETO                                               │
│ [Texto específico do contrato...]                                          │
│                                                                             │
│ CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES DA CONTRATADA                            │
│ [Texto específico do contrato...]                                          │
│                                                                             │
│ [... demais cláusulas ...]                                                 │
│                                                                             │
├────────────────────────────────┬────────────────────────────────────────────┤
│                                │                                            │
│     ______________________     │      ______________________               │
│     [NOME DO CONTRATANTE]      │      FC SERVIÇOS E SOLUÇÕES               │
│     CPF: [DOCUMENTO]           │      ADMINISTRATIVAS LTDA                 │
│     CONTRATANTE                │      CNPJ: 57.815.628/0001-62             │
│                                │      CONTRATADA                            │
│                                │                                            │
├────────────────────────────────┴────────────────────────────────────────────┤
│                                                                             │
│ Testemunhas:                                                                │
│ 1. _____________________________________                                    │
│    Nome:                    CPF:                                           │
│                                                                             │
│ 2. _____________________________________                                    │
│    Nome:                    CPF:                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Componentes do Layout Base

#### A. Cabeçalho Institucional (INALTERÁVEL)

```tsx
// Local: frontend/src/app/(dashboard)/contratos/[id]/page.tsx

<div className="bg-[#1e3a5f] text-white py-4 px-6 mb-6 -mx-8 -mt-8">
  <div className="flex items-center gap-4">
    {/* Logo SVG - NUNCA ALTERAR */}
    <div className="flex-shrink-0">
      <svg width="60" height="60" viewBox="0 0 100 100">
        {/* Balança com FC */}
        <circle cx="50" cy="50" r="45" stroke="white" strokeWidth="3" fill="none"/>
        <line x1="50" y1="15" x2="50" y2="85" stroke="white" strokeWidth="3"/>
        {/* ... resto do SVG ... */}
        <text x="42" y="58" fill="white" fontSize="24" fontWeight="bold">F</text>
        <text x="54" y="58" fill="white" fontSize="24" fontWeight="bold">C</text>
      </svg>
    </div>
    <div className="flex-1">
      <h1 className="text-2xl font-bold tracking-wide">
        F C Soluções Financeiras
      </h1>
    </div>
  </div>
</div>
```

**REGRA DE OURO:** O cabeçalho é **INALTERÁVEL** entre contratos. A única coisa que muda é o subtítulo do tipo de serviço.

#### B. Seção CONTRATANTE (Dinâmica)

Campos que vêm do formulário:
- `contratante_nome` (texto)
- `contratante_documento` (CPF/CNPJ formatado)
- `contratante_email` (email)
- `contratante_telefone` (opcional)
- `contratante_endereco` (texto)

#### C. Seção CONTRATADA (Fixa)

**SEMPRE IGUAL em todos os contratos:**
```
Razão Social: FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA
CNPJ: 57.815.628/0001-62
E-mail: contato@fcsolucoesfinanceiras.com
Contato: (16) 99301-7396
Endereço: Rua Maria das Graças de Negreiros Bonilha, nº 30, sala 3, 
          Jardim Nova Aliança Sul, Ribeirão Preto/SP, CEP 14022-100
```

#### D. Cláusulas (Variáveis por Template)

**Estrutura padrão:**
```
CLÁUSULA [NUMERO] - [TÍTULO EM MAIÚSCULAS]
[Texto da cláusula com variáveis entre colchetes]
```

**Números por extenso:**
- PRIMEIRA, SEGUNDA, TERCEIRA, QUARTA, QUINTA
- SEXTA, SÉTIMA, OITAVA, NONA, DÉCIMA
- DÉCIMA PRIMEIRA, DÉCIMA SEGUNDA...

---

## 📄 SISTEMA DE TEMPLATES JSON

### 4.1 Estrutura do Arquivo de Template

Cada contrato é definido por um arquivo JSON no diretório `contratos/templates/`:

```json
{
  "id": "bacen",
  "nome": "Contrato Bacen - Remoção SCR",
  "categoria": "Bacen",
  "descricao": "Prestação de serviços para remoção de apontamentos no Sistema de Informações de Crédito",
  "versao": "1.0.0",
  "data_criacao": "2026-02-03",
  
  "campos_formulario": [
    {
      "nome": "contratante_nome",
      "label": "Nome Completo",
      "tipo": "texto",
      "placeholder": "Digite o nome completo",
      "obrigatorio": true,
      "secao": "dados_contratante"
    },
    {
      "nome": "contratante_documento",
      "label": "CPF/CNPJ",
      "tipo": "documento",
      "placeholder": "000.000.000-00",
      "obrigatorio": true,
      "secao": "dados_contratante",
      "validacao": "cpf_cnpj"
    },
    {
      "nome": "valor_total",
      "label": "Valor Total do Serviço",
      "tipo": "moeda",
      "placeholder": "R$ 0,00",
      "obrigatorio": true,
      "secao": "valores",
      "calcula_extenso": "valor_total_extenso"
    }
  ],
  
  "clausulas": [
    {
      "numero": "PRIMEIRA",
      "titulo": "DO OBJETO",
      "conteudo": "O presente contrato tem como objeto a prestação de serviços de consultoria e intermediação administrativa pela CONTRATADA em favor do(a) CONTRATANTE, visando a adoção de procedimentos administrativos para a regularização de apontamentos de prejuízo registrados no Sistema de Informações de Crédito (SCR) do Banco Central do Brasil."
    },
    {
      "numero": "SEGUNDA",
      "titulo": "DAS OBRIGAÇÕES DA CONTRATADA",
      "conteudo": "A CONTRATADA se compromete a: a) Realizar uma análise detalhada da situação do(a) CONTRATANTE junto ao SCR; b) Elaborar e protocolar os requerimentos administrativos necessários junto às instituições financeiras pertinentes; c) Acompanhar o andamento dos procedimentos..."
    }
  ],
  
  "variaveis_disponiveis": [
    "{contratante_nome}",
    "{contratante_documento}",
    "{contratante_email}",
    "{contratante_endereco}",
    "{valor_total}",
    "{valor_total_extenso}",
    "{valor_entrada}",
    "{valor_entrada_extenso}",
    "{qtd_parcelas}",
    "{valor_parcela}",
    "{prazo_1}",
    "{prazo_2}",
    "{data_assinatura}",
    "{local_assinatura}"
  ]
}
```

### 4.2 Tipos de Campos Suportados

| Tipo | Descrição | Validação | Exemplo |
|------|-----------|-----------|---------|
| `texto` | Texto livre | Mínimo 3 caracteres | Nomes, endereços |
| `documento` | CPF ou CNPJ | CPF: 11 dígitos<br>CNPJ: 14 dígitos | 33429258847 |
| `email` | Endereço de email | Regex de email | exemplo@email.com |
| `moeda` | Valor monetário | > 0 | R$ 2.500,00 |
| `inteiro` | Número inteiro | >= 0 | 12 parcelas |
| `data` | Data | Formato DD/MM/AAAA | 03/02/2026 |
| `telefone` | Telefone | Mínimo 10 dígitos | (16) 99301-7396 |

### 4.3 Variáveis Calculadas Automaticamente

Estas variáveis são **geradas automaticamente** pelo sistema:

| Variável | Origem | Exemplo |
|----------|--------|---------|
| `numero` | Geração automática | CNT-2026-0004 |
| `valor_total_extenso` | Cálculo do backend | "dois mil e quinhentos reais" |
| `valor_entrada_extenso` | Cálculo do backend | "quinhentos reais" |
| `valor_parcela_extenso` | Cálculo do backend | "mil reais" |
| `qtd_parcelas_extenso` | Cálculo do backend | "duas" |
| `prazo_1_extenso` | Cálculo do backend | "trinta" |
| `prazo_2_extenso` | Cálculo do backend | "sessenta" |

---

## 🔄 FLUXO COMPLETO DE FUNCIONAMENTO

### 5.1 Fluxo de Criação de Contrato

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUXO: CRIAÇÃO DE NOVO CONTRATO                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  PASSO 1 │────►│  PASSO 2 │────►│  PASSO 3 │────►│  PASSO 4 │
│          │     │          │     │          │     │          │
│  USUÁRIO │     │ FRONTEND │     │ BACKEND  │     │  BANCO   │
│  SELECIONA    │  VALIDA  │     │  SALVA   │     │  ARMAZENA│
│  TEMPLATE     │  DADOS   │     │          │     │          │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │                │                │                │
     ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  1. USUÁRIO clica em "Bacen" no menu                                        │
│     └──► Sistema carrega template/bacen.json                               │
│                                                                             │
│  2. FRONTEND renderiza formulário dinâmico baseado nos campos do JSON      │
│     └──► Exibe: Nome, CPF, Email, Valor Total, etc.                        │
│                                                                             │
│  3. USUÁRIO preenche formulário                                             │
│     └──► Frontend valida em tempo real (máscaras, obrigatórios)            │
│                                                                             │
│  4. USUÁRIO clica "Criar Contrato"                                          │
│     └──► Frontend envia POST /api/v1/contratos/                            │
│                                                                             │
│  5. BACKEND recebe dados                                                    │
│     ├──► Valida dados com Pydantic                                         │
│     ├──► Calcula valores por extenso                                       │
│     ├──► Gera número do contrato (CNT-YYYY-NNNN)                           │
│     └──► Verifica/cria cliente                                             │
│                                                                             │
│  6. BACKEND salva no PostgreSQL                                             │
│     └──► INSERT na tabela contratos                                        │
│                                                                             │
│  7. BACKEND retorna contrato criado                                         │
│     └──► Frontend redireciona para /contratos/[id]                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Fluxo de Visualização/PDF

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUXO: VISUALIZAÇÃO E PDF                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  USUÁRIO │────►│  FRONTEND│────►│   DADOS  │────►│   PDF    │
│  CLICA   │     │  BUSCA   │     │  SÃO     │     │  É       │
│  "VER"   │     │  CONTRATO│     │  APLICADOS     │  GERADO  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                │                │
     ▼                ▼                ▼                ▼

1. USUÁRIO clica no olho (👁️) na lista de contratos
   └──► Navega para /contratos/[id]

2. FRONTEND faz GET /api/v1/contratos/{id}
   └──► Recebe objeto completo do contrato

3. FRONTEND renderiza LAYOUT BASE com os dados
   ├──► Cabeçalho institucional (fixo)
   ├──► Dados do contratante (do banco)
   ├──► Dados da contratada (fixo)
   ├──► Cláusulas específicas do template
   └──► Assinaturas (do banco + fixo)

4. USUÁRIO clica "Visualizar PDF" ou "Download"
   └──► Chama generateContractPDF(contrato)

5. SISTEMA abre nova janela com HTML formatado
   └──► Chama window.print() automaticamente

6. USUÁRIO escolhe "Salvar como PDF"
   └──► PDF gerado com layout institucional
```

---

## 📝 GUIA: COMO ADICIONAR NOVAS CLÁUSULAS

### 6.1 Processo Passo a Passo

#### PASSO 1: Identificar o Template

```bash
# Localize o arquivo do template
ls contratos/templates/
# bacen.json, serasa.json, etc.
```

#### PASSO 2: Editar o Arquivo JSON

Abra o template e localize a seção `"clausulas"`:

```json
{
  "clausulas": [
    {
      "numero": "PRIMEIRA",
      "titulo": "DO OBJETO",
      "conteudo": "..."
    },
    // 👉 ADICIONAR NOVA CLÁUSULA AQUI
    {
      "numero": "DÉCIMA PRIMEIRA",
      "titulo": "DA RESCIÇÃO",
      "conteudo": "Em caso de rescisão contratual por qualquer motivo, o(a) CONTRATANTE deverá pagar à CONTRATADA os serviços já prestados até a data da rescisão."
    }
  ]
}
```

#### PASSO 3: Usar Variáveis (se necessário)

Se a cláusula precisa de dados dinâmicos:

```json
{
  "numero": "DÉCIMA SEGUNDA",
  "titulo": "DO PAGAMENTO",
  "conteudo": "O valor total de {valor_total} ({valor_total_extenso}) deverá ser pago conforme acordado entre as partes."
}
```

#### PASSO 4: Validação

Após editar, verifique:
1. JSON está válido (use um validador online)
2. Número da cláusula está correto
3. Título está em MAIÚSCULAS
4. Variáveis estão entre chaves `{variavel}`

---

## 🆕 GUIA: COMO CRIAR NOVO MÓDULO DE CONTRATO

### 7.1 Checklist de Criação

Quando receber um novo contrato em Word, siga EXATAMENTE este checklist:

#### ✅ FASE 1: ANÁLISE DO DOCUMENTO WORD

- [ ] 1.1 Identificar o **nome do serviço** (ex: "Serasa", "Protesto", "Cheques")
- [ ] 1.2 Contar quantas **cláusulas** existem
- [ ] 1.3 Identificar **campos do formulário** necessários
- [ ] 1.4 Verificar se usa os **mesmos campos financeiros** (valor, entrada, parcelas)
- [ ] 1.5 Identificar **dados específicos** do contrato

#### ✅ FASE 2: CRIAÇÃO DO ARQUIVO JSON

```bash
# 1. Copie o template base (bacen.json)
cp contratos/templates/bacen.json contratos/templates/novo_servico.json

# 2. Edite o novo arquivo
# Altere: id, nome, categoria, descricao
# Mantenha: estrutura de campos (se iguais)
# Adicione: novos campos específicos
# Edite: cláusulas conforme Word
```

#### ✅ FASE 3: ESTRUTURA DO JSON

```json
{
  "id": "serasa",                    // 👉 ALTERAR: identificador único
  "nome": "Contrato Serasa",         // 👉 ALTERAR: nome exibido
  "categoria": "Serasa",             // 👉 ALTERAR: categoria
  "descricao": "Remoção de...",      // 👉 ALTERAR: descrição
  
  "campos_formulario": [
    // 👉 MANTER se iguais ao Bacen
    // 👉 ADICIONAR campos específicos do novo serviço
    {
      "nome": "numero_processo_serasa",
      "label": "Número do Processo Serasa",
      "tipo": "texto",
      "obrigatorio": true,
      "secao": "dados_especificos"
    }
  ],
  
  "clausulas": [
    // 👉 ALTERAR: copiar texto do Word
    {
      "numero": "PRIMEIRA",
      "titulo": "DO OBJETO",
      "conteudo": "[Texto do Word adaptado]"
    }
    // ... demais cláusulas
  ]
}
```

#### ✅ FASE 4: TESTES

- [ ] 4.1 Sistema reconhece o novo template?
- [ ] 4.2 Formulário renderiza corretamente?
- [ ] 4.3 Validações funcionam?
- [ ] 4.4 PDF gerado com layout correto?
- [ ] 4.5 Cláusulas aparecem na ordem certa?

---

## 🔧 EXEMPLO PRÁTICO: CRIANDO CONTRATO SERASA

### Cenário
Recebemos um Word com contrato Serasa com 8 cláusulas específicas.

### Passo 1: Criar o JSON

```json
{
  "id": "serasa",
  "nome": "Contrato Serasa - Regularização de Débitos",
  "categoria": "Serasa",
  "descricao": "Prestação de serviços para regularização e negociação de débitos cadastrados na Serasa Experian",
  "versao": "1.0.0",
  "data_criacao": "2026-02-03",
  
  "campos_formulario": [
    {
      "nome": "contratante_nome",
      "label": "Nome Completo",
      "tipo": "texto",
      "obrigatorio": true,
      "secao": "dados_contratante"
    },
    {
      "nome": "contratante_documento",
      "label": "CPF/CNPJ",
      "tipo": "documento",
      "obrigatorio": true,
      "secao": "dados_contratante"
    },
    {
      "nome": "numero_cadastro_serasa",
      "label": "Número de Cadastro Serasa",
      "tipo": "texto",
      "obrigatorio": false,
      "secao": "dados_especificos"
    },
    {
      "nome": "valor_total",
      "label": "Valor Total",
      "tipo": "moeda",
      "obrigatorio": true,
      "secao": "valores",
      "calcula_extenso": "valor_total_extenso"
    },
    {
      "nome": "valor_entrada",
      "label": "Valor de Entrada",
      "tipo": "moeda",
      "obrigatorio": true,
      "secao": "valores",
      "calcula_extenso": "valor_entrada_extenso"
    },
    {
      "nome": "qtd_parcelas",
      "label": "Quantidade de Parcelas",
      "tipo": "inteiro",
      "obrigatorio": true,
      "secao": "valores"
    }
  ],
  
  "clausulas": [
    {
      "numero": "PRIMEIRA",
      "titulo": "DO OBJETO",
      "conteudo": "O presente contrato tem como objeto a prestação de serviços de consultoria e intermediação para regularização de débitos cadastrados na Serasa Experian em nome do(a) CONTRATANTE."
    },
    {
      "numero": "SEGUNDA",
      "titulo": "DAS OBRIGAÇÕES DA CONTRATADA",
      "conteudo": "A CONTRATADA se obriga a: a) Analisar o cadastro do(a) CONTRATANTE junto à Serasa Experian; b) Negociar com credores os termos de pagamento; c) Acompanhar o processo até a baixa do apontamento."
    },
    {
      "numero": "TERCEIRA",
      "titulo": "DO VALOR E FORMA DE PAGAMENTO",
      "conteudo": "O(a) CONTRATANTE pagará à CONTRATADA o valor total de {valor_total} ({valor_total_extenso}), sendo {valor_entrada} ({valor_entrada_extenso}) de entrada e o restante em {qtd_parcelas} parcelas."
    }
    // ... continuar com as demais cláusulas
  ]
}
```

### Passo 2: Adicionar ao Menu

Edite o componente de menu para incluir o novo card:

```tsx
// frontend/src/app/contratos/page.tsx (ou similar)

const templates = [
  {
    id: 'bacen',
    nome: 'Bacen',
    descricao: 'Remoção SCR',
    imagem: '/images/bacen.png'
  },
  {
    id: 'serasa',  // 👉 ADICIONAR
    nome: 'Serasa',
    descricao: 'Regularização de Débitos',
    imagem: '/images/serasa.png'
  }
];
```

---

## ⚠️ REGRAS E RESTRIÇÕES

### Regras de Ouro

1. **NUNCA ALTERE o Layout Base** (cabeçalho, fonte, cores)
2. **SEMPRE mantenha a seção CONTRATADA idêntica**
3. **NUNCA remova campos obrigatórios** (nome, documento, valor)
4. **SEMPRE valide o JSON** antes de salvar
5. **NUNCA mude os IDs dos templates existentes**

### Campos Obrigatórios em Todo Contrato

```json
{
  "campos_obrigatorios": [
    "contratante_nome",
    "contratante_documento", 
    "contratante_email",
    "contratante_endereco",
    "valor_total",
    "valor_entrada",
    "qtd_parcelas"
  ]
}
```

---

## 📚 REFERÊNCIAS RÁPIDAS

### Comandos Úteis

```bash
# Ver templates existentes
ls -la contratos/templates/

# Validar JSON
cat contratos/templates/bacen.json | python -m json.tool

# Buscar texto em todos os templates
grep -r "OBJETO" contratos/templates/

# Ver últimas modificações
ls -lt contratos/templates/
```

### Arquivos-Chave

| Arquivo | Função | Quando Editar |
|---------|--------|---------------|
| `contratos/templates/*.json` | Dados dos contratos | Novo template ou cláusula |
| `frontend/src/lib/pdf.ts` | Geração de PDF | Nunca (layout base) |
| `frontend/src/app/contratos/[id]/page.tsx` | Visualização | Nunca (layout base) |

---

## 🎯 CHECKLIST FINAL

Antes de considerar um novo módulo pronto:

- [ ] Template JSON criado e válido
- [ ] Todas as cláusulas do Word foram transferidas
- [ ] Campos de formulário definidos
- [ ] Card adicionado ao menu de templates
- [ ] Teste de criação de contrato funciona
- [ ] Teste de geração de PDF funciona
- [ ] Layout visual está correto
- [ ] Valores por extenso calculam corretamente

---

## 📞 SUPORTE

**Dúvidas técnicas:** Consulte este documento primeiro  
**Problemas de implementação:** Verifique logs do backend/frontend  
**Novos requisitos:** Documente antes de implementar

---

*Documento criado em: 2026-02-03*  
*Versão: 1.0.0*  
*Status: Ativo e em uso*  
*Próxima revisão: Quando novos módulos forem adicionados*

---

**FIM DO DOCUMENTO**
