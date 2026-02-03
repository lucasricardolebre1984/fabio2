# DECISIONS - Decisões Arquiteturais

## Data: 2026-02-03
## Projeto: FC Soluções Financeiras SaaS

---

## DECISÃO-001: Sistema de Contratos Dinâmicos com Templates

### Contexto
O sistema precisa suportar múltiplos tipos de contratos pré-definidos (Bacen, Serasa, etc.) com layout institucional fixo, mas campos variáveis que são preenchidos dinamicamente.

### Requisitos do Negócio
1. **Menu Contratos**: Exibir cards/tiles dos tipos de contratos disponíveis
2. **Seleção**: Ao clicar em um tipo (ex: Bacen), abrir o contrato no layout institucional
3. **Preenchimento Dinâmico**:
   - Campos entre `[COLCHETES]` = input do usuário
   - Campos entre `(PARÊNTESES)` = calculados automaticamente (extenso)
4. **Preview em Tempo Real**: Enquanto digita, o contrato atualiza os valores
5. **Salvamento**: Salva o contrato e cadastra o cliente automaticamente
6. **Menu Clientes**: Mostra histórico de contratos do cliente

### Arquitetura Proposta

#### Estrutura de Templates
```
contratos/templates/
├── bacen.json              # Template Bacen
├── serasa.json             # Template Serasa (futuro)
├── protesto.json           # Template Protesto (futuro)
└── _layout-institutional/  # Componentes de layout reusáveis
```

#### Formato do Template (JSON)
```json
{
  "id": "bacen",
  "nome": "Contrato Bacen - Remoção SCR",
  "categoria": "Bacen",
  "descricao": "Remoção de apontamentos no Sistema de Informações de Crédito",
  "layout": "institucional",  // Referencia o layout base
  "campos": [
    {
      "nome": "contratante_nome",
      "label": "Nome Completo",
      "tipo": "texto",
      "placeholder": "João da Silva",
      "secao": "dados_contratante",
      "obrigatorio": true
    },
    {
      "nome": "valor_total",
      "label": "Valor Total",
      "tipo": "moeda",
      "secao": "valores",
      "obrigatorio": true,
      "calcula_extenso": "valor_total_extenso"
    }
  ],
  "clausulas": [
    {
      "numero": "PRIMEIRA",
      "titulo": "DO OBJETO",
      "conteudo": "O presente contrato tem como objeto...",
      "variaveis": []  // Se houver variáveis específicas na cláusula
    }
  ],
  "preview_config": {
    "orientacao": "portrait",  // portrait | landscape
    "margens": {"topo": 30, "direita": 25, "fundo": 30, "esquerda": 25},
    "fonte_principal": "Times New Roman",
    "tamanho_fonte": 12,
    "cor_fonte": "#000000"
  }
}
```

#### Fluxo de Uso
```
┌─────────────────────────────────────────────────────────────────┐
│  MENU CONTRATOS                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│  │  BACEN   │  │ SERASA   │  │ PROTESTO │  ...                  │
│  │ [Imagem] │  │ [Imagem] │  │ [Imagem] │                       │
│  │ Clique   │  │ Clique   │  │ Clique   │                       │
│  └──────────┘  └──────────┘  └──────────┘                       │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  EDITOR DE CONTRATO                                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [CABEÇALHO INSTITUCIONAL COM LOGO]                       │  │
│  │                                                           │  │
│  │  DADOS DO CONTRATANTE:                                   │  │
│  │  Nome: [____________________]                           │  │
│  │  CPF:   [____________________]                           │  │
│  │                                                           │  │
│  │  VALORES:                                                │  │
│  │  Total: R$ [________] (calcula extenso automaticamente)  │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  PREVIEW DO CONTRATO (Atualiza em tempo real)            │  │
│  │                                                           │  │
│  │  CONTRATO DE PRESTAÇÃO DE SERVIÇOS                       │  │
│  │                                                           │  │
│  │  CONTRATANTE: João da Silva                              │  │
│  │  CPF: 123.456.789-00                                     │  │
│  │                                                           │  │
│  │  CLÁUSULA PRIMEIRA...                                    │  │
│  │  Valor: R$ 1.000,00 (um mil reais)                       │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [SALVAR CONTRATO]  [GERAR PDF]  [CANCELAR]                     │
└─────────────────────────────────────────────────────────────────┘
```

