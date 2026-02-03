# Implementação - Sistema de Contratos Dinâmicos

**Data:** 2026-02-03  
**Status:** 🟡 Em Desenvolvimento

---

## ✅ O QUE FOI FEITO

### 1. Documentação Arquitetural
- ✅ `docs/DECISIONS.md` - Decisão arquitetural completa sobre o sistema de templates
- ✅ Fluxo de uso documentado
- ✅ Estrutura de templates definida

### 2. Template Bacen Completo
- ✅ `contratos/templates/bacen-v2.json` - Template com todas as cláusulas
- ✅ 13 campos dinâmicos configurados
- ✅ 11 cláusulas legais do contrato Bacen
- ✅ Configuração de layout institucional
- ✅ Campos calculados (extensos) mapeados

---

## 🟡 O QUE FALTA IMPLEMENTAR

### Frontend

**1. Menu de Seleção de Contratos (`/contratos`)**
```
┌─────────────────────────────────────────┐
│  Escolha o Tipo de Contrato             │
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │  🏦      │  │  📊      │            │
│  │  BACEN   │  │  SERASA  │            │
│  │          │  │          │            │
│  │ Remoção  │  │ Limpeza  │            │
│  │ de SCR   │  │ Nome     │            │
│  └──────────┘  └──────────┘            │
│                                         │
└─────────────────────────────────────────┘
```
- Grid de cards com templates disponíveis
- Cada card: imagem, nome, descrição
- Ao clicar: `/contratos/novo?template=bacen`

**2. Editor de Contrato com Preview (`/contratos/novo?template=bacen`)**
```
┌──────────────────────────────────────────────────────────┐
│  [Painel Esquerdo: Formulário]  │  [Painel Direito: PDF]  │
│                                 │                         │
│  DADOS DO CONTRATANTE:         │  [CABEÇALHO FC]         │
│  Nome: [________________]      │                         │
│  CPF:  [________________]      │  CONTRATANTE: João      │
│                                │  CPF: 123.456...        │
│  VALORES:                      │                         │
│  Total: R$ [________]          │  CLÁUSULA PRIMEIRA...   │
│          ↓ (digita)            │                         │
│          ↓ (atualiza)          │  Valor: R$ 1.000,00     │
│          ↓                     │  (um mil reais)         │
│  Preview: R$ 1.000,00          │                         │
│  (um mil reais)                │  [SALVAR] [PDF]         │
│                                │                         │
└──────────────────────────────────────────────────────────┘
```
- Painel dividido: formulário (esq) + preview (dir)
- Campos dinâmicos atualizam em tempo real
- Cálculo automático de extensos
- Botões: Salvar, Gerar PDF, Cancelar

**3. Componentes Necessários**
- `ContratoPreview` - Renderiza o contrato com valores substituídos
- `FormularioDinamico` - Gera campos baseado no template
- `MenuTemplates` - Grid de seleção de contratos

### Backend

**1. Serviço de Templates**
```python
GET  /api/v1/contratos/templates         # Lista templates
GET  /api/v1/contratos/templates/{id}    # Detalhes do template
```

**2. Serviço de Cálculo de Extensos**
```python
# Já existe: app/services/extenso_service.py
# Precisa garantir que está funcionando corretamente
valorPorExtenso(1500.50)  # → "mil quinhentos reais e cinquenta centavos"
numeroPorExtenso(12)      # → "doze"
```

**3. Geração de PDF**
- Integrar WeasyPrint (requer GTK+ no Windows)
- Ou usar biblioteca alternativa (pdfkit, reportlab)

---

## 📋 PRÓXIMOS PASSOS (PRIORIDADE)

### Fase 1 - Menu de Templates (2h)
1. Criar página `/contratos` com grid de cards
2. Cada card mostra: nome, descrição, imagem do tipo
3. Ao clicar: navega para editor com `?template=bacen`

### Fase 2 - Editor com Preview (4h)
1. Layout split-screen (formulário + preview)
2. Formulário dinâmico baseado no template JSON
3. Preview atualizando em tempo real
4. Cálculo automático de extensos

### Fase 3 - Salvar e Cadastrar Cliente (2h)
1. Botão "Salvar Contrato"
2. Validação de campos obrigatórios
3. POST para `/api/v1/contratos`
4. Cadastro automático de cliente
5. Redirecionamento para lista

### Fase 4 - Geração de PDF (3h)
1. Instalar GTK+ para Windows
2. Configurar WeasyPrint
3. Botão "Gerar PDF"
4. Download do arquivo PDF

---

## 🔧 ARQUIVOS CRIADOS/ATUALIZADOS

### Documentação
- `docs/DECISIONS.md` - Decisão arquitetural
- `docs/IMPLEMENTACAO_CONTRATOS.md` - Este arquivo

### Templates
- `contratos/templates/bacen-v2.json` - Template completo Bacen
- `contratos/extracao_docx.txt` - Extração do modelo DOCX
- `contratos/extracao_pdf.txt` - Extração do modelo PDF
- `contratos/extrair_modelos.py` - Script de extração

---

## 🎯 EXEMPLO DE USO FINAL

```
1. Usuário clica em "Contratos" no menu
2. Vê grid com: Bacen, Serasa, Protesto...
3. Clica em "Bacen"
4. Abre editor com:
   - Formulário à esquerda (campos vazios)
   - Preview à direita (contrato com [CAMPOS])
5. Preenche nome: "João da Silva"
6. Preview atualiza automaticamente
7. Preenche valor: "1500,00"
8. Preview mostra: "R$ 1.500,00 (mil quinhentos reais)"
9. Clica "Salvar"
10. Contrato salvo + Cliente cadastrado
11. Redireciona para lista de contratos
12. Clica "PDF" → Baixa contrato assinável
```

---

*Documentado em: 2026-02-03*  
*Responsável: Lucas Lebre (Automania-AI)*
