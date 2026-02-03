# Configurar Projeto FC Solucoes (sem instalar programas)
# Execute na pasta do projeto

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAR PROJETO" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Set-Location C:
Set-Location projetos
Set-Location fabio2

# 1. Docker
Write-Host "`n[1/3] Iniciando Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "Docker ja esta rodando!" -ForegroundColor Green
} catch {
    Write-Host "Iniciando Docker Desktop..." -ForegroundColor Gray
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
    Write-Host "Aguarde 30 segundos..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

Write-Host "Subindo PostgreSQL e Redis..." -ForegroundColor Gray
docker-compose -f docker-compose.local.yml up -d
Write-Host "OK!" -ForegroundColor Green

# 2. Backend
Write-Host "`n[2/3] Configurando Backend..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path "venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Gray
    python -m venv venv
}

Write-Host "Ativando ambiente..." -ForegroundColor Gray
.\venv\Scripts\activate

Write-Host "Instalando dependencias (pode demorar)..." -ForegroundColor Gray
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ..\.env.example .env
}

Write-Host "OK!" -ForegroundColor Green
Set-Location ..

# 3. Frontend
Write-Host "`n[3/3] Configurando Frontend..." -ForegroundColor Yellow
Set-Location frontend

Write-Host "Instalando dependencias Node..." -ForegroundColor Gray
npm install

if (-not (Test-Path ".env.local")) {
    Set-Content -Path ".env.local" -Value "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1"
}

Write-Host "OK!" -ForegroundColor Green
Set-Location ..

# FIM
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "  PROJETO CONFIGURADO!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "`nPara iniciar:" -ForegroundColor Yellow
Write-Host "`nTERMINAL 1:" -ForegroundColor Cyan
Write-Host "cd C:\projetos\fabio2\backend" -ForegroundColor Gray
Write-Host ".\venv\Scripts\activate" -ForegroundColor Gray
Write-Host "uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host "`nTERMINAL 2:" -ForegroundColor Cyan
Write-Host "cd C:\projetos\fabio2\frontend" -ForegroundColor Gray
Write-Host "npm run dev" -ForegroundColor Gray
Write-Host "`nAcesse: http://localhost:3000" -ForegroundColor Green
