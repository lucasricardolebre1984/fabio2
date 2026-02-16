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
- Agenda: operacional no modulo web, com inconsistencia no fluxo via VIVA (BUG-104)
- Campanhas: operacional com persistencia, ainda com pendencia de aderencia semantica (BUG-015/BUG-099)
- WhatsApp: operacional
- VIVA: operacional com inconsistencias de orquestracao (BUG-104, BUG-105, BUG-106, BUG-107)

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
- BUG-104: agenda confirma criacao, mas consulta posterior pode nao refletir
- BUG-105: VIVA nao consulta consistentemente dados reais de modulos SaaS
- BUG-106: excesso de confirmacoes e quebra de ordem direta
- BUG-107: drift de memoria/persona fora da ancora canonica

## Evidencias desta rodada

- Matriz menu -> API -> banco -> COFRE: `docs/AUDIT/menu-endpoint-matrix.md`
- Auditoria documental: `docs/AUDIT/DOCS_AUDIT_2026-02-16.md`

## Diretriz de deploy institucional

- Alvo principal: Ubuntu AWS virgem (stack Docker)
- Nao usar Vercel como alvo institucional desta operacao

Atualizado em: 2026-02-16
