# Script de Setup Automático - Windows
# Executar como: .\setup-windows.ps1

Write-Host "🚀 FC Soluções Financeiras - Setup Local" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Verificar se está na pasta correta
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Erro: Execute este script na pasta raiz do projeto (fabio2/)" -ForegroundColor Red
    exit 1
}

# Verificar Docker
Write-Host "`n📦 Verificando Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "✅ Docker encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker não encontrado. Instale o Docker Desktop:" -ForegroundColor Red
    Write-Host "   https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    exit 1
}

# Verificar Python
Write-Host "`n🐍 Verificando Python..." -ForegroundColor Yellow
try {
    python --version | Out-Null
    Write-Host "✅ Python encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado. Instale o Python 3.11+:" -ForegroundColor Red
    Write-Host "   https://python.org" -ForegroundColor Cyan
    exit 1
}

# Verificar Node
Write-Host "`n⬢ Verificando Node.js..." -ForegroundColor Yellow
try {
    node --version | Out-Null
    Write-Host "✅ Node.js encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js não encontrado. Instale o Node.js 18+:" -ForegroundColor Red
    Write-Host "   https://nodejs.org" -ForegroundColor Cyan
    exit 1
}

# Subir Docker
Write-Host "`n🐳 Iniciando containers Docker..." -ForegroundColor Yellow
docker-compose up -d postgres redis

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostgreSQL e Redis iniciados" -ForegroundColor Green
} else {
    Write-Host "❌ Erro ao iniciar Docker" -ForegroundColor Red
    exit 1
}

# Setup Backend
Write-Host "`n⚙️ Configurando Backend..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path "venv")) {
    Write-Host "   Criando ambiente virtual..." -ForegroundColor Gray
    python -m venv venv
}

Write-Host "   Ativando ambiente virtual..." -ForegroundColor Gray
.\venv\Scripts\activate

Write-Host "   Instalando dependências..." -ForegroundColor Gray
pip install -r requirements.txt -q

if (-not (Test-Path ".env")) {
    Write-Host "   Criando arquivo .env..." -ForegroundColor Gray
    Copy-Item ..\.env.example .env
}

Write-Host "✅ Backend configurado" -ForegroundColor Green
Set-Location ..

# Setup Frontend
Write-Host "`n🎨 Configurando Frontend..." -ForegroundColor Yellow
Set-Location frontend

Write-Host "   Instalando dependências..." -ForegroundColor Gray
npm install --silent

if (-not (Test-Path ".env.local")) {
    Write-Host "   Criando .env.local..." -ForegroundColor Gray
    Set-Content -Path ".env.local" -Value "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1"
}

Write-Host "✅ Frontend configurado" -ForegroundColor Green
Set-Location ..

# Resumo
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "✅ SETUP CONCLUÍDO!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "`nPara iniciar o sistema:" -ForegroundColor Yellow
Write-Host "`n1. Terminal 1 (Backend):" -ForegroundColor Cyan
Write-Host "   cd backend; .\venv\Scripts\activate; uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "`n2. Terminal 2 (Frontend):" -ForegroundColor Cyan
Write-Host "   cd frontend; npm run dev" -ForegroundColor White
Write-Host "`n3. Acesse: http://localhost:3000" -ForegroundColor Green
Write-Host "`n📖 Leia o arquivo SETUP.md para mais detalhes" -ForegroundColor Yellow
