# Script de Instalação - FC Soluções Financeiras
# Execute como Administrador

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  INSTALADOR FC SOLUCOES FINANCEIRAS" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Verificar Admin
$admin = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $admin.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERRO: Execute como Administrador!" -ForegroundColor Red
    Write-Host "Botao direito no PowerShell -> Executar como administrador" -ForegroundColor Yellow
    exit 1
}

# Funcao para testar comando
function Test-Command {
    param($Command)
    try { 
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true 
    } catch { 
        return $false 
    }
}

# 1. Chocolatey
Write-Host "`n[1/6] Verificando Chocolatey..." -ForegroundColor Yellow
if (-not (Test-Command choco)) {
    Write-Host "Instalando Chocolatey..." -ForegroundColor Gray
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = 3072
    Invoke-Expression ((New-Object Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "OK!" -ForegroundColor Green
} else {
    Write-Host "Ja instalado!" -ForegroundColor Green
}

# 2. Docker
Write-Host "`n[2/6] Verificando Docker..." -ForegroundColor Yellow
if (-not (Test-Command docker)) {
    Write-Host "Instalando Docker Desktop (pode demorar)..." -ForegroundColor Gray
    choco install docker-desktop -y
    Write-Host "OK! REINICIE O PC DEPOIS!" -ForegroundColor Red
} else {
    Write-Host "Ja instalado!" -ForegroundColor Green
}

# 3. Node.js
Write-Host "`n[3/6] Verificando Node.js..." -ForegroundColor Yellow
if (-not (Test-Command node)) {
    Write-Host "Instalando Node.js..." -ForegroundColor Gray
    choco install nodejs-lts -y
    $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "OK!" -ForegroundColor Green
} else {
    Write-Host "Ja instalado!" -ForegroundColor Green
}

# 4. Python
Write-Host "`n[4/6] Verificando Python..." -ForegroundColor Yellow
if (-not (Test-Command python)) {
    Write-Host "Instalando Python 3.11..." -ForegroundColor Gray
    choco install python --version=3.11.0 -y
    $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "OK!" -ForegroundColor Green
} else {
    Write-Host "Ja instalado!" -ForegroundColor Green
}

# 5. Docker Containers
Write-Host "`n[5/6] Iniciando bancos de dados..." -ForegroundColor Yellow
Set-Location C:
Set-Location projetos
Set-Location fabio2

try {
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
    Write-Host "Aguardando Docker..." -ForegroundColor Gray
    Start-Sleep -Seconds 10
    docker-compose -f docker-compose.local.yml up -d
    Write-Host "OK! PostgreSQL e Redis iniciados!" -ForegroundColor Green
} catch {
    Write-Host "AVISO: Inicie o Docker Desktop manualmente" -ForegroundColor Yellow
}

# 6. Backend
Write-Host "`n[6/6] Configurando Backend..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path "venv")) {
    python -m venv venv
}

# Ativar e instalar
$activatePath = Join-Path $PWD "venv\Scripts\Activate.ps1"
& $activatePath

Write-Host "Instalando dependencias Python (aguarde)..." -ForegroundColor Gray
pip install -r requirements.txt -q

if (-not (Test-Path ".env")) {
    Copy-Item ..\.env.example .env
}

Write-Host "OK!" -ForegroundColor Green
Set-Location ..

# Frontend
Write-Host "`nConfigurando Frontend..." -ForegroundColor Yellow
Set-Location frontend

Write-Host "Instalando dependencias Node (aguarde)..." -ForegroundColor Gray
npm install --silent

if (-not (Test-Path ".env.local")) {
    Set-Content -Path ".env.local" -Value "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1"
}

Write-Host "OK!" -ForegroundColor Green
Set-Location ..

# FIM
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "  INSTALACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "`nProximos passos:" -ForegroundColor Yellow
Write-Host "1. Abra DOCKER DESKTOP e espere ficar verde" -ForegroundColor White
Write-Host "2. Abra 2 terminais (NAO como admin):" -ForegroundColor White
Write-Host "`nTERMINAL 1 - Backend:" -ForegroundColor Cyan
Write-Host "cd C:\projetos\fabio2\backend" -ForegroundColor Gray
Write-Host ".\venv\Scripts\activate" -ForegroundColor Gray
Write-Host "uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host "`nTERMINAL 2 - Frontend:" -ForegroundColor Cyan
Write-Host "cd C:\projetos\fabio2\frontend" -ForegroundColor Gray
Write-Host "npm run dev" -ForegroundColor Gray
Write-Host "`n3. Acesse: http://localhost:3000" -ForegroundColor Green

$resp = Read-Host "`nDeseja iniciar agora? (s/n)"
if ($resp -eq "s") {
    Start-Process powershell -ArgumentList "-NoExit","-Command","cd C:\projetos\fabio2\backend; .\venv\Scripts\activate; uvicorn app.main:app --reload"
    Start-Sleep -Seconds 3
    Start-Process powershell -ArgumentList "-NoExit","-Command","cd C:\projetos\fabio2\frontend; npm run dev"
    Start-Process "http://localhost:3000"
}
