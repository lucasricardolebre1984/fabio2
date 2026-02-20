# VIVIANE Naturalidade - Blindagem 2026-02-20

## Objetivo
- Blindar comportamento da Viviane para atendimento natural.
- Eliminar preco espontaneo nao solicitado.
- Preservar contexto e reduzir friccao de lead.

## Mudancas de codigo
- `backend/app/services/viva_ia_service.py`
  - `_resposta_identidade_variada(...)` com branch de empatia para feedback de tom/preco.
  - `_is_money_humor_intent(...)` + `_build_money_humor_reply(...)`.
  - `_remover_preco_nao_solicitado(...)` + `_sentenca_tem_preco(...)`.
  - `asked_price` em `_garantir_resposta_texto(...)`.
  - regra dinamica no prompt: preco apenas sob demanda.
- `backend/COFRE/persona-skills/VIVIANE.md`
  - politicas de naturalidade e preco ajustadas.
- `backend/tests/test_viviane_humanizacao.py`
  - testes de regressao novos para os cenarios acima.

## Validacao
- `PYTHONPATH=C:\\projetos\\fabio2\\backend pytest tests/test_viviane_humanizacao.py -q`
- Resultado: `17 passed`.

