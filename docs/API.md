# API - FC Soluções Financeiras

> **Base URL:** `http://localhost:8000/api/v1`  
> **Versão:** 1.0.0  
> **Data:** 2026-02-05

---

## Autenticação

- Tipo: Bearer JWT
- Header: `Authorization: Bearer <access_token>`
- Tokens são emitidos em `/auth/login` e renovados em `/auth/refresh`.

Erros comuns
- `401` Token ausente, inválido ou expirado
- `403` Usuário inativo ou sem permissão

---

## Auth

### POST /auth/login

Autenticação pública.

Request (JSON)
```json
{
  "email": "fabio@fcsolucoes.com",
  "password": "1234"
}
```

Response 200
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "fabio@fcsolucoes.com",
    "nome": "Fábio",
    "role": "admin",
    "ativo": true,
    "created_at": "2026-02-05T12:00:00Z",
    "updated_at": null
  }
}
```

Erros
- `401` Email ou senha incorretos
- `403` Usuário inativo

### POST /auth/refresh

Requer Bearer.

Request (JSON)
```json
{
  "refresh_token": "..."
}
```

Response 200
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": { "id": "uuid", "email": "..." }
}
```

Erros
- `401` Token de refresh inválido

### POST /auth/logout

Requer Bearer. Não invalida servidor; client deve remover tokens.

Response 200
```json
{ "message": "Logout realizado com sucesso" }
```

### GET /auth/me

Requer Bearer.

Response 200
```json
{
  "id": "uuid",
  "email": "fabio@fcsolucoes.com",
  "nome": "Fábio",
  "role": "admin",
  "ativo": true
}
```

---

## Contratos

### GET /contratos/templates

Requer Bearer (operador).

Response 200
```json
[
  {
    "id": "uuid",
    "nome": "Contrato Bacen - Remoção SCR",
    "tipo": "bacen",
    "descricao": "...",
    "versao": "1.0",
    "ativo": true,
    "campos": [],
    "secoes": [],
    "created_at": "2026-02-05T12:00:00Z",
    "updated_at": null
  }
]
```

### GET /contratos/templates/{template_id}

Requer Bearer (operador).

Response 200
```json
{
  "id": "uuid",
  "nome": "Contrato Bacen - Remoção SCR",
  "tipo": "bacen",
  "descricao": "...",
  "versao": "1.0",
  "ativo": true,
  "campos": [],
  "secoes": [],
  "clausulas": [],
  "assinaturas": [],
  "layout": "institucional",
  "contratada_nome": "...",
  "contratada_cnpj": "...",
  "contratada_email": "...",
  "contratada_endereco": "...",
  "contratada_telefone": "...",
  "created_at": "2026-02-05T12:00:00Z",
  "updated_at": null
}
```

Erros
- `404` Template não encontrado

### POST /contratos

Requer Bearer (operador).

Request (JSON)
```json
{
  "template_id": "bacen",
  "contratante_nome": "João da Silva",
  "contratante_documento": "12345678900",
  "contratante_email": "joao@email.com",
  "contratante_telefone": "11999999999",
  "contratante_endereco": "Rua X, 123",
  "valor_total": 1000.00,
  "valor_entrada": 200.00,
  "qtd_parcelas": 4,
  "valor_parcela": 200.00,
  "prazo_1": 30,
  "prazo_2": 60,
  "local_assinatura": "Ribeirão Preto/SP",
  "data_assinatura": "05/02/2026",
  "valor_total_extenso": null,
  "valor_entrada_extenso": null,
  "qtd_parcelas_extenso": null,
  "valor_parcela_extenso": null,
  "prazo_1_extenso": null,
  "prazo_2_extenso": null,
  "dados_extras": {}
}
```

