# 📘 MANUAL DO CLIENTE - FC Soluções Financeiras SaaS

> **Versão:** 1.2  
> **Última atualização:** 2026-02-08  
> **Sistema:** FC Soluções Financeiras - Gestão de Contratos  
> **Público-alvo:** Fábio (Administrador) e Operadores

---

## 1. Primeiros Passos

Login
- URL local: http://localhost:3000
- Email: fabio@fcsolucoes.com
- Senha: 1234 (desenvolvimento)

Menu lateral
- Chat IA VIVA
- Contratos
- Clientes
- Agenda
- WhatsApp

---

## 2. Chat IA VIVA (Interno)

Acesso
- Rota: `/viva`

Funcionalidades
- Chat com respostas automáticas
- Menu de prompts laterais
- Análise de imagens
- Audio:
  - WhatsApp (webhook): transcricao ativa
  - Chat interno `/viva`: botao presente, operacao pendente

Prompts laterais
- Landing Pages
- Logos & Brand
- Imagens FC
- Imagens Rezeta

---

## 3. Contratos

Criar contrato
1. Acesse `Contratos` no menu
2. Escolha o template (Bacen disponível)
3. Preencha dados do cliente e valores
4. Salve o contrato

Visualizar e editar
- Visualização institucional com faixa azul
- Fonte Times New Roman
- Botão de edição na página do contrato

PDF
- Gerado via impressão do navegador (Ctrl+P -> Salvar como PDF)
- Download backend tambem disponivel na lista (`/api/v1/contratos/{id}/pdf`)

---

## 4. Clientes

- Cadastro automático ao criar contrato
- Página `/clientes` com histórico e contratos vinculados

---

## 5. Agenda

- Página `/agenda` para compromissos
- Eventos vinculados a clientes e contratos

---

## 6. WhatsApp

Conectar
- Página `/whatsapp`
- Clique em Conectar e escaneie o QR Code

Conversas com VIVA
- Página `/whatsapp/conversas`
- Histórico completo e status da conversa

---

## 7. Agentes (Catálogo Visual)

Agentes disponíveis no catálogo
- Agente de Tradução
- Agente de Slides/Pôsteres GLM
- Agente de modelo de efeito de vídeo

Ação
- CTA: “Saber mais” em cada card

---

## 8. Dicas Rápidas

- Use o menu lateral para navegar
- Gere PDF apenas depois de revisar o contrato
- Mantenha dados do cliente atualizados

---

## 9. Resolução de Problemas

Login não funciona
- Confirme email e senha
- Verifique backend ativo em `http://localhost:8000`

PDF não aparece
- Verifique popups liberados no navegador

Áudio no VIVA não funciona
- Status conhecido:
  - WhatsApp: audio com transcricao funciona
  - Chat interno `/viva`: botao de audio ainda pendente

---

**Sistema desenvolvido por:** Automania AI  
**Para:** FC Soluções Financeiras

*Este manual é atualizado regularmente. Verifique a data da última versão.*
