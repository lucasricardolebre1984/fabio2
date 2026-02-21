# VIVA Stream Canonical Orchestration (2026-02-21)

## Objetivo
- Eliminar divergencia entre `/api/v1/viva/chat` e `/api/v1/viva/chat/stream`.
- Garantir que stream nao confirme acao operacional sem execucao real no SaaS.

## Sintoma validado
- Conversa no `/viva` confirmou criacao de agenda.
- Painel `/agenda` nao exibiu o compromisso informado na resposta do chat.
- Logs mostraram uso predominante de `POST /api/v1/viva/chat/stream`.

## Causa raiz
- O caminho de stream mantinha logica separada e nao reaproveitava toda a orquestracao deterministica do caminho canonico.
- Isso permitia resposta livre do modelo para intencoes que exigem execucao real (agenda, consultas de dominio, etc.).

## Correcao aplicada
- `handle_chat_with_viva_stream` passou a delegar para `handle_chat_with_viva`.
- A resposta canonica e emitida em SSE como:
  - chunk unico `content`;
  - evento final `done` com `session_id`.

## Resultado esperado
- Mesmo comportamento funcional entre chat normal e chat stream.
- Sem "feito/agendado" quando a agenda nao foi realmente criada.
- Sem loops de desambiguacao fora da persona canonica para comandos diretos.

## Arquivo alterado
- `backend/app/services/viva_chat_orchestrator_service.py`
