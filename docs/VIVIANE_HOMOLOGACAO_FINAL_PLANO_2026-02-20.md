# Viviane - Plano de Homologacao Final (2026-02-20)

## Objetivo aprovado
- Manter uma unica persona comercial externa: **Viviane**.
- Base fixa de conhecimento: **regras de venda, produtos e precos oficiais**.
- Conversa natural (sem tom robotico e sem loop de perguntas).
- Nao perder lead no WhatsApp.
- Preparar proxima etapa multimodal: entender audio/imagem e enviar audio.

## Estado atual (apos hotfix)
- Resposta outbound voltou a chegar no WhatsApp com `@lid` (Evolution v2.3.7).
- Fluxo de handoff humano foi blindado para evitar repeticao de transferencia.
- Extracao de nome e cidade ficou mais natural em respostas curtas.
- Naturalidade conversational reforcada (humor + empatia + sem preco espontaneo).
- Persona Viviane foi separada em arquivo dedicado no COFRE:
  - `backend/COFRE/persona-skills/viviane/AGENT.md`

## Fonte de verdade da Viviane
- Prompt base da persona: `backend/COFRE/persona-skills/viviane/AGENT.md`
- Regras e precos carregados em runtime por:
  - `frontend/src/app/viva/REGRAS/Descrição_Detalhada_dos_Serviços_Rezeta_Brasil.md`
  - `frontend/src/app/viva/REGRAS/tabela_precos_ia_01_planilha1.csv`
- Motor do atendimento WhatsApp:
  - `backend/app/services/viva_ia_service.py`
  - `backend/app/services/viva_knowledge_service.py`

## Endpoints documentados para homologacao
- Snapshot runtime (OpenAPI real):
  - `docs/AUDIT/ENDPOINTS_RUNTIME_SNAPSHOT_2026-02-20_113105.md`
  - `docs/AUDIT/endpoints-runtime-2026-02-20_113105.json`
- Espelho institucional no COFRE:
  - `backend/COFRE/system/blindagem/audit/ENDPOINTS_RUNTIME_SNAPSHOT_2026-02-20_113105.md`
  - `backend/COFRE/system/blindagem/audit/endpoints-runtime-2026-02-20_113105.json`

## Escopo da proxima implementacao (homologacao final)
1. Naturalidade total sem perder contexto
- Responder perguntas sociais sem travar fluxo.
- Evitar repeticao de perguntas ja respondidas.
- Handoff humano sem retrabalho.

2. Persona enxuta + inteligencia livre controlada
- Trava de conhecimento em produtos/precos/regras.
- Fora disso, conversa natural orientada por GPT (sem scripts engessados).
- Sem sobrecarga de metrica no texto ao cliente.

3. Multimodal WhatsApp
- Entrada: texto, audio e imagem.
- Saida: texto e audio TTS institucional.
- Regras de seguranca para nao enviar documento sensivel por chat.

4. CRM/Funil
- Lead novo, qualificado, transferido humano, fechado/perdido.
- Registro consistente no SaaS sem duplicidade de estado.

## Gate de homologacao final (AWS)
- Conversa natural validada com 10 cenarios reais sem loop.
- Entrega WhatsApp validada em numeros diferentes (sem hardcode).
- Documentacao atualizada em `docs/` e `backend/COFRE/`.
- Rollback patch versionado em `backend/COFRE/system/blindagem/rollback/`.

