# WhatsApp VIVA - Instalacao e Operacao Completa

> Projeto: FC Solucoes Financeiras SaaS  
> Ambiente alvo: Docker local (Windows) e pronto para migracao Ubuntu  
> Data de consolidacao: 2026-02-07

## 1. Objetivo
Garantir instalacao, ativacao e operacao estavel do atendimento WhatsApp com a VIVA
(persona Viviane), incluindo conexao Evolution, webhook, backend e validacao funcional.

## 2. Arquitetura ativa
```text
WhatsApp <-> Evolution API (container: fabio2-evolution)
                   |
                   v
Webhook: http://backend:8000/api/v1/webhook/evolution
                   |
                   v
FastAPI (container: fabio2-backend)
  - EvolutionWebhookService
  - VivaIAService
  - WhatsAppService
  - OpenAIService (chat, audio, imagem e visao)
                   |
                   v
PostgreSQL (conversas e mensagens)
```

## 3. Containers obrigatorios
- `fabio2-backend` (porta `8000`)
- `fabio2-evolution` (porta `8080`)
- `fabio2-postgres` (porta `5432`)
- `fabio2-redis` (porta `6379`)

Subida:
```powershell
cd C:\projetos\fabio2
docker compose up -d
docker ps
```

Health:
```powershell
curl -UseBasicParsing http://localhost:8000/health
```

Esperado:
- `{"status":"healthy","version":"1.0.0"}`

## 4. Parametros criticos (Evolution)
No `docker-compose.yml`, manter:
- `AUTHENTICATION_API_KEY=${EVOLUTION_API_KEY:-default_key_change_in_production}`
- `WEBSOCKET_ENABLED=true`
- `CONFIG_SESSION_PHONE_VERSION=2.3000.1032141294`
- `LOG_BAILEYS=error`

Observacao:
- A chave global usada no Manager deve ser a mesma de `EVOLUTION_API_KEY`.

## 4.1 Parametros criticos (OpenAI)
No `backend/.env`, manter:
- `OPENAI_API_KEY=<sua_chave>`
- `OPENAI_API_MODEL=gpt-5-mini`
- `OPENAI_IMAGE_MODEL=gpt-image-1`
- `OPENAI_AUDIO_MODEL=gpt-4o-mini-transcribe`

Observacao:
- O backend le `backend/.env` diretamente; evite sobrescrever `OPENAI_API_KEY` vazio no `docker-compose`.

## 5. Login no Evolution Manager
URL:
- `http://localhost:8080/manager/login`

Campos:
- Server URL: `http://localhost:8080`
- API Key Global: `default_key_change_in_production` (ou valor custom do seu `.env`)

## 6. Instancia operacional
Instancia definitiva:
- `fc-solucoes`

Estado esperado:
- `Conectado` no Manager
- `open` no endpoint `/api/v1/whatsapp/status`

## 7. Webhook - ativacoes corretas
Tela: `Eventos > Webhook` da instancia `fc-solucoes`

Configuracao obrigatoria:
- `Ativo`: ON
- `URL`: `http://backend:8000/api/v1/webhook/evolution`
- `Webhook por Eventos`: OFF
- `Webhook Base64`: ON

Eventos ON (somente os necessarios):
- `MESSAGES_UPSERT`
- `CONNECTION_UPDATE`

Eventos OFF:
- todos os demais (intencional, para reduzir ruido e carga).

Checklist rapido da tela:
- `Ativo`: ON
- `Webhook por Eventos`: OFF
- `Webhook Base64`: ON
- `MESSAGES_UPSERT`: ON
- `CONNECTION_UPDATE`: ON

Validacao via API:
```powershell
$h=@{apikey='default_key_change_in_production'}
Invoke-RestMethod -Method Get -Uri 'http://localhost:8080/webhook/find/fc-solucoes' -Headers $h
```

## 7.1 Integracoes do Evolution (deixar OFF)
Para este projeto, a IA roda no backend FastAPI (VIVA + OpenAI), nao no painel interno do Evolution.

Deixe DESATIVADO no Evolution:
- `Integracoes > OpenAI`
- `Integracoes > Dify`
- `Integracoes > Typebot`
- `Integracoes > Flowise`

Motivo:
- evita conflito de dupla automacao;
- garante que toda regra comercial/persona da Viviane passe pelo backend versionado.

## 8. Regras da VIVA (conhecimento)
Fonte carregada via volume no backend:
- `frontend/src/app/viva/REGRAS/Descrição_Detalhada_dos_Serviços_Rezeta_Brasil.md`
- `frontend/src/app/viva/REGRAS/Tabela Precços IA.xlsx`
- `frontend/src/app/viva/REGRAS/tabela_precos_ia_01_planilha1.csv`

Mount no backend:
- `./frontend/src/app/viva/REGRAS:/app/viva_rules`

## 9. Teste funcional minimo (homologacao)
1. Cliente envia `Ola` para numero conectado.
2. VIVA pede nome.
3. Cliente informa nome.
4. VIVA se apresenta como Viviane.
5. Cliente informa objetivo (`limpar meu nome`).
6. VIVA continua qualificacao (cidade/urgencia etc.).

Criticos:
- Sem erro `Text is required`.
- Sem travamento apos primeira resposta.
- Mensagens salvas em `whatsapp_conversas` e `whatsapp_mensagens`.

## 10. Comandos de diagnostico rapido
Webhook recebendo:
```powershell
docker logs --since 10m fabio2-backend | Select-String "POST /api/v1/webhook/evolution"
```

Envio para WhatsApp:
```powershell
docker logs --since 10m fabio2-backend | Select-String "message/sendText/fc-solucoes"
```

Erros recentes de envio:
```powershell
docker exec c538ba33c880_fabio2-postgres psql -U fabio2_user -d fabio2 -c "select enviada, erro, created_at from whatsapp_mensagens order by created_at desc limit 20;"
```

## 11. Incidentes conhecidos e tratamento
1. QR nao aparece:
- Causa comum: versao de sessao desatualizada.
- Acao: validar `CONFIG_SESSION_PHONE_VERSION`.

2. Sem resposta no WhatsApp:
- Causa comum: webhook desativado ou eventos errados.
- Acao: garantir `MESSAGES_UPSERT` e `CONNECTION_UPDATE`.

3. Erro `Text is required`:
- Causa comum: resposta vazia do modelo.
- Acao aplicada: fallback obrigatorio antes de envio.

4. Erro `exists:false` (numero nao entregavel):
- Causa: JID invalido/nao existente.
- Acao aplicada: marcar numero como `non_deliverable` e parar retries automaticos.

## 12. Checklist de go-live (Ubuntu)
- [ ] Mesma chave `EVOLUTION_API_KEY` em backend e evolution
- [ ] URL do webhook apontando para backend interno do compose
- [ ] Instancia `fc-solucoes` conectada e `open`
- [ ] Eventos corretos no webhook
- [ ] Teste real de mensagem ponta a ponta concluido
- [ ] Logs sem `400 Bad Request` para conversas validas

## 13. Comando de agenda via VIVA (chat interno)
No chat interno `/viva`, a VIVA pode criar compromisso direto na agenda com:

```text
agendar TITULO | DD/MM/AAAA HH:MM | descricao opcional
```

Exemplo:
```text
agendar Follow-up Rezeta | 09/02/2026 15:00 | confirmar proposta
```

Resultado esperado:
- endpoint `/api/v1/viva/chat` retorna confirmacao de criacao;
- evento aparece em `/api/v1/agenda` e na tela `/agenda`.

---

Atualizado em: 2026-02-07
