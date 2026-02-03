@echo off
chcp 65001 >nul
echo 🚀 FC Soluções Financeiras - Iniciar Local
echo ===========================================

REM Verificar Docker
docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está rodando! Inicie o Docker Desktop primeiro.
    pause
    exit /b 1
)

REM Subir bancos
echo 📦 Iniciando PostgreSQL e Redis...
docker-compose -f docker-compose.local.yml up -d

if errorlevel 1 (
    echo ❌ Erro ao iniciar Docker
    pause
    exit /b 1
)

echo ✅ Bancos de dados iniciados!
echo.
echo 📋 Próximos passos:
echo.
echo 1. Abra o TERMINAL 1 e execute:
echo    cd backend
echo    .\venv\Scripts\activate
echo    uvicorn app.main:app --reload
echo.
echo 2. Abra o TERMINAL 2 e execute:
echo    cd frontend
echo    npm run dev
echo.
echo 3. Acesse: http://localhost:3000
echo.
pause
