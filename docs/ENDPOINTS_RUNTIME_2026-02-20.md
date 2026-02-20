# ENDPOINTS Runtime - Snapshot COFRE

- Data: 2026-02-20
- Origem: runtime FastAPI (app.main)
- Base URL: `http://localhost:8000/api/v1`

- Total metodo+rota: **81**

## agenda

| Metodo | Rota | Handler |
|---|---|---|
| `GET` | `/api/v1/agenda` | `list_eventos` |
| `POST` | `/api/v1/agenda` | `create_evento` |
| `GET` | `/api/v1/agenda/hoje` | `get_eventos_hoje` |
| `DELETE` | `/api/v1/agenda/{evento_id}` | `delete_evento` |
| `GET` | `/api/v1/agenda/{evento_id}` | `get_evento` |
| `PUT` | `/api/v1/agenda/{evento_id}` | `update_evento` |
| `PATCH` | `/api/v1/agenda/{evento_id}/concluir` | `concluir_evento` |

## auth

| Metodo | Rota | Handler |
|---|---|---|
| `POST` | `/api/v1/auth/login` | `login` |
| `POST` | `/api/v1/auth/logout` | `logout` |
| `GET` | `/api/v1/auth/me` | `get_me` |
| `POST` | `/api/v1/auth/refresh` | `refresh_token` |

## clientes

| Metodo | Rota | Handler |
|---|---|---|
| `GET` | `/api/v1/clientes` | `list_clientes` |
| `POST` | `/api/v1/clientes` | `create_cliente` |
| `POST` | `/api/v1/clientes/deduplicar-documentos` | `deduplicar_clientes_documento` |
| `GET` | `/api/v1/clientes/documento/{documento}` | `get_cliente_by_documento` |
| `POST` | `/api/v1/clientes/sincronizar-contratos` | `sincronizar_clientes_por_contratos` |
| `DELETE` | `/api/v1/clientes/{cliente_id}` | `delete_cliente` |
| `GET` | `/api/v1/clientes/{cliente_id}` | `get_cliente` |
| `PUT` | `/api/v1/clientes/{cliente_id}` | `update_cliente` |
| `GET` | `/api/v1/clientes/{cliente_id}/contratos` | `get_cliente_contratos` |
| `GET` | `/api/v1/clientes/{cliente_id}/historico` | `get_cliente_historico` |

## cofre

| Metodo | Rota | Handler |
|---|---|---|
| `GET` | `/api/v1/cofre/memories/status` | `cofre_memory_status` |
| `POST` | `/api/v1/cofre/memories/sync-db-tables` | `cofre_memory_sync_db_tables` |
| `GET` | `/api/v1/cofre/memories/tables` | `cofre_memory_tables` |
| `GET` | `/api/v1/cofre/memories/{table_name}/tail` | `cofre_memory_table_tail` |
| `GET` | `/api/v1/cofre/system/manifest` | `cofre_system_manifest` |
| `GET` | `/api/v1/cofre/system/schema-status` | `cofre_system_schema_status` |

## contratos

| Metodo | Rota | Handler |
|---|---|---|
| `GET` | `/api/v1/contratos` | `list_contratos` |
| `POST` | `/api/v1/contratos` | `create_contrato` |
| `GET` | `/api/v1/contratos/templates` | `list_templates` |
| `GET` | `/api/v1/contratos/templates/{template_id}` | `get_template` |
| `DELETE` | `/api/v1/contratos/{contrato_id}` | `delete_contrato` |
| `GET` | `/api/v1/contratos/{contrato_id}` | `get_contrato` |
| `PUT` | `/api/v1/contratos/{contrato_id}` | `update_contrato` |
| `POST` | `/api/v1/contratos/{contrato_id}/enviar` | `send_whatsapp` |
| `GET` | `/api/v1/contratos/{contrato_id}/pdf` | `generate_pdf` |

## google-calendar

| Metodo | Rota | Handler |
|---|---|---|
| `GET` | `/api/v1/google-calendar/callback` | `google_calendar_callback` |
| `GET` | `/api/v1/google-calendar/connect-url` | `google_calendar_connect_url` |
| `POST` | `/api/v1/google-calendar/disconnect` | `google_calendar_disconnect` |
| `GET` | `/api/v1/google-calendar/status` | `google_calendar_status` |
| `POST` | `/api/v1/google-calendar/sync/agenda/{evento_id}` | `google_calendar_sync_agenda_event` |

