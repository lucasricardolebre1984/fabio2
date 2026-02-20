# Auditoria - Ajuste de Logo no Layout de Contratos

Data: 2026-02-20  
Escopo: ajuste de proporcao da logo no cabecalho institucional dos contratos, sem aumentar a faixa azul.

## Solicitacao validada

- Ajustar apenas a logo no layout de contratos (rota de visualizacao).
- Executar com rollback institucional e documentacao para agentes.

## Arquivos alterados

- `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
- `frontend/src/lib/pdf.ts`
- `backend/app/services/pdf_service_playwright.py`
- `frontend/public/logo2-tight.png`
- `contratos/logo2-tight.png`
- `docs/CONTRATOS_LAYOUT_LOGO_MANUAL_AGENTES.md`

## Delta aplicado

- Preview da rota `/contratos/{id}`:
  - troca para asset recortado `logo2-tight.png` (sem margens transparentes);
  - logo fixada em `92x92` sem zoom/clip, preservando altura da faixa azul.
- PDF frontend:
  - troca para `logo2-tight.png` mantendo altura da logo em `78px`.
- PDF backend:
  - preferencia para `logo2-tight.png` no loader de assets;
  - box da logo mantida em `88x88` (faixa sem aumento).

## Validacoes executadas

- `python -m py_compile backend/app/services/pdf_service_playwright.py` -> OK
- `npm run lint -- --file "src/app/(dashboard)/contratos/[id]/page.tsx" --file "src/lib/pdf.ts"` -> OK
- `npm run lint -- --file "src/app/(dashboard)/contratos/[id]/page.tsx"` -> OK (ajuste fino da faixa)

## Rollback institucional

- Baseline pre-fix:
  - `backend/COFRE/system/blindagem/rollback/rollback_contratos_logo_layout_20260220_131317_pre_fix_baseline.txt`
- Patch da rodada:
  - `backend/COFRE/system/blindagem/rollback/rollback_contratos_logo_layout_20260220_131317.patch`
