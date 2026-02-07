# STATUS do projeto - FC Solucoes Financeiras

Data: 07/02/2026
Sessao: alinhamento final da operacao WhatsApp VIVA com cliente
Status: V1.5 homologada localmente com cliente (OpenAI + Evolution estável)

## Objetivo atual
Consolidar operacao comercial da Viviane no WhatsApp com regras de negocio,
qualificacao de lead, politica de preco e governanca de atendimento humano.

## Funcionalidades operacionais
- Contratos com templates dinamicos
- Clientes e agenda
- Chat interno VIVA em `/viva`
- Conexao WhatsApp em `/whatsapp`
- Gestao de conversas em `/whatsapp/conversas`

## Estado WhatsApp/VIVA
- Instancia Evolution definitiva: `fc-solucoes`
- Instancia de teste removida: `tmp-fc-8601`
- Persona comercial aprovada: Viviane, consultora da Rezeta
- Fontes de conhecimento organizadas em `frontend/src/app/viva/REGRAS`
- Provedor IA ativo: OpenAI (`gpt-5-mini`)

## Decisoes validadas com cliente
- Modo B (VIVA conduz; humano por excecao)
- Tom hibrido (consultivo + acolhedor)
- Fluxo 1 (objetivo -> perfil -> urgencia -> proximo passo)
- SLA 24/7 com callback em ate 15 min
- Coleta obrigatoria: nome, telefone, servico, cidade, urgencia
- Diagnostico 360 como recomendacao inicial
- Venda direta sem 360: Limpa Nome, Score e Rating
- Oferta inicial com margem de 15% sobre tabela
- Negociacao fina de preco somente com humano
- Objecao financeira registrada para follow-up

## Proximo gate
Iniciar ciclo de melhoria incremental (etiquetas de lead, scripts PF/PJ e painel de metricas),
mantendo observabilidade do webhook e taxa de conversao.

## Documentos de referencia
- `docs/WHATSAPP_VIVA_PACOTE_DEFINITIVO.md`
- `docs/INTEGRACAO_WHATSAPP_VIVA.md`
- `docs/DECISIONS.md`
- `docs/SESSION.md`
- `docs/API.md`

---

Atualizado em: 07/02/2026
