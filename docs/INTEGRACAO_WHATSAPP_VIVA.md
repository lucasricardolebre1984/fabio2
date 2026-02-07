# Integracao WhatsApp + VIVA

> Data: 07/02/2026
> Versao: 1.4.0
> Status: Operacao estabilizada com webhook ativo e runbook completo

## Visao geral
Integracao entre WhatsApp (Evolution), backend FastAPI, frontend Next.js e
motor de atendimento da VIVA para operacao comercial da Rezeta.

## Documento operacional oficial
- `docs/WHATSAPP_INSTALACAO_OPERACIONAL.md`
- Este documento acima e a referencia de instalacao, ativacao, testes e troubleshooting.

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
V1.4 aplicada no backend com:
- normalizacao de eventos webhook (`MESSAGES_UPSERT` / `CONNECTION_UPDATE`);
- fallback contra resposta vazia do modelo;
- bloqueio de retries para JID nao entregavel (`exists:false`);
- base de conhecimento carregada por volume no container.

Proximo passo:
- homologacao assistida com cliente e monitoramento de conversao.

## Ativacoes obrigatorias no Evolution Manager
- Ativo: ON
- URL: `http://backend:8000/api/v1/webhook/evolution`
- Webhook por Eventos: OFF
- Webhook Base64: ON
- Eventos ON: `MESSAGES_UPSERT`, `CONNECTION_UPDATE`

## Suporte a audio (WhatsApp)
- Webhook agora detecta `audioMessage` e tenta transcrever automaticamente.
- Fluxo: Evolution (midia base64) -> transcricao Z.AI (`glm-asr-2512`) -> VIVA.
- Se a transcricao falhar, a Viviane responde com fallback pedindo texto/audio curto
  para manter atendimento sem travar a conversa.

---

Documento atualizado em: 07/02/2026
