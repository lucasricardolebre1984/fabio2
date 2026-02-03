@echo off
chcp 65001 >nul
echo ==========================================
echo   INICIAR SERVIDORES FC SOLUCOES
echo ==========================================
echo.
echo Escolha uma opcao:
echo [1] Backend apenas
echo [2] Frontend apenas
echo [3] Ambos (2 janelas)
echo [4] Docker (PostgreSQL/Redis) apenas
echo.
set /p opcao="Opcao: "

if "%opcao%"=="1" goto backend
if "%opcao%"=="2" goto frontend
if "%opcao%"=="3" goto ambos
if "%opcao%"=="4" goto docker

goto fim

:backend
cd /d C:\projetos\fabio2\backend
powershell -NoExit -Command ".\venv\Scripts\activate; uvicorn app.main:app --reload"
goto fim

:frontend
cd /d C:\projetos\fabio2\frontend
powershell -NoExit -Command "npm run dev"
goto fim

:ambos
cd /d C:\projetos\fabio2
start powershell -NoExit -Command "cd backend; .\venv\Scripts\activate; uvicorn app.main:app --reload"
timeout /t 3 >nul
start powershell -NoExit -Command "cd frontend; npm run dev"
echo.
echo Servidores iniciados!
echo Acesse: http://localhost:3000
timeout /t 2 >nul
start http://localhost:3000
goto fim

:docker
cd /d C:\projetos\fabio2
docker-compose -f docker-compose.local.yml up -d
echo.
echo Docker iniciado!
echo PostgreSQL: localhost:5432
echo Redis: localhost:6379
pause

:fim
