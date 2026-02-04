# 📘 MANUAL DO CLIENTE - FC Soluções Financeiras SaaS

> **Versão:** 1.1  
> **Última atualização:** 2026-02-04  
> **Sistema:** FC Soluções Financeiras - Gestão Completa  
> **Público-alvo:** Fábio (Administrador) e Operadores

---

## 🎯 BEM-VINDO AO SEU SISTEMA

Este é seu **SaaS completo** para gestão de contratos financeiros, clientes, agenda e criação de imagens com IA.

---

## 📋 ÍNDICE

1. [Primeiros Passos](#1-primeiros-passos)
2. [Contratos](#2-contratos)
3. [Clientes](#3-clientes)
4. [Agenda](#4-agenda)
5. [WhatsApp](#5-whatsapp)
6. [Imagens (NOVO)](#6-imagens)
7. [Dicas e Atalhos](#7-dicas-e-atalhos)
8. [Resolução de Problemas](#8-resolução-de-problemas)

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
│                                  [Agenda] [WhatsApp]       │
│                                  [Imagens] [Sair]          │
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

### 📄 Visualizar/Gerar PDF

1. Vá em Contratos → Lista
2. Clique no olho (👁️) ao lado do contrato
3. Clique em "Visualizar PDF" ou "Download"
4. Na nova janela, use Ctrl+P → "Salvar como PDF"

---

## 3. CLIENTES

### 👥 Cadastrar Cliente

**Caminho:** Menu → Clientes → Novo Cliente

O sistema cadastra clientes automaticamente quando você cria um contrato, mas você pode:

- Ver histórico completo de contratos por cliente
- Editar dados cadastrais
- Adicionar anotações

---

## 4. AGENDA

### 📅 Criar Compromisso

**Caminho:** Menu → Agenda

- Visualize compromissos em calendário
- Crie eventos vinculados a clientes
- Receba lembretes (em desenvolvimento)

---

## 5. WHATSAPP

### 💬 Conectar WhatsApp

**Caminho:** Menu → WhatsApp

1. Escaneie o QR Code com seu WhatsApp
2. Pronto! O sistema está conectado
3. Você pode enviar contratos e mensagens direto do sistema

### 📤 Enviar Contrato por WhatsApp

1. Abra o contrato (visualização)
2. Clique em "Enviar"
3. Digite o número do cliente
4. Clique "Enviar"

---

## 6. IMAGENS (NOVO)

> **Módulo de criação e gestão de imagens com IA**

### 🎨 Gerar Imagem com IA

**Caminho:** Menu → Imagens → Gerar com IA

**Passo a passo:**

1. **Digite o Prompt:**
   ```
   Exemplo: "Professional marketing flyer for financial services company,
   modern design, blue and white colors, business people shaking hands,
   clean background, corporate aesthetic, high quality"
   ```

2. **Escolha o Formato:**
   - **1:1** (Quadrado) - Feed Instagram
   - **16:9** (Paisagem) - Banner/Story horizontal
   - **9:16** (Retrato) - Story vertical

3. **Clique em "Gerar Imagem"**
   - Aguarde 30-60 segundos
   - A imagem aparecerá no preview

4. **Salvar ou Gerar Nova**
   - "Ver na Galeria" - Salva e vai para a lista
   - "Gerar Outra" - Cria variação

### 📤 Upload de Imagem

**Caminho:** Menu → Imagens → Upload

1. Clique na área de upload ou arraste um arquivo
2. Formatos suportados: JPG, PNG, WebP (máx. 10MB)
3. Dê um nome para a imagem
4. Selecione o formato apropriado
5. Clique "Fazer Upload"

### 📁 Pasta Campanhas

**O que é:** Imagens aprovadas para uso em campanhas de marketing

**Como funciona:**
1. Gere ou faça upload de uma imagem
2. Na galeria, clique em "Aprovar" na imagem desejada
3. A imagem é movida automaticamente para a pasta Campanhas
4. O nome é formatado: `YYYYMMDD_nome_imagem.ext`
   - Exemplo: `20260204_campanha_bacen.png`

**Para que serve:**
- Organiza imagens aprovadas
- Facilita encontrar campanhas passadas
- Padroniza nomenclatura por data

### 🖼️ Gerenciar Imagens

**Caminho:** Menu → Imagens

**Filtros disponíveis:**
- **Status:** Todas / Rascunho / Aprovada
- **Tipo:** Todas / Gerada por IA / Upload

**Visualizações:**
- **Grid:** Miniaturas em grade
- **Lista:** Detalhes em linhas

**Tabs:**
- **Todas** - Todas as imagens
- **Geradas por IA** - Apenas imagens criadas pela IA
- **Uploads** - Apenas imagens enviadas
- **Campanhas** - Apenas imagens aprovadas

**Ações em cada imagem:**
- **Aprovar** - Move para pasta Campanhas
- **Excluir** - Remove permanentemente

---

## 7. DICAS E ATALHOS

### ⌨️ Atalhos do Teclado

| Atalho | Ação |
|--------|------|
| Ctrl + S | Salvar (em formulários) |
| Ctrl + P | Imprimir/Salvar PDF |
| Esc | Fechar modais |

### 💡 Dicas Gerais

1. **Valores por extenso** são calculados automaticamente
2. **Número do contrato** é gerado automaticamente (CNT-YYYY-NNNN)
3. **Clientes** são cadastrados automaticamente ao criar contrato
4. **Imagens geradas** ficam em "Rascunho" até serem aprovadas
5. **Backup** é feito automaticamente no servidor

---

## 8. RESOLUÇÃO DE PROBLEMAS

### ❌ Erro de Login

**Problema:** "Email ou senha incorretos"

**Solução:**
- Verifique se digitou o email correto: `fabio@fcsolucoes.com`
- Senha padrão em desenvolvimento: `1234`
- Limpe o cache do navegador (Ctrl+Shift+Del)

### ❌ WhatsApp Desconectado

**Problema:** QR Code não aparece ou não conecta

**Solução:**
1. Vá em Menu → WhatsApp
2. Clique "Desconectar" (se estiver conectado)
3. Clique "Conectar"
4. Escaneie o QR Code novamente

### ❌ Imagem não Gera

**Problema:** Erro ao gerar imagem com IA

**Solução:**
1. Verifique se o prompt tem pelo menos 10 caracteres
2. Aguarde 30-60 segundos (pode demorar em alta demanda)
3. Tente um prompt mais simples
4. Verifique sua conexão com internet

### ❌ Upload Falha

**Problema:** Erro ao fazer upload de imagem

**Solução:**
1. Verifique o formato (JPG, PNG, WebP apenas)
2. Verifique o tamanho (máx. 10MB)
3. Tente um arquivo menor
4. Verifique sua conexão

### 🆘 Suporte

Em caso de problemas persistentes:
- **Responsável técnico:** Lucas Lebre (Automania-AI)
- **Documentação:** Verifique a pasta `docs/` do projeto

---

## 📊 RESUMO DOS MÓDULOS

| Módulo | Função | Status |
|--------|--------|--------|
| Contratos | Criar e gerenciar contratos | ✅ Pronto |
| Clientes | CRM e histórico | ✅ Pronto |
| Agenda | Compromissos e lembretes | ✅ Pronto |
| WhatsApp | Envio de mensagens e contratos | ✅ Pronto |
| Imagens | Geração com IA + Gestão | ✅ **NOVO** |

---

*Atualizado em: 2026-02-04*  
*Versão: 1.1 - Inclui módulo de Imagens*
