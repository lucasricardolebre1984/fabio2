# Auditoria - Anexos Fixos em Contratos

Data: 2026-03-11  
Escopo: insercao automatica de anexos institucionais no layout de contratos (preview/impressao/PDF), preservando o padrao visual existente.

## Contexto de governanca

- Execucao autorizada pelo usuario como excecao operacional pre-Gate0.
- Modulo afetado: `core-contratos`.
- Contrato afetado: renderizacao final do documento contratual.
- Eventos afetados: nenhum evento de runtime foi criado/alterado.

## Requisito implementado

1. `TERMODECIENCIAGERAL.md` anexado automaticamente em todos os contratos.
2. `TERMODECIENCIARATING.md` anexado automaticamente apenas em:
   - `aumento_score`
   - `rating_convencional`
   - `rating_express_pj`
   - `rating_full_pj`
3. Preenchimento restrito ao cabecalho dos anexos:
   - numero do contrato
   - data
   - nome do cliente
   - documento do cliente
4. Campos de assinatura permanecem como campos fixos de assinatura.

## Tratamento de conteudo

- O arquivo de rating fornecido continha conteudo de conversa + bloco markdown.
- Foi aplicada sanitizacao para persistir apenas o texto juridico do anexo em `contratos/anexos/TERMODECIENCIARATING.md`.

## Arquivos alterados

- `contratos/anexos/TERMODECIENCIAGERAL.md`
- `contratos/anexos/TERMODECIENCIARATING.md`
- `backend/app/services/contrato_annex_loader.py`
- `backend/app/services/contrato_service.py`
- `backend/app/services/pdf_service_playwright.py`
- `backend/app/services/pdf_service.py`
- `backend/app/schemas/contrato.py`
- `backend/tests/test_contrato_annex_loader.py`
- `frontend/src/lib/pdf.ts`
- `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
- `docs/BUGSREPORT.md`
- `docs/STATUS.md`
- `docs/SESSION.md`

## Validacoes executadas

- `python -m py_compile backend/app/services/contrato_annex_loader.py backend/app/services/contrato_service.py backend/app/services/pdf_service_playwright.py backend/app/services/pdf_service.py backend/app/schemas/contrato.py` -> OK
- `npm run lint -- --file "src/lib/pdf.ts" --file "src/app/(dashboard)/contratos/[id]/page.tsx"` -> OK
- `PYTHONPATH=c:\\projetos\\fabio2\\backend DEBUG=false pytest tests/test_contrato_annex_loader.py -q` -> `2 passed`

## Rollback institucional

- Baseline pre-fix:
  - `backend/COFRE/system/blindagem/rollback/rollback_contratos_anexos_fixos_20260311_111327_pre_fix_baseline.txt`
- Patch da rodada:
  - `backend/COFRE/system/blindagem/rollback/rollback_contratos_anexos_fixos_20260311_111327.patch`
