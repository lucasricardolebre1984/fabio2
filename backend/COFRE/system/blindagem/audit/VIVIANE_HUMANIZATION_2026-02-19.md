# Viviane Humanization - 2026-02-19

## Objetivo
Eliminar comportamento insistente no WhatsApp e aumentar naturalidade conversacional para evitar perda de lead.

## Problema observado
- Repeticao excessiva da mesma pergunta de cadastro (ex.: cidade) em mensagens consecutivas.
- Falta de resposta contextual em perguntas de identidade/valor.
- Encerramento frio quando cliente demonstra desinteresse.

## Ajustes aplicados
Arquivo: `backend/app/services/viva_ia_service.py`

1. Regras de persona reforcadas no prompt base
- responder primeiro ao que o cliente acabou de perguntar;
- evitar insistencia na mesma pendencia;
- desacelerar quando houver cansaco/desinteresse.

2. Novos comportamentos de intencao
- `disengage intent`: detecta sinais de saida ("nao quero mais", "vou procurar outra empresa", etc.) e encerra com elegancia sem pressionar.
- `who am i query`: responde dados conhecidos do cliente com naturalidade.
- `price question`: responde valor de forma direta sem prender em pergunta de cadastro no mesmo turno.
- saudacao em fase de atendimento: responde humana e breve, sem repetir coleta obrigatoria a cada "oi".

3. Anti-insistencia por repeticao
- rastreio no contexto: `last_missing_field` e `missing_field_streak`.
- fallback humanizado quando a mesma pendencia repete >= 3 vezes: muda para tom "sem pressa".

## Testes de blindagem
Novo arquivo: `backend/tests/test_viviane_humanizacao.py`
- `test_disengage_intent_detected`
- `test_who_am_i_reply_contains_known_data`
- `test_price_question_detected`
- `test_fallback_reduces_insistence_when_missing_field_repeats`

Execucao:
- `pytest backend/tests/test_viviane_humanizacao.py -q` -> 4 passed
- `pytest backend/tests/test_viva_domain_intents.py backend/tests/test_viviane_humanizacao.py -q` -> 19 passed

## Resultado esperado em conversa real
- Menos repeticao da mesma pergunta.
- Mais naturalidade em interrupcoes e perguntas avulsas.
- Menor friccao no funil sem perder condução comercial.