#### Componentes Frontend

**1. Menu de Contratos (`/contratos`)**
- Grid de cards com os templates disponíveis
- Cada card: imagem ilustrativa, nome, descrição breve
- Ao clicar: navega para `/contratos/novo?template=bacen`

**2. Editor de Contrato (`/contratos/novo?template=bacen`)**
- **Painel Esquerdo**: Formulário dinâmico gerado do template
- **Painel Direito**: Preview do contrato atualizando em tempo real
- Campos calculados (extenso) atualizam automaticamente

**3. Preview do Contrato**
- Renderiza o HTML/CSS do layout institucional
- Substitui `[VARIAVEIS]` pelos valores digitados
- Calcula `(extensos)` automaticamente

#### Campos Dinâmicos

**Sintaxe no Template:**
- `[NOME_CAMPO]` = Input do usuário
- `(NOME_CAMPO_EXTENSO)` = Valor calculado automaticamente

**Exemplo:**
```
Pelos serviços prestados, o(a) CONTRATANTE pagará à CONTRATADA 
o valor total de R$ [valor_total] (valor_total_extenso), a ser pago 
da seguinte forma:

Entrada: R$ [valor_entrada] (valor_entrada_extenso)
Parcelas: [qtd_parcelas] parcelas de R$ [valor_parcela] (valor_parcela_extenso)
```

**Processamento:**
```javascript
// Pseudo-código
function processarTemplate(template, valores) {
  let html = template.html_base;
  
  // Substitui inputs
  for (const [campo, valor] of Object.entries(valores)) {
    html = html.replace(`[${campo}]`, valor);
  }
  
  // Calcula extensos
  for (const campo of template.campos_com_extenso) {
    const valor = valores[campo.nome];
    const extenso = numeroPorExtenso(valor);
    html = html.replace(`(${campo.nome}_extenso)`, extenso);
  }
  
  return html;
}
```

#### Backend - Serviço de Templates

**Endpoints:**
```
GET  /api/v1/contratos/templates              # Lista templates disponíveis
GET  /api/v1/contratos/templates/{id}         # Detalhes do template
POST /api/v1/contratos                        # Cria contrato a partir do template
```

**Serviço Extenso:**
- `valorPorExtenso(1500.50)` → "mil quinhentos reais e cinquenta centavos"
- `numeroPorExtenso(12)` → "doze"

### Vantagens
1. **Reusabilidade**: Mesmo layout para vários contratos
2. **Manutenibilidade**: Mudanças no layout refletem em todos
3. **Escalabilidade**: Fácil adicionar novos tipos de contrato
4. **UX**: Preview em tempo real reduz erros

### Próximos Passos
1. Criar template JSON do Bacen com todas as cláusulas
2. Implementar componente `ContratoPreview` no frontend
3. Criar página `MenuContratos` com seleção de templates
4. Implementar serviço de cálculo de extensos

### Alternativas Consideradas

| Alternativa | Prós | Contras |
|-------------|------|---------|
| **A: PDF editável** | Formato final imediato | Difícil preview dinâmico, UX ruim |
| **B: Word DOCX** | Familiar para usuários | Complexo editar no browser |
| **C: HTML Dinâmico (Escolhida)** | Preview em tempo real, fácil gerar PDF | Requer desenvolvimento inicial |

**Decisão:** Implementar solução C (HTML Dinâmico) por melhor UX e facilidade de manutenção.

---

*Documentado em: 2026-02-03*  
*Autor: Lucas Lebre (Automania-AI)*  
*Aprovado por: Fábio (FC Soluções Financeiras)*
