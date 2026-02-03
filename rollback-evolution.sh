#!/bin/bash
# ROLLBACK EVOLUTION API - Script de reversão
# Data: 2026-02-03
# Uso: ./rollback-evolution.sh

echo "🔙 Iniciando Rollback da Evolution API..."
echo "================================================"

# 1. Parar e remover container evolution
echo "1. Parando container evolution-api..."
docker stop fabio2-evolution 2>/dev/null || true
docker rm fabio2-evolution 2>/dev/null || true

# 2. Restaurar docker-compose original (do git)
echo "2. Restaurando docker-compose.yml original..."
git checkout docker-compose.yml

# 3. Remover volume de dados da evolution (opcional - mantém instâncias)
echo "3. Limpando dados temporários..."
docker volume rm fabio2_evolution_data 2>/dev/null || true

# 4. Recriar container evolution sem configuração de banco
echo "4. Recriando container evolution-api..."
docker-compose up -d evolution-api

echo "================================================"
echo "✅ Rollback concluído!"
echo ""
echo "Status:"
docker ps --filter name=evolution --format "table {{.Names}}\t{{.Status}}"
