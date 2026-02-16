# STATUS do projeto - FC Solucoes Financeiras

Data: 2026-02-16
Status geral: operacional em ambiente local, com pendencias criticas abertas na VIVA (agenda, consulta de dados reais e obediencia de comando direto).

## Fonte de verdade ativa

- Persona canonica: `backend/COFRE/persona-skills/AGENT.md`
- Skills canonicas: `backend/COFRE/persona-skills/*.md`
- Memorias canonicas: `backend/COFRE/memories/<tabela>/`
- Protocolo: `docs/COFRE_RAG_PROTOCOL.md`

## Estado dos modulos

- Contratos: operacional
- Clientes: operacional
- Agenda: operacional no modulo web, com ajuste de saudacao da VIVA em validacao (BUG-104)
- Campanhas: operacional com persistencia, ainda com pendencia de aderencia semantica (BUG-015/BUG-099)
- WhatsApp: operacional
- VIVA: operacional com inconsistencias de orquestracao (BUG-104, BUG-107) e correcao de contratos em validacao (BUG-105, BUG-106)

## Veredito gate a gate (auditoria vigente)

- Gate 1 Seguranca: Parcial
- Gate 2 Streaming VIVA: Parcial
- Gate 3 Frontend Performance: Parcial
- Gate 4 UX VIVA: Parcial
- Gate 5 Voz/TTS: Parcial
- Gate 6 Google Calendar: Parcial
- Gate 7 Testes: Nao concluido
- Gate 8 Build/Deploy: Parcial
- Gate 9 Documentacao/Rollback final: Em consolidacao nesta rodada

## Pendencias criticas abertas

- BUG-099: latencia alta no chat interno da VIVA
- BUG-104: em validacao apos ajuste de consulta de agenda (`liste`/`lite agenda`) e estabilizacao de saudacao
- BUG-105: em validacao apos ajuste de roteamento de contratos (modelos vs emitidos por cliente)
- BUG-106: em validacao apos ajuste de confirmacoes curtas
- BUG-107: drift de memoria/persona fora da ancora canonica

## Evidencias desta rodada

- Matriz menu -> API -> banco -> COFRE: `docs/AUDIT/menu-endpoint-matrix.md`
- Auditoria documental: `docs/AUDIT/DOCS_AUDIT_2026-02-16.md`

## Diretriz de deploy institucional

- Alvo principal: Ubuntu AWS virgem (stack Docker)
- Nao usar Vercel como alvo institucional desta operacao

Atualizado em: 2026-02-16
