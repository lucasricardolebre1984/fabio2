# VIVA Chat Layout - Blindagem de Espaco (2026-02-20)

## Escopo
- Correção visual cirúrgica da tela `/viva` para ampliar area util do chat.
- Sem impacto em regras de negocio, backend ou persona Viviane.

## Arquivo alterado
- `frontend/src/app/viva/page.tsx`

## Alteracoes
- Largura/altura do layout ajustadas para melhor uso de viewport.
- Input mais compacto para liberar area de leitura.
- Container de conversa ampliado para reduzir espaco morto lateral.
- Rodada 2: composicao full-width + input mais baixo.
- Rodada 3: full-bleed no container do `/viva` para remover espaco morto inferior.

## Evidencias
- `backend/COFRE/system/blindagem/audit/playwright-viva-layout-2026-02-20.png`
- `backend/COFRE/system/blindagem/audit/playwright-viva-layout-2026-02-20.json`
- `backend/COFRE/system/blindagem/audit/playwright-viva-layout-tuning2-2026-02-20.png`
- `backend/COFRE/system/blindagem/audit/playwright-viva-layout-tuning2-2026-02-20.json`
- `backend/COFRE/system/blindagem/audit/playwright-viva-layout-tuning3-2026-02-20.png`
- `backend/COFRE/system/blindagem/audit/playwright-viva-layout-tuning3-2026-02-20.json`

## Rollback pre-change
- `backend/COFRE/system/blindagem/rollback/ROLLBACK_VIVA_CHAT_LAYOUT_20260220_120200.md`
- `backend/COFRE/system/blindagem/rollback/ROLLBACK_VIVA_CHAT_LAYOUT_TUNING2_20260220_123800.md`
- `backend/COFRE/system/blindagem/rollback/rollback_viva_chat_layout_tuning2_20260220_124500.patch`
- `backend/COFRE/system/blindagem/rollback/rollback_viva_chat_layout_tuning3_pre_20260220_124900.patch`
