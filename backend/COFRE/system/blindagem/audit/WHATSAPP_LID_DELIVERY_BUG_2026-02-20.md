# BUG REPORT - WhatsApp @lid sem entrega no celular

- Data: 2026-02-20
- Contexto: homologacao SaaS FC Solucoes (VIVA/Viviane)
- Severidade: alta (risco de perda de lead)

## Sintoma

- Mensagem entra no SaaS (`whatsapp/conversas`), VIVA responde no painel, mas o cliente nao recebe no celular em alguns chats.
- Casos recorrentes com `remoteJid` no formato `@lid`.

## Evidencia tecnica

1. Evolution logs:
- inbound: `messages.upsert` com `remoteJid: <id>@lid`
- outbound: `sendText` retorna `exists:false` para `<id>@lid`

2. Banco (`whatsapp_mensagens`):
- mensagens IA com `enviada=false`
- erro com payload `exists:false`.

3. Banco (`whatsapp_conversas.contexto_ia`):
- quando falha em `@lid`, fila `pending_outbound` fica preenchida.
- indicador de recuperacao: `needs_manual_bind=true`.

## Causa raiz

- Em parte dos eventos o provedor entrega apenas identificador `@lid` sem numero real roteavel (`@s.whatsapp.net`) no evento de mensagem.
- Sem numero real confiavel, o envio nao e roteavel automaticamente.

## Correcoes aplicadas

1. Fila resiliente:
- Mensagens nao entregues em `@lid` entram em `pending_outbound` para reprocesso.

2. Manual bind + flush:
- Endpoint: `POST /api/v1/whatsapp-chat/conversas/{conversa_id}/bind-number`
- Registra `resolved_whatsapp_number` no contexto e dispara flush imediato da fila.

3. Guard rails de seguranca:
- Removida heuristica insegura de mapeamento por nome/foto para evitar envio para numero errado.
- Permitidas apenas fontes confiaveis (`manual_bind`, `lid_meta`, `prior_lid_binding`, `user_text` validado).

## Procedimento operacional homologacao

1. Receber mensagem nova no chat.
2. Se resposta nao sair no celular e houver `@lid` + `exists:false`, executar bind manual do numero real.
3. Confirmar flush (`pending_sent > 0`).
4. Revalidar no celular alvo.

## Critero de aceite

- Conversas com numero roteavel: entrega automatica.
- Conversas `@lid` sem numero resolvido: sinalizacao explicita para bind (sem perda silenciosa).
- Sem envio para numero inferido de forma insegura.
