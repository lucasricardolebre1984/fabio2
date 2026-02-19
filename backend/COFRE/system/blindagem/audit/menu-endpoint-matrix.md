# Auditoria Institucional: Menu -> API -> Banco -> COFRE

Gerado em: `2026-02-16T05:42:55.224467+00:00`

## Veredito por menu

| Menu | Rota | Status | Endpoints faltando | Tabelas faltando | COFRE faltando |
|---|---|---|---:|---:|---:|
| Chat IA VIVA | `/viva` | `ok` | 0 | 0 | 0 |
| Campanhas | `/campanhas` | `ok` | 0 | 0 | 0 |
| Contratos | `/contratos` | `ok` | 0 | 0 | 0 |
| Clientes | `/clientes` | `ok` | 0 | 0 | 0 |
| Agenda | `/agenda` | `ok` | 0 | 0 | 0 |
| WhatsApp | `/whatsapp` | `ok` | 0 | 0 | 0 |

## Checks semanticos (VIVA)

- `contracts_list_intent`: OK
- `contract_templates_intent`: OK
- `clients_list_intent`: OK
- `services_catalog_intent`: OK
- `agenda_guardrail_recent_prompt`: OK
- `agenda_guardrail_simple_confirmation`: OK

## Detalhes por menu

### Chat IA VIVA (`/viva`)
- Status: `ok`
- Pages: `frontend\src\app\viva\page.tsx`
- Frontend endpoints: `/api/v1/viva/audio/speak`, `/api/v1/viva/audio/transcribe`, `/api/v1/viva/chat`, `/api/v1/viva/chat/stream`, `/api/v1/viva/status`, `/api/v1/viva/tts/status`, `/api/v1/viva/vision/upload`
- Missing backend endpoints: nenhum
- Expected DB tables: `viva_chat_sessions`, `viva_chat_messages`, `viva_memory_vectors`
- Missing DB tables: nenhuma
- Missing COFRE dirs: nenhuma

### Campanhas (`/campanhas`)
- Status: `ok`
- Pages: `frontend\src\app\(dashboard)\campanhas\page.tsx`
- Frontend endpoints: `/api/v1/viva/campanhas/reset-all`, `/api/v1/viva/campanhas/{param}`
- Missing backend endpoints: nenhum
- Expected DB tables: `viva_campanhas`
- Missing DB tables: nenhuma
- Missing COFRE dirs: nenhuma

### Contratos (`/contratos`)
- Status: `ok`
- Pages: `frontend\src\app\(dashboard)\contratos\page.tsx`
- Frontend endpoints: nenhum detectado
- Missing backend endpoints: nenhum
- Expected DB tables: `contratos`, `contrato_templates`
- Missing DB tables: nenhuma
- Missing COFRE dirs: nenhuma

### Clientes (`/clientes`)
- Status: `ok`
- Pages: `frontend\src\app\(dashboard)\clientes\page.tsx`
- Frontend endpoints: `/api/v1/clientes`, `/api/v1/clientes/deduplicar-documentos`, `/api/v1/clientes/sincronizar-contratos`, `/api/v1/clientes/{param}`, `/api/v1/clientes/{param}/contratos`
- Missing backend endpoints: nenhum
- Expected DB tables: `clientes`
- Missing DB tables: nenhuma
- Missing COFRE dirs: nenhuma

### Agenda (`/agenda`)
- Status: `ok`
- Pages: `frontend\src\app\(dashboard)\agenda\page.tsx`
- Frontend endpoints: `/api/v1/agenda`, `/api/v1/agenda/{param}`, `/api/v1/agenda/{param}/concluir`, `/api/v1/google-calendar/connect-url`, `/api/v1/google-calendar/disconnect`, `/api/v1/google-calendar/status`, `/api/v1/google-calendar/sync/agenda/{param}`
- Missing backend endpoints: nenhum
- Expected DB tables: `agenda`
- Missing DB tables: nenhuma
- Missing COFRE dirs: nenhuma

### WhatsApp (`/whatsapp`)
- Status: `ok`
- Pages: `frontend\src\app\(dashboard)\whatsapp\page.tsx`
- Frontend endpoints: `/api/v1/whatsapp/desconectar`, `/api/v1/whatsapp/status`
- Missing backend endpoints: nenhum
- Expected DB tables: `whatsapp_conversas`, `whatsapp_mensagens`
- Missing DB tables: nenhuma
- Missing COFRE dirs: nenhuma
