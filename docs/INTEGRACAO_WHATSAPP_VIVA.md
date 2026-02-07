# Integracao WhatsApp + VIVA

> Data: 07/02/2026
> Versao: 1.3.0
> Status: V1 de teste aplicada e pronta para homologacao

## Visao geral
Integracao entre WhatsApp (Evolution), backend FastAPI, frontend Next.js e
motor de atendimento da VIVA para operacao comercial da Rezeta.

## Fluxo tecnico
```text
WhatsApp -> Evolution API -> /api/v1/webhook/evolution
                         -> EvolutionWebhookService
                         -> VivaIAService
                         -> PostgreSQL (conversas/mensagens)
                         -> Frontend /whatsapp/conversas
```

## Rotas principais
Webhook
- POST `/api/v1/webhook/evolution`
- GET `/api/v1/webhook/evolution`

Conexao WhatsApp
- GET `/api/v1/whatsapp/status`
- POST `/api/v1/whatsapp/conectar`
- POST `/api/v1/whatsapp/desconectar`
- POST `/api/v1/whatsapp/enviar-texto`
- POST `/api/v1/whatsapp/enviar-arquivo`

Conversas
- GET `/api/v1/whatsapp-chat/conversas`
- GET `/api/v1/whatsapp-chat/conversas/{id}`
- GET `/api/v1/whatsapp-chat/conversas/{id}/mensagens`
- POST `/api/v1/whatsapp-chat/conversas/{id}/arquivar`
- GET `/api/v1/whatsapp-chat/status`

## Pacote operacional aprovado (negocio)
- Modo B com persona Viviane (consultora Rezeta).
- Fluxo de qualificacao: objetivo -> perfil -> urgencia -> proximo passo.
- Coleta minima: nome, telefone, servico, cidade e urgencia.
- Politica de resposta P1/P2 com adaptacao de formalidade.
- SLA 24/7 com callback de ate 15 minutos.
- Diagnostico 360 como oferta recomendada inicial.
- Excecao de venda direta: Limpa Nome, Score e Rating.
- Tabela de preco com margem operacional de 15% para oferta inicial.

## Fontes de conhecimento V1
- `frontend/src/app/viva/REGRAS/Descrição_Detalhada_dos_Serviços_Rezeta_Brasil.md`
- `frontend/src/app/viva/REGRAS/Tabela Precços IA.xlsx`
- `frontend/src/app/viva/REGRAS/tabela_precos_ia_01_planilha1.csv`

## Gate atual
V1 aplicada no backend com leitura das regras/precos via volume no container.
Proximo passo: homologacao com conversa real e ajuste fino do roteiro.

---

Documento atualizado em: 07/02/2026
