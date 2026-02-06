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
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  [SALVAR] ──► Salva contrato + cadastra cliente                │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes de Layout

#### Cabeçalho Institucional (Reutilizável)
```
┌─────────────────────────────────────────────────────────────────┐
│  [LOGO FC]  FC SOLUÇÕES FINANCEIRAS                    Tel:... │
│             CNPJ: 57.815.628/0001-62                            │
│             Endereço completo...                                │
├─────────────────────────────────────────────────────────────────┤
│              CONTRATO DE PRESTAÇÃO DE SERVIÇOS                  │
│                       Bacen - Remoção SCR                       │
└─────────────────────────────────────────────────────────────────┘
```

### Alternativas Consideradas

| Alternativa | Prós | Contras |
|-------------|------|---------|
| **A: PDF editável** | Formato final imediato | Difícil preview dinâmico, UX ruim |
| **B: Word DOCX** | Familiar para usuários | Complexo editar no browser |
| **C: HTML Dinâmico (Escolhida)** | Preview em tempo real, fácil gerar PDF | Requer desenvolvimento inicial |

**Decisão:** Implementar solução C (HTML Dinâmico) por melhor UX e facilidade de manutenção.

---

## DECISÃO-002: Geração de PDF - Browser Print vs Backend

### Contexto
Após tentativas frustradas com bibliotecas backend (WeasyPrint, Playwright), foi necessário escolher uma solução robusta para geração de PDF.

### Problemas Encontrados

| Biblioteca | Problema |
|------------|----------|
| **WeasyPrint** | Requer GTK+ no Windows - instalação complexa |
| **Playwright** | `NotImplementedError: subprocess_exec` no Windows asyncio |
| **Puppeteer** | Mesmo problema de subprocess no Windows |

### Solução Escolhida: Browser Print (Frontend)

**Arquitetura:**
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │     │  Nova Janela     │     │  PDF Gerado     │
│  (Next.js)      │────►│  (HTML Puro)     │────►│  (Browser Print)│
│                 │     │                  │     │                 │
│ generatePDF()   │     │ window.print()   │     │ Save as PDF     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

**Vantagens:**
- ✅ Funciona em qualquer sistema operacional
- ✅ Layout idêntico entre visualização e impressão
- ✅ Controle total do CSS/HTML
- ✅ Não requer instalação de dependências pesadas
- ✅ Preview imediato antes de salvar

**Desvantagens:**
- ⚠️ Requer ação do usuário para salvar
- ⚠️ Popups devem estar permitidos

**Decisão:** Implementar geração de PDF via browser print (frontend).

---

## DECISÃO-003: Layout Institucional - Cabeçalho e Tipografia

### Contexto
O cabeçalho original continha dados redundantes (CNPJ, endereço, telefone) que já apareciam na seção CONTRATADA.

### Mudanças Realizadas

#### 1. Fonte
- **Anterior:** Inter (sans-serif) - padrão Tailwind
- **Nova:** Times New Roman (serif) - fonte institucional tradicional

#### 2. Cabeçalho
- **Anterior:** Logo + dados completos da empresa (redundante)
- **Novo:** Faixa azul (#1e3a5f) com logo SVG + nome da empresa

```
ANTES:
┌──────────────────────────────────────────────────────────────┐
│  [FC]  FC SOLUÇÕES FINANCEIRAS                      Tel:...  │
│        CNPJ: 57.815.628/0001-62                              │
│        Rua Maria das Graças...                               │
│        contato@...                                           │
└──────────────────────────────────────────────────────────────┘

NOVO:
┌──────────────────────────────────────────────────────────────┐
│██████████████████████████████████████████████████████████████│
│█  [⚖️]  F C Soluções Financeiras                            █│
│██████████████████████████████████████████████████████████████│
└──────────────────────────────────────────────────────────────┘
```

### Motivação
1. **Eliminar redundância:** Dados da empresa aparecem na seção CONTRATADA
2. **Visual institucional:** Faixa azul é mais profissional
3. **Economia de espaço:** Mais espaço para o conteúdo do contrato
4. **Consistência:** Mesmo layout em visualização e PDF

### Arquivos Afetados
- `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
- `frontend/src/lib/pdf.ts`

---

*Documentado em: 2026-02-03*  
*Autor: Lucas Lebre (Automania-AI)*  
*Aprovado por: Fábio (FC Soluções Financeiras)*

---

## DECISÃO-004: Modelos Z.AI e Fallback para VIVA

### Contexto
O sistema passou a operar com IA VIVA no chat interno e no fluxo WhatsApp. Era necessário definir modelos oficiais e estabelecer fallback quando a API principal não estiver disponível.

### Opções consideradas
A. Z.AI como principal (GLM-4.7 e modelos multimodais)
B. OpenRouter como principal (modelos gratuitos)
C. Modo local com templates (sem API)

### Decisão
- **Principal:** Z.AI com os modelos oficiais
- **Fallback:** OpenRouter quando disponível
- **Fallback final:** modo local com templates

### Modelos Oficiais
- Chat: `GLM-4.7`
- Visão: `GLM-4.6V`
- Imagem: `GLM-Image`
- Áudio: `GLM-ASR-2512`
- Vídeo: `CogVideoX-3`

### Motivo
- Z.AI cobre chat e multimodal com consistência
- OpenRouter garante operação gratuita quando necessário
- Modo local evita indisponibilidade total

---

*Documentado em: 2026-02-05*

---

## DECISÃO-005: Persona simples da VIVA no prompt principal

### Contexto
O chat interno precisava reconhecer o contexto do servidor e as capacidades multimodais, sem depender de prompts longos ou específicos.

### Decisão
Adicionar uma persona simples no prompt principal da VIVA informando:
- Contexto do servidor (SaaS interno)
- Empresas (FC Soluções e RezetaBrasil)
- Capacidades (chat, imagens, visão, áudio, vídeo)

### Motivo
- Reduz alucinação sobre limitações
- Melhora a compreensão do ambiente
- Facilita uso com prompts secundários

---

*Documentado em: 2026-02-05*

---

## DECISÃO-006: Roteamento de intenção de imagem no backend

### Contexto
O chat interno precisava gerar imagens quando solicitado, sem duplicar regras no frontend.

### Decisão
Centralizar a detecção de intenção de imagem no backend (`/viva/chat`) e retornar mídia estruturada.

### Motivo
- Evita lógica duplicada no frontend
- Permite uso futuro no WhatsApp e outros canais
- Mantém governança e consistência institucional

---

*Documentado em: 2026-02-05*
