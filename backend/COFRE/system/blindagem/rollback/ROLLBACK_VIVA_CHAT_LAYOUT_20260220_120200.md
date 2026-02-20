# Rollback Pre-Change - Viva Chat Layout (2026-02-20 12:02)

## Base de rollback
- Commit base (antes do ajuste de layout): `e737e2a`
- Arquivo alvo principal:
  - `frontend/src/app/viva/page.tsx`

## Reversao cirurgica (somente layout do chat /viva)
1. Voltar arquivo para o estado base:
```powershell
git -C C:\projetos\fabio2 checkout e737e2a -- frontend/src/app/viva/page.tsx
```

2. Validar diff:
```powershell
git -C C:\projetos\fabio2 diff -- frontend/src/app/viva/page.tsx
```

3. Se estiver correto, commitar rollback:
```powershell
git -C C:\projetos\fabio2 add frontend/src/app/viva/page.tsx
git -C C:\projetos\fabio2 commit -m "revert: restore viva chat layout to pre-20260220 tuning"
git -C C:\projetos\fabio2 push origin main
```

## Escopo
- Este rollback nao toca backend, WhatsApp, persona Viviane ou COFRE de memoria.
- Escopo estrito de UI da tela `/viva`.

