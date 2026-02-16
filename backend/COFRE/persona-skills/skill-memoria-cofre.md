---
name: memoria_cofre
description: Define como registrar, consultar e apagar memorias no COFRE como trilha auditavel semantica. Acionar quando houver salvar memoria, consultar memoria, limpar memoria ou reset de historico.
---

# Skill Memoria COFRE

## Objetivo
Manter a memoria da VIVA rastreavel em um unico local: COFRE/memories.

## Regras
1. Toda escrita relevante gera espelho em COFRE/memories/<tabela>.
2. Todo delete funcional (UI/API) deve refletir delete correspondente no COFRE.
3. Nao manter memoria critica em caminho fora do COFRE.
4. Priorizar continuidade semantica: usar memoria para contexto, nao para engessar resposta.

## Tabelas espelhadas
- viva_chat_sessions
- viva_chat_messages
- viva_campanhas
- viva_handoff_tasks
- viva_memory_vectors
- redis_viva_memory_medium

## Comandos operacionais
- status da memoria: listar tabelas e ultimos eventos
- reset campanhas: limpar banco + arquivos de campanha no COFRE
- apagar campanha por id: remover banco + snapshot do item no COFRE
