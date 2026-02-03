# CONTRATO BACEN - Especificação de Campos

> **Template:** Bacen - Remoção SCR  
> **Fonte:** contratos/bacenmodelo.docx  
> **Versão:** 1.0.0  

---

## 📋 Resumo

Contrato de Prestação de Serviços para remoção de apontamentos de prejuízo no Sistema de Informações de Crédito (SCR) do Banco Central.

**Partes:**
- **CONTRATANTE:** Cliente (preenchido no formulário)
- **CONTRATADA:** FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA (fixo)

---

## 📝 Campos do Formulário

### Seção 1: Dados do Contratante

| Campo | Label | Tipo | Obrigatório | Máscara | Placeholder |
|-------|-------|------|-------------|---------|-------------|
| contratante_nome | Nome Completo | texto | ✅ | - | João da Silva |
| contratante_documento | CPF/CNPJ | cpf_cnpj | ✅ | 000.000.000-00 / 00.000.000/0000-00 | |
| contratante_email | E-mail | email | ✅ | - | joao@email.com |
| contratante_telefone | Telefone | telefone | ❌ | (00) 00000-0000 | |
| contratante_endereco | Endereço Completo | texto | ✅ | - | Rua das Flores, 123 - Centro |

### Seção 2: Valores do Contrato

| Campo | Label | Tipo | Obrigatório | Máscara | Extenso (auto) |
|-------|-------|------|-------------|---------|----------------|
| valor_total | Valor Total | moeda | ✅ | R$ #.##0,00 | valor_total_extenso |
| valor_entrada | Valor da Entrada | moeda | ✅ | R$ #.##0,00 | valor_entrada_extenso |
| qtd_parcelas | Quantidade de Parcelas | numero | ✅ | 0 | qtd_parcelas_extenso |
| valor_parcela | Valor da Parcela | moeda | ✅ | R$ #.##0,00 | valor_parcela_extenso |
| prazo_1 | Prazo 1 (dias) | numero | ✅ | 0 | prazo_1_extenso |
| prazo_2 | Prazo 2 (dias) | numero | ✅ | 0 | prazo_2_extenso |

### Seção 3: Dados da Assinatura

| Campo | Label | Tipo | Obrigatório | Placeholder |
|-------|-------|------|-------------|-------------|
| local_assinatura | Local | texto | ✅ | Ribeirão Preto/SP |
| data_assinatura | Data | data | ✅ | - |

---

## 🏛️ Dados Fixos (Contratada)

```yaml
contratada_nome: "FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA"
contratada_cnpj: "57.815.628/0001-62"
contratada_email: "contato@fcsolucoesfinanceiras.com"
contratada_endereco: "Rua Maria das Graças de Negreiros Bonilha, nº 30, sala 3, Jardim Nova Aliança Sul, Ribeirão Preto/SP, CEP 14022-100"
contratada_telefone: "(16) 99301-7396"
```

---

## 📄 Cláusulas do Contrato

### CLÁUSULA PRIMEIRA - DO OBJETO
```
O presente contrato tem como objeto a prestação de serviços de consultoria e 
intermediação administrativa pela CONTRATADA em favor do(a) CONTRATANTE, 
visando a adoção de procedimentos administrativos para a regularização de 
apontamentos de prejuízo registrados no Sistema de Informações de Crédito 
(SCR) do Banco Central do Brasil, vinculados ao CPF/CNPJ do(a) CONTRATANTE.
```

### CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES DA CONTRATADA
- Realizar análise detalhada da situação junto ao SCR
- Elaborar e protocolar requerimentos administrativos
- Acompanhar o andamento dos procedimentos
- Manter o CONTRATANTE informado

### CLÁUSULA TERCEIRA - DAS OBRIGAÇÕES DO CONTRATANTE
- Fornecer documentos e informações solicitados
- Efetuar pagamentos nas datas acordadas
- Não tratar diretamente com instituições financeiras

### CLÁUSULA QUARTA - DO VALOR E DA FORMA DE PAGAMENTO
**Texto template:**
```
Pelos serviços prestados, o(a) CONTRATANTE pagará à CONTRATADA o valor 
total de R$ [valor_total] ([valor_total_extenso]), a ser pago da seguinte forma:

Entrada: R$ [valor_entrada] ([valor_entrada_extenso]), a ser paga no ato 
da assinatura deste contrato.

Parcelas: [qtd_parcelas] ([qtd_parcelas_extenso]) parcelas de 
R$ [valor_parcela] ([valor_parcela_extenso]), com vencimento em 
[prazo_1] ([prazo_1_extenso]) e [prazo_2] ([prazo_2_extenso]) dias, 
respectivamente, a contar da data de assinatura.
```