## health

| Metodo | Rota | Handler |
|---|---|---|
| `GET` | `/api/v1/health` | `health_check_v1` |

## viva

| Metodo | Rota | Handler |
|---|---|---|
| `POST` | `/api/v1/viva/audio/speak` | `speak_text` |
| `POST` | `/api/v1/viva/audio/transcribe` | `transcribe_audio` |
| `GET` | `/api/v1/viva/campanhas` | `list_campanhas` |
| `POST` | `/api/v1/viva/campanhas` | `save_campanha` |
| `POST` | `/api/v1/viva/campanhas/reset-all` | `reset_all_campanhas` |
| `POST` | `/api/v1/viva/campanhas/reset-patterns` | `reset_campanha_patterns` |
| `DELETE` | `/api/v1/viva/campanhas/{campanha_id}` | `delete_campanha` |
| `GET` | `/api/v1/viva/campanhas/{campanha_id}` | `get_campanha` |
| `GET` | `/api/v1/viva/capabilities` | `get_capabilities` |
| `POST` | `/api/v1/viva/chat` | `chat_with_viva` |
| `POST` | `/api/v1/viva/chat/session/new` | `create_chat_session` |
| `GET` | `/api/v1/viva/chat/sessions` | `list_chat_sessions` |
| `GET` | `/api/v1/viva/chat/snapshot` | `get_chat_snapshot` |
| `POST` | `/api/v1/viva/chat/stream` | `chat_with_viva_stream` |
| `GET` | `/api/v1/viva/handoff` | `list_handoff` |
| `POST` | `/api/v1/viva/handoff/process-due` | `process_handoff_due` |
| `POST` | `/api/v1/viva/handoff/schedule` | `schedule_handoff` |
| `POST` | `/api/v1/viva/image/generate` | `generate_image` |
| `GET` | `/api/v1/viva/modules/status` | `get_modules_status` |
| `GET` | `/api/v1/viva/persona/status` | `get_persona_status` |
| `GET` | `/api/v1/viva/status` | `viva_status` |
| `GET` | `/api/v1/viva/tts/status` | `tts_status` |
| `POST` | `/api/v1/viva/video/generate` | `generate_video` |
| `GET` | `/api/v1/viva/video/result/{task_id}` | `get_video_result` |
| `POST` | `/api/v1/viva/vision` | `analyze_image` |
| `POST` | `/api/v1/viva/vision/upload` | `analyze_image_upload` |

## webhook

| Metodo | Rota | Handler |
|---|---|---|
| `GET` | `/api/v1/webhook/evolution` | `evolution_webhook_verify` |
| `POST` | `/api/v1/webhook/evolution` | `evolution_webhook` |

## whatsapp

| Metodo | Rota | Handler |
|---|---|---|
| `POST` | `/api/v1/whatsapp/conectar` | `conectar` |
| `POST` | `/api/v1/whatsapp/desconectar` | `desconectar` |
| `POST` | `/api/v1/whatsapp/enviar-arquivo` | `enviar_arquivo` |
| `POST` | `/api/v1/whatsapp/enviar-texto` | `enviar_texto` |
| `GET` | `/api/v1/whatsapp/status` | `get_status` |

## whatsapp-chat

| Metodo | Rota | Handler |
|---|---|---|
| `GET` | `/api/v1/whatsapp-chat/conversas` | `listar_conversas` |
| `GET` | `/api/v1/whatsapp-chat/conversas/{conversa_id}` | `obter_conversa` |
| `POST` | `/api/v1/whatsapp-chat/conversas/{conversa_id}/arquivar` | `arquivar_conversa` |
| `POST` | `/api/v1/whatsapp-chat/conversas/{conversa_id}/bind-number` | `bind_numero_real` |
| `GET` | `/api/v1/whatsapp-chat/conversas/{conversa_id}/mensagens` | `listar_mensagens` |
| `GET` | `/api/v1/whatsapp-chat/status` | `status_whatsapp` |
