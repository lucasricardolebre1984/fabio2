# VIVA_CAMPAIGN_CONTEXT_TRUTH_GUARD_2026-02-21

## Contexto
- Conversa de campanha no `/viva` quebrava para respostas de agenda no meio do briefing.
- Sintomas observados:
  - resposta indevida `Nao consegui confirmar criacao de compromisso...` durante definicao de CTA;
  - resposta indevida `Total geral de campanhas feitas: N` em mensagens de tema (sem pergunta de contagem);
  - texto alucinado de sucesso (`Campanha criada... Formatos gerados... Local salvo...`) sem execucao real.

## Causas raiz
1. Intent de contagem de campanha ampla demais (`tem`, `temos`, `alguma`) gerava falso positivo.
2. Guard de agenda era aplicado mesmo sem operacao de agenda na mensagem.
3. Follow-up de campanha (ex.: resposta direta de CTA) nao disparava geracao real automaticamente quando havia campanha pendente.
4. Sanitizacao de resposta fake cobria apenas links/publicacao, nao cobria "sucesso de campanha" textual sem execucao.

## Blindagem aplicada
1. `backend/app/services/assistant/intents/campanhas.py`
   - `is_campaign_count_intent` endurecido por regex contextual.
   - Removido gatilho por tokens genericos isolados.

2. `backend/app/services/viva_chat_orchestrator_service.py`
   - Novo helper `_should_generate_pending_campaign_followup(...)`.
   - Follow-up com `CTA`/confirmacao de campanha pendente agora pode disparar geracao real.
   - Guard de agenda so atua quando ha operacao de agenda realmente solicitada.

3. `backend/app/services/viva_chat_runtime_helpers_service.py`
   - ` _sanitize_fake_asset_delivery_reply(...)` ampliado para bloquear "campanha criada + formatos/local salvo" sem execucao real.

## Testes de regressao
- `backend/tests/test_viva_domain_intents.py`
  - novo caso contra falso positivo de contagem em frase de tema de campanha.
- `backend/tests/test_viva_chat_orchestrator_guards.py`
  - cobre detecao de confirmacao de agenda e follow-up de campanha pendente.
- `backend/tests/test_viva_chat_runtime_sanitizers.py`
  - cobre bloqueio de "sucesso fake" textual.

## Validacao executada
```bash
cd backend
set PYTHONPATH=.
pytest tests/test_viva_domain_intents.py tests/test_viva_chat_orchestrator_guards.py tests/test_viva_chat_runtime_sanitizers.py tests/test_evolution_webhook_lid_resolution.py -q
```
Resultado: `28 passed`.

## Rollback
```bash
git restore backend/app/services/assistant/intents/campanhas.py
git restore backend/app/services/viva_chat_orchestrator_service.py
git restore backend/app/services/viva_chat_runtime_helpers_service.py
git restore backend/tests/test_viva_domain_intents.py
git restore backend/tests/test_viva_chat_orchestrator_guards.py
git restore backend/tests/test_viva_chat_runtime_sanitizers.py
```
