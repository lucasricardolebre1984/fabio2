# COFRE x Banco - Mapeamento Canonico

- Data: 2026-02-20
- Regra alvo: `pastas = nomes das tabelas` em `backend/COFRE/memories/`

## Resultado
- Tabelas publicas: **21**
- Pastas correspondentes encontradas: **21**
- Faltantes: **0**
- Extras (nao tabela): **1**

## Tabelas mapeadas

| Tabela | Pasta COFRE | Status |
|---|---|---|
| `agenda` | `backend/COFRE/memories/agenda` | OK |
| `campanha_imagens` | `backend/COFRE/memories/campanha_imagens` | OK |
| `clientes` | `backend/COFRE/memories/clientes` | OK |
| `cofre_manifest_registry` | `backend/COFRE/memories/cofre_manifest_registry` | OK |
| `cofre_memory_registry` | `backend/COFRE/memories/cofre_memory_registry` | OK |
| `cofre_persona_registry` | `backend/COFRE/memories/cofre_persona_registry` | OK |
| `cofre_skill_registry` | `backend/COFRE/memories/cofre_skill_registry` | OK |
| `contrato_templates` | `backend/COFRE/memories/contrato_templates` | OK |
| `contratos` | `backend/COFRE/memories/contratos` | OK |
| `google_calendar_connections` | `backend/COFRE/memories/google_calendar_connections` | OK |
| `google_calendar_event_links` | `backend/COFRE/memories/google_calendar_event_links` | OK |
| `imagens` | `backend/COFRE/memories/imagens` | OK |
| `imagens_custos` | `backend/COFRE/memories/imagens_custos` | OK |
| `users` | `backend/COFRE/memories/users` | OK |
| `viva_campanhas` | `backend/COFRE/memories/viva_campanhas` | OK |
| `viva_chat_messages` | `backend/COFRE/memories/viva_chat_messages` | OK |
| `viva_chat_sessions` | `backend/COFRE/memories/viva_chat_sessions` | OK |
| `viva_handoff_tasks` | `backend/COFRE/memories/viva_handoff_tasks` | OK |
| `viva_memory_vectors` | `backend/COFRE/memories/viva_memory_vectors` | OK |
| `whatsapp_conversas` | `backend/COFRE/memories/whatsapp_conversas` | OK |
| `whatsapp_mensagens` | `backend/COFRE/memories/whatsapp_mensagens` | OK |

## Extras observados em COFRE/memories

- `redis_viva_memory_medium` (mantido: suporte de memoria/infra)

## Decisao de blindagem

- Nao mover nem renomear tabelas mapeadas (100% aderente).
- Qualquer nova tabela deve criar pasta homonima no COFRE.
- Validacao recorrente via `/api/v1/cofre/memories/sync-db-tables`.