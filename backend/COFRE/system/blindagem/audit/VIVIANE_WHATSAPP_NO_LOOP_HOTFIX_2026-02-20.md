# Viviane WhatsApp - Hotfix Anti-Loop (2026-02-20)

## Escopo
- Remover perda de lead por repeticao de perguntas no atendimento externo da Viviane.
- Blindar handoff humano para nao ficar em ciclo de confirmacao.
- Separar formalmente a persona Viviane no COFRE.

## Causa raiz observada
- Extracao de nome falhava em frase natural (`fala com Glauco`), forçando repeticao.
- Cidade em resposta curta (`Ribeirao Preto`) nao era consolidada quando contexto ja esperava cidade.
- Pedido de humano era aceito, mas fluxo voltava a perguntar transferencia/cidade varias vezes.

## Correcao aplicada
- Arquivo: `backend/app/services/viva_ia_service.py`
  - novos gatilhos de handoff humano (inclusive variacoes femininas);
  - estado de handoff no contexto (`requested` -> `in_progress`);
  - respostas de handoff sem loop e sem repetir historico;
  - extracao de nome em linguagem natural (`fala com`, `me chama de`, `Nome, ...`);
  - extracao de cidade por resposta curta quando contexto exige cidade.
- Arquivo: `backend/COFRE/persona-skills/viviane/AGENT.md`
  - prompt canonico da persona WhatsApp externa.
- Arquivo: `backend/COFRE/persona-skills/viva/AGENT.md`
  - governanca explicita: VIVA interna separada da Viviane externa.
- Arquivo: `backend/COFRE/README.md`
  - estrutura canonica atualizada para duas personas no COFRE.

## Evidencias
- Endpoints runtime:
  - `backend/COFRE/system/blindagem/audit/ENDPOINTS_RUNTIME_SNAPSHOT_2026-02-20_113105.md`
  - `backend/COFRE/system/blindagem/audit/endpoints-runtime-2026-02-20_113105.json`
- UI WhatsApp (Playwright):
  - `backend/COFRE/system/blindagem/audit/playwright-whatsapp-conversas-2026-02-20.json`
  - `docs/AUDIT/playwright-whatsapp-conversas-2026-02-20.png`

## Resultado esperado
- Menos friccao no fluxo comercial.
- Transferencia humana objetiva, sem insistencia.
- Menor risco de cancelamento por repeticao.


