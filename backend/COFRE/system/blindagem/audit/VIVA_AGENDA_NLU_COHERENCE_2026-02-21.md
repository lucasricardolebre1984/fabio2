# Blindagem: Coerencia Agenda VIVA (2026-02-21)

## Sintoma observado

- VIVA confirmava criacao de compromisso em casos como `crie para daqui meia hora ...`, mas o compromisso nao aparecia na agenda SaaS.
- Consulta `o que tem na agenda` podia cair em fluxo conversacional generico em vez de consulta deterministica.

## Causa raiz

- O parser de criacao natural nao reconhecia comando com verbo `crie` isolado.
- O parser relativo nao tratava `daqui meia hora`.
- A deteccao de consulta nao cobria frases comuns como `o que tem na agenda`, `agenda de ontem` e consulta por data/hora explicita.

## Correcao aplicada

- Ampliado NLU de criacao:
  - verbos: `criar`/`crie`;
  - relativo: suporte a `daqui meia hora`.
- Ampliado NLU de consulta:
  - frases: `o que tem na agenda`, `agenda de ontem`, `consultar/verifique agenda`;
  - janela com data/hora explicita (`DD/MM/AAAA HH:MM`) e data explicita.

## Arquivo alterado

- `backend/app/services/viva_agenda_nlu_service.py`

## Validacao sugerida

1. `o que tem na agenda`
2. `hoje`
3. `crie para daqui meia hora ACORDA NEGAO`
4. `verifique a agenda de ontem`
5. `verifique a agenda em 20/02/2026 22:25`

Resultado esperado:
- consultas sempre usam rota de agenda;
- criacao retorna evento real e aparece no painel.
