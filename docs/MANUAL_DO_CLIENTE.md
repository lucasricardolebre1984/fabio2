# 📘 MANUAL DO CLIENTE - FC Soluções Financeiras SaaS

> **Versão:** 1.0  
> **Última atualização:** 2026-02-04  
> **Sistema:** FC Soluções Financeiras - Gestão de Contratos  
> **Público-alvo:** Fábio (Administrador) e Operadores

---

## 🎯 BEM-VINDO AO SEU SISTEMA

Este é seu **SaaS completo** para gestão de contratos financeiros. Aqui você pode criar, gerenciar, enviar contratos e acompanhar seus clientes em um só lugar.

---

## 📋 ÍNDICE

1. [Primeiros Passos](#1-primeiros-passos)
2. [Contratos](#2-contratos)
3. [Clientes](#3-clientes)
4. [Agenda](#4-agenda)
5. [WhatsApp](#5-whatsapp)
6. [Dicas e Atalhos](#6-dicas-e-atalhos)
7. [Resolução de Problemas](#7-resolução-de-problemas)

---

## 1. PRIMEIROS PASSOS

### 🔐 Login

**Acesso:** http://localhost:3000 (local) ou seu domínio na web

```
Email: fabio@fcsolucoes.com
Senha: 1234 (em desenvolvimento) ou sua senha definida
```

### 🎨 Interface Principal

```
┌─────────────────────────────────────────────────────────────┐
│  FC SOLUÇÕES FINANCEIRAS        [Contratos] [Clientes]     │
│                                  [Agenda] [WhatsApp] [Sair] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 DASHBOARD PRINCIPAL                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Contratos   │  │ Clientes    │  │ Agenda Hoje │         │
│  │    15       │  │    42       │  │   3 eventos │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. CONTRATOS

### 📄 Criar Novo Contrato

**Caminho:** Menu → Contratos → Novo Contrato

**Passo a passo:**

1. **Escolha o Template:**
   - **Bacen** - Consulta BACEN (empréstimos/títulos)
   - **Serasa** - Consulta Serasa Experian
   - **Protesto** - Consulta em cartório de protestos

2. **Preencha os dados do contratante:**
   ```
   Nome completo: João da Silva
   CPF: 123.456.789-00
   Email: joao@email.com
   Telefone: (11) 98765-4321
   Endereço: Rua das Flores, 123 - São Paulo/SP
   ```

3. **Configure os valores:**
   ```
   Valor total: R$ 10.000,00
   Valor entrada: R$ 2.000,00
   Quantidade de parcelas: 12
   
   → O sistema calcula automaticamente:
   • Valor da parcela: R$ 666,67
   • Valores por extenso (para o contrato)
   • Prazos de carência
   ```

4. **Defina os prazos:**
   ```
   Prazo 1ª carência: 30 dias
   Prazo 2ª carência: 60 dias
   Local de assinatura: São Paulo/SP
   ```

5. **Clique em "Salvar"** ✅

### 👁️ Visualizar Contrato

- Veja o contrato formatado com **layout institucional**
- Faixa azul metálica no cabeçalho
- Fonte Times New Roman (estilo formal)
- Cálculos automáticos por extenso

### 🖨️ Gerar PDF

```
No contrato → Botão "Baixar PDF"
→ Arquivo salvo: Contrato_Bacen_Joao_Silva_2026.pdf
```

### ✏️ Editar Contrato

1. Abra o contrato
2. Clique em "Editar" (lápis ✏️)
3. Altere os campos necessários
4. Salve

**Nota:** Campos calculados (valores por extenso) atualizam automaticamente!

### 📤 Enviar Contrato por WhatsApp

```
No contrato → Botão "📱 Enviar WhatsApp"
→ Selecione o número do cliente
→ Adicione mensagem personalizada (opcional)
→ Clique "Enviar"
```

**Exemplo de mensagem:**
```
Olá João! Segue o contrato da consulta BACEN. 
Por favor, revise e me confirme o recebimento. Obrigado!
```

### 🗑️ Excluir Contrato

```
Lista de contratos → Ícone 🗑️ → Confirmar
⚠️ Atenção: Esta ação não pode ser desfeita!
```

---

## 3. CLIENTES

### ➕ Cadastrar Cliente

**Caminho:** Menu → Clientes → Novo Cliente

```
Dados pessoais:
├── Nome completo
├── CPF/CNPJ
├── Email
├── Telefone
├── Endereço completo
└── Observações
```

### 📋 Histórico do Cliente

Ao clicar em um cliente, você vê:
- **Dados cadastrais**
- **Contratos realizados** (lista completa)
- **Status de cada contrato**
- **Botão para criar novo contrato** deste cliente

### 🔍 Buscar Cliente

```
Barra de pesquisa → Digite nome, CPF ou email
→ Resultados em tempo real
```

---

## 4. AGENDA

### 📅 Criar Compromisso

**Caminho:** Menu → Agenda → Novo Evento

```
Título: Reunião com João Silva
Data: 04/02/2026
Hora: 14:00
Tipo: Reunião / Ligação / Cobrança / Outro
Cliente: [Selecione da lista]
Descrição: Discutir proposta de consulta BACEN
Lembrete: 30 minutos antes
```

### 🔔 Tipos de Eventos

| Ícone | Tipo | Uso |
|-------|------|-----|
| 🤝 | Reunião | Atendimento presencial |
| 📞 | Ligação | Call de prospecção |
| 💰 | Cobrança | Follow-up de pagamento |
| 📝 | Outro | Tarefas diversas |

### 📆 Visualizações

- **Dia** - Agenda detalhada hora a hora
- **Semana** - Visão geral da semana
- **Mês** - Calendário mensal com eventos

### 🔗 Integração com Contratos

```
Ao criar contrato → Opção "Agendar retorno"
→ Cria evento automático na agenda
→ Vinculado ao cliente
```

---

## 5. WHATSAPP

### 📱 Configuração Inicial

**Caminho:** Menu → WhatsApp

```
1. Clique "Conectar WhatsApp"
2. Escaneie o QR Code com seu celular
3. Pronto! Seu número está conectado
```

### 💬 Funcionalidades Disponíveis

#### Enviar Contrato
```
Contrato aberto → Botão "📤 Enviar WhatsApp"
→ Escolha o contato
→ PDF enviado automaticamente
```

#### Enviar Mensagem
```
WhatsApp → Nova mensagem
→ Digite número ou escolha contato
→ Escreva mensagem
→ Envie texto, imagem ou documento
```

#### Histórico de Conversas
```
Cliente → Aba "Conversas"
→ Veja todo histórico WhatsApp
→ Mensagens enviadas e recebidas
```

#### Cobrança Automática
```
Configurar → Cobranças
→ Defina dias antes do vencimento
→ Mensagem automática enviada
```

### 📊 Status das Mensagens

| Status | Significado |
|--------|-------------|
| ⏳ | Enviando |
| ✓ | Enviado |
| ✓✓ | Entregue |
| ✓✓ (azul) | Lido |

---

## 6. DICAS E ATALHOS

### ⌨️ Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| `Ctrl + N` | Novo contrato |
| `Ctrl + F` | Buscar |
| `Ctrl + S` | Salvar |
| `Esc` | Fechar/Voltar |

### 💡 Dicas de Produtividade

1. **Use templates pré-preenchidos**
   - Crie contratos mais rápido com dados automáticos

2. **Agende sempre**
   - Todo contrato deve ter um follow-up na agenda

3. **Envie confirmação**
   - Sempre envie o contrato por WhatsApp e peça confirmação

4. **Mantenha os dados atualizados**
   - Cliente mudou de telefone? Atualize imediatamente

5. **Use as observações**
   - Anote preferências do cliente para personalizar atendimento

---

## 7. RESOLUÇÃO DE PROBLEMAS

### ❌ Não consigo fazer login

```
Verifique:
✓ Email está correto (fabio@fcsolucoes.com)
✓ Caps Lock desligado
✓ Conexão com internet

Solução: Clique "Esqueci a senha" ou contate o suporte
```

### ❌ Contrato não gera PDF

```
Verifique:
✓ Todos os campos obrigatórios estão preenchidos
✓ CPF está no formato correto
✓ Valores são números válidos

Solução: Edite o contrato e complete os dados faltantes
```

### ❌ WhatsApp desconectou

```
Verifique:
✓ Celular está com internet
✓ WhatsApp Web está ativo no celular

Solução: Menu WhatsApp → Reconectar → Escaneie QR Code
```

### ❌ Não recebo notificações da agenda

```
Verifique:
✓ Notificações do navegador estão permitidas
✓ Lembrete está configurado no evento

Solução: Configurações → Notificações → Ativar
```

---

## 📞 SUPORTE

**Problemas técnicos:**
- Email: suporte@automaniaai.com.br
- WhatsApp: (16) 99999-9999

**Sugestões de melhorias:**
- Use o botão "💡 Sugerir" no menu principal

---

## 🎓 PRÓXIMOS PASSOS

Para aproveitar 100% do sistema:

1. ✅ Crie seu primeiro contrato de teste
2. ✅ Cadastre 3 clientes
3. ✅ Agende 2 compromissos
4. ✅ Conecte seu WhatsApp
5. ✅ Envie um contrato para seu próprio número

---

**Sistema desenvolvido por:** Automania AI  
**Para:** FC Soluções Financeiras  
**Versão atual:** 1.0 - Janeiro/2026

---

*Este manual é atualizado regularmente. Verifique a data da última versão.*
