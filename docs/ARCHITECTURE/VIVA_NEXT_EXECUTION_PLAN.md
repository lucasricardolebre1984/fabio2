# VIVA - Plano de Execucao (Proximas Ordens)

> Data: 2026-02-10  
> Status atual: memoria hibrida ativa (curta + media + longa) e handoff operacional VIVA -> Viviane em producao local.

## Objetivo
Concluir estabilizacao final da VIVA com foco em qualidade criativa de campanhas, modularizacao do backend e operacao auditavel.

## Etapa 1 - Modularizacao do monolito VIVA (BUG-062)
- Quebrar `backend/app/api/v1/viva.py` em modulos de dominio:
  - `viva_chat_orchestrator.py`
  - `viva_campaign_service.py`
  - `viva_media_service.py`
  - `viva_memory_service.py` (ja criado, manter como dominio isolado)
- Criterio de aceite:
  - mesmas rotas/contratos HTTP;
  - regressao zero nos smoke tests existentes.

## Etapa 2 - Qualidade criativa de imagem FC/Rezeta (BUG-061)
- Introduzir memoria visual por marca/campanha (brief + imagem aprovada) para guiar variacoes futuras.
- Adicionar validacao automatica minima por heuristica de aderencia:
  - marca correta;
  - tema/oferta presentes no prompt final;
  - evitar repeticao de composicao/personagem.
- Criterio de aceite:
  - 3 geracoes seguidas por marca sem repeticao dominante de personagem/cena.

## Etapa 3 - Governanca de memoria
- Deduplicacao semantica da memoria longa (evitar reindex duplicado recorrente).
- Politica de retention:
  - media (Redis): TTL curto operacional;
  - longa (pgvector): retention por relevancia + janela temporal.
- Criterio de aceite:
  - endpoint de status com contadores estaveis e sem crescimento descontrolado.

## Etapa 4 - UX de recuperacao de contexto
- Frontend `/viva`:
  - listar sessoes (`/chat/sessions`);
  - permitir restaurar snapshot por sessao.
- Criterio de aceite:
  - usuario consegue limpar chat e reabrir contexto antigo manualmente em 2 cliques.

## Etapa 5 - Validacao final de entrega
- Checklist de prova de vida:
  - agenda natural;
  - handoff automatico para Viviane;
  - memoria vetorial com busca;
  - campanhas FC/Rezeta com aderencia visual.
- Criterio de aceite:
  - execucao completa sem erro `500` em fluxo principal.

## Risco principal atual
- Crescimento de complexidade no `viva.py` enquanto a modularizacao total (Etapa 1) nao for concluida.

## Mitigacao
- Manter protocolo docs-first + rollback institucional antes de cada bloco.

---

## Atualizacao 2026-02-13 - Plano Fechado em 3 Gates

### Gate 1 - Governanca e rollback (concluido)
- snapshot pre-change criado em `docs/ROLLBACK/rollback-20260213-140923-pre-doc-gates-*`;
- estado atual consolidado em `SESSION`, `STATUS`, `ARCHITECTURE` e `BUGSREPORT`.

### Gate 2 - Modularizacao comercial (em andamento)
- estruturar produto em modulos pre-configurados:
  1. `core_saas`
  2. `modulo_viva`
  3. `modulo_viviane`
  4. `modulo_campanhas`
  5. `modulo_memoria`
- manter um orquestrador unico com roteamento por skills (`generate_campanha` como skill obrigatoria).

### Gate 3 - Homologacao final (pendente)
- fala continua com stack de voz ao vivo padronizada;
- troca do avatar oficial da VIVA;
- definicao de voz institucional;
- certificacao semantica do RAG para venda modular premium.

Criterio de saida do Gate 3:
- voz consistente em multiplos dispositivos;
- avatar oficial ativo no frontend;
- RAG com score/relevancia validados por conjunto de casos reais.
