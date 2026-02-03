# Script de Instalação Completa - FC Soluções Financeiras
# Executar como Administrador no PowerShell

param(
    [switch]$SkipDocker,
    [switch]$SkipNode,
    [switch]$SkipPython
)

Write-Host "🚀 Instalador FC Soluções Financeiras" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Verificar se é administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "❌ Execute este script como Administrador!" -ForegroundColor Red
    Write-Host "   Clique com botão direito no PowerShell → 'Executar como administrador'" -ForegroundColor Yellow
    exit 1
}

# Função para verificar comando existe
function Test-Command($Command) {
    try { Get-Command $Command -ErrorAction Stop | Out-Null; return $true }
    catch { return $false }
}

# 1. Instalar Chocolatey (gerenciador de pacotes)
Write-Host "`n📦 Verificando Chocolatey..." -ForegroundColor Yellow
if (-not (Test-Command choco)) {
    Write-Host "   Instalando Chocolatey..." -ForegroundColor Gray
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    # Recarregar PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    Write-Host "   ✅ Chocolatey instalado" -ForegroundColor Green
} else {
    Write-Host "   ✅ Chocolatey já instalado" -ForegroundColor Green
}

# 2. Instalar Docker Desktop
if (-not $SkipDocker) {
    Write-Host "`n🐳 Verificando Docker..." -ForegroundColor Yellow
    if (-not (Test-Command docker)) {
        Write-Host "   Instalando Docker Desktop..." -ForegroundColor Gray
        Write-Host "   (Isso pode levar alguns minutos...)" -ForegroundColor Gray
        choco install docker-desktop -y
        Write-Host "   ✅ Docker Desktop instalado" -ForegroundColor Green
        Write-Host "   ⚠️  REINICIE O COMPUTADOR após a instalação!" -ForegroundColor Red -BackgroundColor Yellow
        Write-Host "   Depois execute este script novamente." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "   ✅ Docker já instalado" -ForegroundColor Green
    }
} else {
    Write-Host "`n🐳 Pulando Docker (parâmetro -SkipDocker)" -ForegroundColor Gray
}

# 3. Instalar Node.js
if (-not $SkipNode) {
    Write-Host "`n⬢ Verificando Node.js..." -ForegroundColor Yellow
    if (-not (Test-Command node)) {
        Write-Host "   Instalando Node.js LTS..." -ForegroundColor Gray
        choco install nodejs-lts -y
        # Recarregar PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        Write-Host "   ✅ Node.js instalado" -ForegroundColor Green
    } else {
        $nodeVersion = node --version
        Write-Host "   ✅ Node.js já instalado ($nodeVersion)" -ForegroundColor Green
    }
} else {
    Write-Host "`n⬢ Pulando Node.js (parâmetro -SkipNode)" -ForegroundColor Gray
}

# 4. Instalar Python
if (-not $SkipPython) {
    Write-Host "`n🐍 Verificando Python..." -ForegroundColor Yellow
    if (-not (Test-Command python)) {
        Write-Host "   Instalando Python 3.11..." -ForegroundColor Gray
        choco install python --version=3.11.0 -y
        # Recarregar PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        Write-Host "   ✅ Python instalado" -ForegroundColor Green
    } else {
        $pythonVersion = python --version
        Write-Host "   ✅ Python já instalado ($pythonVersion)" -ForegroundColor Green
    }
} else {
    Write-Host "`n🐍 Pulando Python (parâmetro -SkipPython)" -ForegroundColor Gray
}

# 5. Configurar Projeto
Write-Host "`n⚙️ Configurando Projeto..." -ForegroundColor Yellow
Set-Location $PSScriptRoot

# Verificar se está na pasta correta
if (-not (Test-Path "docker-compose.local.yml")) {
    Write-Host "❌ Erro: Execute este script na pasta c:\projetos\fabio2\" -ForegroundColor Red
    exit 1
}

