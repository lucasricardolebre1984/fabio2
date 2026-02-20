# Manual de Configuração - Logo no Layout de Contratos

Data: 2026-02-20  
Escopo: orientar qualquer agente a ajustar somente a logo do cabecalho institucional de contratos, sem quebrar preview e PDF.

## Objetivo

Ajustar tamanho/proporcao da logo no cabecalho azul dos contratos, mantendo:
- rota funcional: `/contratos/{id}`;
- consistencia visual institucional;
- rastreabilidade com rollback no COFRE.

## Arquivos que controlam a logo

1. Preview da tela de contrato (frontend):
- `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
- asset recomendado para balanca proporcional sem crescer faixa:
  - `frontend/public/logo2-tight.png`
  - `contratos/logo2-tight.png` (para PDF backend)

2. PDF gerado pelo navegador (botao Visualizar PDF/Download):
- `frontend/src/lib/pdf.ts`

3. PDF backend (`GET /api/v1/contratos/{id}/pdf`):
- `backend/app/services/pdf_service_playwright.py`

## Regras de alteracao (cirurgica)

- Alterar apenas parametros de logo (width, height, classes/CSS da logo).
- Quando a logo tiver margens transparentes excessivas, preferir asset recortado (tight) em vez de `scale` com clipping.
- Nao alterar textos juridicos, clausulas, placeholders ou estrutura de dados.
- Nao alterar cores, tipografia ou fluxo de salvamento/envio.
- Manter o path da imagem oficial: `logo2.png`.

## Fluxo institucional recomendado

1. Criar rollback pre-fix no COFRE:
- `backend/COFRE/system/blindagem/rollback/rollback_<contexto>_<timestamp>_pre_fix_baseline.txt`

2. Aplicar ajuste no arquivo-alvo.

3. Validar:
- abrir `/contratos/{id}` e conferir cabecalho;
- gerar PDF pelo frontend;
- testar endpoint de PDF backend.

4. Registrar evidencias:
- atualizar `backend/COFRE/system/blindagem/BLINDAGEM_INDEX.md`;
- registrar auditoria curta em `backend/COFRE/system/blindagem/audit/`.

## Checklist rapido para agentes

- [ ] Ajuste ficou restrito ao tamanho/proporcao da logo.
- [ ] Cabecalho nao perdeu alinhamento.
- [ ] Preview da rota `/contratos/{id}` continua renderizando.
- [ ] PDF frontend continua abrindo.
- [ ] PDF backend continua retornando `200`.
- [ ] Rollback institucional criado e referenciado no COFRE.

## Rollback padrao

Se houver regressao, restaurar arquivos do commit baseline:

```bash
git restore --source=<commit_baseline> -- "frontend/src/app/(dashboard)/contratos/[id]/page.tsx"
git restore --source=<commit_baseline> -- "frontend/src/lib/pdf.ts"
git restore --source=<commit_baseline> -- "backend/app/services/pdf_service_playwright.py"
```

Depois, revalidar `/contratos/{id}` e PDF.
