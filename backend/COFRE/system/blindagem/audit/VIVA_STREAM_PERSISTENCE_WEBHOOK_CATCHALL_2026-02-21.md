# Blindagem: Persistencia VIVA Stream + Webhook Evolution Catchall (2026-02-21)

## Sintomas em producao

- Chat VIVA (web) exibia respostas, mas as sessoes ficavam com `message_count=1` e/ou o snapshot retornava apenas mensagens do usuario.
- Em streaming (SSE), o frontend recebia `done` antes da persistencia final, e desconexoes podiam interromper a gravacao.
- Evolution (WhatsApp) podia enviar webhooks por evento em paths diferentes, gerando `404` no backend quando `byEvents=true`.

## Causa raiz

- `append_chat_message()` insere no banco, mas nao executa `commit()` automaticamente.
- `handle_chat_with_viva()` e `handle_chat_with_viva_stream()` gravavam mensagens `ia` sem commit explicito.
- O streaming emitia `done` antes de persistir a resposta completa.
- Rota do webhook existia apenas em `/api/v1/webhook/evolution`, mas a Evolution pode chamar `/api/v1/webhook/evolution/<evento>`.

## Correcao aplicada (cirurgica)

- Commit explicito apos gravar mensagens `ia` (non-stream e stream).
- Streaming emite `done` apenas apos persistencia/commit.
- Best-effort: se o cliente desconectar (CancelledError) e houver conteudo parcial, tenta persistir.
- Webhook catchall: aceita `/api/v1/webhook/evolution/{path:path}` e injeta `event` a partir do path quando ausente.

## Arquivos alterados

- `backend/app/services/viva_chat_orchestrator_service.py`
- `backend/app/api/v1/webhook.py`
- `docs/STATUS.md`

## Validacao recomendada (EC2)

1) Streaming:

```bash
curl -sS -N https://fabio.automaniaai.com.br/api/v1/viva/chat/stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mensagem":"teste persistencia","contexto":[]}' | head -n 20
```

2) Verificar que o snapshot inclui mensagens `usuario` e `ia`:

```bash
curl -sS https://fabio.automaniaai.com.br/api/v1/viva/chat/snapshot \
  -H "Authorization: Bearer $TOKEN" | jq '.messages | length'
```

3) Webhook catchall (simulacao):

```bash
curl -sS -X POST https://fabio.automaniaai.com.br/api/v1/webhook/evolution/messages-upsert \
  -H "Content-Type: application/json" \
  -d '{"data": {"key": "dummy"}}'
```

