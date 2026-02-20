# VIVA Chat Layout Space Audit - 2026-02-20

## Objetivo
- Melhorar aproveitamento da tela na aba `/viva` sem alterar fluxo funcional do chat.

## Evidencia inicial
- Print do operador mostrou perda de area util no chat (input alto + coluna central estreita).

## Ajuste aplicado
- Arquivo: `frontend/src/app/viva/page.tsx`
- Mudancas:
  - `h-[calc(100vh-4rem)]` -> `h-[calc(100dvh-4rem)] min-h-0`
  - `w-64` -> `w-56` no menu lateral
  - header reduzido (`px-6 py-4` -> `px-4 py-3`)
  - mensagens: `max-w-3xl` -> `max-w-5xl`
  - bolha: `max-w-[80%]` -> `max-w-[88%] lg:max-w-[82%]`
  - input: `rows=3` -> `rows=2`
  - input height: `88..220` -> `56..160`
  - aviso inferior com menor altura visual

## Validacao
- Screenshot pos-ajuste:
  - `docs/AUDIT/playwright-viva-layout-2026-02-20.png`
- Metadados da coleta:
  - `docs/AUDIT/playwright-viva-layout-2026-02-20.json`

## Rollback
- Pre-change documentado em:
  - `backend/COFRE/system/blindagem/rollback/ROLLBACK_VIVA_CHAT_LAYOUT_20260220_120200.md`

