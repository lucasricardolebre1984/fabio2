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

## Rodada 2 (ajuste forte)
- foco: ampliar ainda mais area util horizontal e reduzir altura do composer.
- mudancas:
  - menu lateral: `w-56` -> `w-52`
  - header: `px-4 py-3` -> `px-3 py-2`
  - coluna de mensagens: `max-w-5xl` -> `w-full` (full width util)
  - bolhas: `max-w-[88%]` -> `max-w-[94%]`
  - input height: `56..160` -> `44..120`
  - textarea: `text-base/leading-6` -> `text-sm/leading-5`
  - botao enviar: `h-12` -> `h-10`

## Rodada 3 (espaco morto inferior)
- foco: remover area vazia no rodape causada por padding do `AppShell`.
- mudanca:
  - container raiz do `/viva` com full-bleed: `-m-4 md:-m-8` + `overflow-hidden`.

## Validacao
- Screenshot pos-ajuste:
  - `docs/AUDIT/playwright-viva-layout-2026-02-20.png`
- Metadados da coleta:
  - `docs/AUDIT/playwright-viva-layout-2026-02-20.json`
- Evidencias rodada 2:
  - `docs/AUDIT/playwright-viva-layout-tuning2-2026-02-20.png`
  - `docs/AUDIT/playwright-viva-layout-tuning2-2026-02-20.json`
- Evidencias rodada 3:
  - `docs/AUDIT/playwright-viva-layout-tuning3-2026-02-20.png`
  - `docs/AUDIT/playwright-viva-layout-tuning3-2026-02-20.json`

## Rollback
- Pre-change documentado em:
  - `backend/COFRE/system/blindagem/rollback/ROLLBACK_VIVA_CHAT_LAYOUT_20260220_120200.md`
- Rodada 2:
  - `backend/COFRE/system/blindagem/rollback/ROLLBACK_VIVA_CHAT_LAYOUT_TUNING2_20260220_123800.md`
  - `backend/COFRE/system/blindagem/rollback/rollback_viva_chat_layout_tuning2_20260220_124500.patch`
- Rodada 3:
  - `backend/COFRE/system/blindagem/rollback/rollback_viva_chat_layout_tuning3_pre_20260220_124900.patch`