Response 201
```json
{
  "id": "uuid",
  "numero": "CNT-2026-0001",
  "status": "rascunho",
  "template_id": "bacen",
  "template_nome": "Contrato Bacen - Remoção SCR",
  "contratante_nome": "João da Silva",
  "contratante_documento": "12345678900",
  "contratante_email": "joao@email.com",
  "contratante_telefone": "11999999999",
  "contratante_endereco": "Rua X, 123",
  "valor_total": 1000.0,
  "valor_total_extenso": "mil reais",
  "valor_entrada": 200.0,
  "valor_entrada_extenso": "duzentos reais",
  "qtd_parcelas": 4,
  "qtd_parcelas_extenso": "quatro",
  "valor_parcela": 200.0,
  "valor_parcela_extenso": "duzentos reais",
  "prazo_1": 30,
  "prazo_1_extenso": "trinta",
  "prazo_2": 60,
  "prazo_2_extenso": "sessenta",
  "local_assinatura": "Ribeirão Preto/SP",
  "data_assinatura": "05/02/2026",
  "dados_extras": {},
  "pdf_url": null,
  "created_by": "uuid",
  "created_at": "2026-02-05T12:00:00Z",
  "updated_at": null
}
```

### GET /contratos

Requer Bearer (operador).

Query params
- `status` rascunho | finalizado | enviado | cancelado
- `search` texto para nome, número ou documento
- `page` padrão 1
- `page_size` padrão 20