# Iniciar Docker
Write-Host "`n🐳 Iniciando Docker..." -ForegroundColor Yellow
try {
    # Tentar iniciar Docker Desktop
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
    Write-Host "   Aguardando Docker iniciar (30 segundos)..." -ForegroundColor Gray
    Start-Sleep -Seconds 30
    
    # Verificar se Docker está rodando
    docker ps | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Docker está rodando" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Docker pode estar iniciando ainda..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Não foi possível iniciar Docker automaticamente" -ForegroundColor Yellow
    Write-Host "   Inicie o Docker Desktop manualmente" -ForegroundColor Yellow
}

# Subir containers
Write-Host "`n📦 Subindo PostgreSQL e Redis..." -ForegroundColor Yellow
docker-compose -f docker-compose.local.yml up -d
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Containers iniciados" -ForegroundColor Green
} else {
    Write-Host "   ❌ Erro ao iniciar containers" -ForegroundColor Red
    Write-Host "   Verifique se o Docker Desktop está rodando" -ForegroundColor Yellow
}

# Configurar Backend
Write-Host "`n⚙️ Configurando Backend..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path "venv")) {
    Write-Host "   Criando ambiente virtual Python..." -ForegroundColor Gray
    python -m venv venv
}

Write-Host "   Ativando ambiente virtual..." -ForegroundColor Gray
.\venv\Scripts\activate

Write-Host "   Instalando dependências Python (isso pode levar alguns minutos)..." -ForegroundColor Gray
pip install -r requirements.txt -q

if (-not (Test-Path ".env")) {
    Write-Host "   Criando arquivo .env..." -ForegroundColor Gray
    Copy-Item ..\.env.example .env
}

Write-Host "   ✅ Backend configurado" -ForegroundColor Green
Set-Location ..

# Configurar Frontend
Write-Host "`n🎨 Configurando Frontend..." -ForegroundColor Yellow
Set-Location frontend

Write-Host "   Instalando dependências Node.js (isso pode levar alguns minutos)..." -ForegroundColor Gray
npm install --silent

if (-not (Test-Path ".env.local")) {
    Write-Host "   Criando arquivo .env.local..." -ForegroundColor Gray
    Set-Content -Path ".env.local" -Value "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1"
}

Write-Host "   ✅ Frontend configurado" -ForegroundColor Green
Set-Location ..

# Resumo final
Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "✅ INSTALAÇÃO CONCLUÍDA!" -ForegroundColor Green -BackgroundColor Black
Write-Host "======================================" -ForegroundColor Cyan

Write-Host "`n🚀 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "`n1. Abra o Docker Desktop e espere ficar verde" -ForegroundColor Cyan
Write-Host "2. Abra 2 terminais PowerShell (NÃO como admin):" -ForegroundColor Cyan
Write-Host "`n   TERMINAL 1 - Backend:" -ForegroundColor White
Write-Host "   cd c:\projetos\fabio2\backend" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\activate" -ForegroundColor Gray
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host "`n   TERMINAL 2 - Frontend:" -ForegroundColor White
Write-Host "   cd c:\projetos\fabio2\frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host "`n3. Acesse: http://localhost:3000" -ForegroundColor Green

Write-Host "`n📖 Para criar usuário, veja: teste-local.md" -ForegroundColor Yellow

# Perguntar se quer iniciar agora
Write-Host "`n" -NoNewline
$iniciar = Read-Host "Deseja iniciar os servidores agora? (s/n)"
if ($iniciar -eq 's' -or $iniciar -eq 'S') {
    Write-Host "`n🚀 Iniciando..." -ForegroundColor Green
    
    # Terminal 1 - Backend
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\projetos\fabio2\backend; .\venv\Scripts\activate; uvicorn app.main:app --reload"
    
    # Aguardar um pouco
    Start-Sleep -Seconds 3
    
    # Terminal 2 - Frontend
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\projetos\fabio2\frontend; npm run dev"
    
    Write-Host "`n✅ Terminais abertos! Acesse: http://localhost:3000" -ForegroundColor Green
    Start-Process "http://localhost:3000"
}

Write-Host "`n✅ Pronto!" -ForegroundColor Green
