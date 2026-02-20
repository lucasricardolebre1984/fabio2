# EVOLUTION LID FIX - Homologacao WhatsApp

- Data: 2026-02-20
- Ambiente: docker local (`c:\projetos\fabio2`)
- Objetivo: eliminar falha de entrega em conversas `@lid`.

## Causa raiz confirmada

1. Stack antiga em uso: `atendai/evolution-api:latest` (runtime `v2.2.3`).
2. Em `v2.2.3`, envio para `@lid` retornava `400 exists:false` em parte dos cenarios.
3. Logs mostravam erros de sessao criptografica (`No matching sessions found`, `Bad MAC`) no mesmo jid.

## Correcao aplicada

- Upgrade da Evolution para imagem oficial atualizada:
  - `evoapicloud/evolution-api:v2.3.7`
- Arquivos atualizados:
  - `docker-compose.yml`
  - `docker-compose.local.yml`
  - `docker-compose-prod.yml`

## Evidencia de sucesso

1. Runtime após upgrade:
- `GET http://localhost:8080/` -> `version: 2.3.7`

2. Envio direto para `@lid`:
- `POST /message/sendText/fc-solucoes` com `number=223927414591688@lid`
- resposta `PENDING` sem `exists:false`.

3. Logs Evolution (`v2.3.7`):
- `OnWhatsappCache ... creating remoteJid=223927414591688@lid`
- `Sending message to 223927414591688@lid`
- `Update messages ... status: 3`

4. Backend (SaaS) após webhook de teste:
- ultima mensagem IA na conversa `223927414591688` com `enviada=true`.

## Blindagem funcional

- Fluxo de `@lid` voltou a responder no celular alvo sem depender de bind manual para este jid.
- Fila pendente segue ativa como fallback operacional.
- Flag `needs_manual_bind` agora e limpa automaticamente apos envio bem-sucedido.

## Observacao operacional

- Manter Evolution em versao >= `v2.3.7` para preservar suporte de roteamento `@lid`.
- Se houver novo erro de sessao, revalidar conexao da instancia (`connectionState=open`) e logs de cache/jid.
