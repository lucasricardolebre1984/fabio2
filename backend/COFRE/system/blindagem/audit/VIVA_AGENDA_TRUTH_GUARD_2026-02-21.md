# VIVA Agenda Truth Guard (2026-02-21)

## Objetivo
- Evitar confirmacao falsa de criacao/consulta de agenda no chat da VIVA.
- Reforcar saudacao institucional com "Fabio" no cumprimento.

## Alteracao aplicada
- Arquivo: `backend/app/services/viva_chat_orchestrator_service.py`
- Mudancas:
  - Aplicado `_ensure_fabio_greeting(...)` antes do `finalize` de resposta livre.
  - Validacao de payload de agenda com tratamento de `ValidationError/ValueError/TypeError` antes de criar evento.
  - Guardas anti-hallucination:
    - se resposta afirma criacao sem `agenda_created=True`, retorna mensagem de nao confirmacao.
    - se resposta afirma consulta sem `agenda_checked=True`, retorna mensagem de nao confirmacao.
  - Logs de sucesso de criacao:
    - `viva_agenda_create_ok user_id=... evento_id=... titulo=... data_inicio=...`

## Resultado esperado
- VIVA nao confirma "criei/marquei/consultei" sem execucao real comprovada.
- Saudacoes simples retornam com padrao contendo "Fabio".