### CLÁUSULA QUINTA - DO PRAZO DE EXECUÇÃO
Prazo estimado: 45 a 60 dias úteis a partir da assinatura e pagamento da entrada.

### CLÁUSULA SEXTA - GARANTIA DE RESULTADO
- Serviço vinculado à efetiva baixa dos apontamentos
- Sem resultado em 60 dias → rescisão automática
- Reembolso integral em até 30 dias
- Multa de 10% + juros em caso de atraso no reembolso

### CLÁUSULA SÉTIMA - DO INADIMPLEMENTO
- Multa de 10% sobre parcela em atraso
- Juros de 1% ao mês (pro rata die)
- Correção monetária pelo IPCA
- Suspensão após 30 dias de atraso

### CLÁUSULA OITAVA - ALOCAÇÃO DE RECURSOS
- Fase I: Análise e onboarding (gratuita)
- Fase II: Execução (inicia após assinatura)
- Custos são irreversíveis
- Sem devolução em caso de desistência

### CLÁUSULA NONA - CONFIDENCIALIDADE
Manter sigilo das informações.

### CLÁUSULA DÉCIMA - DO FORO
Foro da Comarca de São Paulo/SP.

### CLÁUSULA DÉCIMA PRIMEIRA - DOS ANEXOS
Anexo I - Termo de Ciência e Consentimento Expresso (deve ser assinado junto).

---

## 🖊️ Assinaturas

```
_________________________________
[contratante_nome]
CONTRATANTE

_________________________________
FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA
CONTRATADA

[local_assinatura], [data_assinatura].

Testemunhas:
1. _____________________________
   Nome:
   CPF:

2. _____________________________
   Nome:
   CPF:
```

---

## 🔧 Placeholders no Template

### Formato de Substituição

| Placeholder | Descrição | Exemplo |
|-------------|-----------|---------|
| `[CAMPO]` | Campo a preencher | `[contratante_nome]` |
| `(CAMPO)` | Valor por extenso | `(valor_total_extenso)` |

### Mapeamento de Campos

```javascript
const placeholders = {
  // Contratante
  "[contratante_nome]": contratante_nome,
  "[contratante_documento]": contratante_documento,
  "[contratante_email]": contratante_email,
  "[contratante_endereco]": contratante_endereco,
  
  // Contratada (fixos)
  "[contratada_nome]": "FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA",
  "[contratada_cnpj]": "57.815.628/0001-62",
  
  // Valores (formatados)
  "[valor_total]": formatMoney(valor_total),
  "[valor_entrada]": formatMoney(valor_entrada),
  "[qtd_parcelas]": qtd_parcelas,
  "[valor_parcela]": formatMoney(valor_parcela),
  "[prazo_1]": prazo_1,
  "[prazo_2]": prazo_2,
  
  // Valores por extenso
  "(valor_total_extenso)": extenso(valor_total),
  "(valor_entrada_extenso)": extenso(valor_entrada),
  "(qtd_parcelas_extenso)": extenso(qtd_parcelas),
  "(valor_parcela_extenso)": extenso(valor_parcela),
  "(prazo_1_extenso)": extenso(prazo_1),
  "(prazo_2_extenso)": extenso(prazo_2),
  
  // Local e data
  "[local_assinatura]": local_assinatura,
  "[data_assinatura]": formatDate(data_assinatura),
};
```

---

## 📊 Validações de Negócio

```javascript
// Regras de validação
const validacoes = {
  valor_total: {
    min: 0.01,
    max: 999999.99,
    message: "Valor deve ser maior que zero"
  },
  valor_entrada: {
    max: "valor_total",
    message: "Entrada não pode ser maior que o valor total"
  },
  valor_parcela: {
    formula: "(valor_total - valor_entrada) / qtd_parcelas",
    auto_calculate: true
  },
  prazo_1: {
    min: 1,
    max: 999
  },
  prazo_2: {
    min: 1,
    max: 999,
    gt: "prazo_1"  // Deve ser maior que prazo_1
  }
};
```

---

*Documento atualizado em: 2026-02-03*
