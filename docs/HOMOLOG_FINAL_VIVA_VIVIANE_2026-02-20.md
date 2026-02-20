# Homologacao Final - VIVA/Viviane no SaaS

- Data: 2026-02-20
- Objetivo: fechar homologacao funcional do SaaS com atendimento WhatsApp natural, sem perda de lead.

## Escopo final do projeto (nivel SaaS)

1. Core SaaS
- Clientes, Contratos, Agenda, Campanhas, WhatsApp e Chat IA VIVA.

2. Integracao WhatsApp
- Evolution API conectada e operacional.
- Webhook Evolution -> Backend (`/api/v1/webhook/evolution`).
- Chat SaaS consumindo conversas/mensagens de `whatsapp_conversas` e `whatsapp_mensagens`.

3. Persona ativa
- Uma unica persona comercial: Viviane.
- Naturalidade alta de conversa, sem respostas mecanicas repetitivas.
- Base comercial controlada por regras de produtos/precos.

## Endpoints runtime validados

- Catalogo principal de API: `docs/API_ENDPOINTS_CATALOG_2026-02-20.md`
- Snapshot complementar de runtime: `docs/ENDPOINTS_RUNTIME_2026-02-20.md`

## Estado da entrega WhatsApp

- Evolucao de stack aplicada para estabilizar `@lid`:
  - imagem: `evoapicloud/evolution-api:v2.3.7`
- Evidencia: envios `@lid` sem erro `exists:false` observado na stack antiga.

## Regras de separacao documental

1. `docs/`
- Documentacao de projeto (arquitetura, endpoints, status de homologacao, plano final).

2. `backend/COFRE/`
- Conteudo exclusivo de VIVA/Viviane:
  - persona
  - memorias
  - auditoria de fluxo Viva/WhatsApp
  - blindagem/rollback de componentes da IA

## Plano de implementacao final (proxima etapa)

1. Humanizacao conversacional total
- reduzir insistencia em coleta de nome
- responder perguntas abertas com contexto e fluidez
- manter foco comercial com transicao suave para coleta minima

2. Escopo de conhecimento
- restringir respostas de produto/preco a regras oficiais da pasta de regras
- manter o restante da conversa com condução natural do modelo

3. Multimodal
- consolidar trilha: audio entrada, imagem entrada, audio saida
- garantir fallback amigavel em falha de transcricao/tts

4. Conversao de lead
- garantir captura minima para CRM interno (nome + objetivo + contato + etapa)
- evitar perda silenciosa com fila/rastreabilidade

5. Homologacao final
- roteiro de testes ponta a ponta
- checklist de aceite operacional
