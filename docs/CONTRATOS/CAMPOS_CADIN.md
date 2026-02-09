# CONTRATO CADIN PF/PJ - Especificação de Campos

> **Template:** CADIN PF/PJ  
> **Fonte:** `contratos/cadinpfpjmodelo.docx`  
> **Versão:** 1.1.0

---

## Resumo

Instrumento de prestação de serviços para regularização de pendências do(a)
CONTRATANTE no CADIN, com foco em adoção de procedimentos administrativos
junto aos órgãos federais para obtenção de CND/documento equivalente.

Partes:
- CONTRATANTE: cliente (preenchido no formulário)
- CONTRATADA: FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA (fixo)

---

## Campos Operacionais

### Seção 1: Dados do Contratante

| Campo | Label | Tipo | Obrigatório |
|---|---|---|---|
| `contratante_nome` | Nome Completo | texto | sim |
| `contratante_documento` | CPF/CNPJ | cpf_cnpj | sim |
| `contratante_email` | E-mail | email | sim |
| `contratante_telefone` | Telefone | telefone | não |
| `contratante_endereco` | Endereço Completo | texto | sim |

### Seção 2: Valores e Pagamento

| Campo | Label | Tipo | Obrigatório |
|---|---|---|---|
| `valor_total` | Valor Total | moeda | sim |
| `valor_entrada` | Entrada | moeda | sim |
| `qtd_parcelas` | Quantidade de Parcelas | número | sim |
| `valor_parcela` | Valor da Parcela | moeda | sim |
| `prazo_1` | Prazo 1 (dias) | número | sim |
| `prazo_2` | Prazo 2 (dias) | número | sim |

### Seção 3: Assinatura

| Campo | Label | Tipo | Obrigatório |
|---|---|---|---|
| `local_assinatura` | Local da Assinatura | texto | sim |
| `data_assinatura` | Data da Assinatura | data | sim |

---

## Cláusulas Base (modelo oficial)

1. **Do Objeto**  
2. **Das Despesas e Honorários**  
3. **Do Prazo e Garantia**  
4. **Da Proteção de Dados (LGPD)**  
5. **Do Foro**

Observação: os detalhes completos (itens 1.1, §1º, 2.1...5.1) foram transpostos
do `cadinpfpjmodelo.docx` para o template `contratos/templates/cadin.json`.

---

## Logo Institucional

- Arquivo oficial usado no layout azul: `contratos/logo2.png`
- Origem: `contratos/logo2.jpeg` (convertida para PNG transparente para preservar apenas a balança branca no cabeçalho)

---

## Arquivos Relacionados

- `contratos/templates/cadin.json`
- `contratos/cadinpfpjmodelo.docx`
- `contratos/logo2.png`
- `frontend/public/logo2.png`

---

Atualizado em: 2026-02-09
