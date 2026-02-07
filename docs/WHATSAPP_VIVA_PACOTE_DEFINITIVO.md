# WhatsApp VIVA - pacote definitivo de atendimento

## Objetivo
Implementar atendimento comercial no WhatsApp com linguagem humana,
personalizada, institucional e com controle operacional para conversao.

## Status da base tecnica (07/02/2026)
- Front `/whatsapp` conectado ao backend (`status`, `conectar`, `desconectar`).
- Chat `/whatsapp/conversas` conectado ao backend (`conversas`, `mensagens`,
  `enviar-texto`, `arquivar`).
- Webhook recebe entrada e encaminha para processamento da VIVA.
- Instancia operacional no Evolution: `fc-solucoes`.
- Instancia de teste removida: `tmp-fc-8601`.

## Decisao comercial aprovada com cliente (07/02/2026)

### 1) Modo de operacao
- **Modo B**: VIVA conduz quase todo o atendimento.
- Atendimento humano entra por excecao e negociacao.

### 2) Persona e identidade
- Nome operacional: **Viviane, consultora de negocios da Rezeta**.
- Nao parecer robotica.
- Nao abrir conversa com frase padrao de IA.
- Se cliente insistir em "voce e IA?", responder com variacao humana,
  sem negar de forma seca e sem confirmar tecnicamente.

### 3) Tom de comunicacao
- **Hibrido (Tom 1 + Tom 3)**:
  - consultivo, direto e cordial;
  - simples e acolhedor.
- Regra de adaptacao:
  - conversa comum: P1 (curta);
  - conversa muito formal: P2 (mais completa).

### 4) Fluxo de qualificacao
- **Fluxo 1**: objetivo -> perfil -> urgencia -> proximo passo.
- Coleta obrigatoria minima:
  - nome;
  - telefone;
  - servico desejado;
  - cidade;
  - urgencia.

### 5) Politica de resposta
- Padrao: **P1** (1 a 4 linhas, 1 pergunta por vez, com proximo passo).
- Fallback: **P2** quando o cliente adotar tom formal.
- Encerramento por inatividade: ate **3 tentativas** sem resposta.

### 6) Janela comercial e SLA
- **SLA S3**: atendimento 24/7 com fila e callback.
- Callback fora da janela operacional: **ate 15 minutos**.
- KPI de primeira resposta: alvo de **30 segundos**.

## Regras de transferencia para humano
Transferir quando houver:
- pedido explicito de humano;
- reclamacao;
- urgencia critica;
- duvida sensivel juridica/financeira;
- negociacao de valor/condicao;
- cliente pedindo atendente especifico;
- assunto fora do descritivo oficial dos servicos.

## Regra de oferta comercial
- `Diagnostico 360` deve ser sugerido como primeira recomendacao para
  mapear cenario completo.
- Excecoes de venda direta (sem depender de 360):
  - Limpa Nome;
  - Aumento de Score;
  - Aumento de Rating.

## Politica de preco e negociacao
- Preco base operacional vem da tabela interna.
- Aplicar margem de **+15%** sobre valor de referencia para oferta inicial.
- Ajuste comercial fora da faixa inicial: somente atendimento humano.
- Se nao fechar por preco, registrar no cadastro:
  - motivo nao fechamento = financeiro;
  - acao = follow-up futuro.

## Guardrails fixos
- Nao prometer taxa, prazo, aprovacao ou condicao sem validacao humana.
- Nao inventar informacao juridica/financeira.
- Em caso sensivel, orientar e escalar.
- Linguagem sem jargao tecnico desnecessario.

## Fontes oficiais de conhecimento da Viviane (V1)
- Contexto institucional e portfolio:
  - `frontend/src/app/viva/REGRAS/Descrição_Detalhada_dos_Serviços_Rezeta_Brasil.md`
- Tabela comercial inicial:
  - `frontend/src/app/viva/REGRAS/Tabela Precços IA.xlsx`
  - `frontend/src/app/viva/REGRAS/tabela_precos_ia_01_planilha1.csv`

## Modelo de manutencao continua
- Conhecimento por arquivo versionado no Git.
- Ajustes de preco por tabela, sem reescrever fluxo inteiro.
- Evolucao por revisoes curtas (V1, V1.1, V1.2...).

## KPIs priorizados
- Tempo medio de primeira resposta: **30 segundos**.
- Taxa de transferencia para humano: **indiferente** (foco em conversao).
- Taxa de agendamento/conversao por origem de lead.
- Taxa de abandono da conversa.

## Roadmap acordado
1. Base (pronta): conexao Evolution + chat + webhook + persona.
2. Etiquetas de lead (quente/morno/frio) e prioridade.
3. Scripts de oferta por tipo de cliente (PF/PJ).
4. Painel de metricas operacionais no frontend.

## Gate institucional
- Esta versao documenta o acordo final com o cliente e libera a
  implementacao da V1 de teste no backend.

## Execucao concluida (07/02/2026 - 17:20)
- Homologado localmente com cliente no WhatsApp real.
- VIVA operando com OpenAI (`gpt-5-mini`) no runtime.
- Fluxo comercial da Viviane validado com contexto, qualificacao e proposta.
- Transcricao de audio ativa via OpenAI.
- Processo Evolution consolidado:
  - instancia oficial `fc-solucoes`;
  - webhook unico para backend;
  - `Webhook por Eventos`: OFF;
  - `Webhook Base64`: ON;
  - eventos ativos: `MESSAGES_UPSERT`, `CONNECTION_UPDATE`;
  - integracoes nativas do Evolution mantidas OFF para evitar conflito.

## Ajustes tecnicos complementares (07/02/2026 - noite)
- Contratos voltaram a criar/vincular clientes automaticamente.
- Endpoint de saneamento criado: `POST /api/v1/clientes/sincronizar-contratos`.
- Tela `Clientes` agora tem cadastro manual + sincronizacao.
- Tela `Agenda` minima funcional (criar/listar/concluir/excluir).
- Chat interno da VIVA passou a criar agenda com comando:
  - `agendar TITULO | DD/MM/AAAA HH:MM | descricao opcional`

## Operacao e instalacao
- Runbook completo: `docs/WHATSAPP_INSTALACAO_OPERACIONAL.md`
- Ativacoes obrigatorias no Evolution:
  - Ativo: ON
  - URL: `http://backend:8000/api/v1/webhook/evolution`
  - Webhook por Eventos: OFF
  - Webhook Base64: ON
  - Eventos ON: `MESSAGES_UPSERT`, `CONNECTION_UPDATE`

---

Documento atualizado em: 07/02/2026
