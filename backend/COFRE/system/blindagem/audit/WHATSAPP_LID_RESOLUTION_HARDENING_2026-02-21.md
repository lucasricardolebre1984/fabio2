# WHATSAPP_LID_RESOLUTION_HARDENING_2026-02-21

## Contexto
- Sintoma: conversas `@lid` podiam ficar sem resposta no WhatsApp, mesmo com webhook ativo.
- Impacto: mensagem inbound recebida, mas sem entrega outbound em alguns contatos com `remoteJid` mascarado.

## Causa raiz confirmada
- A rotina `_resolve_lid_number` estava restrita a candidatos "explicitos" (preferential + alt metadata).
- Em cenarios comuns de Evolution, esses campos nao vinham preenchidos no payload.
- Resultado: retorno `None` para `@lid`, mantendo `erro_codigo=lid_unresolved` e sem envio final.

## Correcao aplicada
- Arquivo: `backend/app/services/whatsapp_service.py`
- Metodo: `_resolve_lid_number(...)`
- Ajustes:
  1. Mantida validacao forte por `POST /chat/whatsappNumbers/{instance}` antes de qualquer envio.
  2. Reativado match seguro por foto de perfil:
     - aceita apenas quando o match de `profilePicUrl` for unico.
  3. Reativado match por similaridade de nome + proximidade temporal de chat:
     - score minimo por nome;
     - bonus de score por `updatedAt` proximo ao chat `@lid`.
  4. Fallback nao validado continua bloqueado.

## Resultado esperado
- `@lid` com contexto parcial passa a resolver para numero entregavel sem "chute cego".
- Fluxo permanece seguro: candidato so e usado se validado pela Evolution.

## Evidencia de validacao
- Testes executados:
  - `pytest tests/test_whatsapp_lid_resolution.py tests/test_evolution_webhook_lid_resolution.py tests/test_viva_domain_intents.py tests/test_viva_chat_orchestrator_guards.py tests/test_viva_chat_runtime_sanitizers.py -q`
- Resultado:
  - `33 passed`

## Rollback cirurgico
- Reverter apenas bloco `_resolve_lid_number(...)` em:
  - `backend/app/services/whatsapp_service.py`