Response 200
```json
{
  "items": [ { "id": "uuid", "numero": "CNT-2026-0001" } ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### GET /contratos/{contrato_id}

Requer Bearer (operador).

Response 200
```json
{ "id": "uuid", "numero": "CNT-2026-0001" }
```

Erros
- `404` Contrato não encontrado

### PUT /contratos/{contrato_id}

Requer Bearer (operador).

Request (JSON)
```json
{
  "status": "finalizado",
  "dados_extras": {},
  "pdf_url": "/storage/contrato.pdf"
}
```

Response 200
```json
{ "id": "uuid", "status": "finalizado" }
```

### DELETE /contratos/{contrato_id}

Requer Bearer (admin).

Response 204

### GET /contratos/{contrato_id}/pdf

Requer Bearer (operador). Retorna PDF binário.

Response 200
- `Content-Type: application/pdf`

Erros
- `500` Erro ao gerar PDF

### POST /contratos/{contrato_id}/enviar

Requer Bearer (operador).

Query params
- `telefone` número do destinatário

Response 200
```json
{ "message": "Contrato enviado com sucesso", "result": { } }
```

---

## Clientes

### POST /clientes

Requer Bearer (operador).

Request (JSON)
```json
{
  "nome": "João da Silva",
  "tipo_pessoa": "fisica",
  "documento": "12345678900",
  "email": "joao@email.com",
  "telefone": "11999999999",
  "endereco": "Rua X, 123",
  "cidade": "São Paulo",
  "estado": "SP",
  "cep": "01000000",
  "observacoes": ""
}
```

Response 201
```json
{ "id": "uuid", "nome": "João da Silva" }
```

Erros
- `409` Cliente com documento já existe

### GET /clientes

Requer Bearer (operador).

Query params
- `search` nome ou documento
- `page` padrão 1
- `page_size` padrão 20

Response 200
```json
{
  "items": [ { "id": "uuid", "nome": "João" } ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### GET /clientes/{cliente_id}

Requer Bearer (operador).

Response 200
```json
{ "id": "uuid", "nome": "João" }
```

### GET /clientes/documento/{documento}

Requer Bearer (operador).

Response 200
```json
{ "id": "uuid", "documento": "12345678900" }
```

### PUT /clientes/{cliente_id}

Requer Bearer (operador).

Request (JSON)
```json
{ "telefone": "11999999999", "endereco": "Rua X, 123" }
```

Response 200
```json
{ "id": "uuid" }
```

### DELETE /clientes/{cliente_id}

Requer Bearer (admin).

Response 204

### GET /clientes/{cliente_id}/contratos

Requer Bearer (operador).

Response 200
```json
[ { "id": "uuid", "numero": "CNT-2026-0001" } ]
```

### GET /clientes/{cliente_id}/historico

Requer Bearer (operador).

Response 200
```json
{
  "cliente": { "id": "uuid", "nome": "João" },
  "contratos": [ { "id": "uuid" } ],
  "agenda": [ { "id": "uuid" } ]
}
```

---

## Agenda

### POST /agenda

Requer Bearer (operador).

Request (JSON)
```json
{
  "titulo": "Reunião",
  "descricao": "Alinhar contrato",
  "tipo": "outro",
  "data_inicio": "2026-02-05T14:00:00Z",
  "data_fim": "2026-02-05T15:00:00Z",
  "cliente_id": "uuid",
  "contrato_id": "uuid"
}
```

Response 201
```json
{ "id": "uuid", "titulo": "Reunião" }
```

### GET /agenda

Requer Bearer (operador).

Query params
- `inicio` datetime
- `fim` datetime
- `cliente_id` uuid
- `concluido` true | false
- `page` padrão 1
- `page_size` padrão 20

Response 200
```json
{
  "items": [ { "id": "uuid", "titulo": "Reunião" } ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### GET /agenda/hoje

Requer Bearer (operador).

Response 200
```json
{ "items": [ { "id": "uuid" } ], "total": 1, "page": 1, "page_size": 20 }
```

### GET /agenda/{evento_id}

Requer Bearer (operador).

Response 200
```json
{ "id": "uuid", "titulo": "Reunião" }
```

### PUT /agenda/{evento_id}

Requer Bearer (operador).

Request (JSON)
```json
{ "titulo": "Reunião atualizada" }
```

Response 200
```json
{ "id": "uuid", "titulo": "Reunião atualizada" }
```

### PATCH /agenda/{evento_id}/concluir

Requer Bearer (operador).

Response 200
```json
{ "id": "uuid", "concluido": true }
```

### DELETE /agenda/{evento_id}

Requer Bearer (operador).

Response 204

---

## WhatsApp (Evolution API)

### GET /whatsapp/status

Requer Bearer (operador).

Response 200
```json
{ "conectado": true, "estado": "open", "numero": "55..." }
```

### POST /whatsapp/conectar

Requer Bearer (operador).

Response 200
```json
{ "sucesso": true, "qr_code": "..." }
```

### POST /whatsapp/desconectar

Requer Bearer (operador).

Response 200
```json
{ "sucesso": true, "mensagem": "Desconectado com sucesso" }
```

### POST /whatsapp/enviar-texto

Requer Bearer (operador).

Query params
- `numero`
- `mensagem`

Response 200
```json
{ "sucesso": true, "mensagem": "Mensagem enviada com sucesso" }
```

### POST /whatsapp/enviar-arquivo

Requer Bearer (operador).

Query params
- `numero`
- `arquivo_url`
- `legenda` opcional

Response 200
```json
{ "sucesso": true, "mensagem": "Documento enviado com sucesso" }
```

---

## Webhook

### POST /webhook/evolution

Público. Recebe eventos do Evolution API.

Response 200
```json
{ "status": "received" }
```

### GET /webhook/evolution

Público. Health do webhook.

Response 200
```json
{ "status": "webhook ativo", "service": "evolution" }
```

---

## WhatsApp Chat

Observação
- As rotas exigem Bearer JWT (`require_operador`) no backend.
- Sem token válido, as chamadas retornam `401`.

### GET /whatsapp-chat/conversas

Query params
- `status` ativa | arquivada | aguardando
- `instance` nome da instância
- `limit` 1-100

Response 200
```json
[
  {
    "id": "uuid",
    "numero_telefone": "5511999999999",
    "nome_contato": null,
    "instance_name": "fc-solucoes",
    "status": "ativa",
    "ultima_mensagem_em": "2026-02-05T12:00:00Z",
    "created_at": "2026-02-05T12:00:00Z"
  }
]
```

### GET /whatsapp-chat/conversas/{conversa_id}

Response 200
```json
{
  "id": "uuid",
  "numero_telefone": "5511999999999",
  "nome_contato": null,
  "instance_name": "fc-solucoes",
  "status": "ativa",
  "contexto_ia": {},
  "ultima_mensagem_em": "2026-02-05T12:00:00Z",
  "created_at": "2026-02-05T12:00:00Z",
  "updated_at": "2026-02-05T12:00:00Z",
  "mensagens": []
}
```

### GET /whatsapp-chat/conversas/{conversa_id}/mensagens

Query params
- `limit` 1-200

Response 200
```json
[
  {
    "id": "uuid",
    "tipo_origem": "usuario",
    "conteudo": "Olá",
    "lida": false,
    "enviada": true,
    "created_at": "2026-02-05T12:00:00Z"
  }
]
```

### POST /whatsapp-chat/conversas/{conversa_id}/arquivar

Response 200
```json
{ "status": "arquivada" }
```

### GET /whatsapp-chat/status

Response 200
```json
{ "conversas_ativas": 0, "mensagens_hoje": 0, "status": "online" }
```

---

## VIVA (Chat Interno)

### POST /viva/chat

Requer Bearer.

Request (JSON)
```json
{
  "mensagem": "Olá, VIVA",
  "prompt_extra": "Campo legado (opcional); mantido por compatibilidade, sem uso ativo no runtime atual",
  "contexto": [
    {
      "id": "123",
      "tipo": "usuario",
      "conteudo": "Oi",
      "timestamp": "2026-02-05T12:00:00Z",
      "modo": "CRIADORLANDPAGE"
    }
  ]
}
```

Response 200
```json
{
  "resposta": "...",
  "midia": [
    { "tipo": "imagem", "url": "https://..." }
  ]
}
```

### POST /viva/vision

Requer Bearer.

Request (JSON)
```json
{
  "image_base64": "<base64 sem data:>",
  "prompt": "Descreva a imagem"
}
```

Response 200
```json
{ "analise": "..." }
```

### POST /viva/vision/upload

Requer Bearer.

Request (multipart/form-data)
- `file` arquivo de imagem
- `prompt` opcional

Response 200
```json
{ "analise": "..." }
```

### POST /viva/audio/transcribe

Requer Bearer.

Request (multipart/form-data)
- `file` arquivo de áudio

Response 200
```json
{ "transcricao": "..." }
```

### POST /viva/image/generate

Requer Bearer.

Request (JSON)
```json
{
  "prompt": "Imagem de escritório moderno",
  "width": 1024,
  "height": 1024
}
```

Response 200
```json
{ "success": true, "url": "..." }
```

### GET /viva/status

Requer Bearer.

Response 200 (exemplo modo local)
```json
{ "api_configurada": true, "modelo": "VIVA Local (Sem API)", "tipo": "Templates pré-programados" }
```

Response 200 (exemplo OpenRouter)
```json
{ "api_configurada": true, "modelo": "meta-llama/llama-3.2-3b-instruct:free", "tipo": "OpenRouter (Gratuito)" }
```

---

## Health

### GET /health

Response 200
```json
{ "status": "healthy", "version": "1.0.0" }
```

### GET /

Response 200
```json
{ "message": "FC Soluções Financeiras API", "version": "1.0.0", "docs": "/docs" }
```

---

*Documento atualizado em: 2026-02-05*

---

## Contrato operacional WhatsApp VIVA (negocio) - V1

Data de aprovacao: 07/02/2026

### Comportamento esperado da assistente
- Identidade: Viviane, consultora de negocios da Rezeta.
- Nao iniciar com declaracao de IA.
- Linguagem humana, contextual e sem resposta enlatada.
- Politica P1 (curta) com fallback P2 para cliente formal.

### Coleta minima obrigatoria no atendimento
- Nome
- Telefone
- Servico desejado
- Cidade
- Urgencia

### Regras comerciais
- Recomendar Diagnostico 360 como primeiro passo padrao.
- Permitir venda direta para Limpa Nome, Score e Rating.
- Oferta inicial com +15% sobre tabela interna.
- Negociacao de ajuste final: apenas atendimento humano.

### Regras de escala para humano
Escalar quando houver:
- pedido explicito de humano;
- reclamacao;
- urgencia critica;
- duvida juridica/financeira sensivel;
- negociacao de valor;
- assunto fora do catalogo oficial.

### Registro de follow-up
Quando o motivo de nao fechamento for financeiro, registrar no cliente:
- `motivo_nao_fechamento = financeiro`
- `acao_followup = pendente`
- `retorno_previsto = data definida pela operacao`

### Fonte de regras/precos
- `frontend/src/app/viva/REGRAS/Descrição_Detalhada_dos_Serviços_Rezeta_Brasil.md`
- `frontend/src/app/viva/REGRAS/tabela_precos_ia_01_planilha1.csv`
