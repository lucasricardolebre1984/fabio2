# ROLLBACK EVOLUTION API - Script de reversão (PowerShell)
# Data: 2026-02-03

Write-Host "🔙 Iniciando Rollback da Evolution API..." -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Yellow

# 1. Parar e remover container evolution
Write-Host "1. Parando container evolution-api..." -ForegroundColor Cyan
docker stop fabio2-evolution 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "   Container já parado ou não existe" -ForegroundColor Gray }

docker rm fabio2-evolution 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "   Container já removido ou não existe" -ForegroundColor Gray }

# 2. Restaurar docker-compose original (do git)
Write-Host "2. Restaurando docker-compose.yml original..." -ForegroundColor Cyan
git checkout docker-compose.yml
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao restaurar docker-compose.yml" -ForegroundColor Red
    exit 1
}

# 3. Remover volume de dados da evolution
Write-Host "3. Limpando dados temporários..." -ForegroundColor Cyan
docker volume rm fabio2_evolution_data 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "   Volume já removido ou não existe" -ForegroundColor Gray }

# 4. Recriar container evolution
Write-Host "4. Recriando container evolution-api..." -ForegroundColor Cyan
docker-compose up -d evolution-api

Write-Host "================================================" -ForegroundColor Green
Write-Host "✅ Rollback concluído!" -ForegroundColor Green
Write-Host ""
Write-Host "Status dos containers:" -ForegroundColor Cyan
docker ps --filter name=evolution --format "table {{.Names}}\t{{.Status}}"
